from __future__ import annotations

import re
from pathlib import Path
from validator.reports.models import Violation

_DIFF_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)$")

def _touched_files(patch_text: str) -> list[str]:
    files: list[str] = []
    for line in patch_text.splitlines():
        m = _DIFF_RE.match(line.strip())
        if m:
            # b-path is authoritative for new files
            files.append(m.group(2))
    return files

def check_test_patch_boundaries(test_patch: Path) -> list[Violation]:
    txt = test_patch.read_text(encoding="utf-8", errors="replace")
    touched = _touched_files(txt)

    allowed = {"test.sh"}
    new_tests = [p for p in touched if p.startswith("tests/test_") and p.endswith("_problem.py")]

    violations: list[Violation] = []
    for p in touched:
        if p in allowed:
            continue
        if p.startswith("tests/test_") and p.endswith("_problem.py"):
            continue
        violations.append(Violation(
            code="TEST_PATCH_BOUNDARY",
            message="test.patch modified forbidden files",
            evidence=p,
            suggested_fix="test.patch may change only test.sh and exactly one tests/test_*_problem.py",
        ))

    if len(new_tests) != 1:
        violations.append(Violation(
            code="TEST_PATCH_TESTCOUNT",
            message="test.patch must touch exactly one tests/test_*_problem.py",
            evidence=f"found={len(new_tests)}",
            suggested_fix="Ensure exactly one new problem test module is added/modified.",
        ))
    return violations

def check_solution_patch_boundaries(solution_patch: Path) -> list[Violation]:
    txt = solution_patch.read_text(encoding="utf-8", errors="replace")
    touched = _touched_files(txt)

    violations: list[Violation] = []
    for p in touched:
        if p.startswith("tests/") or p == "test.sh" or p.endswith("Dockerfile.problem"):
            violations.append(Violation(
                code="SOLUTION_PATCH_BOUNDARY",
                message="solution.patch modified forbidden files",
                evidence=p,
                suggested_fix="solution.patch must modify production code only.",
            ))
    return violations
