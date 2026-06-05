from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from termdoctor.models import CommandResult, ErrorRule, ParsedError


@dataclass
class EngineDiagnosis:
    language: str
    display_name: str
    parsed_error: ParsedError
    rule: ErrorRule | None
    command_result: CommandResult | None = None
    module_context: Any | None = None
    framework_context: Any | None = None


class BaseEngine(ABC):
    language: str = "unknown"
    display_name: str = "Unknown"

    @abstractmethod
    def can_handle_command(self, command: str | list[str]) -> bool:
        pass

    @abstractmethod
    def can_handle_text(self, text: str) -> bool:
        pass

    @abstractmethod
    def parse_error(self, text: str) -> ParsedError | None:
        pass

    @abstractmethod
    def find_rule(self, parsed_error: ParsedError) -> ErrorRule | None:
        pass

    @abstractmethod
    def diagnose(
        self,
        text: str,
        command_result: CommandResult | None = None,
    ) -> EngineDiagnosis | None:
        pass