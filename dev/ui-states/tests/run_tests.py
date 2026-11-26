"""Run state_check.py on the fixtures and compare each file's hits to its "expect:" line.

Usage:
    python3 tests/run_tests.py

Every fixture names the checks it should trigger on an "expect:" line. Files in good/
expect none. Prints one line per mismatch and exits 1 if there are any.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from state_check import CODE_EXTENSIONS, check_file, code_files  # noqa: E402

EXPECT = re.compile(r"expect:(.*?)(?:-->|\*/|$)", re.MULTILINE)


def main():
    fixtures = sorted(p for p in (HERE / "fixtures").rglob("*") if p.suffix in CODE_EXTENSIONS)
    failures = 0
    for path in fixtures:
        declared = EXPECT.search(path.read_text(encoding="utf-8"))
        if not declared:
            print(f"{path.relative_to(HERE)}: no expect: line")
            failures += 1
            continue
        expected = {c.strip() for c in declared.group(1).split(",") if c.strip()}
        got = {check for _, _, check, _ in check_file(path)}
        if got != expected:
            missed = ", ".join(sorted(expected - got)) or "none"
            extra = ", ".join(sorted(got - expected)) or "none"
            print(f"{path.relative_to(HERE)}: missed {missed}; unexpected {extra}")
            failures += 1
    walked = {p.resolve() for p in code_files([str(HERE / "fixtures" / "bad"), str(HERE / "fixtures" / "good")])}
    for path in fixtures:  # a folder walk must reach every fixture, or real files get skipped too
        if path.resolve() not in walked:
            print(f"{path.relative_to(HERE)}: skipped when walking its folder")
            failures += 1
    print(f"{len(fixtures) - failures} of {len(fixtures)} fixtures pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
