# Changelog

All notable changes to this project will be documented in this file.

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