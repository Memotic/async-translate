import os
from typing import Dict, Optional

import aiohttp as aiohttp
from aiohttp import ContentTypeError

from async_translate.abc import BaseProvider, Translation
from async_translate.errors import TranslatorException


class DeepL(BaseProvider):
    def __init__(self, auth_key=""):
        self.auth_key: str = auth_key or os.environ["DEEPL_AUTH_KEY"]
        self.api_url = "https://api{}.deepl.com/v2/".format('-free' if self.auth_key.endswith(':fx') else '')
        self.session = aiohttp.ClientSession()

    async def _request(self, endpoint, data: Optional[Dict] = None):
        if data is None:
            data = {}
        data.update(auth_key=self.auth_key)
        async with self.session.post(self.api_url + endpoint, data=data) as resp:
            try:
                return await resp.json()
            except ContentTypeError as e:
                raise TranslatorException((await resp.read()).decode()) from e

    async def get_languages(self, *args, **kwargs) -> Dict[str, str]:
        raw_languages = await self._request("languages")
        return {
            lang['language'].casefold(): lang['name']
            for lang in raw_languages
        }

    async def detect(self, content) -> str:
        raise NotImplementedError

    async def translate(self, content: str, to: str, fro="", **options) -> [Translation]:
        options.update(text=content, target_lang=to)
        if fro:
            options['source_lang'] = fro
        raw_translation = await self._request("translate", options)
        translation = raw_translation['translations'][0]
        return Translation(provider=self, to=to, text=translation['text'],
                           detectedLanguage=translation['detected_source_language'])
