from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # py3.11+
except ImportError:  # pragma: no cover
    tomllib = None

@dataclass(frozen=True)
class Policy:
    docker_build_timeout_s: int = 900
    base_timeout_s: int = 900
    new_timeout_s: int = 900
    postchecks_timeout_s: int = 300
    max_log_bytes: int = 2_000_000

    docker_network: str = "none"
    docker_cpus: float = 2.0
    docker_memory: str = "4g"

    test_patch_min_bytes: int = 14_336
    solution_patch_min_bytes: int = 2_765

    description_ascii_only: bool = True
    description_lf_only: bool = True

    enforce_test_patch_boundaries: bool = True
    enforce_solution_patch_boundaries: bool = True

    enforce_base_ignores_new: bool = True
    enforce_new_runs_only_new: bool = True
    forbid_backticks: bool = True

def load_policy(policy_path: Path | None) -> Policy:
    if policy_path is None or not policy_path.exists():
        return Policy()

    if tomllib is None:
        return Policy()

    raw = tomllib.loads(policy_path.read_text(encoding="utf-8"))
    limits = raw.get("limits", {})
    docker = raw.get("docker", {})
    gates = raw.get("gates", {})
    rules_pb = raw.get("rules", {}).get("patch_boundaries", {})
    rules_sh = raw.get("rules", {}).get("test_sh", {})

    return Policy(
        docker_build_timeout_s=int(limits.get("docker_build_timeout_s", 900)),
        base_timeout_s=int(limits.get("base_timeout_s", 900)),
        new_timeout_s=int(limits.get("new_timeout_s", 900)),
        postchecks_timeout_s=int(limits.get("postchecks_timeout_s", 300)),
        max_log_bytes=int(limits.get("max_log_bytes", 2_000_000)),

        docker_network=str(docker.get("network", "none")),
        docker_cpus=float(docker.get("cpus", 2.0)),
        docker_memory=str(docker.get("memory", "4g")),

        test_patch_min_bytes=int(gates.get("test_patch_min_bytes", 14_336)),
        solution_patch_min_bytes=int(gates.get("solution_patch_min_bytes", 2_765)),
        description_ascii_only=bool(gates.get("description_ascii_only", True)),
        description_lf_only=bool(gates.get("description_lf_only", True)),

        enforce_test_patch_boundaries=bool(rules_pb.get("enforce_test_patch_boundaries", True)),
        enforce_solution_patch_boundaries=bool(rules_pb.get("enforce_solution_patch_boundaries", True)),

        enforce_base_ignores_new=bool(rules_sh.get("enforce_base_ignores_new", True)),
        enforce_new_runs_only_new=bool(rules_sh.get("enforce_new_runs_only_new", True)),
        forbid_backticks=bool(rules_sh.get("forbid_backticks", True)),
    )
