from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from validator.core.subprocess import run_cmd, CmdResult

@dataclass(frozen=True)
class DockerConfig:
    network: str
    cpus: float
    memory: str

def docker_build(tag: str, dockerfile: Path, context_dir: Path, timeout_s: int, max_log_bytes: int) -> CmdResult:
    cmd = [
        "docker", "build",
        "-f", str(dockerfile),
        "-t", tag,
        str(context_dir),
    ]
    return run_cmd(cmd, cwd=str(context_dir), timeout_s=timeout_s, max_log_bytes=max_log_bytes)

def docker_run(tag: str, repo_dir: Path, command: list[str], timeout_s: int, max_log_bytes: int, cfg: DockerConfig) -> CmdResult:
    cmd = [
        "docker", "run", "--rm",
        "--network", cfg.network,
        "--cpus", str(cfg.cpus),
        "--memory", cfg.memory,
        "-v", f"{str(repo_dir)}:/app",
        "-w", "/app",
        tag,
    ] + command
    return run_cmd(cmd, cwd=str(repo_dir), timeout_s=timeout_s, max_log_bytes=max_log_bytes)

def docker_image_tag(job_id: str) -> str:
    return f"validator-job:{job_id}"
