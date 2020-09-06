import os
import uuid
from typing import Dict

import aiohttp
from aiocache import cached

from async_translate.abc import BaseProvider, ONE_DAY, Translation

MS_API_VER = "?api-version=3.0"


class Azure(BaseProvider):
    """
    Microsoft Azure Cognitive Services translator Backend
    Required environment variables:
    `MS_TRANSLATE_KEY`
    """
    backend = "azure"
    ms_endpoint = "https://api.cognitive.microsofttranslator.com/"
    icon = "https://connectoricons-prod.azureedge.net/microsofttranslator/icon_1.0.1303.1871.png"

    def __init__(self):
        self.session = aiohttp.ClientSession()
        if 'MS_TRANSLATE_KEY' not in os.environ:
            raise Exception("Please set/export the 'MS_TRANSLATE_KEY' environment variable.")
        self.ms_key = os.environ['MS_TRANSLATE_KEY']

    @property
    def headers(self):
        return {
            'Ocp-Apim-Subscription-Key': self.ms_key,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

    @cached(ttl=ONE_DAY)
    async def get_languages(self) -> Dict[str, str]:
        url = self.ms_endpoint + "languages" + MS_API_VER + "&scope=translation"
        async with self.session.get(url, headers=self.headers) as resp:
            raw_langs = (await resp.json())['translation']

            return {key: value['name'] for key, value in raw_langs.items()}

    async def detect(self, content) -> str:
        """Detect the language of the given content"""
        url = self.ms_endpoint + "detect" + MS_API_VER
        json_content = [{"text": content}]
        async with self.session.post(url, headers=self.headers, json=json_content) as resp:

            return (await resp.json())[0]['language']

    async def translate(self, content: str, to: str, fro="", **options) -> [Translation]:
        """
        Translates text using the Azure API
        :param content: the text to translate
        :param to: the language code to translate to
        :param fro: Optional language to translate from
        :return: the translation
        """
        url = self.ms_endpoint + "translate" + MS_API_VER + "&to=" + to
        if fro:
            url += "&from=" + fro

        profanity_filter = options.get('profanity_filter') or 0

        url += "&profanityAction=" + ['NoAction', 'Marked', 'Marked'][profanity_filter]
        if profanity_filter == 1:
            url += "&profanityMarker=Tag"

        json_content = [{"text": content}]
        async with self.session.post(url, headers=self.headers, json=json_content) as resp:
            json_response = (await resp.json())[0]
            translation_response = []

            try:
                detected_language = json_response.get('detectedLanguage').get('language')
            except AttributeError:
                detected_language = None

            if ts := json_response.get('translations'):
                for translation in ts:
                    translation_response.append(
                        Translation(text=translation.get('text'), to=translation.get('to'),
                                    backend=self,
                                    detectedLanguage=detected_language)
                    )
            return translation_response
