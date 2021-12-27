from functools import cached_property
from types import MappingProxyType
from typing import Optional, Dict, Set, Mapping
from .caseinsensitivedict import CaseInsensitiveDict
from .abc import BaseProvider, Translation
from .errors import *


class AsyncTranslate:
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}  # {'provider_name': ProviderInstance() }
        self._languages: Dict[str, Set[str]] = {}  # {'language_name': {'provider_name'} }
        self._language_names: Dict[str, str] = {}  # {'en': 'English'}

    @property
    def providers(self) -> Mapping[str, BaseProvider]:
        """Returns read-only copy of the providers"""
        return MappingProxyType(self._providers)

    @property
    def languages(self) -> Mapping[str, Set[str]]:
        """Returns read-only copy of the languages"""
        return MappingProxyType(self._languages)

    @property
    def language_names(self) -> Mapping[str, str]:
        return CaseInsensitiveDict(self._language_names)

    @cached_property
    def language_by_names(self) -> Mapping[str, str]:
        """Returns read-only copy of language codes with their English names"""
        return CaseInsensitiveDict({name: code for code, name in self._language_names.items()})

    @cached_property
    def default_provider(self) -> BaseProvider:
        """Returns the default (first) provider"""
        return next(iter(self._providers.values()))

    async def close(self):
        """Close all Provider aiohttp loops"""
        for provider in self._providers.values():
            await provider.close()

    async def add_provider(self, provider: BaseProvider):
        """Add a translator provider"""
        if not isinstance(provider, BaseProvider):
            raise TypeError('Providers must derive from BaseProvider')

        # Add to internal store
        provider_name = provider.name.casefold()
        if provider_name in self._providers:
            raise ProviderAlreadyAdded(provider_name)
        self._providers[provider_name] = provider

        languages = await provider.get_languages()
        for code, language_name in languages.items():
            self._language_names[code] = language_name
            if code in self._languages:
                self._languages[code].add(provider_name)
            else:
                self._languages[code] = {provider_name}

    async def add_providers(self, *backends: [BaseProvider]):
        """Add multiple providers"""
        for b in backends:
            await self.add_provider(b)

    def provider_for(self, language: str, preferred: Optional[str] = "") -> BaseProvider:
        try:
            available_providers = list(self._languages[language])
        except KeyError:
            raise LanguageNotSupported(language)
        return self._providers[preferred if preferred in available_providers else available_providers[0]]

    async def translate(self, to: str, content: str, provider: BaseProvider,
                        source_language: Optional[str] = None, **options) -> Translation:
        # Assumes to & source_language are valid language codes
        if source_language and source_language == to:
            raise DetectedAsSameError(to_language=to, detected_language=source_language)

        # Detect translating to/from same language
        detected_language = await self.providers.get('azure').detect(content.strip())
        if to == detected_language:
            raise DetectedAsSameError(to_language=to, detected_language=detected_language)
        return await provider.translate(content, to=to, fro=source_language, **options)
