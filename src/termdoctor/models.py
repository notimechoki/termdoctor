from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandResult:
    command: str
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


@dataclass
class ParsedError:
    error_type: str
    message: str
    raw_text: str
    file_path: str | None = None
    line_number: int | None = None
    extracted: dict[str, str] = field(default_factory=dict)


@dataclass
class ErrorRule:
    id: str
    error: str
    title: str
    explanation: str
    causes: list[str]
    fixes: list[str]
    match: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ErrorRule":
        return cls(
            id=str(data.get("id", "")),
            error=str(data.get("error", "")),
            title=str(data.get("title", "")),
            explanation=str(data.get("explanation", "")),
            causes=list(data.get("causes", [])),
            fixes=list(data.get("fixes", [])),
            match=list(data.get("match", [])),
            examples=list(data.get("examples", [])),
        )


@dataclass
class DependencyInfo:
    requirements_file: str | None
    pyproject_file: str | None
    requirements_dependencies: list[str] = field(default_factory=list)
    pyproject_dependencies: list[str] = field(default_factory=list)

    @property
    def all_dependencies(self) -> list[str]:
        seen: set[str] = set()
        dependencies: list[str] = []

        for dependency in [*self.requirements_dependencies, *self.pyproject_dependencies]:
            normalized = dependency.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            dependencies.append(dependency)

        return dependencies


@dataclass
class FrameworkInfo:
    name: str
    detected: bool
    evidence: list[str] = field(default_factory=list)


@dataclass
class FrameworkDetectionResult:
    frameworks: list[FrameworkInfo] = field(default_factory=list)

    @property
    def detected_frameworks(self) -> list[FrameworkInfo]:
        return [framework for framework in self.frameworks if framework.detected]

    def is_detected(self, name: str) -> bool:
        normalized = name.lower()

        for framework in self.frameworks:
            if framework.name.lower() == normalized and framework.detected:
                return True

        return False


@dataclass
class PythonEnvironment:
    python_version: str
    python_executable: str
    current_dir: str
    project_root: str
    cwd: str
    venv_active: bool
    active_venv_path: str | None
    project_venv_path: str | None
    activation_command: str | None
    requirements_file: str | None
    pyproject_file: str | None
    env_file: str | None
    env_example_file: str | None
    tests_dir: str | None
    dependency_info: DependencyInfo
    framework_info: FrameworkDetectionResult


@dataclass
class ModuleDiagnosisContext:
    module_name: str
    package_name: str
    package_hint: str | None
    in_requirements: bool
    in_pyproject: bool
    has_requirements_file: bool
    has_pyproject_file: bool
    venv_active: bool
    active_venv_path: str | None
    project_venv_path: str | None
    activation_command: str | None
    python_executable: str
    current_dir: str
    project_root: str


@dataclass
class FrameworkDiagnosisContext:
    detected_frameworks: list[FrameworkInfo]
    matched_framework: str | None
    evidence: list[str] = field(default_factory=list)


@dataclass
class PythonDoctorResult:
    environment: PythonEnvironment
    checks: list[tuple[str, bool]]
    warnings: list[str]
    suggestions: list[str]