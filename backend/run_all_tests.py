import sys
import pytest

def main() -> int:
    # Default: defer to pytest.ini for verbosity, warnings, and testpaths
    args = [
        "backend/test_files",
    ]

    # Allow passing through extra args, e.g., to include integration tests
    # Usage examples:
    #   python backend/run_all_tests.py                # unit-style tests only
    #   python backend/run_all_tests.py -m integration # only integration
    #   python backend/run_all_tests.py -m "not integration" -vv
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())


