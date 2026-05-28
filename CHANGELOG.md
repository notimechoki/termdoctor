# Changelog

## 0.2.2 - Reports & Better Python Diagnosis

### Added

- Added `termdoctor report`.
- Added Markdown report generation from the last saved error.
- Added Markdown report generation from a traceback file.
- Added `--output` for writing reports to a file.
- Added `--show-raw/--no-raw` for including or excluding raw traceback in reports.
- Added `src/termdoctor/report.py`.
- Added rules for more Python errors:
  - `UnboundLocalError`
  - `AssertionError`
  - `RuntimeError`
  - `OSError`
  - `IsADirectoryError`
  - `NotADirectoryError`
  - `EOFError`
  - `ConnectionError`
  - `TimeoutError`
  - `BrokenPipeError`
  - `MemoryError`
- Added more Python error examples.
- Added tests for report generation.
- Added parser tests for additional Python errors.
- Added matcher tests for additional Python rules.
- Added CLI tests for the report command.

### Improved

- Improved Python traceback detail extraction for `UnboundLocalError`.
- Improved path extraction for `IsADirectoryError` and `NotADirectoryError`.
- Improved project usefulness by making errors easier to share through Markdown reports.

### Changed

- Updated package version to `0.2.2`.

## 0.2.1 - Environment Polish

### Added

- Added project root detection from nested directories.
- Added OS-aware virtual environment activation hints.
- Added support for nested requirements files with `-r` / `--requirement`.
- Added more package hints for common Python imports.
- Added tests for project root detection, platform utilities, and CLI commands.

### Improved

- Improved `termdoctor env` output with current directory and project root.
- Improved `termdoctor doctor python` suggestions for virtual environments.
- Improved `ModuleNotFoundError` environment context.
- Improved dependency parsing for more real-world requirements files.

## 0.2.0 - Python Environment Awareness

### Added

- Added `termdoctor env`.
- Added `termdoctor doctor python`.
- Added Python version detection.
- Added Python executable detection.
- Added virtual environment detection.
- Added project virtual environment detection.
- Added `requirements.txt` detection.
- Added basic `requirements.txt` dependency parsing.
- Added `pyproject.toml` detection.
- Added basic `[project] dependencies` parsing from `pyproject.toml`.
- Added package-name hints for common import/package mismatches.
- Added environment-aware context for `ModuleNotFoundError`.
- Added environment/dependency tests.
- Added `examples/missing_dotenv.py`.

### Improved

- Improved `ModuleNotFoundError` diagnosis.
- Improved suggestions when a project virtual environment exists but is not active.
- Improved suggestions when a missing package is already listed in `requirements.txt`.
- Improved suggestions when a missing package is already listed in `pyproject.toml`.
- Improved terminal output with environment context tables.

### Changed

- Updated package version to `0.2.0`.
- Updated `ModuleNotFoundError` rule to avoid blindly suggesting `pip install {module}` in every case.
- Added `tomli` fallback dependency for Python 3.10 compatibility.

## 0.1.1 - Stability Patch

### Added

- Added safer command execution format with `termdoctor run -- ...`.
- Added support for dotted Python error names like `json.decoder.JSONDecodeError`.
- Added more Python error examples.
- Added more parser tests.
- Added matcher tests for more error types.
- Added history tests.
- Added command input tests.

### Improved

- Improved command parsing.
- Improved handling of paths with spaces when using `termdoctor run -- ...`.
- Improved traceback parsing for chained exceptions.
- Improved history table output.
- Improved terminal formatting.
- Improved no-error-detected message.

### Fixed

- Fixed command execution for argument lists.
- Fixed parsing for tracebacks with dotted exception names.
- Fixed parsing when traceback contains chained exception messages.
- Fixed the typo in the test filename: `test_mathcer.py` -> `test_matcher.py`.

## 0.1.0 - Initial Release

### Added

- Initial Python-only CLI.
- Rule-based Python error diagnosis.
- `termdoctor run` command.
- `termdoctor explain` command.
- `termdoctor paste` command.
- `termdoctor history` command.
- `termdoctor clear` command.
- YAML-based Python error rules.
- Basic examples and tests.
