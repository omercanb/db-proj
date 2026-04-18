from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from plox.types.lox_token import Token


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self.values: Dict[str, Any] = {}
        self.enclosing: Optional[Environment] = enclosing

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: "Token") -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        from plox.types.runtime_error import RuntimeError

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: "Token", value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        from plox.types.runtime_error import RuntimeError

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
