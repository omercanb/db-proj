import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    def __init__(self, lox_file: str):
        self.lox_file = lox_file
        self.output = ""
        self.error = ""
        self.exit_code = 0

    def run_with_print(self):
        result = subprocess.run(
            ["python3", "plox/lox.py", "--print", self.lox_file],
            capture_output=True,
            text=True,
        )
        self.output = result.stdout
        self.error = result.stderr
        self.exit_code = result.returncode


class TestResult:
    def __init__(
        self, test_file: str, passed: bool, expected: str, actual: str, error: str
    ):
        self.test_file = test_file
        self.passed = passed
        self.expected = expected
        self.actual = actual
        self.error = error

    def print_result(self):
        name = os.path.basename(self.test_file)
        if self.passed:
            print(f"✓ {name}")
        else:
            print(f"✗ {name}")
            if self.error and self.error.strip():
                print(f"  Error: {self.error}")
            print("  Expected:")
            for line in self.expected.split("\n"):
                print(f"    | {line}")
            print("  Actual:")
            for line in self.actual.split("\n"):
                print(f"    | {line}")


class LoxTestFramework:
    def __init__(self, test_files_dir: str):
        self.test_files_dir = test_files_dir
        self.results = []

    def run_all_tests(self):
        if not os.path.isdir(self.test_files_dir):
            print(f"Test directory not found: {self.test_files_dir}", file=sys.stderr)
            return

        test_files = sorted(glob.glob(os.path.join(self.test_files_dir, "*.lox")))

        if not test_files:
            print(f"No .lox files found in {self.test_files_dir}")
            return

        print(f"Running {len(test_files)} tests...\n")

        for test_file in test_files:
            self.run_test(test_file)

        self.print_summary()

    def run_test(self, lox_file: str):
        runner = TestRunner(lox_file)
        runner.run_with_print()

        expected_file = lox_file.replace(".lox", ".expected")
        expected = self.read_expected_output(expected_file)

        if expected is None:
            self.generate_expected_output(lox_file, runner.output)
            self.results.append(
                TestResult(
                    lox_file,
                    True,
                    runner.output,
                    runner.output,
                    "Generated new expected output",
                )
            )
        else:
            actual = runner.output
            passed = actual == expected
            self.results.append(
                TestResult(lox_file, passed, expected, actual, runner.error)
            )

    def read_expected_output(self, path: str):
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read()
        except IOError as e:
            print(f"Error reading expected output: {e}", file=sys.stderr)
        return None

    def generate_expected_output(self, lox_file: str, output: str):
        expected_file = lox_file.replace(".lox", ".expected")
        try:
            with open(expected_file, "w") as f:
                f.write(output)
            print(f"Generated: {expected_file}")
        except IOError as e:
            print(f"Error writing expected output: {e}", file=sys.stderr)

    def print_summary(self):
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        print("\n" + "=" * 60)
        print("Test Results")
        print("=" * 60 + "\n")

        for result in self.results:
            result.print_result()

        print("\n" + "=" * 60)
        print(f"Summary: {passed} passed, {failed} failed out of {len(self.results)}")
        print("=" * 60)

        if failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    test_dir = sys.argv[1] if len(sys.argv) > 1 else "testFiles"

    LoxTestFramework(test_dir).run_all_tests()
