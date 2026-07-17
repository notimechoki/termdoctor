from dataclasses import dataclass, field
from typing import Any, Literal


DoctorStatus = Literal["ok", "warn", "info"]


@dataclass
class CommandResult:
    command: str
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def diagnostic_text(self) -> str:
        parts = [part.rstrip() for part in (self.stdout, self.stderr) if part.strip()]
        return "\n".join(parts)


@dataclass
class TracebackFrame:
    file_path: str
    line_number: int
    function_name: str | None = None
    code_line: str | None = None


@dataclass
class ParsedError:
    error_type: str
    message: str
    raw_text: str
    language: str = "python"
    file_path: str | None = None
    line_number: int | None = None
    full_error_type: str | None = None
    frames: list[TracebackFrame] = field(default_factory=list)
    exception_chain: list[str] = field(default_factory=list)
    source_context: list[str] = field(default_factory=list)
    extracted: dict[str, str] = field(default_factory=dict)


@dataclass
class ErrorRule:
    id: str
    error: str
    title: str
    explanation: str
    causes: list[str]
    fixes: list[str]
    match_any: list[str] = field(default_factory=list)
    match_all: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    full_error_types: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    priority: int = 0

    @property
    def match(self) -> list[str]:
        return self.match_any

    @property
    def is_fallback(self) -> bool:
        return not any(
            (
                self.match_any,
                self.match_all,
                self.exclude,
                self.full_error_types,
                self.frameworks,
            )
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ErrorRule":
        match_any = data.get("match_any", data.get("match", []))
        return cls(
            id=str(data.get("id", "")),
            error=str(data.get("error", "")),
            title=str(data.get("title", "")),
            explanation=str(data.get("explanation", "")),
            causes=list(data.get("causes", [])),
            fixes=list(data.get("fixes", [])),
            match_any=list(match_any or []),
            match_all=list(data.get("match_all", []) or []),
            exclude=list(data.get("exclude", []) or []),
            full_error_types=list(data.get("full_error_types", []) or []),
            frameworks=list(data.get("frameworks", []) or []),
            examples=list(data.get("examples", []) or []),
            priority=int(data.get("priority", 0)),
        )


@dataclass
class DependencyInfo:
    requirements_file: str | None
    pyproject_file: str | None
    requirements_dependencies: list[str] = field(default_factory=list)
    pyproject_dependencies: list[str] = field(default_factory=list)
    dependency_files: list[str] = field(default_factory=list)
    source_dependencies: dict[str, list[str]] = field(default_factory=dict)

    @property
    def all_dependencies(self) -> list[str]:
        seen: set[str] = set()
        dependencies: list[str] = []

        sources = self.source_dependencies.values() or [
            self.requirements_dependencies,
            self.pyproject_dependencies,
        ]
        for source_dependencies in sources:
            for dependency in source_dependencies:
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
        return any(
            framework.name.lower() == normalized and framework.detected
            for framework in self.frameworks
        )


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
    top_level_module: str
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
    is_standard_library: bool = False
    local_module_path: str | None = None

    @property
    def should_suggest_install(self) -> bool:
        return not self.is_standard_library and self.local_module_path is None


@dataclass
class FrameworkDiagnosisContext:
    detected_frameworks: list[FrameworkInfo]
    matched_framework: str | None
    evidence: list[str] = field(default_factory=list)


@dataclass
class DiagnosticField:
    label_key: str
    value: str


@dataclass
class DiagnosticMessage:
    key: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticSection:
    title_key: str
    fields: list[DiagnosticField] = field(default_factory=list)
    suggestions: list[DiagnosticMessage] = field(default_factory=list)


@dataclass
class DoctorCheck:
    label_key: str
    status: DoctorStatus
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class PythonDoctorResult:
    environment: PythonEnvironment
    checks: list[DoctorCheck]
    warnings: list[DiagnosticMessage]
    suggestions: list[DiagnosticMessage]
