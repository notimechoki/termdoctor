from importlib import resources
import shlex

import yaml

from termdoctor.engines.base import BaseEngine, EngineDiagnosis
from termdoctor.engines.python.environment import build_module_diagnosis_context, get_python_environment
from termdoctor.engines.python.frameworks import build_framework_diagnosis_context
from termdoctor.engines.python.parser import parse_python_error
from termdoctor.models import CommandResult, ErrorRule, ParsedError


class PythonEngine(BaseEngine):
    language = "python"
    display_name = "Python"

    command_markers = {
        "python",
        "python3",
        "py",
        "pytest",
        "django-admin",
        "uvicorn",
        "gunicorn",
        "flask",
        "alembic",
    }

    text_markers = (
        "Traceback (most recent call last):",
        "ModuleNotFoundError",
        "NameError",
        "TypeError",
        "ValueError",
        "SyntaxError",
        "IndentationError",
        "AttributeError",
        "KeyError",
        "IndexError",
        "FileNotFoundError",
        "django.",
        "fastapi.",
        "pydantic.",
        "sqlalchemy.",
        "alembic.",
        "aiogram.",
        "telebot.",
        "_pytest.",
    )

    def can_handle_command(self, command: str | list[str]) -> bool:
        parts = command_to_parts(command)

        if not parts:
            return False

        executable = parts[0].split("/")[-1].lower()

        if executable in self.command_markers:
            return True

        if len(parts) >= 2 and parts[0].lower() in {"uv", "poetry", "pipenv"}:
            return parts[1].lower() in {"run"} and any(
                part.split("/")[-1].lower() in self.command_markers for part in parts[2:]
            )

        return False

    def can_handle_text(self, text: str) -> bool:
        return any(marker in text for marker in self.text_markers)

    def parse_error(self, text: str) -> ParsedError | None:
        parsed_error = parse_python_error(text)

        if parsed_error:
            parsed_error.language = self.language

        return parsed_error

    def load_rules(self) -> list[ErrorRule]:
        rules_file = resources.files("termdoctor").joinpath("engines/python/rules.yml")

        with rules_file.open("r", encoding="utf-8") as file:
            raw_rules = yaml.safe_load(file) or []

        rules: list[ErrorRule] = []

        for raw_rule in raw_rules:
            rules.append(ErrorRule.from_dict(raw_rule))

        return rules

    def find_rule(self, parsed_error: ParsedError) -> ErrorRule | None:
        rules = self.load_rules()
        exact_error_rules: list[ErrorRule] = []

        for rule in rules:
            if rule.error == parsed_error.error_type:
                exact_error_rules.append(rule)

        if not exact_error_rules:
            return None

        searchable_text = build_searchable_text(parsed_error)

        for rule in exact_error_rules:
            if not rule.match:
                continue

            for phrase in rule.match:
                if phrase.lower() in searchable_text:
                    return rule

        for rule in exact_error_rules:
            if not rule.match:
                return rule

        return exact_error_rules[0]

    def diagnose(
        self,
        text: str,
        command_result: CommandResult | None = None,
    ) -> EngineDiagnosis | None:
        parsed_error = self.parse_error(text)

        if parsed_error is None:
            return None

        rule = self.find_rule(parsed_error)
        environment = get_python_environment()

        module_context = None

        if parsed_error.error_type == "ModuleNotFoundError":
            module_name = parsed_error.extracted.get("module")

            if module_name:
                module_context = build_module_diagnosis_context(module_name)

        framework_context = build_framework_diagnosis_context(parsed_error, environment.framework_info)

        return EngineDiagnosis(
            language=self.language,
            display_name=self.display_name,
            parsed_error=parsed_error,
            rule=rule,
            command_result=command_result,
            module_context=module_context,
            framework_context=framework_context,
        )


def command_to_parts(command: str | list[str]) -> list[str]:
    if isinstance(command, list):
        return command

    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def build_searchable_text(parsed_error: ParsedError) -> str:
    parts = [
        parsed_error.error_type,
        parsed_error.message,
        parsed_error.raw_text,
    ]

    full_error_type = parsed_error.extracted.get("full_error_type")

    if full_error_type:
        parts.append(full_error_type)

    return "\n".join(parts).lower()