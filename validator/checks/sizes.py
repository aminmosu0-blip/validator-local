from __future__ import annotations

from pathlib import Path
from validator.reports.models import Violation

def check_min_size(path: Path, min_bytes: int, code: str) -> list[Violation]:
    sz = path.stat().st_size
    if sz < min_bytes:
        return [Violation(
            code=code,
            message=f"{path.name} is too small",
            evidence=f"size={sz} bytes, min={min_bytes} bytes",
            suggested_fix="Broaden coverage via real invariants/entrypoints; do not pad.",
        )]
    return []
