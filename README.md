<p align="center">
  <img src="assets/banner.png" alt="TermDoctor banner" width="100%">
</p>

<h1 align="center">TermDoctor</h1>

<p align="center">
  <strong>A multilingual CLI assistant that explains Python terminal errors and suggests practical fixes.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Typer-CLI-009688?style=for-the-badge" alt="Typer">
  <img src="https://img.shields.io/badge/Rich-Terminal_UI-4B8BBE?style=for-the-badge" alt="Rich">
  <img src="https://img.shields.io/badge/Version-0.3.1-blue?style=for-the-badge" alt="Version 0.3.1">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a command-line debugging assistant for Python projects.

It can run a command, capture both `stdout` and `stderr`, parse a Python traceback, identify the most relevant rule, inspect the project environment, and explain the problem in English or Russian.

Version **0.3.1** is focused on making the Python engine reliable before additional programming-language engines are introduced.

Current stable engine:

| Engine | Status |
|---|---|
| Python | Supported |

Interface languages:

| Language | Code | Aliases |
|---|---|---|
| English | `en` | `eng`, `english` |
| Russian | `ru` | `rus`, `russian`, `рус`, `русский` |

---

## Highlights in 0.3.1

- 105 Python diagnosis rules with complete English and Russian explanations.
- Strict rule matching that avoids false framework diagnoses.
- Correct separation between interface language (`--lang`) and programming-language engine (`--engine`).
- Detection of `python3.10`, `python3.13`, Windows `python.exe`/`pytest.exe`, and common environment runners.
- ANSI-colored traceback support.
- Custom exception class support, including names that do not end in `Error`.
- Full traceback frame collection, exception chains, and source-code context.
- More precise `TypeError`, `ValueError`, `ImportError`, and `AttributeError` diagnosis.
- Smarter `ModuleNotFoundError` handling for standard-library and local project modules.
- Improved framework detection for Django, FastAPI, Flask, Pydantic, SQLAlchemy, Alembic, pytest, aiogram, and pyTelegramBotAPI.
- Dependency reading from multiple requirements files, nested includes, PEP 621 optional dependencies, dependency groups, Poetry sections, and Pipfile.
- Safer history storage with output limits, secret redaction, serialized atomic writes, and `--no-history`.
- Markdown reports use the original error working directory instead of whichever directory is currently open.

---

## Installation

### Install from GitHub with pipx

```bash
pipx install git+https://github.com/notimechoki/termdoctor.git
```

Check the installation:

```bash
termdoctor --version
termdoctor --help
```

### Install from a local clone

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
termdoctor --help
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

### Development installation

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

pytest
```

---

## Interface language

Use a language for one command:

```bash
termdoctor --lang ru explain error.txt
termdoctor --lang rus run -- python main.py
termdoctor --lang en doctor python
```

Save a default language:

```bash
termdoctor config language ru
termdoctor config language
```

Or use an environment variable:

```bash
TERMDOCTOR_LANG=ru termdoctor explain error.txt
```

Language resolution order:

1. global `--lang` option;
2. `TERMDOCTOR_LANG` environment variable;
3. saved TermDoctor configuration;
4. system locale;
5. English fallback.

Unknown translation keys safely fall back to English.

---

## Commands

| Command | Description |
|---|---|
| `termdoctor --help` | Show CLI help |
| `termdoctor --version` | Show the installed version |
| `termdoctor languages` | Show interface languages and registered engines |
| `termdoctor run -- python main.py` | Run a command and diagnose failure |
| `termdoctor run --no-history -- python main.py` | Diagnose without saving output to history |
| `termdoctor explain error.txt` | Explain a traceback from a file |
| `termdoctor explain error.txt --engine python` | Force the Python engine |
| `termdoctor paste` | Read a traceback from stdin |
| `termdoctor report last` | Generate a Markdown report from the latest saved failure |
| `termdoctor report error.txt -o report.md` | Write a report to a file |
| `termdoctor env` | Inspect the current Python project environment |
| `termdoctor doctor python` | Run project-level Python checks |
| `termdoctor history` | Show saved failed commands |
| `termdoctor clear` | Clear saved history |
| `termdoctor config language ru` | Save the default interface language |

`--lang python` after `explain`, `paste`, or `report` is retained as a compatibility alias for the old 0.3.0 engine option. New usage should prefer `--engine python` and reserve the global `--lang` option for the interface language.

---

## Examples

### Run a Python file

```bash
termdoctor run -- python examples/name_error.py
```

### Run with Russian explanations

```bash
termdoctor --lang ru run -- python examples/name_error.py
```

### Explain a saved traceback

```bash
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt
termdoctor explain examples/framework_tracebacks/fastapi_response_validation_error.txt
termdoctor explain examples/framework_tracebacks/sqlalchemy_operational_error.txt
```

### Force the Python engine

```bash
termdoctor explain error.txt --engine python
```

### Generate a report

```bash
termdoctor run -- python examples/name_error.py
termdoctor --lang ru report last --output reports/name-error.md
```

### Inspect the project

```bash
termdoctor env
termdoctor doctor python
```

---

## Python diagnosis

### Traceback parsing

The Python engine supports:

- standard Python tracebacks;
- ANSI-colored terminal output;
- dotted exception names such as `sqlalchemy.exc.OperationalError`;
- user-defined exceptions such as `Boom`;
- chained exceptions;
- `ExceptionGroup` output;
- all discovered traceback frames;
- nearby source lines when the file is available;
- preference for a project frame over a final `site-packages` frame.

### Rule matching

Specialized rules are selected only when their evidence actually matches. A rule may use:

- `match_any`;
- `match_all`;
- `exclude`;
- exact `full_error_types`;
- framework constraints;
- numeric priority.

If a specialized rule does not match, TermDoctor uses a generic fallback only when one exists. It no longer returns the first rule merely because the short exception class name is the same.

### Framework and ecosystem context

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

Primary dependencies prove framework detection. Supporting packages are only additional evidence. For example, installing Pydantic alone no longer marks a project as FastAPI.

### Dependency files

TermDoctor reads dependencies from:

- `requirements.txt`;
- `requirements-dev.txt` and other `requirements*.txt` files;
- nested `-r` and `--requirement` includes;
- PEP 621 `project.dependencies`;
- PEP 621 optional dependencies;
- dependency groups;
- Poetry dependencies and groups;
- `Pipfile` packages and dev-packages;
- VCS requirements with `#egg=` or PEP 508 direct references.

### Missing modules

For `ModuleNotFoundError`, TermDoctor checks whether the import is:

- part of the standard library;
- a local module in the project or `src/` layout;
- listed in requirements or project metadata;
- known under a different installation name.

Install suggestions use the active interpreter form:

```bash
/path/to/python -m pip install package
```

This avoids accidentally installing into a different Python environment.

---

## History and privacy

Failed commands are stored in:

```text
~/.termdoctor/history.json
```

TermDoctor 0.3.1:

- keeps at most 30 items;
- limits saved output size;
- redacts common tokens, passwords, API keys, bearer tokens, and credentials inside common database URLs;
- serializes concurrent updates and writes history atomically;
- attempts to use private directory/file permissions;
- backs up malformed history before starting a new file;
- supports `--no-history` for sensitive runs.

Automatic redaction is a safety layer, not a guarantee that every custom secret format can be recognized. Use `--no-history` for commands that may print sensitive information.

---

## Architecture

```text
src/termdoctor/
├── cli.py
├── i18n.py
├── models.py
├── renderer.py
├── report.py
├── locales/
│   ├── en.yml
│   └── ru.yml
├── core/
│   ├── history.py
│   ├── platform_utils.py
│   ├── project.py
│   └── runner.py
└── engines/
    ├── base.py
    ├── detector.py
    ├── registry.py
    └── python/
        ├── dependencies.py
        ├── engine.py
        ├── environment.py
        ├── frameworks.py
        ├── matcher.py
        ├── package_hints.py
        ├── parser.py
        ├── rules.yml
        ├── rules.ru.yml
        └── rules_loader.py
```

`EngineDiagnosis` exposes generic diagnostic sections, while engine-specific context remains available for compatibility and detailed reports. This keeps the renderer from needing a new hard-coded table for every future language engine.

---

## Development

Run the complete test suite:

```bash
pytest
```

Run coverage:

```bash
pytest --cov=termdoctor --cov-report=term-missing
```

Build release artifacts:

```bash
python -m build
```

Useful manual checks:

```bash
termdoctor --version
termdoctor languages
termdoctor --lang ru run -- python examples/name_error.py
termdoctor explain examples/framework_tracebacks/django_no_reverse_match.txt
termdoctor report examples/framework_tracebacks/django_no_reverse_match.txt -o report.md
termdoctor doctor python
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT License.

## Author

Created by [notimechoki](https://github.com/notimechoki).
