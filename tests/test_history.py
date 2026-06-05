from pathlib import Path

from termdoctor.core import history
from termdoctor.core.history import clear_history, load_history, save_failed_run
from termdoctor.models import CommandResult, ParsedError


def test_history_saves_failed_run(tmp_path, monkeypatch):
    history_file = tmp_path / "history.json"

    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(history, "HISTORY_FILE", history_file)

    command_result = CommandResult(
        command="python main.py",
        cwd=str(Path.cwd()),
        exit_code=1,
        stdout="",
        stderr="NameError: name 'username' is not defined",
        duration_seconds=0.1,
    )
    parsed_error = ParsedError(
        error_type="NameError",
        message="name 'username' is not defined",
        raw_text="NameError: name 'username' is not defined",
        extracted={"name": "username"},
    )

    save_failed_run(command_result, parsed_error)

    items = load_history()

    assert len(items) == 1
    assert items[0]["error_type"] == "NameError"
    assert items[0]["command"] == "python main.py"


def test_history_limit(tmp_path, monkeypatch):
    history_file = tmp_path / "history.json"

    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(history, "HISTORY_FILE", history_file)
    monkeypatch.setattr(history, "MAX_HISTORY_ITEMS", 2)

    for index in range(3):
        command_result = CommandResult(
            command=f"python file_{index}.py",
            cwd=str(Path.cwd()),
            exit_code=1,
            stdout="",
            stderr="NameError: name 'x' is not defined",
            duration_seconds=0.1,
        )
        parsed_error = ParsedError(
            error_type="NameError",
            message="name 'x' is not defined",
            raw_text="NameError: name 'x' is not defined",
        )
        save_failed_run(command_result, parsed_error)

    items = load_history()

    assert len(items) == 2
    assert items[0]["command"] == "python file_1.py"
    assert items[1]["command"] == "python file_2.py"


def test_clear_history(tmp_path, monkeypatch):
    history_file = tmp_path / "history.json"

    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(history, "HISTORY_FILE", history_file)

    command_result = CommandResult(
        command="python main.py",
        cwd=str(Path.cwd()),
        exit_code=1,
        stdout="",
        stderr="NameError: name 'username' is not defined",
        duration_seconds=0.1,
    )
    parsed_error = ParsedError(
        error_type="NameError",
        message="name 'username' is not defined",
        raw_text="NameError: name 'username' is not defined",
    )

    save_failed_run(command_result, parsed_error)
    clear_history()

    assert load_history() == []