from abc import ABC, abstractmethod
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        pass

    def __str__(self) -> str:
        return "<callable>"
