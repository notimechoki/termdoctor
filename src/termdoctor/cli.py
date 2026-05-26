from pathlib import Path
import sys

import typer

from termdoctor import __version__
from termdoctor.environment import (
    build_module_diagnosis_context,
    diagnose_python_project,
    get_python_environment,
)
from termdoctor.history import (
    clear_history,
    get_last_history_item,
    load_history,
    save_failed_run,
)
from termdoctor.matcher import find_rule
from termdoctor.parser import parse_python_error
from termdoctor.renderer import (
    console,
    render_command_output,
    render_diagnosis,
    render_history,
    render_no_python_error_found,
    render_python_doctor,
    render_python_environment,
    render_success,
)
from termdoctor.runner import run_shell_command


app = typer.Typer(
    name="termdoctor",
    help="Explain Python terminal errors and suggest practical fixes.",
    add_completion=False,
    no_args_is_help=True,
)

doctor_app = typer.Typer(
    name="doctor",
    help="Run project-level diagnostics.",
    add_completion=False,
    no_args_is_help=True,
)

app.add_typer(doctor_app, name="doctor")


def version_callback(value: bool) -> None:
    if value:
        console.print(f"TermDoctor {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show TermDoctor version.",
        callback=version_callback,
        is_eager=True,
    )
) -> None:
    pass


@app.command(
    "run",
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def run_command(
    ctx: typer.Context,
    command: str | None = typer.Argument(
        None,
        help=(
            "Command to run. Examples: "
            'termdoctor run "python main.py" or termdoctor run -- python main.py'
        ),
    ),
) -> None:
    command_to_run = build_command_input(command=command, extra_args=list(ctx.args))

    if command_to_run is None:
        console.print("[red]Error:[/red] Please provide a command.")
        console.print('Example 1: termdoctor run "python main.py"')
        console.print("Example 2: termdoctor run -- python main.py")
        raise typer.Exit(code=1)

    command_result = run_shell_command(command_to_run)

    if command_result.exit_code == 0:
        render_success(command_result)
        raise typer.Exit(code=0)

    render_command_output(command_result)

    text_to_parse = command_result.stderr or command_result.stdout
    parsed_error = parse_python_error(text_to_parse)

    save_failed_run(command_result, parsed_error)

    if parsed_error is None:
        render_no_python_error_found(text_to_parse)
        raise typer.Exit(code=command_result.exit_code)

    rule = find_rule(parsed_error)
    module_context = None

    if parsed_error.error_type == "ModuleNotFoundError":
        module_name = parsed_error.extracted.get("module")

        if module_name:
            module_context = build_module_diagnosis_context(module_name)

    render_diagnosis(parsed_error, rule, command_result, module_context=module_context)

    raise typer.Exit(code=command_result.exit_code)


def build_command_input(command: str | None, extra_args: list[str]) -> str | list[str] | None:
    if command and extra_args:
        return [command, *extra_args]

    if command:
        stripped_command = command.strip()
        return stripped_command if stripped_command else None

    if extra_args:
        return extra_args

    return None


@app.command("env")
def show_environment() -> None:
    environment = get_python_environment()
    render_python_environment(environment)


@doctor_app.command("python")
def doctor_python() -> None:
    result = diagnose_python_project()
    render_python_doctor(result)


@app.command("explain")
def explain_error(
    source: str = typer.Argument(
        "last",
        help='Use "last" or provide a path to a file with a Python traceback.',
    ),
) -> None:
    text = ""

    if source == "last":
        last_item = get_last_history_item()

        if not last_item:
            console.print("[yellow]No history found.[/yellow]")
            console.print('Run something first, for example: termdoctor run "python main.py"')
            raise typer.Exit(code=1)

        text = last_item.get("stderr") or last_item.get("stdout") or ""

    else:
        path = Path(source)

        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8")
        else:
            text = source

    parsed_error = parse_python_error(text)

    if parsed_error is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    rule = find_rule(parsed_error)
    module_context = None

    if parsed_error.error_type == "ModuleNotFoundError":
        module_name = parsed_error.extracted.get("module")

        if module_name:
            module_context = build_module_diagnosis_context(module_name)

    render_diagnosis(parsed_error, rule, module_context=module_context)


@app.command("paste")
def paste_error() -> None:
    console.print("[bold]Paste a Python traceback below.[/bold]")
    console.print("Press Ctrl+D on Linux/macOS or Ctrl+Z then Enter on Windows when finished.")
    console.print()

    text = sys.stdin.read()

    parsed_error = parse_python_error(text)

    if parsed_error is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    rule = find_rule(parsed_error)
    module_context = None

    if parsed_error.error_type == "ModuleNotFoundError":
        module_name = parsed_error.extracted.get("module")

        if module_name:
            module_context = build_module_diagnosis_context(module_name)

    render_diagnosis(parsed_error, rule, module_context=module_context)


@app.command("history")
def show_history(
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of history items to show.",
    )
) -> None:
    items = load_history()

    if limit > 0:
        items = items[-limit:]

    render_history(items)


@app.command("clear")
def clear_saved_history() -> None:
    clear_history()
    console.print("[green]History cleared.[/green]")


def main() -> None:
    app()