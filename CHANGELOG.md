# Changelog

## 0.2.3 - Python Framework Diagnosis

### Added

- Added framework detection for Python projects.
- Added framework context in terminal diagnosis output.
- Added detected frameworks to `termdoctor env`.
- Added framework-aware suggestions to `termdoctor doctor python`.
- Added framework context to generated Markdown reports.
- Added support for common Django traceback patterns:
  - `ImproperlyConfigured`
  - `NoReverseMatch`
  - `TemplateDoesNotExist`
  - common `django.db.utils.*` errors
- Added support for common FastAPI and Pydantic traceback patterns:
  - `ResponseValidationError`
  - `RequestValidationError`
  - `ValidationError`
- Added support for common Flask/Jinja/Werkzeug traceback patterns:
  - `BuildError`
  - `TemplateNotFound`
- Added support for common SQLAlchemy traceback patterns:
  - `OperationalError`
  - `IntegrityError`
  - `ProgrammingError`
  - `PendingRollbackError`
- Added support for common Alembic migration errors.
- Added support for common pytest fixture and assertion errors.
- Added support for common aiogram Telegram API errors.
- Added support for common pyTelegramBotAPI Telegram API errors.
- Added example traceback files for supported frameworks.
- Added framework detection tests.
- Added parser and matcher tests for framework errors.

### Improved

- Improved traceback parser for framework exceptions that do not end with `Error`.
- Improved matcher so `match` rules are searched across message, raw traceback, and full dotted error type.
- Improved Python environment output with detected frameworks.
- Improved project doctor output with framework-specific suggestions.
- Improved report generation with framework context.

### Changed

- Bumped version to `0.2.3`.

## 0.2.2 - Reports & Better Python Diagnosis

### Added

- Added `termdoctor report`.
- Added Markdown report generation.
- Added report generation from last error.
- Added report generation from traceback files.
- Added `--output` support for reports.
- Added `--show-raw/--no-raw` support.
- Added more Python standard error rules.
- Added more examples and tests.

## 0.2.1 - Environment Polish

### Added

- Added project root detection.
- Added OS-aware virtual environment activation hints.
- Added nested requirements parsing with `-r` and `--requirement`.
- Added more package hints.
- Added more CLI tests.

## 0.2.0 - Python Environment Awareness

### Added

- Added `termdoctor env`.
- Added `termdoctor doctor python`.
- Added Python environment detection.
- Added dependency file detection.
- Added smarter `ModuleNotFoundError` suggestions.

## 0.1.1 - Stability Patch

### Added

- Added safer command execution format with `termdoctor run -- ...`.
- Added more Python error examples and tests.

### Improved

- Improved command parsing.
- Improved traceback parsing.
- Improved history table output.

## 0.1.0 - Initial Release

### Added

- Initial Python-only CLI.
- Rule-based Python error diagnosis.
- Basic examples and tests.
