from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from validator.core.artifacts import SubmissionArtifacts
from validator.core.sandbox import create_sandbox, write_text
from validator.core.subprocess import run_cmd
from validator.core.docker import DockerConfig, docker_build, docker_run, docker_image_tag
from validator.checks.preflight import run_preflight
from validator.checks.policy import load_policy
from validator.reports.models import Report, StageResult

def _extract_repo_zip(zip_path: Path, dest: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)

def _ensure_git(repo_root: Path, max_log_bytes: int) -> None:
    if (repo_root / ".git").exists():
        return

    run_cmd(["git", "init"], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)
    run_cmd(["git", "add", "-A"], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)
    run_cmd(["git", "commit", "-m", "baseline"], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)

def _reset_clean(repo_root: Path, max_log_bytes: int) -> None:
    run_cmd(["git", "reset", "--hard"], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)
    run_cmd(["git", "clean", "-xdf"], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)

def _apply_patch(repo_root: Path, patch_path: Path, max_log_bytes: int) -> StageResult:
    r = run_cmd(["git", "apply", str(patch_path)], cwd=str(repo_root), timeout_s=60, max_log_bytes=max_log_bytes)
    return StageResult(
        name=f"APPLY_{patch_path.name}",
        ok=r.ok,
        exit_code=r.exit_code,
        elapsed_ms=r.elapsed_ms,
        cmd=r.cmd,
        stdout_tail=r.stdout_tail,
        stderr_tail=r.stderr_tail,
    )

def run_triad_job(submission_dir: Path, artifacts: SubmissionArtifacts) -> Report:
    policy = load_policy(artifacts.policy)
    sb = create_sandbox(submission_dir)

    report = Report(
        ok=False,
        job_id=sb.job_id,
        submission_dir=str(submission_dir),
        runs_dir=str(sb.root),
        stages=[],
        violations=[],
        summary={},
    )

    # --- PRECHECK / PREFLIGHT
    pre = run_preflight(submission_dir, artifacts, policy=policy)
    report.violations.extend(pre.violations)
    report.stages.append(pre.stage_result)
    if not pre.ok:
        report.ok = False
        report.summary = {"triad": "SKIPPED", "reason": "preflight_failed"}
        return report

    # --- EXTRACT
    stage = StageResult(name="EXTRACT_REPO", ok=True, exit_code=0, elapsed_ms=0, cmd=[], stdout_tail="", stderr_tail="")
    try:
        _extract_repo_zip(artifacts.repo_zip, sb.repo_dir)
    except Exception as exc:
        stage.ok = False
        stage.stderr_tail = str(exc)
        report.stages.append(stage)
        report.summary = {"triad": "FAIL", "reason": "extract_failed"}
        return report
    report.stages.append(stage)

    # repo may extract into a single top-level folder; normalize to that
    repo_root = sb.repo_dir
    entries = [p for p in repo_root.iterdir()]
    if len(entries) == 1 and entries[0].is_dir():
        repo_root = entries[0]

    # --- ENSURE GIT
    stage_git = StageResult(name="ENSURE_GIT_BASELINE", ok=True, exit_code=0, elapsed_ms=0, cmd=[], stdout_tail="", stderr_tail="")
    try:
        _ensure_git(repo_root, policy.max_log_bytes)
    except Exception as exc:
        stage_git.ok = False
        stage_git.stderr_tail = str(exc)
        report.stages.append(stage_git)
        report.summary = {"triad": "FAIL", "reason": "git_init_failed"}
        return report
    report.stages.append(stage_git)

    # --- BUILD IMAGE
    tag = docker_image_tag(sb.job_id)
    r_build = docker_build(tag, artifacts.dockerfile, repo_root, policy.docker_build_timeout_s, policy.max_log_bytes)
    report.stages.append(StageResult(
        name="DOCKER_BUILD",
        ok=r_build.ok,
        exit_code=r_build.exit_code,
        elapsed_ms=r_build.elapsed_ms,
        cmd=r_build.cmd,
        stdout_tail=r_build.stdout_tail,
        stderr_tail=r_build.stderr_tail,
    ))
    if not r_build.ok:
        report.summary = {"triad": "FAIL", "reason": "docker_build_failed"}
        return report

    cfg = DockerConfig(network=policy.docker_network, cpus=policy.docker_cpus, memory=policy.docker_memory)

    # --- PHASE 1: test.patch only
    _reset_clean(repo_root, policy.max_log_bytes)
    report.stages.append(_apply_patch(repo_root, artifacts.test_patch, policy.max_log_bytes))

    r_base1 = docker_run(tag, repo_root, ["bash", "-lc", "chmod +x test.sh && ./test.sh base"], policy.base_timeout_s, policy.max_log_bytes, cfg)
    report.stages.append(StageResult("TESTPATCH_BASE", r_base1.ok, r_base1.exit_code, r_base1.elapsed_ms, r_base1.cmd, r_base1.stdout_tail, r_base1.stderr_tail))
    if not r_base1.ok:
        report.summary = {"triad": "FAIL", "reason": "base_failed_with_test_patch"}
        return report

    r_new1 = docker_run(tag, repo_root, ["bash", "-lc", "chmod +x test.sh && ./test.sh new"], policy.new_timeout_s, policy.max_log_bytes, cfg)
    # new must FAIL in phase 1
    ok_new_expected_fail = (r_new1.exit_code != 0)
    report.stages.append(StageResult("TESTPATCH_NEW_EXPECT_FAIL", ok_new_expected_fail, r_new1.exit_code, r_new1.elapsed_ms, r_new1.cmd, r_new1.stdout_tail, r_new1.stderr_tail))
    if not ok_new_expected_fail:
        report.summary = {"triad": "FAIL", "reason": "new_unexpectedly_passed_with_test_patch"}
        return report

    # --- PHASE 2: test.patch + solution.patch
    _reset_clean(repo_root, policy.max_log_bytes)
    report.stages.append(_apply_patch(repo_root, artifacts.test_patch, policy.max_log_bytes))
    report.stages.append(_apply_patch(repo_root, artifacts.solution_patch, policy.max_log_bytes))

    r_base2 = docker_run(tag, repo_root, ["bash", "-lc", "chmod +x test.sh && ./test.sh base"], policy.base_timeout_s, policy.max_log_bytes, cfg)
    report.stages.append(StageResult("BOTH_BASE", r_base2.ok, r_base2.exit_code, r_base2.elapsed_ms, r_base2.cmd, r_base2.stdout_tail, r_base2.stderr_tail))
    if not r_base2.ok:
        report.summary = {"triad": "FAIL", "reason": "base_failed_with_both_patches"}
        return report

    r_new2 = docker_run(tag, repo_root, ["bash", "-lc", "chmod +x test.sh && ./test.sh new"], policy.new_timeout_s, policy.max_log_bytes, cfg)
    report.stages.append(StageResult("BOTH_NEW", r_new2.ok, r_new2.exit_code, r_new2.elapsed_ms, r_new2.cmd, r_new2.stdout_tail, r_new2.stderr_tail))
    if not r_new2.ok:
        report.summary = {"triad": "FAIL", "reason": "new_failed_with_both_patches"}
        return report

    report.ok = True
    report.summary = {"triad": "OK"}
    return report
