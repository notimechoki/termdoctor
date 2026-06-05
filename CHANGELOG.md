# Changelog

## 0.3.0 - Language Engine Architecture

### Added

- Added language engine architecture.
- Added `BaseEngine` abstraction.
- Added `EngineDiagnosis` model.
- Added `PythonEngine`.
- Added `LanguageDetector`.
- Added default engine registry.
- Added language-specific Python rules at `src/termdoctor/engines/python/rules.yml`.
- Added `termdoctor languages` command.
- Added `--lang python` option for `explain`, `paste`, and `report`.
- Added engine tests.
- Added CLI tests for language engine commands.

### Changed

- Moved Python rule loading into `PythonEngine`.
- Updated CLI diagnosis flow to use language detection.
- Updated Markdown reports to use engine diagnosis.
- Updated `matcher.py` and `rules_loader.py` as compatibility wrappers around `PythonEngine`.
- Updated package data to include language-specific rules.
- Updated README for engine-based architecture.

### Removed

- Removed old global `src/termdoctor/rules/python_errors.yml` rule location.

## 0.2.3 - Python Framework Diagnosis

### Added

- Added framework detection for Django, FastAPI, Flask, Pydantic, SQLAlchemy, Alembic, pytest, aiogram, and pyTelegramBotAPI.
- Added framework-aware diagnosis context.
- Added framework-specific Python rules.
- Added framework traceback examples.
- Added framework tests.

## 0.2.2 - Reports & Better Python Diagnosis

### Added

- Added Markdown report generation.
- Added `termdoctor report` command.
- Added more Python error rules.
- Added more report tests and examples.

## 0.2.1 - Environment Polish

### Added

- Added project root detection.
- Added OS-aware virtual environment activation hints.
- Added nested requirements parsing.
- Added more package hints.

## 0.2.0 - Python Environment Awareness

### Added

- Added `termdoctor env`.
- Added `termdoctor doctor python`.
- Added Python environment and dependency awareness.
- Added smarter `ModuleNotFoundError` diagnosis.

## 0.1.1 - Stability Patch

### Added

- Added safer command execution format with `termdoctor run -- ...`.
- Improved traceback parsing and history output.

## 0.1.0 - Initial Release

### Added

- Initial Python-only CLI.
- Rule-based Python error diagnosis.
- Basic examples and tests.
