from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Violation:
    code: str
    message: str
    evidence: str = ""
    suggested_fix: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "evidence": self.evidence,
            "suggested_fix": self.suggested_fix,
        }

@dataclass
class StageResult:
    name: str
    ok: bool
    exit_code: int
    elapsed_ms: int
    cmd: list[str]
    stdout_tail: str
    stderr_tail: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "elapsed_ms": self.elapsed_ms,
            "cmd": self.cmd,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }

@dataclass
class Report:
    ok: bool
    job_id: str
    submission_dir: str
    runs_dir: str
    stages: list[StageResult] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "job_id": self.job_id,
            "submission_dir": self.submission_dir,
            "runs_dir": self.runs_dir,
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
            "stages": [s.to_dict() for s in self.stages],
        }
