from typing import Any

from plox.types import expr as expr_module
from plox.types import stmt as stmt_module


class AstPrinter:
    def print_stmt(self, statement: stmt_module.Stmt) -> None:
        print(self.visit(statement))

    def print_expr(self, expression: expr_module.Expr) -> None:
        print(self.visit(expression))

    def visit(self, node: Any) -> str:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"No visitor for {type(node).__name__}")
        return method(node)

    # Expression visitors
    def visit_Assign(self, node: expr_module.Assign) -> str:
        return self.parenthesize(f"assign {node.name.lexeme}", node.value)

    def visit_Binary(self, node: expr_module.Binary) -> str:
        return self.parenthesize(node.op.lexeme, node.left, node.right)

    def visit_Logical(self, node: expr_module.Logical) -> str:
        return self.parenthesize(node.op.lexeme, node.left, node.right)

    def visit_Unary(self, node: expr_module.Unary) -> str:
        return self.parenthesize(node.op.lexeme, node.right)

    def visit_Grouping(self, node: expr_module.Grouping) -> str:
        return self.parenthesize("group", node.expr)

    def visit_Literal(self, node: expr_module.Literal) -> str:
        if node.value is None:
            return "nil"
        return str(node.value)

    def visit_Variable(self, node: expr_module.Variable) -> str:
        return node.name.lexeme

    def visit_Call(self, node: expr_module.Call) -> str:
        result = self.parenthesize("call", node.callee, *node.arguments)
        return result

    # Statement visitors
    def visit_Expression(self, node: stmt_module.Expression) -> str:
        return self.visit(node.expr)

    def visit_Print(self, node: stmt_module.Print) -> str:
        return self.parenthesize("print", node.expr)

    def visit_Var(self, node: stmt_module.Var) -> str:
        if node.initializer is None:
            return f"(var {node.name.lexeme})"
        return f"(var {node.name.lexeme} = {self.visit(node.initializer)})"

    def visit_If(self, node: stmt_module.If) -> str:
        if node.else_branch is None:
            return self.parenthesize("if", node.condition, node.then_branch)
        return self.parenthesize(
            "if", node.condition, node.then_branch, node.else_branch
        )

    def visit_While(self, node: stmt_module.While) -> str:
        return self.parenthesize("while", node.condition, node.body)

    def visit_For(self, node: stmt_module.For) -> str:
        parts = [node.initializer, node.condition, node.increment, node.body]
        return self.parenthesize("for", *[p for p in parts if p is not None])

    def visit_Function(self, node: stmt_module.Function) -> str:
        return (
            "(function "
            + node.name.lexeme
            + " "
            + "(params "
            + " ".join([param.lexeme for param in node.params])
            + ") "
            + self.parenthesize("body", *node.body)
            + ")"
        )

    def visit_Return(self, node: stmt_module.Return) -> str:
        return self.parenthesize("return", node.value)

    def visit_Break(self, node: stmt_module.Break) -> str:
        return "break"

    def visit_Continue(self, node: stmt_module.Continue) -> str:
        return "continue"

    def visit_Block(self, node: stmt_module.Block) -> str:
        items: str = " ".join(self.visit(stmt) for stmt in node.statements)
        return f"{{ {items} }}"

    def parenthesize(self, name: str, *exprs: Any) -> str:
        result = f"({name}"
        for expr in exprs:
            if expr is None:
                continue
            result += f" {self.visit(expr)}"
        result += ")"
        return result
