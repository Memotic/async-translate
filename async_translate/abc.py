from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

ONE_DAY = 86400


@dataclass
class Translation:
    text: str
    to: str
    source: Optional[str] = None


class BaseProvider(ABC):
    icon = ""

    @property
    def name(self) -> str:
        """Shortcut to get name of the provider"""
        return self.__class__.__name__

    @abstractmethod
    async def get_languages(self, locale=None, *args, **kwargs) -> Dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def detect(self, content) -> str:
        raise NotImplementedError

    @abstractmethod
    async def translate(self, content: str, to: str, source="", **options) -> Translation:
        raise NotImplementedError

    async def close(self):
        pass
