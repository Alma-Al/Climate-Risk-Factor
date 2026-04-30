from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests"
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    failures = []
    tests_run = 0
    for path in sorted(TEST_DIR.glob("test_*.py")):
        module = load_module(path)
        for name in dir(module):
            if not name.startswith("test_"):
                continue
            test_fn = getattr(module, name)
            if not callable(test_fn):
                continue
            tests_run += 1
            try:
                test_fn()
                print(f"PASS {path.name}::{name}")
            except Exception as exc:  # noqa: BLE001 - test runner should capture all failures
                failures.append((path.name, name, exc, traceback.format_exc()))
                print(f"FAIL {path.name}::{name}: {exc}")

    print(f"\nRan {tests_run} tests.")
    if failures:
        print(f"{len(failures)} failed.")
        for filename, name, _exc, tb in failures:
            print(f"\n--- {filename}::{name} ---")
            print(tb)
        sys.exit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
