from dataclasses import dataclass
from typing import Any


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


@dataclass
class ReturnException(Exception):
    value: Any
