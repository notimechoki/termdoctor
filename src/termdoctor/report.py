from pathlib import Path
from typing import Any

from termdoctor.environment import build_module_diagnosis_context, get_python_environment
from termdoctor.history import get_last_history_item
from termdoctor.matcher import find_rule
from termdoctor.models import ErrorRule, ModuleDiagnosisContext, ParsedError, PythonEnvironment
from termdoctor.parser import parse_python_error
from termdoctor.renderer import apply_context


def load_report_source(source: str) -> tuple[str, dict[str, Any]]:
    if source == "last":
        last_item = get_last_history_item()

        if not last_item:
            raise ValueError("No saved errors found. Run a failing command first.")

        text = last_item.get("stderr") or last_item.get("stdout") or ""

        metadata = {
            "source": "last",
            "command": last_item.get("command"),
            "cwd": last_item.get("cwd"),
            "exit_code": last_item.get("exit_code"),
            "timestamp": last_item.get("timestamp"),
        }

        return text, metadata

    path = Path(source)

    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8"), {
            "source": str(path),
            "command": None,
            "cwd": None,
            "exit_code": None,
            "timestamp": None,
        }

    return source, {
        "source": "raw",
        "command": None,
        "cwd": None,
        "exit_code": None,
        "timestamp": None,
    }


def build_markdown_report(source: str, include_raw: bool = True) -> str:
    text, metadata = load_report_source(source)
    parsed_error = parse_python_error(text)

    if parsed_error is None:
        raise ValueError("No Python error could be detected in the provided source.")

    rule = find_rule(parsed_error)

    module_context = None

    if parsed_error.error_type == "ModuleNotFoundError":
        module_name = parsed_error.extracted.get("module")

        if module_name:
            module_context = build_module_diagnosis_context(module_name)

    environment = get_python_environment()

    return render_markdown_report(
        parsed_error=parsed_error,
        rule=rule,
        environment=environment,
        module_context=module_context,
        raw_traceback=text,
        metadata=metadata,
        include_raw=include_raw,
    )


def render_markdown_report(
    parsed_error: ParsedError,
    rule: ErrorRule | None,
    environment: PythonEnvironment,
    module_context: ModuleDiagnosisContext | None,
    raw_traceback: str,
    metadata: dict[str, Any],
    include_raw: bool,
) -> str:
    lines: list[str] = []

    lines.append("# TermDoctor Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Error:** `{parsed_error.error_type}`")

    if parsed_error.message:
        lines.append(f"- **Message:** `{parsed_error.message}`")

    if parsed_error.file_path:
        location = parsed_error.file_path

        if parsed_error.line_number is not None:
            location += f":{parsed_error.line_number}"

        lines.append(f"- **Location:** `{location}`")

    if metadata.get("command"):
        lines.append(f"- **Command:** `{metadata['command']}`")

    if metadata.get("exit_code") is not None:
        lines.append(f"- **Exit code:** `{metadata['exit_code']}`")

    if metadata.get("cwd"):
        lines.append(f"- **Working directory:** `{metadata['cwd']}`")

    if metadata.get("timestamp"):
        lines.append(f"- **Timestamp:** `{metadata['timestamp']}`")

    lines.append("")

    if rule:
        lines.append("## Diagnosis")
        lines.append("")
        lines.append(apply_context(rule.explanation, parsed_error))
        lines.append("")

        if rule.causes:
            lines.append("## Most likely causes")
            lines.append("")

            for index, cause in enumerate(rule.causes, start=1):
                lines.append(f"{index}. {apply_context(cause, parsed_error)}")

            lines.append("")

        if rule.fixes:
            lines.append("## Suggested fixes")
            lines.append("")

            for index, fix in enumerate(rule.fixes, start=1):
                lines.append(f"{index}. {apply_context(fix, parsed_error)}")

            lines.append("")

    else:
        lines.append("## Diagnosis")
        lines.append("")
        lines.append("TermDoctor detected a Python error, but no detailed rule exists for this error yet.")
        lines.append("")

    if module_context:
        lines.append("## Module context")
        lines.append("")
        lines.append(f"- **Missing import:** `{module_context.module_name}`")
        lines.append(f"- **Suggested package:** `{module_context.package_name}`")

        if module_context.package_hint:
            lines.append(
                f"- **Package hint:** import `{module_context.module_name}` is usually installed as `{module_context.package_hint}`"
            )

        lines.append(f"- **Package in requirements.txt:** {'yes' if module_context.in_requirements else 'no'}")
        lines.append(f"- **Package in pyproject.toml:** {'yes' if module_context.in_pyproject else 'no'}")

        if module_context.activation_command:
            lines.append(f"- **Activation command:** `{module_context.activation_command}`")

        lines.append("")

    lines.append("## Environment")
    lines.append("")
    lines.append(f"- **Python version:** `{environment.python_version}`")
    lines.append(f"- **Python executable:** `{environment.python_executable}`")
    lines.append(f"- **Current directory:** `{environment.current_dir}`")
    lines.append(f"- **Project root:** `{environment.project_root}`")
    lines.append(f"- **Virtual environment:** `{'active' if environment.venv_active else 'not active'}`")
    lines.append(f"- **Active venv path:** `{environment.active_venv_path or '-'}`")
    lines.append(f"- **Project venv path:** `{environment.project_venv_path or '-'}`")
    lines.append(f"- **requirements.txt:** `{environment.requirements_file or '-'}`")
    lines.append(f"- **pyproject.toml:** `{environment.pyproject_file or '-'}`")
    lines.append("")

    dependencies = environment.dependency_info.all_dependencies

    if dependencies:
        lines.append("## Detected dependencies")
        lines.append("")

        for dependency in dependencies:
            lines.append(f"- `{dependency}`")

        lines.append("")

    if include_raw:
        lines.append("## Raw traceback")
        lines.append("")
        lines.append("```text")
        lines.append(raw_traceback.strip())
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_report(markdown: str, output_path: str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")

    return path