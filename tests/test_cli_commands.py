from typer.testing import CliRunner

from termdoctor import __version__
from termdoctor.cli import app


runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "TermDoctor" in result.output
    assert __version__ in result.output.replace("\x1b[1;36m", "").replace("\x1b[0m", "")


def test_env_command_runs():
    result = runner.invoke(app, ["env"])

    assert result.exit_code == 0
    assert "Python environment" in result.output


def test_doctor_python_command_runs():
    result = runner.invoke(app, ["doctor", "python"])

    assert result.exit_code == 0
    assert "TermDoctor Python doctor" in result.output