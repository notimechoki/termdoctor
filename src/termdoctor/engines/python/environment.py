import os
import sys
from pathlib import Path

from termdoctor.engines.python.dependencies import collect_dependency_info, dependency_exists
from termdoctor.engines.python.frameworks import detect_frameworks
from termdoctor.engines.python.package_hints import get_install_name, get_package_hint
from termdoctor.core.platform_utils import get_activation_command
from termdoctor.core.project import find_project_root
from termdoctor.models import ModuleDiagnosisContext, PythonDoctorResult, PythonEnvironment


def get_python_environment(cwd: Path | None = None) -> PythonEnvironment:
    current_dir = (cwd or Path.cwd()).resolve()
    project_root = find_project_root(current_dir)

    dependency_info = collect_dependency_info(project_root)
    framework_info = detect_frameworks(project_root, dependency_info.all_dependencies)

    active_venv_path = get_active_venv_path()
    project_venv_path = find_project_venv(project_root)
    activation_command = get_activation_command(project_venv_path)

    requirements_file = str(project_root / "requirements.txt") if (project_root / "requirements.txt").exists() else None
    pyproject_file = str(project_root / "pyproject.toml") if (project_root / "pyproject.toml").exists() else None
    env_file = str(project_root / ".env") if (project_root / ".env").exists() else None
    env_example_file = str(project_root / ".env.example") if (project_root / ".env.example").exists() else None
    tests_dir = str(project_root / "tests") if (project_root / "tests").exists() else None

    return PythonEnvironment(
        python_version=get_python_version(),
        python_executable=sys.executable,
        current_dir=str(current_dir),
        project_root=str(project_root),
        cwd=str(project_root),
        venv_active=is_venv_active(),
        active_venv_path=active_venv_path,
        project_venv_path=project_venv_path,
        activation_command=activation_command,
        requirements_file=requirements_file,
        pyproject_file=pyproject_file,
        env_file=env_file,
        env_example_file=env_example_file,
        tests_dir=tests_dir,
        dependency_info=dependency_info,
        framework_info=framework_info,
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
    current_dir = cwd or Path.cwd()
    environment = get_python_environment(current_dir)

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
        activation_command=environment.activation_command,
        python_executable=environment.python_executable,
        current_dir=environment.current_dir,
        project_root=environment.project_root,
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

    for framework in environment.framework_info.frameworks:
        checks.append((f"{framework.name} detected", framework.detected))

    warnings: list[str] = []
    suggestions: list[str] = []

    if not environment.venv_active:
        warnings.append("Virtual environment is not active.")

        if environment.project_venv_path:
            if environment.activation_command:
                suggestions.append(f"Activate the project virtual environment: {environment.activation_command}")
            else:
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

    add_framework_suggestions(environment, warnings, suggestions)

    return PythonDoctorResult(
        environment=environment,
        checks=checks,
        warnings=warnings,
        suggestions=deduplicate(suggestions),
    )


def add_framework_suggestions(
    environment: PythonEnvironment,
    warnings: list[str],
    suggestions: list[str],
) -> None:
    frameworks = environment.framework_info

    if frameworks.is_detected("Django"):
        if not (Path(environment.project_root) / "manage.py").exists():
            warnings.append("Django dependency was detected, but manage.py was not found.")
        suggestions.append("For Django errors, check settings.py, INSTALLED_APPS, database settings, templates, and URL names.")

    if frameworks.is_detected("FastAPI"):
        suggestions.append("For FastAPI errors, check request/response models, Pydantic validation, and Uvicorn import paths.")

    if frameworks.is_detected("Flask"):
        suggestions.append("For Flask errors, check app factory/import path, routes, templates, and environment variables.")

    if frameworks.is_detected("SQLAlchemy"):
        suggestions.append("For SQLAlchemy errors, check database URL, sessions, models, relationships, and applied migrations.")

    if frameworks.is_detected("Alembic"):
        suggestions.append("For Alembic errors, check alembic.ini, env.py, revision IDs, and migration state.")

    if frameworks.is_detected("pytest"):
        suggestions.append("For pytest errors, check test discovery, fixture names, conftest.py, and assertion output.")

    if frameworks.is_detected("aiogram"):
        suggestions.append("For aiogram errors, check bot token, router registration, async handlers, and Telegram API error details.")

    if frameworks.is_detected("pyTelegramBotAPI"):
        suggestions.append("For pyTelegramBotAPI errors, check bot token, handler filters, polling/webhook mode, and Telegram API error details.")


def deduplicate(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for item in items:
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result