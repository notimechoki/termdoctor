import os
import sys
from pathlib import Path

from termdoctor.dependencies import collect_dependency_info, dependency_exists
from termdoctor.models import ModuleDiagnosisContext, PythonDoctorResult, PythonEnvironment
from termdoctor.package_hints import get_install_name, get_package_hint


def get_python_environment(cwd: Path | None = None) -> PythonEnvironment:
    root = cwd or Path.cwd()

    dependency_info = collect_dependency_info(root)

    active_venv_path = get_active_venv_path()
    project_venv_path = find_project_venv(root)

    requirements_file = str(root / "requirements.txt") if (root / "requirements.txt").exists() else None
    pyproject_file = str(root / "pyproject.toml") if (root / "pyproject.toml").exists() else None
    env_file = str(root / ".env") if (root / ".env").exists() else None
    env_example_file = str(root / ".env.example") if (root / ".env.example").exists() else None
    tests_dir = str(root / "tests") if (root / "tests").exists() else None

    return PythonEnvironment(
        python_version=get_python_version(),
        python_executable=sys.executable,
        cwd=str(root),
        venv_active=is_venv_active(),
        active_venv_path=active_venv_path,
        project_venv_path=project_venv_path,
        requirements_file=requirements_file,
        pyproject_file=pyproject_file,
        env_file=env_file,
        env_example_file=env_example_file,
        tests_dir=tests_dir,
        dependency_info=dependency_info,
    )


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def is_venv_active() -> bool:
    if os.environ.get("VIRTUAL_ENV"):
        return True

    return sys.prefix != sys.base_prefix


def get_active_venv_path() -> str | None:
    virtual_env = os.environ.get("VIRTUAL_ENV")

    if virtual_env:
        return virtual_env

    if sys.prefix != sys.base_prefix:
        return sys.prefix

    return None


def find_project_venv(cwd: Path | None = None) -> str | None:
    root = cwd or Path.cwd()

    possible_names = [".venv", "venv", "env"]

    for name in possible_names:
        candidate = root / name

        if candidate.exists() and candidate.is_dir():
            return str(candidate)

    return None


def build_module_diagnosis_context(module_name: str, cwd: Path | None = None) -> ModuleDiagnosisContext:
    root = cwd or Path.cwd()
    environment = get_python_environment(root)

    package_hint = get_package_hint(module_name)
    package_name = get_install_name(module_name)

    dependency_info = environment.dependency_info

    in_requirements = dependency_exists(package_name, dependency_info.requirements_dependencies)
    in_pyproject = dependency_exists(package_name, dependency_info.pyproject_dependencies)

    if not in_requirements and package_hint is None:
        in_requirements = dependency_exists(module_name, dependency_info.requirements_dependencies)

    if not in_pyproject and package_hint is None:
        in_pyproject = dependency_exists(module_name, dependency_info.pyproject_dependencies)

    return ModuleDiagnosisContext(
        module_name=module_name,
        package_name=package_name,
        package_hint=package_hint,
        in_requirements=in_requirements,
        in_pyproject=in_pyproject,
        has_requirements_file=dependency_info.requirements_file is not None,
        has_pyproject_file=dependency_info.pyproject_file is not None,
        venv_active=environment.venv_active,
        active_venv_path=environment.active_venv_path,
        project_venv_path=environment.project_venv_path,
        python_executable=environment.python_executable,
    )


def diagnose_python_project(cwd: Path | None = None) -> PythonDoctorResult:
    environment = get_python_environment(cwd)

    checks: list[tuple[str, bool]] = [
        ("Python is available", bool(environment.python_executable)),
        ("Virtual environment is active", environment.venv_active),
        ("Project virtual environment exists", environment.project_venv_path is not None),
        ("requirements.txt found", environment.requirements_file is not None),
        ("pyproject.toml found", environment.pyproject_file is not None),
        ("tests directory found", environment.tests_dir is not None),
    ]

    warnings: list[str] = []
    suggestions: list[str] = []

    if not environment.venv_active:
        warnings.append("Virtual environment is not active.")

        if environment.project_venv_path:
            suggestions.append("Activate the project virtual environment before running project commands.")
        else:
            suggestions.append("Create and activate a virtual environment for this project.")

    if not environment.requirements_file and not environment.pyproject_file:
        warnings.append("No requirements.txt or pyproject.toml found.")
        suggestions.append("Add a dependency file so project setup is easier to reproduce.")

    if environment.requirements_file:
        suggestions.append("Install dependencies with: pip install -r requirements.txt")

    if environment.pyproject_file:
        suggestions.append("If this project is installable, use: pip install -e .")

    if environment.env_file and not environment.env_example_file:
        warnings.append(".env exists, but .env.example is missing.")
        suggestions.append("Add .env.example with safe placeholder values.")

    if not environment.tests_dir:
        warnings.append("tests directory was not found.")
        suggestions.append("Add tests/ if this project is meant to be maintained or shared.")

    return PythonDoctorResult(
        environment=environment,
        checks=checks,
        warnings=warnings,
        suggestions=deduplicate(suggestions),
    )


def deduplicate(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for item in items:
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result