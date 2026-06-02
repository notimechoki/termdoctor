from pathlib import Path

from termdoctor.dependencies import dependency_exists
from termdoctor.models import FrameworkDetectionResult, FrameworkDiagnosisContext, FrameworkInfo, ParsedError


FRAMEWORK_DEPENDENCY_NAMES: dict[str, list[str]] = {
    "Django": ["django"],
    "FastAPI": ["fastapi", "starlette", "pydantic", "pydantic-settings"],
    "Flask": ["flask", "werkzeug", "jinja2"],
    "SQLAlchemy": ["sqlalchemy"],
    "Alembic": ["alembic"],
    "pytest": ["pytest"],
    "aiogram": ["aiogram"],
    "pyTelegramBotAPI": ["pytelegrambotapi", "telebot"],
}

FRAMEWORK_FILE_MARKERS: dict[str, list[str]] = {
    "Django": ["manage.py"],
    "FastAPI": [],
    "Flask": [],
    "SQLAlchemy": [],
    "Alembic": ["alembic.ini", "migrations/env.py", "alembic/env.py"],
    "pytest": ["pytest.ini", "conftest.py"],
    "aiogram": [],
    "pyTelegramBotAPI": [],
}

FRAMEWORK_ERROR_MARKERS: dict[str, list[str]] = {
    "Django": [
        "django.",
        "django.core.exceptions",
        "django.db.utils",
        "NoReverseMatch",
        "TemplateDoesNotExist",
        "ImproperlyConfigured",
    ],
    "FastAPI": [
        "fastapi.",
        "starlette.",
        "pydantic.",
        "ResponseValidationError",
        "RequestValidationError",
        "422 Unprocessable Entity",
    ],
    "Flask": [
        "flask.",
        "werkzeug.",
        "jinja2.",
        "BuildError",
        "TemplateNotFound",
    ],
    "SQLAlchemy": [
        "sqlalchemy.",
        "sqlalchemy.exc",
        "IntegrityError",
        "OperationalError",
        "ProgrammingError",
        "PendingRollbackError",
    ],
    "Alembic": [
        "alembic.",
        "alembic.util.exc",
        "CommandError",
        "Can't locate revision",
        "Target database is not up to date",
    ],
    "pytest": [
        "pytest",
        "FixtureLookupError",
        "fixture",
        "collected 0 items",
    ],
    "aiogram": [
        "aiogram.",
        "TelegramBadRequest",
        "TelegramUnauthorized",
        "TelegramForbidden",
        "TelegramRetryAfter",
    ],
    "pyTelegramBotAPI": [
        "telebot.",
        "ApiTelegramException",
        "Error code:",
        "Telegram API",
    ],
}


def detect_frameworks(project_root: Path, dependencies: list[str]) -> FrameworkDetectionResult:
    frameworks: list[FrameworkInfo] = []

    for framework_name, dependency_names in FRAMEWORK_DEPENDENCY_NAMES.items():
        evidence: list[str] = []

        for dependency_name in dependency_names:
            if dependency_exists(dependency_name, dependencies):
                evidence.append(f"dependency:{dependency_name}")

        for marker in FRAMEWORK_FILE_MARKERS.get(framework_name, []):
            if (project_root / marker).exists():
                evidence.append(f"file:{marker}")

        frameworks.append(
            FrameworkInfo(
                name=framework_name,
                detected=bool(evidence),
                evidence=evidence,
            )
        )

    return FrameworkDetectionResult(frameworks=frameworks)


def build_framework_diagnosis_context(
    parsed_error: ParsedError,
    framework_info: FrameworkDetectionResult,
) -> FrameworkDiagnosisContext | None:
    matched_framework = detect_framework_from_error(parsed_error)

    evidence: list[str] = []

    if matched_framework:
        evidence.append(f"error:{matched_framework}")

    detected = framework_info.detected_frameworks

    if not matched_framework and not detected:
        return None

    return FrameworkDiagnosisContext(
        detected_frameworks=detected,
        matched_framework=matched_framework,
        evidence=evidence,
    )


def detect_framework_from_error(parsed_error: ParsedError) -> str | None:
    searchable = "\n".join(
        [
            parsed_error.error_type,
            parsed_error.message,
            parsed_error.raw_text,
            parsed_error.extracted.get("full_error_type", ""),
        ]
    ).lower()

    for framework_name, markers in FRAMEWORK_ERROR_MARKERS.items():
        for marker in markers:
            if marker.lower() in searchable:
                return framework_name

    return None