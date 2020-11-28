from html import unescape
import os
from typing import Dict

from aiocache import cached
from google.cloud.translate_v3.services.translation_service.async_client import TranslationServiceAsyncClient

from async_translate.abc import BaseProvider, ONE_DAY, Translation


class Google(BaseProvider):
    icon = "https://i.imgur.com/jDPXiQh.png"

    def __init__(self, parent: str = None):
        """

        :param parent: Optional string of parent project. If not present, will get from GOOGLE_TRANSLATE_PARENT env var
        """
        self.client = TranslationServiceAsyncClient()
        try:
            self.parent = parent or os.environ['GOOGLE_TRANSLATE_PARENT']
        except KeyError:
            raise Exception("Please set/export the 'GOOGLE_TRANSLATE_PARENT' environment variable. "
                            "Ex: 'projects/mr-translate-1577912381600/locations/global'")

    @cached(ttl=ONE_DAY)
    async def get_languages(self, display_language_code="en") -> Dict[str, str]:
        langs = (await self.client.get_supported_languages(parent=self.parent,
                                                           display_language_code=display_language_code)).languages
        return {lang.language_code: lang.display_name
                for lang in
                filter(lambda l: l.support_source and l.support_target, langs)
                }

    async def detect(self, content) -> str:
        res = (await self.client.detect_language(parent=self.parent, content=content)).languages[0]
        return res.language_code

    async def translate(self, content: str, to: str, fro="", **options) -> [Translation]:
        """
        Translates text using the Google API
        :param content: the text to translate
        :param to: the language code to translate to
        :param fro: Optional language to translate from
        :return: the translation
        """
        params = {"contents": [content],
                  "target_language_code": to,
                  "parent": self.parent}
        if fro:
            params['source_language_code'] = fro

        translation_response = []
        translations = (await self.client.translate_text(**params)).translations
        for trans in translations:
            translation_response.append(Translation(
                to=to, text=unescape(trans.translated_text),
                provider=self,
                detectedLanguage=trans.detected_language_code or None
            ))
        return translation_response
