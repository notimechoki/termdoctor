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
  <img src="https://img.shields.io/badge/Version-0.1.1-blue?style=for-the-badge" alt="Version 0.1.1">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## What is TermDoctor?

**TermDoctor** is a command-line tool that helps developers understand Python terminal errors.

Instead of showing only a raw traceback, TermDoctor detects the error type, explains what happened in simple English, and suggests practical next steps.

TermDoctor is useful for:

- beginners learning Python;
- students who do not understand terminal errors yet;
- developers who want faster debugging hints;
- teachers and mentors who want clearer error explanations;
- anyone who wants a small local tool for Python traceback diagnosis.

---

## Current version

```text
0.1.1
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

TermDoctor can explain standard Python tracebacks produced by:

| Source | Support status |
|---|---|
| Python scripts | Supported |
| Python modules | Supported |
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
- Store diagnosis rules in a readable YAML file

---

## Tech stack

| Part | Technology |
|---|---|
| Language | Python 3.10+ |
| CLI framework | Typer |
| Terminal UI | Rich |
| Rules format | YAML |
| Rules parser | PyYAML |
| Testing | pytest |
| Packaging | pyproject.toml |
| Recommended installation | pipx |

---

## Installation

### Install directly from GitHub with pipx

This is the recommended way to install TermDoctor globally.

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

After that, restart your terminal and run the install command again.

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

Use this if you want to work on the project and run tests.

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

---

### Show version

```bash
termdoctor --version
```

Expected output:

```text
TermDoctor 0.1.1
```

---

### Run a Python file

```bash
termdoctor run "python main.py"
```

Example:

```bash
termdoctor run "python examples/module_not_found.py"
```

Recommended argument mode:

```bash
termdoctor run -- python examples/module_not_found.py
```

Example with a path that contains spaces:

```bash
termdoctor run -- python "examples/path with spaces/name_error.py"
```

---

### Run a Python module

```bash
termdoctor run "python -m my_module"
```

Recommended argument mode:

```bash
termdoctor run -- python -m my_module
```

---

### Run a Django command

```bash
termdoctor run "python manage.py migrate"
```

Recommended argument mode:

```bash
termdoctor run -- python manage.py migrate
```

TermDoctor does not deeply analyze Django internals, but it can explain normal Python tracebacks produced by Django commands.

---

### Run a FastAPI / Uvicorn command

```bash
termdoctor run "uvicorn app.main:app --reload"
```

Recommended argument mode:

```bash
termdoctor run -- uvicorn app.main:app --reload
```

This works best when the command exits and prints a Python traceback.

---

### Explain the last saved error

```bash
termdoctor explain last
```

This uses the last failed command saved by TermDoctor.

---

### Explain an error from a file

```bash
termdoctor explain error.txt
```

Example `error.txt`:

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import requests_fake
ModuleNotFoundError: No module named 'requests_fake'
```

---

### Paste a traceback manually

```bash
termdoctor paste
```

Then paste your traceback.

Finish input with:

- Linux/macOS: `Ctrl+D`
- Windows: `Ctrl+Z`, then `Enter`

---

### Show history

```bash
termdoctor history
```

Show only the last 5 saved errors:

```bash
termdoctor history --limit 5
```

---

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
| `termdoctor explain last` | Explain the last saved error |
| `termdoctor explain error.txt` | Explain a traceback from a file |
| `termdoctor paste` | Paste a traceback manually |
| `termdoctor history` | Show saved failed command history |
| `termdoctor history --limit 5` | Show a limited number of history items |
| `termdoctor clear` | Clear saved history |

---

## Examples

### ModuleNotFoundError

Command:

```bash
termdoctor run -- python examples/module_not_found.py
```

Possible output:

```text
Python error detected: ModuleNotFoundError

What happened:
Python tried to import `some_missing_package_for_demo`, but it is not available in the current environment.

Most likely causes:
1. The package is not installed.
2. The virtual environment is not activated.
3. You are using a different Python interpreter.

What to try:
1. Activate your virtual environment.
2. Install the missing package: pip install some_missing_package_for_demo
3. Check requirements.txt or pyproject.toml.
```

---

### KeyError

Command:

```bash
termdoctor run -- python examples/key_error.py
```

Possible output:

```text
Python error detected: KeyError

What happened:
Python tried to read key `name` from a dictionary, but that key does not exist.

Most likely causes:
1. The key name is misspelled.
2. The dictionary has a different structure than expected.
3. The key is optional and may be missing.

What to try:
1. Check the dictionary content before accessing `name`.
2. Use dict.get('name') if the key may be optional.
3. Check API response or JSON structure.
```

---

### NameError

Command:

```bash
termdoctor run -- python examples/name_error.py
```

Possible output:

```text
Python error detected: NameError

What happened:
Python found a variable, function, or class name that was not defined.

Most likely causes:
1. There is a typo in the name.
2. The variable is used before assignment.
3. The function or class was not imported.

What to try:
1. Check the spelling.
2. Make sure the name is created before this line.
3. Check imports.
```

---

## How it works

TermDoctor does not use AI.

It works with rule-based logic:

1. It runs the command.
2. It captures `stdout`, `stderr`, and exit code.
3. It tries to detect a Python traceback.
4. It extracts the error type and message.
5. It matches the error with a YAML rule.
6. It prints a clear explanation and possible fixes.

Rules are stored here:

```text
src/termdoctor/rules/python_errors.yml
```

This makes TermDoctor simple, predictable, and easy to extend.

---

## Project structure

```text
termdoctor/
├── src/
│   └── termdoctor/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── history.py
│       ├── matcher.py
│       ├── models.py
│       ├── parser.py
│       ├── renderer.py
│       ├── rules_loader.py
│       ├── runner.py
│       └── rules/
│           └── python_errors.yml
├── examples/
│   ├── attribute_error.py
│   ├── file_not_found.py
│   ├── index_error.py
│   ├── json_decode_error.py
│   ├── key_error.py
│   ├── module_not_found.py
│   ├── name_error.py
│   ├── path with spaces/
│   │   └── name_error.py
│   ├── recursion_error.py
│   ├── syntax_error.py
│   ├── type_error.py
│   ├── value_error.py
│   └── zero_division_error.py
├── tests/
│   ├── test_cli.py
│   ├── test_history.py
│   ├── test_matcher.py
│   └── test_parser.py
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
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
termdoctor run -- python examples/key_error.py
termdoctor run -- python examples/type_error.py
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
    - "The package is not installed."
    - "The virtual environment is not activated."
    - "You are using a different Python interpreter."
  fixes:
    - "Activate your virtual environment."
    - "Install the missing package: pip install {module}"
    - "Check requirements.txt or pyproject.toml."
```

---

## Changelog

See full release notes in [CHANGELOG.md](CHANGELOG.md).

---

## Philosophy

TermDoctor should be:

- simple;
- local-first;
- beginner-friendly;
- predictable;
- easy to extend;
- useful without AI;
- helpful for real debugging.

The goal is not to hide the traceback.

The goal is to explain it.

---

## License

MIT License.

---

## Author

Created by [notimechoki](https://github.com/notimechoki).
