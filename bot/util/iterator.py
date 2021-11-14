from abc import ABC, abstractmethod
from typing import Optional


class Iterator(ABC):

    @abstractmethod
    def next(self) -> Optional:
        pass

    @abstractmethod
    def delete(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class EmptyIterator(Iterator):

    def next(self) -> Optional:
        pass

    def delete(self):
        pass
