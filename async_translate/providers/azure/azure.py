import uuid
from json import JSONDecodeError
from typing import Dict, Optional, Union, Sequence, List, Any

from aiohttp_retry import RetryClient, ExponentialRetry

from async_translate.abc import BaseProvider, Translation
from async_translate.errors import TranslatorException, LanguageNotSupported

MS_API_VER = "?api-version=3.0"
retry_options = ExponentialRetry(attempts=10, start_timeout=8.0, factor=1.3, statuses={429})


class AllKeysExhausted(TranslatorException):
    pass


class RequestException(TranslatorException):
    def __init__(self, base, code: int, message: str):
        self.code: int = code
        self.message: str = message
        super().__init__(base)


class Azure(BaseProvider):
    """
    Microsoft Azure Cognitive Services translator Backend
    """
    backend = "azure"
    ms_endpoint = "https://api.cognitive.microsofttranslator.com/"
    icon = "https://connectoricons-prod.azureedge.net/microsofttranslator/icon_1.0.1303.1871.png"

    def __init__(self, api_keys: Union[str, Sequence[str]]):
        if isinstance(api_keys, str):
            self._api_keys: List[str] = [api_keys]
        else:
            if len(api_keys) < 1:
                raise TranslatorException("No API keys provided")
            self._api_keys: Sequence[str] = api_keys
        self.api_iter = iter(self._api_keys)
        self.current_key = next(self.api_iter)
        self.session: Optional[RetryClient] = None

    @property
    def headers(self):
        return {
            'Ocp-Apim-Subscription-Key': self.current_key,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

    async def _request(self, endpoint, method='post', params: Optional[Dict] = None, json: Any = None,
                       api_key_override: Optional[str] = None):
        if params is None:
            params = {}

        headers = self.headers

        if api_key_override:
            headers['Ocp-Apim-Subscription-Key'] = api_key_override

        if accept_language := params.pop('accept_language', None):
            headers['Accept-Language'] = accept_language
        url = self.ms_endpoint + endpoint + MS_API_VER + "&"
        async with self.session.request(method=method, url=url, params=params, headers=headers, json=json) as resp:
            try:
                data = await resp.json(content_type=None)
                try:
                    if error := data.get('error'):
                        # Handle Free Quota Errors
                        if error['code'] in (401000, 403000, 403001, 429000, 429001, 429002):
                            full_stop = False
                            try:
                                self.current_key = next(self.api_iter)
                            except StopIteration:
                                self.api_iter = iter(self._api_keys)
                                self.current_key = next(self.api_iter)
                                full_stop = True
                            else:
                                return await self._request(endpoint, method, params, json)
                            if full_stop:
                                raise AllKeysExhausted("All API Keys Exhausted", error)
                        else:  # Handle Generic Errors
                            raise RequestException(error, **error)
                except AttributeError:
                    pass
                return data
            except JSONDecodeError as e:
                raise TranslatorException(await resp.text()) from e

    async def get_languages(self, locale=None, *args, **kwargs) -> Dict[str, str]:
        # Setup retry client
        if not self.session:
            self.session = RetryClient(retry_options=retry_options)

        raw_languages = await self._request('languages', 'get',
                                            {'scope': 'translation', 'accept_language': locale})
        return {key: value['name'] for key, value in raw_languages['translation'].items()}

    async def close(self):
        # noinspection PyProtectedMember
        if self.session._closed:
            return
        await self.session.close()

    async def detect(self, content, key_override: Optional[str] = None) -> str:
        """Detect the language of the given content"""
        json_content = [{"text": content}]
        result = await self._request('detect', json=json_content)
        return result[0]['language']

    async def translate(self, content: str, to: str, source="", **options) -> Translation:
        """
        Translates text using the Azure API
        :param content: the text to translate
        :param to: the language code to translate to
        :param source: Optional language to translate from
        :return: the translation
        """
        params = {
            'to': to,
            'profanityAction': ('NoAction', 'Marked', 'Marked')[options.get('profanity_filter') or 0]
        }
        if source:
            params['from'] = source

        if params['profanityAction'] == 1:
            params['profanityMarker'] = 'Tag'

        json_content = [{"text": content}]
        try:
            translation_response = (await self._request('translate', params=params, json=json_content))
        except RequestException as te:
            if te.code in (400004, 400036, 400018, 400035):  # Invalid/missing language
                if te.code in (400018, 400035):  # Invalid 'from'
                    language = source
                    direction = "from"
                else:  # Invalid 'to'
                    language = to
                    direction = "to"
                raise LanguageNotSupported(language=language, direction=direction) from te
            raise

        entry = translation_response[0]
        return Translation(
            text=entry['translations'][0]['text'],
            to=entry['translations'][0]['to'],
            source=entry.get('detectedLanguage', {}).get('language')
        )
