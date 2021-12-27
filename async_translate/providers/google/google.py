import os
from typing import Dict

from aiocache import cached
from google.cloud.translate_v3.services.translation_service.async_client import TranslationServiceAsyncClient

from async_translate.abc import BaseProvider, ONE_DAY, Translation
from async_translate.errors import TranslatorException


class Google(BaseProvider):
    icon = "https://i.imgur.com/jDPXiQh.png"

    def __init__(self, credentials=None, parent: str = None):
        """
        :param credentials: Optional credentials dict
        :param parent: Optional string of parent project. If not present, will get from GOOGLE_TRANSLATE_PARENT env var
        """
        if credentials:
            self.client = TranslationServiceAsyncClient.from_service_account_info(credentials)
        else:
            self.client = TranslationServiceAsyncClient()
        try:
            self.parent = parent or os.environ['GOOGLE_TRANSLATE_PARENT']
        except KeyError:
            raise TranslatorException("Please set/export the 'GOOGLE_TRANSLATE_PARENT' environment variable. "
                                      "Ex: 'projects/mr-translate-1577912381600/locations/global'")

    @cached(ttl=ONE_DAY)
    async def get_languages(self, locale="en") -> Dict[str, str]:
        return {
            lang.language_code: lang.display_name
            for lang in filter(
                lambda l: l.support_source and l.support_target,
                (await self.client.get_supported_languages(parent=self.parent, display_language_code=locale)).languages)
        }

    async def detect(self, content) -> str:
        res = (await self.client.detect_language(parent=self.parent, content=content)).languages[0]
        return res.language_code

    async def translate(self, content: str, to: str, source="", **options) -> Translation:
        """
        Translates text using the Google API
        :param content: the text to translate
        :param to: the language code to translate to
        :param source: Optional language to translate from
        :return: the translation
        """
        params = {"contents": [content],
                  "target_language_code": to,
                  "parent": self.parent,
                  'mime_type': 'text/plain'}
        if source:
            params['source_language_code'] = source

        translation = (await self.client.translate_text(**params)).translations[0]
        return Translation(
            # text=unescape(translation.translated_text),
            text=translation.translated_text,
            to=to,
            source=translation.detected_language_code or None
        )
