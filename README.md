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
  <img src="https://img.shields.io/badge/Version-0.2.2-blue?style=for-the-badge" alt="Version 0.2.2">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a command-line tool that helps developers understand Python terminal errors.

Instead of showing only a raw traceback, TermDoctor detects the error type, explains what happened in simple English, suggests practical next steps, inspects the local Python environment, and can generate Markdown reports.

TermDoctor works locally, does not use AI, does not send data to external services, and uses rule-based diagnosis.

---

## Current version

```text
0.2.2
```

TermDoctor is currently focused on Python errors only.

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

| Source | Support status |
|---|---|
| Python scripts | Supported |
| Python modules | Supported |
| Python environment inspection | Supported |
| requirements.txt inspection | Supported |
| pyproject.toml inspection | Supported |
| Markdown reports | Supported |
| Django commands | Supported if the output contains a normal Python traceback |
| FastAPI / Uvicorn commands | Supported if the command exits and prints a Python traceback |
| pytest output | Basic traceback parsing only |
| Docker logs | Not supported |
| live server logs | Not supported |

### Supported Python errors

| Error | Description |
|---|---|
| `SyntaxError` | Invalid Python syntax |
| `IndentationError` | Incorrect indentation |
| `ModuleNotFoundError` | Missing Python module |
| `ImportError` | Import failed |
| `NameError` | Variable, function, or class name is not defined |
| `UnboundLocalError` | Local variable is used before assignment |
| `TypeError` | Invalid operation or wrong value type |
| `ValueError` | Correct type, invalid value |
| `AttributeError` | Object does not have the requested attribute |
| `KeyError` | Dictionary key does not exist |
| `IndexError` | List, tuple, or string index is out of range |
| `FileNotFoundError` | File or directory was not found |
| `IsADirectoryError` | Expected a file, got a directory |
| `NotADirectoryError` | Expected a directory, got a file |
| `PermissionError` | Not enough permissions |
| `ZeroDivisionError` | Division by zero |
| `RecursionError` | Maximum recursion depth exceeded |
| `UnicodeDecodeError` | Text decoding failed |
| `JSONDecodeError` | Invalid JSON |
| `AssertionError` | Assertion failed |
| `RuntimeError` | Runtime error |
| `OSError` | Operating system error |
| `EOFError` | Input ended unexpectedly |
| `ConnectionError` | Network connection failed |
| `TimeoutError` | Operation timed out |
| `BrokenPipeError` | Broken pipe |
| `MemoryError` | Not enough memory |

---

## Features

- Run commands through `termdoctor`
- Capture `stdout` and `stderr`
- Detect common Python errors
- Explain errors in simple English
- Suggest practical fixes
- Save failed command history
- Explain the last saved error
- Explain a traceback from a text file
- Paste a traceback manually through stdin
- Inspect the current Python environment
- Inspect `requirements.txt`
- Inspect `[project] dependencies` from `pyproject.toml`
- Provide package-name hints for common import/package mismatches
- Generate Markdown reports
- Store diagnosis rules in a readable YAML file

---

## Installation

### Install directly from GitHub with pipx

```bash
pipx install git+https://github.com/notimechoki/termdoctor.git
```

Check that the command is available:

```bash
termdoctor --help
```

If `pipx` is not installed:

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

Restart your terminal after running `pipx ensurepath`.

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

### Development installation

```bash
git clone https://github.com/notimechoki/termdoctor.git
cd termdoctor

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pytest
```

---

## Usage

### Show help

```bash
termdoctor --help
```

### Show version

```bash
termdoctor --version
```

Expected output:

```text
TermDoctor 0.2.2
```

### Run a Python file

```bash
termdoctor run "python main.py"
```

Recommended argument mode:

```bash
termdoctor run -- python main.py
```

Example:

```bash
termdoctor run -- python examples/module_not_found.py
```

### Run a Python module

```bash
termdoctor run -- python -m my_module
```

### Run a Django command

```bash
termdoctor run -- python manage.py migrate
```

### Run a FastAPI / Uvicorn command

```bash
termdoctor run -- uvicorn app.main:app --reload
```

This works best when the command exits and prints a Python traceback.

### Inspect Python environment

```bash
termdoctor env
```

### Diagnose the current Python project

```bash
termdoctor doctor python
```

### Explain the last saved error

```bash
termdoctor explain last
```

### Explain an error from a file

```bash
termdoctor explain error.txt
```

### Paste a traceback manually

```bash
termdoctor paste
```

Finish input with:

- Linux/macOS: `Ctrl+D`
- Windows: `Ctrl+Z`, then `Enter`

### Generate a Markdown report

Generate a report from the last saved error:

```bash
termdoctor report last
```

Write a report to a file:

```bash
termdoctor report last --output report.md
```

Generate a report from a traceback file:

```bash
termdoctor report error.txt --output report.md
```

Generate a report without raw traceback:

```bash
termdoctor report last --output report.md --no-raw
```

### Show history

```bash
termdoctor history
```

Show only the last 5 saved errors:

```bash
termdoctor history --limit 5
```

### Clear history

```bash
termdoctor clear
```

---

## Command reference

| Command | Description |
|---|---|
| `termdoctor --help` | Show help |
| `termdoctor --version` | Show current version |
| `termdoctor run "command"` | Run a command and explain Python errors |
| `termdoctor run -- python main.py` | Run a command in safer argument mode |
| `termdoctor env` | Show Python environment information |
| `termdoctor doctor python` | Diagnose the current Python project |
| `termdoctor explain last` | Explain the last saved error |
| `termdoctor explain error.txt` | Explain a traceback from a file |
| `termdoctor paste` | Paste a traceback manually |
| `termdoctor report last` | Generate a Markdown report from the last saved error |
| `termdoctor report error.txt` | Generate a Markdown report from a traceback file |
| `termdoctor report last --output report.md` | Write a Markdown report to a file |
| `termdoctor history` | Show saved failed command history |
| `termdoctor history --limit 5` | Show a limited number of history items |
| `termdoctor clear` | Clear saved history |

---

## How it works

TermDoctor does not use AI.

It works with rule-based logic:

1. It runs the command.
2. It captures `stdout`, `stderr`, and exit code.
3. It tries to detect a Python traceback.
4. It extracts the error type and message.
5. It matches the error with a YAML rule.
6. It inspects the Python environment when useful.
7. It prints a clear explanation and possible fixes.
8. It can generate a Markdown report.

Rules are stored here:

```text
src/termdoctor/rules/python_errors.yml
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

Run example errors:

```bash
termdoctor run -- python examples/module_not_found.py
termdoctor run -- python examples/name_error.py
termdoctor run -- python examples/unbound_local_error.py
termdoctor run -- python examples/assertion_error.py
termdoctor run -- python examples/json_decode_error.py
```

Generate a report during development:

```bash
termdoctor run -- python examples/name_error.py
termdoctor report last --output reports/name-error.md
```

---

## Adding new rules

Rules are stored in:

```text
src/termdoctor/rules/python_errors.yml
```

A rule looks like this:

```yaml
- id: module_not_found
  error: ModuleNotFoundError
  title: "Python cannot find a module"
  explanation: "Python tried to import `{module}`, but it is not available in the current environment."
  causes:
    - "The package is not installed in the Python environment used to run this command."
  fixes:
    - "Check the environment context shown by TermDoctor."
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
