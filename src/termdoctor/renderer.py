from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from termdoctor.models import CommandResult, ErrorRule, ParsedError


console = Console()


def render_success(command_result: CommandResult) -> None:
    console.print(
        Panel(
            f"Command finished successfully in {command_result.duration_seconds:.2f}s",
            title="TermDoctor",
            border_style="green",
        )
    )

    if command_result.stdout.strip():
        console.print()
        console.print(Panel(command_result.stdout.rstrip(), title="stdout", border_style="green"))


def render_command_output(command_result: CommandResult) -> None:
    if command_result.stdout.strip():
        console.print()
        console.print(Panel(command_result.stdout.rstrip(), title="stdout", border_style="blue"))

    if command_result.stderr.strip():
        console.print()
        console.print(Panel(command_result.stderr.rstrip(), title="stderr", border_style="red"))


def render_diagnosis(
    parsed_error: ParsedError,
    rule: ErrorRule | None,
    command_result: CommandResult | None = None,
) -> None:
    console.print()

    title = f"Python error detected: {parsed_error.error_type}"

    console.print(
        Panel(
            build_error_summary(parsed_error=parsed_error, command_result=command_result),
            title=title,
            border_style="red",
        )
    )

    if rule is None:
        render_unknown_rule(parsed_error)
        return

    console.print()
    console.print(Panel(rule.title, title="What happened", border_style="yellow"))

    explanation = apply_context(rule.explanation, parsed_error)
    console.print(explanation)

    if rule.causes:
        console.print()
        causes_table = Table(title="Most likely causes", show_header=True, header_style="bold")
        causes_table.add_column("#", style="cyan", width=4)
        causes_table.add_column("Cause")

        for index, cause in enumerate(rule.causes, start=1):
            causes_table.add_row(str(index), apply_context(cause, parsed_error))

        console.print(causes_table)

    if rule.fixes:
        console.print()
        fixes_table = Table(title="What to try", show_header=True, header_style="bold")
        fixes_table.add_column("#", style="cyan", width=4)
        fixes_table.add_column("Suggestion")

        for index, fix in enumerate(rule.fixes, start=1):
            fixes_table.add_row(str(index), apply_context(fix, parsed_error))

        console.print(fixes_table)

    if rule.examples:
        console.print()
        examples_text = "\n".join(rule.examples)
        console.print(Panel(examples_text, title="Examples", border_style="green"))


def render_unknown_rule(parsed_error: ParsedError) -> None:
    console.print()
    console.print(
        Panel(
            "TermDoctor detected a Python error, but there is no detailed rule for it yet.\n\n"
            "You can still inspect the traceback above and add a new rule later in:\n"
            "src/termdoctor/rules/python_errors.yml",
            title="No rule found",
            border_style="yellow",
        )
    )


def render_no_python_error_found(text: str) -> None:
    console.print()
    console.print(
        Panel(
            "TermDoctor could not detect a Python traceback or a known Python error line.\n\n"
            "For version 0.1.0, TermDoctor works best with standard Python errors like:\n"
            "ModuleNotFoundError, NameError, TypeError, SyntaxError, KeyError, etc.",
            title="No Python error detected",
            border_style="yellow",
        )
    )

    if text.strip():
        preview = text.strip()

        if len(preview) > 1500:
            preview = preview[:1500] + "\n..."

        console.print()
        console.print(Panel(preview, title="Input preview", border_style="blue"))


def render_history(items: list[dict]) -> None:
    if not items:
        console.print(
            Panel(
                "History is empty.",
                title="TermDoctor history",
                border_style="yellow",
            )
        )
        return

    table = Table(title="TermDoctor history")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Time")
    table.add_column("Error")
    table.add_column("Command")

    for index, item in enumerate(items, start=1):
        error = item.get("error_type") or "Unknown"
        command = item.get("command") or ""
        timestamp = item.get("timestamp") or ""

        table.add_row(str(index), timestamp, error, command)

    console.print(table)


def build_error_summary(
    parsed_error: ParsedError,
    command_result: CommandResult | None = None,
) -> str:
    lines: list[str] = []

    if command_result:
        lines.append(f"Command: {command_result.command}")
        lines.append(f"Exit code: {command_result.exit_code}")
        lines.append(f"Working directory: {command_result.cwd}")

    lines.append(f"Error: {parsed_error.error_type}")

    if parsed_error.message:
        lines.append(f"Message: {parsed_error.message}")

    if parsed_error.file_path:
        location = parsed_error.file_path

        if parsed_error.line_number is not None:
            location += f":{parsed_error.line_number}"

        lines.append(f"Location: {location}")

    return "\n".join(lines)


def apply_context(text: str, parsed_error: ParsedError) -> str:
    context = {
        "error_type": parsed_error.error_type,
        "message": parsed_error.message,
        "file_path": parsed_error.file_path or "unknown file",
        "line_number": str(parsed_error.line_number) if parsed_error.line_number else "unknown line",
        "module": parsed_error.extracted.get("module", "the missing module"),
        "name": parsed_error.extracted.get("name", "the missing name"),
        "key": parsed_error.extracted.get("key", "the missing key"),
        "path": parsed_error.extracted.get("path", "the missing path"),
        "attribute": parsed_error.extracted.get("attribute", "the missing attribute"),
    }

    try:
        return text.format(**context)
    except KeyError:
        return text