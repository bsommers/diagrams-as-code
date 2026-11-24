"""Run one diagram script in a resource-limited child process.

A diagram script is arbitrary Python. The MCP server runs it here instead of in
its own process, so a script that loops forever, allocates without bound, or
writes to file descriptor 1 or reads stdin cannot hang or corrupt the server.

What this gives: a wall-clock timeout (the whole process group is killed), CPU
and address-space limits on POSIX, ``stdin`` closed, ``stdout`` discarded,
``stderr`` capped, and a scrubbed environment. What it does not give: file or
network isolation. A script can still read and write files the server user can;
confine the server with a container for that.

The child is this same module (``python -m diagrams_as_code.sandbox JOB``). It
reports through a result file, never through a pipe a script could write to.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_STDERR = 4096  # bytes of a child's stderr kept for the error message


class SandboxError(Exception):
    """The script could not be run to completion within its limits."""


@dataclass(frozen=True)
class Limits:
    timeout: float = 60.0   # wall-clock seconds
    cpu: int = 60           # CPU seconds (POSIX)
    memory_mb: int = 2048   # address space in MiB (POSIX; best effort on macOS)


def _apply_limits(limits: Limits):
    """A ``preexec_fn`` for the child, or ``None`` where ``resource`` is unavailable."""
    try:
        import resource
    except ImportError:  # Windows: only the wall-clock timeout applies
        return None

    def preexec() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (limits.cpu, limits.cpu + 1))
        cap = limits.memory_mb * 1024 * 1024
        for name in ("RLIMIT_AS", "RLIMIT_DATA"):
            try:
                resource.setrlimit(getattr(resource, name), (cap, cap))
            except (ValueError, OSError, AttributeError):
                pass  # macOS rejects or ignores some of these
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    return preexec


def _env() -> dict[str, str]:
    keep = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "SYSTEMROOT")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env["PYTHONPATH"] = os.pathsep.join(p for p in sys.path if p)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run(job: dict[str, Any], limits: Limits = Limits()) -> dict[str, Any]:
    """Run ``job`` in a child and return its JSON result.

    ``job["op"]`` is ``"render"`` or ``"lint"``; see :func:`_work`. Raises
    :class:`SandboxError` on timeout, a signal or limit kill, or no result.
    """
    with tempfile.TemporaryDirectory(prefix="dac-sandbox-") as tmp:
        job = {**job, "result": str(Path(tmp) / "result.json"), "outdir": str(Path(tmp) / "out")}
        Path(job["outdir"]).mkdir()
        proc = subprocess.Popen(
            [sys.executable, "-m", "diagrams_as_code.sandbox", json.dumps(job)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            env=_env(), cwd=tmp, start_new_session=os.name == "posix",
            preexec_fn=_apply_limits(limits) if os.name == "posix" else None,
        )
        try:
            _, err = proc.communicate(timeout=limits.timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            proc.communicate()
            raise SandboxError(f"script exceeded the {limits.timeout:g}s time limit") from None
        finally:
            _kill(proc)  # reap any grandchildren the script left behind
        result_path = Path(job["result"])
        if not result_path.is_file():
            tail = err[-MAX_STDERR:].decode("utf-8", "replace").strip().splitlines()
            hint = tail[-1] if tail else "no output"
            if proc.returncode and proc.returncode < 0:
                hint = f"killed by signal {-proc.returncode} (CPU or memory limit?); {hint}"
            raise SandboxError(f"script did not complete: {hint}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if "error" in result:
            raise SandboxError(result["error"])
        # Collect output files (name -> bytes) before the temp dir disappears.
        result["files"] = {
            fmt: (Path(name).name, Path(name).read_bytes())
            for fmt, name in result.get("files", {}).items()
        }
        return result


def _kill(proc: subprocess.Popen) -> None:
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass


# --- child side ------------------------------------------------------------

def _work(job: dict[str, Any]) -> dict[str, Any]:
    from diagrams_as_code.audit import audit_findings
    from diagrams_as_code.cli import load_script

    diag, stem = load_script(Path(job["script"]))
    if job["op"] == "lint":
        ignore = set(job.get("ignore") or [])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            findings = [{"kind": f.kind, "detail": f.detail}
                        for f in audit_findings(diag) if f.kind not in ignore]
        return {"findings": findings, "warnings": [str(w.message) for w in caught]}
    from diagrams_as_code.output import render_all

    if job.get("theme"):
        diag.configure(theme=job["theme"])
    if not stem or "/" in stem or "\\" in stem or stem in (".", ".."):
        raise ValueError(f"output name {stem!r} is not a plain file stem")
    written = render_all(diag, Path(job["outdir"]), stem, tuple(job["formats"]))
    return {"stem": stem, "files": {fmt: str(p) for fmt, p in written.items()}}


def _main(argv: list[str]) -> int:
    job = json.loads(argv[1])
    try:
        out = _work(job)
    except BaseException as exc:  # includes SystemExit from a script
        out = {"error": f"{type(exc).__name__}: {exc}"}
    Path(job["result"]).write_text(json.dumps(out), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
