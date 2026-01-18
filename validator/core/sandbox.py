from __future__ import annotations

import shutil
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Sandbox:
    job_id: str
    root: Path
    workdir: Path
    repo_dir: Path
    logs_dir: Path

def create_sandbox(submission_dir: Path) -> Sandbox:
    job_id = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    runs_root = submission_dir / ".validator_runs" / job_id
    workdir = runs_root / "work"
    repo_dir = workdir / "repo"
    logs_dir = runs_root / "stage_logs"

    logs_dir.mkdir(parents=True, exist_ok=True)
    repo_dir.mkdir(parents=True, exist_ok=True)

    return Sandbox(job_id=job_id, root=runs_root, workdir=workdir, repo_dir=repo_dir, logs_dir=logs_dir)

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")

def safe_rmtree(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        return
