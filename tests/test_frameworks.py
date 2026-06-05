from pathlib import Path

from termdoctor.engines.python.frameworks import (
    build_framework_diagnosis_context,
    detect_framework_from_error,
    detect_frameworks,
)
from termdoctor.models import ParsedError


def test_detect_frameworks_from_dependencies(tmp_path):
    result = detect_frameworks(
        project_root=tmp_path,
        dependencies=["django", "fastapi", "sqlalchemy", "alembic", "pytest", "aiogram", "pytelegrambotapi"],
    )

    assert result.is_detected("Django")
    assert result.is_detected("FastAPI")
    assert result.is_detected("SQLAlchemy")
    assert result.is_detected("Alembic")
    assert result.is_detected("pytest")
    assert result.is_detected("aiogram")
    assert result.is_detected("pyTelegramBotAPI")


def test_detect_frameworks_from_files(tmp_path):
    (tmp_path / "manage.py").write_text("", encoding="utf-8")
    (tmp_path / "alembic.ini").write_text("", encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("", encoding="utf-8")

    result = detect_frameworks(project_root=tmp_path, dependencies=[])

    assert result.is_detected("Django")
    assert result.is_detected("Alembic")
    assert result.is_detected("pytest")


def test_detect_framework_from_django_error():
    parsed = ParsedError(
        error_type="NoReverseMatch",
        message="Reverse for 'missing' not found",
        raw_text="django.urls.exceptions.NoReverseMatch: Reverse for 'missing' not found",
        extracted={"full_error_type": "django.urls.exceptions.NoReverseMatch"},
    )

    assert detect_framework_from_error(parsed) == "Django"


def test_detect_framework_from_fastapi_error():
    parsed = ParsedError(
        error_type="ResponseValidationError",
        message="validation errors",
        raw_text="fastapi.exceptions.ResponseValidationError: validation errors",
        extracted={"full_error_type": "fastapi.exceptions.ResponseValidationError"},
    )

    assert detect_framework_from_error(parsed) == "FastAPI"


def test_build_framework_diagnosis_context():
    framework_info = detect_frameworks(Path.cwd(), ["django"])
    parsed = ParsedError(
        error_type="NoReverseMatch",
        message="Reverse for 'missing' not found",
        raw_text="django.urls.exceptions.NoReverseMatch: Reverse for 'missing' not found",
        extracted={"full_error_type": "django.urls.exceptions.NoReverseMatch"},
    )

    context = build_framework_diagnosis_context(parsed, framework_info)

    assert context is not None
    assert context.matched_framework == "Django"
    assert context.detected_frameworks