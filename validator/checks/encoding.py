from __future__ import annotations

from pathlib import Path
from validator.reports.models import Violation

def check_ascii_lf(path: Path, require_ascii: bool, require_lf: bool) -> list[Violation]:
    violations: list[Violation] = []
    data = path.read_bytes()

    if require_ascii:
        try:
            data.decode("ascii")
        except UnicodeDecodeError as e:
            violations.append(Violation(
                code="DESC_ASCII",
                message=f"{path.name} must be ASCII-only",
                evidence=f"non-ascii at byte offset {e.start}",
                suggested_fix="Remove non-ASCII characters.",
            ))

    if require_lf:
        if b"\r\n" in data or b"\r" in data:
            violations.append(Violation(
                code="DESC_LF",
                message=f"{path.name} must use LF-only line endings",
                evidence="CRLF/CR detected",
                suggested_fix="Convert to LF-only line endings.",
            ))

    return violations
