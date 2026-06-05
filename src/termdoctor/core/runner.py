import os
import shlex
import subprocess
import time
from collections.abc import Sequence

from termdoctor.models import CommandResult


CommandInput = str | Sequence[str]


def format_command(command: CommandInput) -> str:
    if isinstance(command, str):
        return command

    return shlex.join(list(command))


def run_shell_command(command: CommandInput) -> CommandResult:
    start_time = time.perf_counter()
    cwd = os.getcwd()
    command_display = format_command(command)

    try:
        if isinstance(command, str):
            completed = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
            )
        else:
            completed = subprocess.run(
                list(command),
                shell=False,
                cwd=cwd,
                capture_output=True,
                text=True,
            )

        duration = time.perf_counter() - start_time

        return CommandResult(
            command=command_display,
            cwd=cwd,
            exit_code=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            duration_seconds=duration,
        )

    except FileNotFoundError as exc:
        duration = time.perf_counter() - start_time

        return CommandResult(
            command=command_display,
            cwd=cwd,
            exit_code=127,
            stdout="",
            stderr=f"FileNotFoundError: {exc}",
            duration_seconds=duration,
        )

    except Exception as exc:
        duration = time.perf_counter() - start_time

        return CommandResult(
            command=command_display,
            cwd=cwd,
            exit_code=1,
            stdout="",
            stderr=f"{exc.__class__.__name__}: {exc}",
            duration_seconds=duration,
        )