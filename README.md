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
  <img src="https://img.shields.io/badge/Version-0.2.0-blue?style=for-the-badge" alt="Version 0.2.0">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a command-line tool that helps developers understand Python terminal errors.

Instead of showing only a raw traceback, TermDoctor detects the error type, explains what happened in simple English, and suggests practical next steps.

TermDoctor can also inspect the current Python environment, detect dependency files, and provide more useful suggestions for missing modules.

---

## Current version

```text
0.2.0
```

TermDoctor is currently focused on Python errors only.

It works locally, does not use AI, does not send data to external services, and uses rule-based diagnosis.

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
| `TypeError` | Invalid operation or wrong value type |
| `ValueError` | Correct type, invalid value |
| `AttributeError` | Object does not have the requested attribute |
| `KeyError` | Dictionary key does not exist |
| `IndexError` | List, tuple, or string index is out of range |
| `FileNotFoundError` | File or directory was not found |
| `PermissionError` | Not enough permissions |
| `ZeroDivisionError` | Division by zero |
| `RecursionError` | Maximum recursion depth exceeded |
| `UnicodeDecodeError` | Text decoding failed |
| `JSONDecodeError` | Invalid JSON |

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
TermDoctor 0.2.0
```

### Show Python environment

```bash
termdoctor env
```

This shows the current Python version, Python executable, virtual environment status, detected project files, and detected dependencies.

### Run Python project diagnosis

```bash
termdoctor doctor python
```

This checks the current directory and prints Python project warnings and suggestions.

### Run a Python file

```bash
termdoctor run "python main.py"
```

Recommended argument mode:

```bash
termdoctor run -- python main.py
```

Example with a path that contains spaces:

```bash
termdoctor run -- python "examples/path with spaces/name_error.py"
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
| `termdoctor env` | Show Python environment information |
| `termdoctor doctor python` | Run Python project diagnosis |
| `termdoctor run "command"` | Run a command and explain Python errors |
| `termdoctor run -- python main.py` | Run a command in safer argument mode |
| `termdoctor explain last` | Explain the last saved error |
| `termdoctor explain error.txt` | Explain a traceback from a file |
| `termdoctor paste` | Paste a traceback manually |
| `termdoctor history` | Show saved failed command history |
| `termdoctor history --limit 5` | Show a limited number of history items |
| `termdoctor clear` | Clear saved history |

---

## Package hints

Some Python imports are installed under different package names.

TermDoctor can show hints for common cases:

| Import name | Install package |
|---|---|
| `dotenv` | `python-dotenv` |
| `PIL` | `pillow` |
| `cv2` | `opencv-python` |
| `yaml` | `PyYAML` |
| `bs4` | `beautifulsoup4` |
| `sklearn` | `scikit-learn` |
| `jwt` | `PyJWT` |
| `Crypto` | `pycryptodome` |
| `dateutil` | `python-dateutil` |
| `magic` | `python-magic` |
| `slugify` | `python-slugify` |

---

## How it works

TermDoctor does not use AI.

It works with rule-based logic:

1. It runs the command.
2. It captures `stdout`, `stderr`, and exit code.
3. It tries to detect a Python traceback.
4. It extracts the error type and message.
5. It inspects the current Python environment.
6. It reads `requirements.txt` and `pyproject.toml` if they exist.
7. It matches the error with a YAML rule.
8. It prints a clear explanation and possible fixes.

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

Run example commands:

```bash
termdoctor env
termdoctor doctor python
termdoctor run -- python examples/module_not_found.py
termdoctor run -- python examples/name_error.py
termdoctor run -- python examples/key_error.py
termdoctor run -- python examples/json_decode_error.py
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
    - "The virtual environment is not activated."
  fixes:
    - "Check the environment context shown by TermDoctor."
    - "Activate your project virtual environment if one exists."
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
