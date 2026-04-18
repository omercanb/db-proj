import time
from typing import Any, List, TYPE_CHECKING

from plox.types.lox_callable import LoxCallable

if TYPE_CHECKING:
    from plox.interpreter import Interpreter


class NativeClock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> float:
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"
