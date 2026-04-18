from typing import TYPE_CHECKING, Any, List

from plox.types.control_flow import ReturnException
from plox.types.environment import Environment
from plox.types.lox_callable import LoxCallable

if TYPE_CHECKING:
    from plox.interpreter import Interpreter
    from plox.types.stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: "Function", closure: Environment) -> None:
        self.declaration: "Function" = declaration
        self.closure: Environment = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value

        # Function had no return value
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
