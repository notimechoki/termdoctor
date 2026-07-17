from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from termdoctor.models import DependencyInfo


REQUIREMENT_SPLIT_PATTERN = re.compile(r"[<>=!~;@\[]")
INCLUDE_PREFIXES = ("-r", "--requirement", "-c", "--constraint")
EDITABLE_PREFIXES = ("-e", "--editable")


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip()).lower()


def parse_requirement_name(line: str) -> str | None:
    cleaned = clean_requirement_line(line)
    if not cleaned:
        return None

    editable_target = parse_option_value(cleaned, EDITABLE_PREFIXES)
    if editable_target is not None:
        return parse_vcs_or_path_name(editable_target)

    if cleaned.startswith("-"):
        return None

    if cleaned.startswith(("git+", "hg+", "svn+", "bzr+", "http://", "https://")):
        return parse_vcs_or_path_name(cleaned)

    name = REQUIREMENT_SPLIT_PATTERN.split(cleaned, maxsplit=1)[0].strip()
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        return None
    return normalize_package_name(name)


def parse_vcs_or_path_name(value: str) -> str | None:
    egg_match = re.search(r"[#&]egg=(?P<name>[A-Za-z0-9_.-]+)", value)
    if egg_match:
        return normalize_package_name(egg_match.group("name"))
    direct_match = re.match(r"(?P<name>[A-Za-z0-9_.-]+)\s*@\s*", value)
    if direct_match:
        return normalize_package_name(direct_match.group("name"))
    return None


def clean_requirement_line(line: str) -> str:
    cleaned = line.strip()
    if not cleaned or cleaned.startswith("#"):
        return ""
    if " #" in cleaned:
        cleaned = cleaned.split(" #", 1)[0].strip()
    return cleaned


def parse_option_value(cleaned: str, prefixes: tuple[str, ...]) -> str | None:
    parts = cleaned.split(maxsplit=1)
    if len(parts) == 2 and parts[0] in prefixes:
        return parts[1].strip()
    for prefix in prefixes:
        marker = f"{prefix}="
        if cleaned.startswith(marker):
            return cleaned[len(marker):].strip()
    return None


def parse_include_path(line: str) -> str | None:
    cleaned = clean_requirement_line(line)
    if not cleaned:
        return None
    return parse_option_value(cleaned, INCLUDE_PREFIXES)


def parse_requirements_txt(path: Path, visited: set[Path] | None = None) -> list[str]:
    if visited is None:
        visited = set()
    try:
        resolved_path = path.resolve()
    except OSError:
        return []
    if resolved_path in visited:
        return []
    visited.add(resolved_path)
    if not path.exists() or not path.is_file():
        return []

    dependencies: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    for line in lines:
        include_path = parse_include_path(line)
        if include_path:
            dependencies.extend(parse_requirements_txt((path.parent / include_path).resolve(), visited))
            continue
        package_name = parse_requirement_name(line)
        if package_name:
            dependencies.append(package_name)
    return unique_sorted(dependencies)


def _append_requirement_items(items: Any, output: list[str]) -> None:
    if not isinstance(items, list):
        return
    for item in items:
        if isinstance(item, str):
            package_name = parse_requirement_name(item)
            if package_name:
                output.append(package_name)


def _append_mapping_keys(mapping: Any, output: list[str], ignored: set[str] | None = None) -> None:
    if not isinstance(mapping, dict):
        return
    ignored = ignored or set()
    for name in mapping:
        if not isinstance(name, str) or name.lower() in ignored:
            continue
        output.append(normalize_package_name(name))


def parse_pyproject_dependencies(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return []

    dependencies: list[str] = []
    project = data.get("project", {})
    if isinstance(project, dict):
        _append_requirement_items(project.get("dependencies"), dependencies)
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for items in optional.values():
                _append_requirement_items(items, dependencies)

    dependency_groups = data.get("dependency-groups", {})
    if isinstance(dependency_groups, dict):
        for items in dependency_groups.values():
            _append_requirement_items(items, dependencies)

    tool = data.get("tool", {})
    if isinstance(tool, dict):
        poetry = tool.get("poetry", {})
        if isinstance(poetry, dict):
            _append_mapping_keys(poetry.get("dependencies"), dependencies, {"python"})
            _append_mapping_keys(poetry.get("dev-dependencies"), dependencies, {"python"})
            groups = poetry.get("group", {})
            if isinstance(groups, dict):
                for group in groups.values():
                    if isinstance(group, dict):
                        _append_mapping_keys(group.get("dependencies"), dependencies, {"python"})
    return unique_sorted(dependencies)


def parse_pipfile_dependencies(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return []
    dependencies: list[str] = []
    _append_mapping_keys(data.get("packages"), dependencies)
    _append_mapping_keys(data.get("dev-packages"), dependencies)
    return unique_sorted(dependencies)


def collect_dependency_info(cwd: Path | None = None) -> DependencyInfo:
    root = (cwd or Path.cwd()).resolve()
    source_dependencies: dict[str, list[str]] = {}

    requirement_paths = sorted(
        path for path in root.glob("requirements*.txt") if path.is_file()
    )
    for path in requirement_paths:
        source_dependencies[str(path)] = parse_requirements_txt(path)

    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file():
        source_dependencies[str(pyproject_path)] = parse_pyproject_dependencies(pyproject_path)

    pipfile_path = root / "Pipfile"
    if pipfile_path.is_file():
        source_dependencies[str(pipfile_path)] = parse_pipfile_dependencies(pipfile_path)

    requirements_path = root / "requirements.txt"
    requirements_file = str(requirements_path) if requirements_path.is_file() else None
    pyproject_file = str(pyproject_path) if pyproject_path.is_file() else None

    requirements_dependencies = unique_sorted(
        dependency
        for path, dependencies in source_dependencies.items()
        if Path(path).name.startswith("requirements")
        for dependency in dependencies
    )
    project_dependencies = unique_sorted(
        dependency
        for path, dependencies in source_dependencies.items()
        if Path(path).name in {"pyproject.toml", "Pipfile"}
        for dependency in dependencies
    )

    return DependencyInfo(
        requirements_file=requirements_file,
        pyproject_file=pyproject_file,
        requirements_dependencies=requirements_dependencies,
        pyproject_dependencies=project_dependencies,
        dependency_files=list(source_dependencies),
        source_dependencies=source_dependencies,
    )


def dependency_exists(package_name: str, dependencies: list[str]) -> bool:
    normalized_package = normalize_package_name(package_name)
    return any(normalize_package_name(dependency) == normalized_package for dependency in dependencies)


def unique_sorted(items) -> list[str]:
    return sorted(set(items))
