from __future__ import annotations

from pathlib import Path
from typing import Any

from termdoctor.core.history import get_history_text, get_last_history_item
from termdoctor.engines.base import EngineDiagnosis
from termdoctor.engines.registry import get_engine_by_language, get_language_detector
from termdoctor.i18n import get_locale, tr
from termdoctor.models import PythonEnvironment
from termdoctor.renderer import apply_context


def load_report_source(source: str) -> tuple[str, dict[str, Any]]:
    if source == "last":
        last_item = get_last_history_item()
        if not last_item:
            raise ValueError(tr("report.no_saved"))
        return get_history_text(last_item), {
            "source": "last",
            "command": last_item.get("command"),
            "cwd": last_item.get("cwd"),
            "exit_code": last_item.get("exit_code"),
            "timestamp": last_item.get("timestamp"),
        }

    path = Path(source)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8"), {
            "source": str(path),
            "command": None,
            "cwd": str(path.resolve().parent),
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


def build_markdown_report(
    source: str,
    include_raw: bool = True,
    engine_name: str | None = None,
    lang: str | None = None,
) -> str:
    selected_engine = engine_name or lang
    text, metadata = load_report_source(source)
    engine = get_engine_by_language(selected_engine) if selected_engine else get_language_detector().detect_for_text(text)
    if engine is None:
        raise ValueError(tr("report.no_engine"))

    cwd = Path(metadata["cwd"]) if metadata.get("cwd") else None
    diagnosis = engine.diagnose(text, cwd=cwd, locale=get_locale())
    if diagnosis is None:
        raise ValueError(tr("report.no_error"))

    environment = diagnosis.environment if diagnosis.language == "python" else None
    return render_markdown_report(diagnosis, environment, text, metadata, include_raw)


def render_markdown_report(
    diagnosis: EngineDiagnosis,
    environment: PythonEnvironment | None,
    raw_traceback: str,
    metadata: dict[str, Any],
    include_raw: bool,
) -> str:
    parsed_error = diagnosis.parsed_error
    rule = diagnosis.rule
    module_context = diagnosis.module_context
    framework_context = diagnosis.framework_context
    lines: list[str] = [f"# {tr('report.title')}", "", f"## {tr('report.summary')}", ""]
    lines.append(f"- **{tr('report.language')}:** `{diagnosis.display_name}`")
    lines.append(f"- **{tr('report.error')}:** `{parsed_error.error_type}`")
    if parsed_error.message:
        lines.append(f"- **{tr('report.message')}:** `{escape_inline_code(parsed_error.message)}`")
    if parsed_error.file_path:
        location = parsed_error.file_path
        if parsed_error.line_number is not None:
            location += f":{parsed_error.line_number}"
        lines.append(f"- **{tr('report.location')}:** `{location}`")
    for metadata_key, translation_key in (
        ("command", "report.command"),
        ("exit_code", "report.exit_code"),
        ("cwd", "report.working_directory"),
        ("timestamp", "report.timestamp"),
    ):
        value = metadata.get(metadata_key)
        if value is not None:
            lines.append(f"- **{tr(translation_key)}:** `{escape_inline_code(str(value))}`")
    lines.append("")

    if len(parsed_error.exception_chain) > 1:
        lines.extend([f"## {tr('report.exception_chain')}", ""])
        for item in parsed_error.exception_chain:
            lines.append(f"- `{item}`")
        lines.append("")

    if parsed_error.source_context:
        lines.extend([f"## {tr('report.source_context')}", "", "```python"])
        lines.extend(parsed_error.source_context)
        lines.extend(["```", ""])

    if framework_context:
        lines.extend([f"## {tr('report.framework_context')}", ""])
        lines.append(f"- **{tr('report.matched_framework')}:** `{framework_context.matched_framework or '-'}`")
        if framework_context.detected_frameworks:
            detected = ", ".join(item.name for item in framework_context.detected_frameworks)
            lines.append(f"- **{tr('report.detected_project')}:** `{detected}`")
        if framework_context.evidence:
            lines.append(f"- **{tr('report.evidence')}:** `{', '.join(framework_context.evidence)}`")
        lines.append("")

    lines.extend([f"## {tr('report.diagnosis')}", ""])
    if rule:
        lines.extend([apply_context(rule.explanation, parsed_error), ""])
        if rule.causes:
            lines.extend([f"## {tr('report.likely_causes')}", ""])
            lines.extend(
                f"{index}. {apply_context(cause, parsed_error)}"
                for index, cause in enumerate(rule.causes, 1)
            )
            lines.append("")
        if rule.fixes:
            lines.extend([f"## {tr('report.fixes')}", ""])
            lines.extend(
                f"{index}. {apply_context(fix, parsed_error)}"
                for index, fix in enumerate(rule.fixes, 1)
            )
            lines.append("")
    else:
        lines.extend([tr("report.unknown_rule"), ""])

    if module_context:
        lines.extend([f"## {tr('report.module_context')}", ""])
        lines.append(f"- **{tr('report.missing_import')}:** `{module_context.module_name}`")
        lines.append(f"- **{tr('report.suggested_package')}:** `{module_context.package_name}`")
        if module_context.package_hint:
            lines.append(
                f"- **{tr('report.package_hint')}:** "
                + tr("report.package_hint_value", module=module_context.module_name, package=module_context.package_hint)
            )
        lines.append(f"- **{tr('report.in_requirements')}:** {tr('common.yes') if module_context.in_requirements else tr('common.no')}")
        lines.append(f"- **{tr('report.in_pyproject')}:** {tr('common.yes') if module_context.in_pyproject else tr('common.no')}")
        if module_context.activation_command:
            lines.append(f"- **{tr('report.activation')}:** `{module_context.activation_command}`")
        lines.append("")

    if environment:
        lines.extend([f"## {tr('report.environment')}", ""])
        environment_rows = (
            ("report.python_version", environment.python_version),
            ("report.python_executable", environment.python_executable),
            ("report.current_directory", environment.current_dir),
            ("report.project_root", environment.project_root),
            ("report.virtual_environment", tr("common.active") if environment.venv_active else tr("common.not_active")),
            ("report.active_venv", environment.active_venv_path or "-"),
            ("report.project_venv", environment.project_venv_path or "-"),
            ("report.requirements", ", ".join(environment.dependency_info.dependency_files) or "-"),
            ("report.pyproject", environment.pyproject_file or "-"),
        )
        for key, value in environment_rows:
            lines.append(f"- **{tr(key)}:** `{escape_inline_code(value)}`")
        lines.append("")
        dependencies = environment.dependency_info.all_dependencies
        if dependencies:
            lines.extend([f"## {tr('report.dependencies')}", ""])
            lines.extend(f"- `{dependency}`" for dependency in dependencies)
            lines.append("")

    if include_raw:
        lines.extend([f"## {tr('report.raw_traceback')}", "", "```text", raw_traceback.strip(), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def escape_inline_code(value: str) -> str:
    return value.replace("`", "\\`")


def write_report(markdown: str, output_path: str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path
