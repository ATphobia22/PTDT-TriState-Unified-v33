"""Fail-closed MODFLOW 6 process boundary."""
from __future__ import annotations

import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model_contracts import FailureClass, ModelRunResult, ModelStatus, Provenance


class Modflow6Runner:
    def __init__(self, executable: str, timeout_seconds: float = 900.0, expected_outputs: tuple[str, ...] = ("model.hds",)) -> None:
        self.executable = executable
        self.timeout_seconds = timeout_seconds
        self.expected_outputs = expected_outputs

    def run(self, workdir: Path, namefile: Path, provenance: Provenance) -> ModelRunResult:
        started = datetime.now(timezone.utc)
        try:
            if not workdir.exists() or not workdir.is_dir():
                return self._failure(started, provenance, FailureClass.INPUT_INVALID, None, "", "workdir does not exist")
            if not namefile.exists():
                return self._failure(started, provenance, FailureClass.INPUT_INVALID, None, "", f"missing namefile: {namefile}")
            proc = subprocess.run(
                self._command(namefile),
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            if Path(self.executable).is_file():
                return self._failure(started, provenance, FailureClass.PROCESS_ERROR, None, "", f"executable exists but could not be started: {exc}")
            return self._failure(started, provenance, FailureClass.EXECUTABLE_MISSING, None, "", "MODFLOW6 executable not found")
        except subprocess.TimeoutExpired as exc:
            return self._failure(started, provenance, FailureClass.TIMEOUT, None, exc.stdout or "", exc.stderr or "MODFLOW6 timed out")
        except OSError as exc:
            return self._failure(started, provenance, FailureClass.PROCESS_ERROR, None, "", str(exc))

        finished = datetime.now(timezone.utc)
        stdout, stderr = proc.stdout or "", proc.stderr or ""
        if proc.returncode != 0:
            return ModelRunResult(ModelStatus.FAILED, FailureClass.PROCESS_ERROR, proc.returncode, stdout, stderr, started, finished, None, provenance, {"returncode": proc.returncode})
        if self._convergence_failed(stdout + "\n" + stderr):
            return ModelRunResult(ModelStatus.FAILED, FailureClass.CONVERGENCE_FAILURE, proc.returncode, stdout, stderr, started, finished, None, provenance, {"reason": "solver convergence indicator detected"})

        ok, failure, diagnostics = self.validate_outputs(workdir, started)
        if not ok:
            return ModelRunResult(ModelStatus.FAILED, failure, proc.returncode, stdout, stderr, started, finished, None, provenance, diagnostics)
        output_path = str(next((p for p in self._output_paths(workdir) if p.exists()), self._output_paths(workdir)[0]))
        return ModelRunResult(ModelStatus.VALID, None, proc.returncode, stdout, stderr, started, finished, output_path, provenance, diagnostics)

    def _command(self, namefile: Path) -> list[str]:
        executable = Path(self.executable)
        if executable.is_file():
            try:
                first_line = executable.read_bytes().splitlines()[0].decode("utf-8", errors="ignore")
            except (OSError, IndexError):
                first_line = ""
            if first_line.startswith("#!"):
                interpreter = shlex.split(first_line[2:].strip())
                if interpreter:
                    return [*interpreter, str(executable), namefile.name]
        return [self.executable, namefile.name]

    def validate_outputs(self, workdir: Path, started_at_utc: datetime) -> tuple[bool, FailureClass | None, dict[str, Any]]:
        paths = self._output_paths(workdir)
        if not any(p.exists() for p in paths):
            return False, FailureClass.OUTPUT_MISSING, {"expected_outputs": [str(p) for p in paths]}
        started_ns = int(started_at_utc.timestamp() * 1_000_000_000)
        stale = [str(p) for p in paths if p.exists() and p.stat().st_mtime_ns < started_ns]
        if stale and all(p.stat().st_mtime_ns < started_ns for p in paths if p.exists()):
            return False, FailureClass.STALE_OUTPUT, {"stale_outputs": stale}
        invalid = [str(p) for p in paths if p.exists() and p.stat().st_size == 0]
        if invalid:
            return False, FailureClass.OUTPUT_INVALID, {"empty_outputs": invalid}
        return True, None, {"validated_outputs": [str(p) for p in paths if p.exists()]}

    def _output_paths(self, workdir: Path) -> list[Path]:
        return [workdir / name for name in self.expected_outputs]

    @staticmethod
    def _convergence_failed(log: str) -> bool:
        patterns = (r"did not converge", r"not converged", r"convergence failure", r"solver failed")
        return any(re.search(pattern, log, re.IGNORECASE) for pattern in patterns)

    @staticmethod
    def _failure(started: datetime, provenance: Provenance, failure: FailureClass, exit_code: int | None, stdout: str, stderr: str) -> ModelRunResult:
        return ModelRunResult(failure_status := ModelStatus.FAILED, failure, exit_code, stdout, stderr, started, datetime.now(timezone.utc), None, provenance, {})
