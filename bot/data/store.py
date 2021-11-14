from abc import ABC, abstractmethod
from typing import Optional

from bot.util.iterator import Iterator


class Store(ABC):

    @abstractmethod
    def store(self, data):
        pass

    @abstractmethod
    def iterator(self) -> Iterator:
        pass


class KeyStore(ABC):

    @abstractmethod
    def put(self, key: str, data: str):
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass
