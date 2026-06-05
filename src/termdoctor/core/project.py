from pathlib import Path


PROJECT_ROOT_MARKERS = {
    "pyproject.toml",
    "requirements.txt",
    ".git",
    "setup.py",
    "setup.cfg",
    "manage.py",
}


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()

    if current.is_file():
        current = current.parent

    for directory in [current, *current.parents]:
        if has_project_marker(directory):
            return directory

    return current


def has_project_marker(directory: Path) -> bool:
    for marker in PROJECT_ROOT_MARKERS:
        if (directory / marker).exists():
            return True

    return False