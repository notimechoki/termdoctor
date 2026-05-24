import json
from datetime import datetime
from pathlib import Path
from typing import Any

from termdoctor.models import CommandResult, ParsedError


HISTORY_DIR = Path.home() / ".termdoctor"
HISTORY_FILE = HISTORY_DIR / "history.json"
MAX_HISTORY_ITEMS = 30


def ensure_history_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except json.JSONDecodeError:
        return []


def save_history(history_items: list[dict[str, Any]]) -> None:
    ensure_history_dir()

    limited_items = history_items[-MAX_HISTORY_ITEMS:]

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(limited_items, file, indent=2, ensure_ascii=False)


def save_failed_run(command_result: CommandResult, parsed_error: ParsedError | None) -> None:
    history_items = load_history()

    item = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "command": command_result.command,
        "cwd": command_result.cwd,
        "exit_code": command_result.exit_code,
        "duration_seconds": round(command_result.duration_seconds, 4),
        "stdout": command_result.stdout,
        "stderr": command_result.stderr,
        "error_type": parsed_error.error_type if parsed_error else None,
        "error_message": parsed_error.message if parsed_error else None,
    }

    history_items.append(item)
    save_history(history_items)


def get_last_history_item() -> dict[str, Any] | None:
    history_items = load_history()

    if not history_items:
        return None

    return history_items[-1]


def clear_history() -> None:
    save_history([])