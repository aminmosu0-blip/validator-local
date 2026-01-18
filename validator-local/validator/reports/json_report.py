from __future__ import annotations

import json
import zipfile
from pathlib import Path

from validator.reports.models import Report

def write_report_files(submission_dir: Path, report: Report) -> None:
    runs_dir = Path(report.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    report_path = runs_dir / "report.json"
    report_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    triad_summary = runs_dir / "triad_summary.json"
    triad_summary.write_text(json.dumps(report.summary, indent=2, sort_keys=True), encoding="utf-8")

    # bundle.zip: inputs + reports + stage logs
    bundle = runs_dir / "bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # include top-level inputs if present
        for name in ["repo.zip", "Dockerfile.problem", "test.patch", "solution.patch", "description.txt", "validator.toml"]:
            p = submission_dir / name
            if p.exists():
                z.write(p, arcname=f"inputs/{name}")

        z.write(report_path, arcname="outputs/report.json")
        z.write(triad_summary, arcname="outputs/triad_summary.json")

        logs_dir = runs_dir / "stage_logs"
        if logs_dir.exists():
            for p in sorted(logs_dir.rglob("*")):
                if p.is_file():
                    z.write(p, arcname=f"outputs/stage_logs/{p.relative_to(logs_dir)}")
