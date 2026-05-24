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