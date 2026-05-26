from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from termdoctor.history import format_history_time, trim_text
from termdoctor.models import (
    CommandResult,
    ErrorRule,
    ModuleDiagnosisContext,
    ParsedError,
    PythonDoctorResult,
    PythonEnvironment,
)


console = Console()


def render_success(command_result: CommandResult) -> None:
    console.print(
        Panel(
            f"[bold green]Command completed successfully[/bold green]\n"
            f"Duration: {command_result.duration_seconds:.2f}s",
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
    module_context: ModuleDiagnosisContext | None = None,
) -> None:
    console.print()

    console.print(
        Panel(
            build_error_summary(parsed_error=parsed_error, command_result=command_result),
            title=f"[bold red]Python error detected: {parsed_error.error_type}[/bold red]",
            border_style="red",
        )
    )

    if module_context:
        render_module_context(module_context)

    if rule is None:
        render_unknown_rule(parsed_error)
        return

    console.print()
    console.print(
        Panel(
            apply_context(rule.explanation, parsed_error),
            title=f"[bold yellow]What happened — {rule.title}[/bold yellow]",
            border_style="yellow",
        )
    )

    if rule.causes:
        console.print()
        causes_table = Table(title="Most likely causes", show_header=True, header_style="bold cyan")
        causes_table.add_column("#", style="cyan", width=4, justify="right")
        causes_table.add_column("Cause")

        for index, cause in enumerate(rule.causes, start=1):
            causes_table.add_row(str(index), apply_context(cause, parsed_error))

        console.print(causes_table)

    if rule.fixes:
        console.print()
        fixes_table = Table(title="What to try", show_header=True, header_style="bold green")
        fixes_table.add_column("#", style="cyan", width=4, justify="right")
        fixes_table.add_column("Suggestion")

        for index, fix in enumerate(rule.fixes, start=1):
            fixes_table.add_row(str(index), apply_context(fix, parsed_error))

        console.print(fixes_table)

    if module_context:
        render_module_suggestions(module_context)

    if rule.examples:
        console.print()
        examples_text = "\n".join(rule.examples)
        console.print(Panel(examples_text, title="Examples", border_style="green"))


def render_module_context(context: ModuleDiagnosisContext) -> None:
    table = Table(title="Environment context", show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan")
    table.add_column("Value")

    table.add_row("Missing import", context.module_name)
    table.add_row("Suggested package", context.package_name)

    if context.package_hint:
        table.add_row("Package hint", f"`{context.module_name}` is usually installed as `{context.package_hint}`")

    table.add_row("Python executable", context.python_executable)
    table.add_row("Virtual environment", "active" if context.venv_active else "not active")
    table.add_row("Active venv path", context.active_venv_path or "-")
    table.add_row("Project venv found", context.project_venv_path or "-")
    table.add_row("requirements.txt", "found" if context.has_requirements_file else "not found")
    table.add_row("pyproject.toml", "found" if context.has_pyproject_file else "not found")
    table.add_row("Package in requirements.txt", "yes" if context.in_requirements else "no")
    table.add_row("Package in pyproject.toml", "yes" if context.in_pyproject else "no")

    console.print()
    console.print(table)


def render_module_suggestions(context: ModuleDiagnosisContext) -> None:
    suggestions: list[str] = []

    if context.package_hint:
        suggestions.append(f"Install the package with: pip install {context.package_hint}")

    if context.project_venv_path and not context.venv_active:
        suggestions.append("Activate the project virtual environment before running the command again.")

    if context.in_requirements:
        suggestions.append("The package is listed in requirements.txt. Try: pip install -r requirements.txt")

    if context.in_pyproject:
        suggestions.append("The package is listed in pyproject.toml. Try: pip install -e .")

    if not context.in_requirements and not context.in_pyproject:
        suggestions.append(f"If this is a third-party package, install it with: pip install {context.package_name}")

    if not suggestions:
        return

    table = Table(title="Environment-aware suggestions", show_header=True, header_style="bold green")
    table.add_column("#", style="cyan", width=4, justify="right")
    table.add_column("Suggestion")

    for index, suggestion in enumerate(deduplicate(suggestions), start=1):
        table.add_row(str(index), suggestion)

    console.print()
    console.print(table)


def render_python_environment(environment: PythonEnvironment) -> None:
    console.print()
    console.print(
        Panel(
            "Current Python environment and project files detected in this directory.",
            title="[bold blue]Python environment[/bold blue]",
            border_style="blue",
        )
    )

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Item", style="cyan")
    table.add_column("Value")

    table.add_row("Python version", environment.python_version)
    table.add_row("Python executable", environment.python_executable)
    table.add_row("Working directory", environment.cwd)
    table.add_row("Virtual environment", "active" if environment.venv_active else "not active")
    table.add_row("Active venv path", environment.active_venv_path or "-")
    table.add_row("Project venv found", environment.project_venv_path or "-")
    table.add_row("requirements.txt", environment.requirements_file or "-")
    table.add_row("pyproject.toml", environment.pyproject_file or "-")
    table.add_row(".env", environment.env_file or "-")
    table.add_row(".env.example", environment.env_example_file or "-")
    table.add_row("tests directory", environment.tests_dir or "-")

    console.print(table)

    render_dependency_summary(environment)


def render_dependency_summary(environment: PythonEnvironment) -> None:
    dependency_info = environment.dependency_info

    if not dependency_info.requirements_dependencies and not dependency_info.pyproject_dependencies:
        console.print()
        console.print(
            Panel(
                "No dependencies were detected in requirements.txt or pyproject.toml.",
                title="Dependencies",
                border_style="yellow",
            )
        )
        return

    table = Table(title="Detected dependencies", show_header=True, header_style="bold green")
    table.add_column("Source", style="cyan")
    table.add_column("Packages")

    if dependency_info.requirements_dependencies:
        table.add_row("requirements.txt", ", ".join(dependency_info.requirements_dependencies))

    if dependency_info.pyproject_dependencies:
        table.add_row("pyproject.toml", ", ".join(dependency_info.pyproject_dependencies))

    console.print()
    console.print(table)


def render_python_doctor(result: PythonDoctorResult) -> None:
    console.print()
    console.print(
        Panel(
            "Python project diagnosis based on the current directory.",
            title="[bold blue]TermDoctor Python doctor[/bold blue]",
            border_style="blue",
        )
    )

    checks_table = Table(title="Checks", show_header=True, header_style="bold cyan")
    checks_table.add_column("Status", width=8)
    checks_table.add_column("Check")

    for label, ok in result.checks:
        status = "[green]OK[/green]" if ok else "[yellow]WARN[/yellow]"
        checks_table.add_row(status, label)

    console.print(checks_table)

    if result.warnings:
        warnings_table = Table(title="Warnings", show_header=True, header_style="bold yellow")
        warnings_table.add_column("#", style="cyan", width=4, justify="right")
        warnings_table.add_column("Warning")

        for index, warning in enumerate(result.warnings, start=1):
            warnings_table.add_row(str(index), warning)

        console.print()
        console.print(warnings_table)

    if result.suggestions:
        suggestions_table = Table(title="Suggestions", show_header=True, header_style="bold green")
        suggestions_table.add_column("#", style="cyan", width=4, justify="right")
        suggestions_table.add_column("Suggestion")

        for index, suggestion in enumerate(result.suggestions, start=1):
            suggestions_table.add_row(str(index), suggestion)

        console.print()
        console.print(suggestions_table)

    console.print()
    render_python_environment(result.environment)


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
            "For version 0.2.0, TermDoctor works best with standard Python errors like:\n"
            "ModuleNotFoundError, NameError, TypeError, SyntaxError, KeyError, JSONDecodeError, etc.",
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
                "No saved errors yet.\n\nRun a command first:\ntermdoctor run \"python main.py\"",
                title="TermDoctor history",
                border_style="yellow",
            )
        )
        return

    table = Table(title="TermDoctor history", show_lines=False)
    table.add_column("#", style="cyan", width=4, justify="right")
    table.add_column("Time", style="dim")
    table.add_column("Error", style="red")
    table.add_column("Exit", justify="right")
    table.add_column("Message")
    table.add_column("Command")

    for index, item in enumerate(items, start=1):
        error = item.get("error_type") or "Unknown"
        command = trim_text(item.get("command") or "", max_length=50)
        timestamp = format_history_time(item.get("timestamp"))
        exit_code = str(item.get("exit_code") or "")
        message = trim_text(item.get("error_message") or "", max_length=45)

        table.add_row(str(index), timestamp, error, exit_code, message, command)

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

    full_error_type = parsed_error.extracted.get("full_error_type")
    if full_error_type:
        lines.append(f"Full error type: {full_error_type}")

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


def deduplicate(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for item in items:
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result