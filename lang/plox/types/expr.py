from dataclasses import dataclass
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from plox.types.lox_token import Token


class Expr:
    pass


@dataclass
class Assign(Expr):
    name: "Token"
    value: Expr


@dataclass
class Binary(Expr):
    left: Expr
    op: "Token"
    right: Expr


@dataclass
class Logical(Expr):
    left: Expr
    op: "Token"
    right: Expr


@dataclass
class Unary(Expr):
    op: "Token"
    right: Expr


@dataclass
class Grouping(Expr):
    expr: Expr


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Variable(Expr):
    name: "Token"


@dataclass
class Call(Expr):
    callee: Expr
    paren: "Token"
    arguments: List[Expr]
