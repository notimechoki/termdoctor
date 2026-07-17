from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from termdoctor.engines.python.dependencies import dependency_exists
from termdoctor.models import FrameworkDetectionResult, FrameworkDiagnosisContext, FrameworkInfo, ParsedError


@dataclass(frozen=True)
class FrameworkDefinition:
    name: str
    primary_dependencies: tuple[str, ...] = ()
    supporting_dependencies: tuple[str, ...] = ()
    file_markers: tuple[str, ...] = ()
    error_markers: tuple[str, ...] = ()


FRAMEWORKS: tuple[FrameworkDefinition, ...] = (
    FrameworkDefinition(
        "Django",
        primary_dependencies=("django",),
        file_markers=("manage.py",),
        error_markers=(
            "django.",
            "NoReverseMatch",
            "TemplateDoesNotExist",
            "ImproperlyConfigured",
            "django.core.management.base.CommandError",
        ),
    ),
    FrameworkDefinition(
        "FastAPI",
        primary_dependencies=("fastapi",),
        supporting_dependencies=("starlette", "pydantic", "pydantic-settings"),
        error_markers=(
            "fastapi.",
            "fastapi.exceptions.ResponseValidationError",
            "fastapi.exceptions.RequestValidationError",
            "ResponseValidationError",
            "RequestValidationError",
        ),
    ),
    FrameworkDefinition(
        "Flask",
        primary_dependencies=("flask",),
        supporting_dependencies=("werkzeug", "jinja2"),
        error_markers=("flask.", "werkzeug.routing.exceptions.BuildError", "flask.templating.TemplateNotFound"),
    ),
    FrameworkDefinition(
        "Pydantic",
        primary_dependencies=("pydantic", "pydantic-settings"),
        error_markers=("pydantic.", "pydantic_core.", "PydanticUserError"),
    ),
    FrameworkDefinition(
        "SQLAlchemy",
        primary_dependencies=("sqlalchemy",),
        error_markers=("sqlalchemy.", "sqlalchemy.exc."),
    ),
    FrameworkDefinition(
        "Alembic",
        primary_dependencies=("alembic",),
        file_markers=("alembic.ini", "migrations/env.py", "alembic/env.py"),
        error_markers=(
            "alembic.",
            "alembic.util.exc.CommandError",
            "Can't locate revision",
            "Target database is not up to date",
        ),
    ),
    FrameworkDefinition(
        "pytest",
        primary_dependencies=("pytest",),
        file_markers=("pytest.ini", "conftest.py"),
        error_markers=("_pytest.", "FixtureLookupError", "pytest.fixture"),
    ),
    FrameworkDefinition(
        "aiogram",
        primary_dependencies=("aiogram",),
        error_markers=("aiogram.", "aiogram.exceptions.Telegram"),
    ),
    FrameworkDefinition(
        "pyTelegramBotAPI",
        primary_dependencies=("pytelegrambotapi",),
        error_markers=("telebot.", "telebot.apihelper.ApiTelegramException"),
    ),
)


def detect_frameworks(project_root: Path, dependencies: list[str]) -> FrameworkDetectionResult:
    frameworks: list[FrameworkInfo] = []
    for definition in FRAMEWORKS:
        evidence: list[str] = []
        primary_found = [
            dependency
            for dependency in definition.primary_dependencies
            if dependency_exists(dependency, dependencies)
        ]
        for dependency in primary_found:
            evidence.append(f"dependency:{dependency}")

        file_found = []
        for marker in definition.file_markers:
            if (project_root / marker).exists():
                file_found.append(marker)
                evidence.append(f"file:{marker}")

        detected = bool(primary_found or file_found)
        if detected:
            for dependency in definition.supporting_dependencies:
                if dependency_exists(dependency, dependencies):
                    evidence.append(f"dependency:{dependency}")

        frameworks.append(FrameworkInfo(definition.name, detected, evidence))
    return FrameworkDetectionResult(frameworks)


def build_framework_diagnosis_context(
    parsed_error: ParsedError,
    framework_info: FrameworkDetectionResult,
) -> FrameworkDiagnosisContext | None:
    matched_framework, matched_evidence = detect_framework_from_error_with_evidence(parsed_error)
    detected = framework_info.detected_frameworks
    if not matched_framework and not detected:
        return None
    evidence = [f"error:{marker}" for marker in matched_evidence]
    return FrameworkDiagnosisContext(
        detected_frameworks=detected,
        matched_framework=matched_framework,
        evidence=evidence,
    )


def detect_framework_from_error(parsed_error: ParsedError) -> str | None:
    return detect_framework_from_error_with_evidence(parsed_error)[0]


def detect_framework_from_error_with_evidence(parsed_error: ParsedError) -> tuple[str | None, list[str]]:
    searchable = "\n".join(
        [
            parsed_error.error_type,
            parsed_error.message,
            parsed_error.raw_text,
            parsed_error.full_error_type or parsed_error.extracted.get("full_error_type", ""),
        ]
    ).lower()

    best_name: str | None = None
    best_markers: list[str] = []
    best_score = -1
    for definition in FRAMEWORKS:
        markers = [marker for marker in definition.error_markers if marker.lower() in searchable]
        if not markers:
            continue
        score = max((20 if "." in marker else 5) + len(marker) for marker in markers)
        if score > best_score:
            best_name = definition.name
            best_markers = markers
            best_score = score
    return best_name, best_markers
