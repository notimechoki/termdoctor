<p align="center">
  <img src="assets/banner.png" alt="TermDoctor banner" width="100%">
</p>

<h1 align="center">TermDoctor</h1>

<p align="center">
  <strong>A CLI tool that explains Python terminal errors and suggests practical fixes.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  </a>
  <a href="https://typer.tiangolo.com/">
    <img src="https://img.shields.io/badge/Typer-CLI-009688?style=for-the-badge" alt="Typer">
  </a>
  <a href="https://github.com/Textualize/rich">
    <img src="https://img.shields.io/badge/Rich-Terminal_UI-4B8BBE?style=for-the-badge" alt="Rich">
  </a>
  <a href="https://pyyaml.org/">
    <img src="https://img.shields.io/badge/PyYAML-Rules-FFCA28?style=for-the-badge" alt="PyYAML">
  </a>
  <img src="https://img.shields.io/badge/Version-0.2.3-blue?style=for-the-badge" alt="Version 0.2.3">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a local command-line tool that explains Python terminal errors and suggests practical fixes.

It reads Python tracebacks, detects the error type, matches it with rule-based explanations, checks the current Python project context, and prints a clearer diagnosis.

TermDoctor does not use AI and does not send your code, errors, or environment data anywhere.

---

## Current version

```text
0.2.3
```

This version focuses on **better Python and Python framework diagnosis**.

---

## What TermDoctor currently supports

### Language support

| Language | Support status |
|---|---|
| Python | Supported |
| JavaScript / TypeScript | Not supported |
| Go | Not supported |
| Rust | Not supported |
| Java | Not supported |
| Bash / Shell | Not supported |

### Python ecosystem support

| Source / framework | Support status |
|---|---|
| Python scripts | Supported |
| Python modules | Supported |
| Django | Supported for common traceback patterns |
| FastAPI | Supported for common traceback patterns |
| Flask | Supported for common traceback patterns |
| SQLAlchemy | Supported for common traceback patterns |
| Alembic | Supported for common traceback patterns |
| pytest | Supported for common traceback patterns |
| aiogram | Supported for common Telegram API traceback patterns |
| pyTelegramBotAPI | Supported for common Telegram API traceback patterns |
| Pydantic | Supported for common validation errors |
| Docker logs | Not supported |
| live server logs | Not supported |

---

## Supported commands

| Command | Description |
|---|---|
| `termdoctor --help` | Show help |
| `termdoctor --version` | Show current version |
| `termdoctor run "command"` | Run a command and explain Python errors |
| `termdoctor run -- python main.py` | Run a command in safer argument mode |
| `termdoctor env` | Show Python environment, dependencies, and detected frameworks |
| `termdoctor doctor python` | Diagnose the current Python project |
| `termdoctor explain last` | Explain the last saved error |
| `termdoctor explain error.txt` | Explain a traceback from a file |
| `termdoctor paste` | Paste a traceback manually |
| `termdoctor report last` | Generate a Markdown report from the last saved error |
| `termdoctor report error.txt` | Generate a Markdown report from a traceback file |
| `termdoctor report last --output report.md` | Save a Markdown report to a file |
| `termdoctor history` | Show saved failed command history |
| `termdoctor history --limit 5` | Show a limited number of history items |
| `termdoctor clear` | Clear saved history |

---

## Installation

### Install directly from GitHub with pipx

```bash
pipx install git+https://github.com/notimechoki/termdoctor.git
```

Check:

```bash
termdoctor --help
```

If `pipx` is not installed:

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

Restart your terminal after `pipx ensurepath`.

---

### Install from a local clone

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate

pip install -e .
termdoctor --help
```

On Windows PowerShell:

```powershell
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -e .
termdoctor --help
```

---

## Usage examples

### Run a Python file

```bash
termdoctor run -- python main.py
```

### Run Django

```bash
termdoctor run -- python manage.py migrate
termdoctor run -- python manage.py runserver
```

### Run FastAPI / Uvicorn

```bash
termdoctor run -- uvicorn app.main:app --reload
```

### Run pytest

```bash
termdoctor run -- pytest
```

### Explain the last saved error

```bash
termdoctor explain last
```

### Generate a Markdown report

```bash
termdoctor report last --output reports/error-report.md
```

### Check the environment

```bash
termdoctor env
```

### Diagnose the Python project

```bash
termdoctor doctor python
```

---

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run example tracebacks:

```bash
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt
termdoctor explain examples/framework_tracebacks/fastapi_response_validation_error.txt
termdoctor explain examples/framework_tracebacks/sqlalchemy_operational_error.txt
termdoctor explain examples/framework_tracebacks/alembic_command_error.txt
termdoctor explain examples/framework_tracebacks/pytest_fixture_error.txt
termdoctor explain examples/framework_tracebacks/aiogram_bad_request.txt
termdoctor explain examples/framework_tracebacks/pytelegrambotapi_api_exception.txt
```

---

## How it works

TermDoctor works with rule-based logic:

1. Runs a command or reads a traceback.
2. Parses the Python traceback.
3. Detects the normalized error type.
4. Matches the error against YAML diagnosis rules.
5. Checks the project environment.
6. Detects known Python frameworks from dependencies and project files.
7. Shows diagnosis, likely causes, and suggestions.
8. Optionally generates a Markdown report.

Rules are stored here:

```text
src/termdoctor/rules/python_errors.yml
```

---

## Changelog

See full release notes in [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT License.

---

## Author

Created by [notimechoki](https://github.com/notimechoki).
