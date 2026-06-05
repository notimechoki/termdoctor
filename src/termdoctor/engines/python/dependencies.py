import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from termdoctor.models import DependencyInfo


REQUIREMENT_SPLIT_PATTERN = re.compile(r"[<>=!~;\[]")
INCLUDE_PREFIXES = ("-r", "--requirement")


def normalize_package_name(name: str) -> str:
    return name.strip().replace("_", "-").lower()


def parse_requirement_name(line: str) -> str | None:
    cleaned = clean_requirement_line(line)

    if not cleaned:
        return None

    if cleaned.startswith("-"):
        return None

    if cleaned.startswith(("git+", "http://", "https://")):
        return None

    name = REQUIREMENT_SPLIT_PATTERN.split(cleaned, maxsplit=1)[0].strip()

    if not name:
        return None

    return normalize_package_name(name)


def clean_requirement_line(line: str) -> str:
    cleaned = line.strip()

    if not cleaned:
        return ""

    if cleaned.startswith("#"):
        return ""

    if " #" in cleaned:
        cleaned = cleaned.split(" #", 1)[0].strip()

    return cleaned


def parse_include_path(line: str) -> str | None:
    cleaned = clean_requirement_line(line)

    if not cleaned:
        return None

    parts = cleaned.split(maxsplit=1)

    if len(parts) == 2 and parts[0] in INCLUDE_PREFIXES:
        return parts[1].strip()

    for prefix in INCLUDE_PREFIXES:
        prefix_with_equals = f"{prefix}="

        if cleaned.startswith(prefix_with_equals):
            return cleaned[len(prefix_with_equals):].strip()

    return None


def parse_requirements_txt(path: Path, visited: set[Path] | None = None) -> list[str]:
    if visited is None:
        visited = set()

    resolved_path = path.resolve()

    if resolved_path in visited:
        return []

    visited.add(resolved_path)

    if not path.exists() or not path.is_file():
        return []

    dependencies: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        include_path = parse_include_path(line)

        if include_path:
            nested_path = (path.parent / include_path).resolve()
            dependencies.extend(parse_requirements_txt(nested_path, visited))
            continue

        package_name = parse_requirement_name(line)

        if package_name:
            dependencies.append(package_name)

    return unique_sorted(dependencies)


def parse_pyproject_dependencies(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return []

    project = data.get("project", {})
    raw_dependencies = project.get("dependencies", [])

    dependencies: list[str] = []

    if isinstance(raw_dependencies, list):
        for item in raw_dependencies:
            if not isinstance(item, str):
                continue

            package_name = parse_requirement_name(item)

            if package_name:
                dependencies.append(package_name)

    return unique_sorted(dependencies)


def collect_dependency_info(cwd: Path | None = None) -> DependencyInfo:
    root = cwd or Path.cwd()

    requirements_path = root / "requirements.txt"
    pyproject_path = root / "pyproject.toml"

    requirements_file = str(requirements_path) if requirements_path.exists() else None
    pyproject_file = str(pyproject_path) if pyproject_path.exists() else None

    return DependencyInfo(
        requirements_file=requirements_file,
        pyproject_file=pyproject_file,
        requirements_dependencies=parse_requirements_txt(requirements_path),
        pyproject_dependencies=parse_pyproject_dependencies(pyproject_path),
    )


def dependency_exists(package_name: str, dependencies: list[str]) -> bool:
    normalized_package = normalize_package_name(package_name)

    for dependency in dependencies:
        if normalize_package_name(dependency) == normalized_package:
            return True

    return False


def unique_sorted(items: list[str]) -> list[str]:
    return sorted(set(items))