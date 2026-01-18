from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from validator.core.artifacts import SubmissionArtifacts
from validator.checks.policy import Policy, load_policy
from validator.checks.boundaries import check_test_patch_boundaries, check_solution_patch_boundaries
from validator.checks.encoding import check_ascii_lf
from validator.checks.sizes import check_min_size
from validator.checks.test_sh import check_test_sh
from validator.reports.models import Violation, StageResult

@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    violations: list[Violation]
    stage_result: StageResult

def run_preflight(submission_dir: Path, artifacts: SubmissionArtifacts, policy: Policy | None = None) -> PreflightResult:
    pol = policy if policy is not None else load_policy(artifacts.policy)
    violations: list[Violation] = []

    # size gates
    violations += check_min_size(artifacts.test_patch, pol.test_patch_min_bytes, "TEST_PATCH_SIZE")
    violations += check_min_size(artifacts.solution_patch, pol.solution_patch_min_bytes, "SOLUTION_PATCH_SIZE")

    # boundaries
    if pol.enforce_test_patch_boundaries:
        violations += check_test_patch_boundaries(artifacts.test_patch)
    if pol.enforce_solution_patch_boundaries:
        violations += check_solution_patch_boundaries(artifacts.solution_patch)

    # description encoding
    if artifacts.description is not None:
        violations += check_ascii_lf(artifacts.description, pol.description_ascii_only, pol.description_lf_only)

    # test.sh rules (requires patch to add it, but we can preflight by parsing patch content)
    # If test.sh exists directly in submission_dir, check it too.
    sh_path = submission_dir / "test.sh"
    if sh_path.exists():
        violations += check_test_sh(sh_path, pol.forbid_backticks)

    ok = (len(violations) == 0)
    stage = StageResult(
        name="PREFLIGHT",
        ok=ok,
        exit_code=0 if ok else 1,
        elapsed_ms=0,
        cmd=[],
        stdout_tail="",
        stderr_tail="\n".join([f"{v.code}: {v.message} ({v.evidence})" for v in violations][:50]),
    )
    return PreflightResult(ok=ok, violations=violations, stage_result=stage)
