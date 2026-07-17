from __future__ import annotations

import json
import os
import re
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from termdoctor.models import CommandResult, ParsedError


HISTORY_DIR = Path.home() / ".termdoctor"
HISTORY_FILE = HISTORY_DIR / "history.json"
MAX_HISTORY_ITEMS = 30
MAX_STREAM_CHARS = 20_000
LOCK_TIMEOUT_SECONDS = 5.0
STALE_LOCK_SECONDS = 30.0
REDACTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(authorization:\s*bearer\s+)[^\s]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)\b(api[_-]?key|token|secret|password|passwd)\b\s*[:=]\s*['\"]?[^\s,'\"}]+"), r"\1=[REDACTED]"),
    (re.compile(r"(?i)(postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s@]+@"), r"\1://[REDACTED]@"),
)


def ensure_history_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        HISTORY_DIR.chmod(0o700)
    except OSError:
        pass


def _lock_file() -> Path:
    return HISTORY_FILE.with_suffix(HISTORY_FILE.suffix + ".lock")


@contextmanager
def history_lock(timeout: float = LOCK_TIMEOUT_SECONDS):
    ensure_history_dir()
    lock_path = _lock_file()
    deadline = time.monotonic() + timeout
    descriptor: int | None = None

    while descriptor is None:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, str(os.getpid()).encode("ascii", errors="ignore"))
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age > STALE_LOCK_SECONDS:
                    lock_path.unlink()
                    continue
            except FileNotFoundError:
                continue
            except OSError:
                pass

            if time.monotonic() >= deadline:
                raise TimeoutError(f"Could not acquire history lock: {lock_path}")
            time.sleep(0.02)

    try:
        yield
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass


def _load_history_unlocked() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup_corrupt_history()
        return []
    except OSError:
        return []
    return data if isinstance(data, list) else []


def load_history() -> list[dict[str, Any]]:
    return _load_history_unlocked()


def backup_corrupt_history() -> None:
    if not HISTORY_FILE.exists():
        return
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = HISTORY_FILE.with_name(f"history.corrupt-{timestamp}.json")
    try:
        HISTORY_FILE.replace(backup)
    except OSError:
        pass


def _save_history_unlocked(history_items: list[dict[str, Any]]) -> None:
    ensure_history_dir()
    limited_items = history_items[-MAX_HISTORY_ITEMS:]
    payload = json.dumps(limited_items, indent=2, ensure_ascii=False)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix="history-",
        suffix=".tmp",
        dir=str(HISTORY_DIR),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        try:
            temporary.chmod(0o600)
        except OSError:
            pass
        os.replace(temporary, HISTORY_FILE)
        try:
            HISTORY_FILE.chmod(0o600)
        except OSError:
            pass
    finally:
        if temporary.exists():
            try:
                temporary.unlink()
            except OSError:
                pass


def save_history(history_items: list[dict[str, Any]]) -> None:
    with history_lock():
        _save_history_unlocked(history_items)


def sanitize_output(value: str, limit: int = MAX_STREAM_CHARS) -> str:
    sanitized = value
    for pattern, replacement in REDACTION_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    if len(sanitized) > limit:
        omitted = len(sanitized) - limit
        sanitized = sanitized[:limit] + f"\n...[truncated {omitted} characters]"
    return sanitized


def save_failed_run(command_result: CommandResult, parsed_error: ParsedError | None) -> None:
    item = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "command": sanitize_output(command_result.command, limit=2_000),
        "cwd": command_result.cwd,
        "exit_code": command_result.exit_code,
        "duration_seconds": round(command_result.duration_seconds, 4),
        "stdout": sanitize_output(command_result.stdout),
        "stderr": sanitize_output(command_result.stderr),
        "diagnostic_text": sanitize_output(command_result.diagnostic_text),
        "error_type": parsed_error.error_type if parsed_error else None,
        "error_message": sanitize_output(parsed_error.message, limit=2_000) if parsed_error else None,
        "file_path": parsed_error.file_path if parsed_error else None,
        "line_number": parsed_error.line_number if parsed_error else None,
    }
    with history_lock():
        history_items = _load_history_unlocked()
        history_items.append(item)
        _save_history_unlocked(history_items)


def get_last_history_item() -> dict[str, Any] | None:
    history_items = load_history()
    return history_items[-1] if history_items else None


def clear_history() -> None:
    with history_lock():
        if HISTORY_FILE.exists():
            try:
                HISTORY_FILE.unlink()
                return
            except OSError:
                pass
        _save_history_unlocked([])


def get_history_text(item: dict[str, Any]) -> str:
    diagnostic = item.get("diagnostic_text")
    if isinstance(diagnostic, str) and diagnostic.strip():
        return diagnostic
    parts = [str(item.get(key) or "").rstrip() for key in ("stdout", "stderr")]
    return "\n".join(part for part in parts if part.strip())


def format_history_time(value: str | None) -> str:
    if not value:
        return "unknown"
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def trim_text(value: str, max_length: int = 80) -> str:
    normalized = " ".join(value.split())
    return normalized if len(normalized) <= max_length else normalized[: max_length - 1] + "…"
