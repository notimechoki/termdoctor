import sys

from termdoctor.environment import (
    build_module_diagnosis_context,
    diagnose_python_project,
    find_project_venv,
    get_python_environment,
    is_venv_active,
)


def test_find_project_venv(tmp_path):
    venv = tmp_path / ".venv"
    venv.mkdir()

    result = find_project_venv(tmp_path)

    assert result == str(venv)


def test_get_python_environment_detects_project_files(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / "requirements.txt").write_text("requests==2.32.3\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
            [project]
            dependencies = [
                "typer>=0.12.0"
            ]
        """,
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()

    environment = get_python_environment(tmp_path)

    assert environment.python_executable == sys.executable
    assert environment.project_venv_path == str(tmp_path / ".venv")
    assert environment.requirements_file == str(tmp_path / "requirements.txt")
    assert environment.pyproject_file == str(tmp_path / "pyproject.toml")
    assert environment.tests_dir == str(tmp_path / "tests")
    assert "requests" in environment.dependency_info.requirements_dependencies
    assert "typer" in environment.dependency_info.pyproject_dependencies


def test_build_module_diagnosis_context_with_package_hint(tmp_path):
    (tmp_path / "requirements.txt").write_text("python-dotenv==1.0.1\n", encoding="utf-8")

    context = build_module_diagnosis_context("dotenv", tmp_path)

    assert context.module_name == "dotenv"
    assert context.package_hint == "python-dotenv"
    assert context.package_name == "python-dotenv"
    assert context.in_requirements is True


def test_diagnose_python_project_returns_warnings(tmp_path):
    result = diagnose_python_project(tmp_path)

    assert result.environment.cwd == str(tmp_path)
    assert result.warnings
    assert result.suggestions


def test_is_venv_active_returns_bool():
    assert isinstance(is_venv_active(), bool)