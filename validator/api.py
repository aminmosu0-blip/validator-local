from __future__ import annotations

import traceback
from pathlib import Path

from validator.core.runner import run_triad_job
from validator.core.artifacts import load_artifacts_from_dir
from validator.checks.preflight import run_preflight
from validator.reports.json_report import write_report_files

def run_static_from_dir(dir_path: str) -> dict:
    base_dir = Path(dir_path)
    job = {
        "ok": False,
        "dir": str(base_dir),
        "phase": "STATIC",
        "violations": [],
    }
    try:
        artifacts = load_artifacts_from_dir(base_dir)
        pre = run_preflight(base_dir, artifacts)
        job["ok"] = pre.ok
        job["violations"] = [v.to_dict() for v in pre.violations]
        return job
    except Exception as exc:
        tb = traceback.format_exc().splitlines()
        return {
            "ok": False,
            "dir": str(base_dir),
            "phase": "STATIC",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback_tail": "\n".join(tb[-120:]),
        }

def run_triad_from_dir(dir_path: str) -> dict:
    base_dir = Path(dir_path)
    try:
        artifacts = load_artifacts_from_dir(base_dir)
        report = run_triad_job(base_dir, artifacts)
        write_report_files(base_dir, report)
        return report.to_dict()
    except Exception as exc:
        tb = traceback.format_exc().splitlines()
        return {
            "ok": False,
            "dir": str(base_dir),
            "phase": "TRIAD",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback_tail": "\n".join(tb[-200:]),
        }
