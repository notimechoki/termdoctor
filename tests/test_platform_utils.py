from pathlib import Path

from termdoctor.core.platform_utils import get_activation_command

def test_get_activation_command_returns_none_without_venv():
    assert get_activation_command(None) is None


def test_get_activation_command_returns_command_for_path():
    command = get_activation_command(str(Path(".venv")))

    assert command is not None
    assert ".venv" in command