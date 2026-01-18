from __future__ import annotations

from pathlib import Path
from validator.reports.models import Violation

def check_test_sh(path: Path, forbid_backticks: bool) -> list[Violation]:
    violations: list[Violation] = []
    txt = path.read_text(encoding="utf-8", errors="replace")

    if forbid_backticks and "`" in txt:
        violations.append(Violation(
            code="TEST_SH_BACKTICKS",
            message="test.sh must not contain backticks",
            evidence="found ` character",
            suggested_fix="Remove backticks; use $(...) or avoid shell substitution.",
        ))

    # lightweight structure checks (not too brittle)
    if "base" not in txt or "new" not in txt:
        violations.append(Violation(
            code="TEST_SH_MODES",
            message="test.sh must support base and new modes",
            evidence="missing 'base' or 'new' token",
            suggested_fix="Implement ./test.sh base and ./test.sh new modes.",
        ))
    if "--ignore" not in txt:
        violations.append(Violation(
            code="TEST_SH_IGNORE",
            message="base mode should ignore the new test file",
            evidence="no --ignore found",
            suggested_fix="Ensure base runs pytest with --ignore=<new_test>.",
        ))
    return violations
