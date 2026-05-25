from termdoctor.cli import build_command_input


def test_build_command_input_string_mode():
    result = build_command_input(
        command="python examples/name_error.py",
        extra_args=[],
    )

    assert result == "python examples/name_error.py"


def test_build_command_input_argument_mode():
    result = build_command_input(
        command="python",
        extra_args=["examples/path with spaces/name_error.py"],
    )

    assert result == ["python", "examples/path with spaces/name_error.py"]


def test_build_command_input_extra_args_only():
    result = build_command_input(
        command=None,
        extra_args=["python", "main.py"],
    )

    assert result == ["python", "main.py"]


def test_build_command_input_empty():
    result = build_command_input(command=None, extra_args=[])

    assert result is None