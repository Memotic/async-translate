import types
from typing import Optional, Dict

from .abc import BaseProvider, Translation
from .errors import ProviderAlreadyAdded, NoProvidersAdded, LanguageNotSupported
from .caseinsensitivedict import CaseInsensitiveDict


class AsyncTranslate:
    def __init__(self):
        self._languages = CaseInsensitiveDict()
        self._providers = CaseInsensitiveDict()
        self.language_names: Dict[str, str] = {}

    @property
    def providers(self):
        """Returns read-only copy of the providers"""
        return types.MappingProxyType(self._providers)

    @property
    def default_provider(self) -> BaseProvider:
        """Returns the default (first) provider"""
        return next(iter(self._providers.values()))

    @property
    def languages(self):
        """Returns read-only copy of the supported languages"""
        return types.MappingProxyType(self._languages)

    async def add_provider(self, provider: BaseProvider):
        """Add a translator provider"""
        if not isinstance(provider, BaseProvider):
            raise TypeError('Providers must derive from BaseProvider')

        name = provider.name

        if name in self._providers:
            raise ProviderAlreadyAdded(name)
        self._providers[name] = provider

        for lang, lang_name in (await provider.get_languages()).items():
            bck_str = [name]
            if added_lang := self._languages.get(lang):
                self._languages[lang] = added_lang + bck_str
            else:
                self._languages[lang] = bck_str
                # Only set name if it hasn't been added already
                self.language_names[lang] = lang_name

    async def add_providers(self, *backends: [BaseProvider]):
        """Add multiple providers"""
        for b in backends:
            await self.add_provider(b)

    def provider_for(self, language: str, preferred: Optional[str] = "") -> BaseProvider:
        """Returns a valid provider for the specified language"""
        # precondition self._providers has at least one provider in it
        backend = self._languages.get(language)
        if not backend or len(backend) == 0:
            raise LanguageNotSupported(language)
        if len(self._providers) == 0:
            raise NoProvidersAdded()
        return self._providers[preferred] if preferred in backend else self._providers[backend[0]]

    async def detect(self, content: str, preferred: Optional[str] = None) -> (str, BaseProvider):
        provider: BaseProvider = self.providers[preferred] if preferred else self.default_provider
        return await provider.detect(content), provider

    async def translate(self, content: str, to: str, fro="", preferred: Optional[str] = None, **options) -> [Translation]:
        """
        Translates the given content to the specified language
        :param content: Content to translate
        :param to: Language code to translate to
        :param fro: Optional language to translate from
        :param preferred: Optional provider to prefer
        :return: A list of translations
        """
        provider = self.provider_for(to, preferred=preferred)
        return await provider.translate(content, to=to, fro=fro, **options)
