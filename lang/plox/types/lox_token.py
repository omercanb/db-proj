from dataclasses import dataclass
from typing import Any
from plox.types.token_type import TokenType


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"
