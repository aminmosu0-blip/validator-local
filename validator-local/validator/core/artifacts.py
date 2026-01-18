from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class SubmissionArtifacts:
    dir_path: Path
    repo_zip: Path
    dockerfile: Path
    test_patch: Path
    solution_patch: Path
    description: Optional[Path]
    policy: Optional[Path]

def _find_repo_zip(dir_path: Path) -> Path:
    direct = dir_path / "repo.zip"
    if direct.exists():
        return direct

    zips = sorted([p for p in dir_path.glob("*.zip") if p.is_file()])
    if len(zips) == 1:
        return zips[0]
    if len(zips) == 0:
        raise FileNotFoundError("No repo.zip found (and no single *.zip to infer).")
    raise FileNotFoundError("Multiple *.zip files found; rename the repo zip to repo.zip.")

def load_artifacts_from_dir(dir_path: Path) -> SubmissionArtifacts:
    repo_zip = _find_repo_zip(dir_path)

    dockerfile = dir_path / "Dockerfile.problem"
    test_patch = dir_path / "test.patch"
    solution_patch = dir_path / "solution.patch"
    description = dir_path / "description.txt"
    policy = dir_path / "validator.toml"

    for req in [dockerfile, test_patch, solution_patch]:
        if not req.exists():
            raise FileNotFoundError(f"Missing required file: {req.name}")

    desc_path = description if description.exists() else None
    policy_path = policy if policy.exists() else None

    return SubmissionArtifacts(
        dir_path=dir_path,
        repo_zip=repo_zip,
        dockerfile=dockerfile,
        test_patch=test_patch,
        solution_patch=solution_patch,
        description=desc_path,
        policy=policy_path,
    )
