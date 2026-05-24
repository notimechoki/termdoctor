import os
import subprocess
import time

from termdoctor.models import CommandResult

def run_shell_command(command: str) -> CommandResult:
    start_time = time.perf_counter()
    cwd = os.getcwd()

    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
        )

        duration = time.perf_counter() - start_time

        return CommandResult(
            command=command,
            cwd=cwd,
            exit_code=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            duration_seconds=duration,
        )
    
    except Exception as exc:
        duration = time.perf_counter() - start_time

        return CommandResult(
            command=command,
            cwd=cwd,
            exit_code=1,
            stdout="",
            stderr=f"{exc.__class__.__name__}: {exc}",
            duration_seconds=duration,
        )