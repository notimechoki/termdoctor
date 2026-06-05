<p align="center">
  <img src="assets/banner.png" alt="TermDoctor banner" width="100%">
</p>

<h1 align="center">TermDoctor</h1>

<p align="center">
  <strong>A CLI tool that explains terminal errors and suggests practical fixes.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Typer-CLI-009688?style=for-the-badge" alt="Typer">
  <img src="https://img.shields.io/badge/Rich-Terminal_UI-4B8BBE?style=for-the-badge" alt="Rich">
  <img src="https://img.shields.io/badge/Version-0.3.0-blue?style=for-the-badge" alt="Version 0.3.0">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a command-line debugging assistant.

It runs a command, captures the error output, detects the language engine, parses the traceback, explains the error in clear English, and suggests practical fixes.

Current stable engine:

| Engine | Status |
|---|---|
| Python | Supported |

TermDoctor is now built around a language engine architecture, so additional engines can be added later without mixing all parsers and rules into one file.

---

## Current version

```text
0.3.0
```

---

## What TermDoctor currently supports

### Python support

TermDoctor supports standard Python tracebacks, Python environment inspection, dependency inspection, Markdown reports, and framework-aware diagnosis for common Python ecosystems.

### Framework-aware Python diagnosis

| Ecosystem | Support |
|---|---|
| Django | Supported |
| FastAPI | Supported |
| Flask | Supported |
| Pydantic | Supported |
| SQLAlchemy | Supported |
| Alembic | Supported |
| pytest | Supported |
| aiogram | Supported |
| pyTelegramBotAPI | Supported |

---

## Installation

### Install from GitHub with pipx

```bash
pipx install git+https://github.com/notimechoki/termdoctor.git
```

Check:

```bash
termdoctor --version
termdoctor --help
```

### Install from local clone

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate

pip install -e .
termdoctor --help
```

### Development install

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pytest
```

---

## Commands

| Command | Description |
|---|---|
| `termdoctor --help` | Show help |
| `termdoctor --version` | Show version |
| `termdoctor languages` | Show registered language engines |
| `termdoctor run -- python main.py` | Run a command and diagnose errors |
| `termdoctor explain error.txt` | Explain traceback from file |
| `termdoctor explain error.txt --lang python` | Force Python engine |
| `termdoctor paste` | Paste traceback manually |
| `termdoctor report last` | Generate Markdown report from last error |
| `termdoctor report error.txt --output report.md` | Write report to file |
| `termdoctor env` | Show Python project environment |
| `termdoctor doctor python` | Run Python project diagnostics |
| `termdoctor history` | Show failed command history |
| `termdoctor clear` | Clear history |

---

## Examples

### Run Python file

```bash
termdoctor run -- python examples/name_error.py
```

### Explain framework traceback

```bash
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt
termdoctor explain examples/framework_tracebacks/fastapi_response_validation_error.txt
termdoctor explain examples/framework_tracebacks/sqlalchemy_operational_error.txt
```

### Force Python engine

```bash
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt --lang python
```

### Generate report

```bash
termdoctor run -- python examples/name_error.py
termdoctor report last --output reports/name-error.md
```

### Check registered engines

```bash
termdoctor languages
```

Output:

```text
Supported language engines
- Python (python)
```

---

## How language engines work

TermDoctor has a small core and language-specific engines.

Current structure:

```text
termdoctor core
├── LanguageDetector
├── BaseEngine
├── engine registry
└── PythonEngine
```

The Python engine owns:

- Python command detection;
- Python traceback parsing;
- Python rule loading;
- Python rule matching;
- Python environment context;
- Python framework context.

This keeps future JavaScript, Bash, Docker, Go, or Rust support separate from the Python logic.

---

## Project structure

```text
src/termdoctor/
├── engines/
│   ├── base.py
│   ├── detector.py
│   ├── registry.py
│   ├── python_engine.py
│   └── python/
│       └── rules.yml
├── cli.py
├── parser.py
├── matcher.py
├── rules_loader.py
├── renderer.py
├── environment.py
├── frameworks.py
├── dependencies.py
├── report.py
└── runner.py
```

---

## Development

Run tests:

```bash
pytest
```

Run a few manual checks:

```bash
termdoctor --version
termdoctor languages
termdoctor run -- python examples/name_error.py
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt
termdoctor report examples/framework_tracebacks/django_no_reverse_match.txt --output reports/django-report.md
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT License.

---

## Author

Created by [notimechoki](https://github.com/notimechoki).
