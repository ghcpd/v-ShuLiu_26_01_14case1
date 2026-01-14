import os
import sys


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    tests_dir = os.path.join(base_dir, "tests")

    # Prefer pytest if available
    try:
        import pytest  # type: ignore
    except ImportError:
        import unittest

        if not os.path.isdir(tests_dir):
            # No tests directory; behave as "no tests" and succeed.
            sys.exit(0)

        loader = unittest.defaultTestLoader
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # Use pytest's default discovery under tests/
        # Rely on pytest's own reporting; do not print custom PASS banners.
        args = ["tests"] if os.path.isdir(tests_dir) else []
        exit_code = pytest.main(args)
        sys.exit(int(exit_code))


if __name__ == "__main__":
    main()
