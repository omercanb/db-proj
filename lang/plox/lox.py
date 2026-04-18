import os
import sys

from plox.ast_printer import AstPrinter
from plox.interpreter import Interpreter
from plox.parser import Parser
from plox.scanner import Scanner

had_error = False
had_runtime_error = False
print_tree = False

interpreter = Interpreter()


def main():
    global print_tree

    if len(sys.argv) > 3:
        print("Usage: lox [script] [--print]")
        sys.exit(64)

    if "--print" in sys.argv:
        print_tree = True
        sys.argv.remove("--print")

    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


def run_file(path: str) -> None:
    global had_error, had_runtime_error
    with open(path, "r") as f:
        source = f.read()
    run(source)
    if had_error:
        sys.exit(65)
    if had_runtime_error:
        sys.exit(70)


def run_prompt() -> None:
    global had_error
    while True:
        try:
            print("> ", end="", flush=True)
            line = input()
            if not line:
                break
            run(line)
            had_error = False
        except EOFError:
            break


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    if had_error:
        return

    if print_tree:
        for statement in statements:
            AstPrinter().print_stmt(statement)

    if had_error:
        return

    interpreter.interpret(statements)


def error(line: int, message: str) -> None:
    global had_error
    report(line, "", message)
    had_error = True


def runtime_error(error) -> None:
    global had_runtime_error
    print(f"[line {error.token.line}] Error: {error.message}", file=sys.stderr)
    had_runtime_error = True


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)


if __name__ == "__main__":
    main()
