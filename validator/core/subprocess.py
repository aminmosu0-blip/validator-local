from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CmdResult:
    ok: bool
    cmd: list[str]
    exit_code: int
    elapsed_ms: int
    stdout_tail: str
    stderr_tail: str

def _tail_bytes(data: bytes, max_bytes: int) -> str:
    if len(data) <= max_bytes:
        return data.decode("utf-8", errors="replace")
    return data[-max_bytes:].decode("utf-8", errors="replace")

def run_cmd(cmd: list[str], cwd: Optional[str], timeout_s: int, max_log_bytes: int, env: Optional[dict] = None) -> CmdResult:
    start = time.time()
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        out, err = p.communicate(timeout=timeout_s)
        code = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        code = 124

    elapsed_ms = int((time.time() - start) * 1000)
    return CmdResult(
        ok=(code == 0),
        cmd=cmd,
        exit_code=code,
        elapsed_ms=elapsed_ms,
        stdout_tail=_tail_bytes(out or b"", max_log_bytes),
        stderr_tail=_tail_bytes(err or b"", max_log_bytes),
    )
