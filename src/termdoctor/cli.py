from pathlib import Path
import sys

import typer

from termdoctor import __version__
from termdoctor.core.history import (
    clear_history,
    get_last_history_item,
    load_history,
    save_failed_run,
)
from termdoctor.core.runner import run_shell_command
from termdoctor.engines.registry import get_default_registry, get_language_detector
from termdoctor.engines.python.environment import diagnose_python_project, get_python_environment
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
from termdoctor.report import build_markdown_report, write_report


app = typer.Typer(
    name="termdoctor",
    help="Explain terminal errors and suggest practical fixes.",
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
    detector = get_language_detector()
    engine = detector.detect_for_command(command_to_run, text_to_parse)

    if engine is None:
        render_no_python_error_found(text_to_parse)
        raise typer.Exit(code=command_result.exit_code)

    diagnosis = engine.diagnose(text_to_parse, command_result=command_result)

    if diagnosis is None:
        render_no_python_error_found(text_to_parse)
        raise typer.Exit(code=command_result.exit_code)

    save_failed_run(command_result, diagnosis.parsed_error)
    render_engine_diagnosis(diagnosis)

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


def render_engine_diagnosis(diagnosis) -> None:
    render_diagnosis(
        diagnosis.parsed_error,
        diagnosis.rule,
        diagnosis.command_result,
        module_context=diagnosis.module_context,
        framework_context=diagnosis.framework_context,
        language_name=diagnosis.display_name,
    )


@app.command("languages")
def show_languages() -> None:
    engines = get_default_registry()

    console.print("[bold]Supported language engines[/bold]")

    for engine in engines:
        console.print(f"- {engine.display_name} ({engine.language})")


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
        help='Use "last" or provide a path to a file with a traceback.',
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        help="Force a language engine. Example: --lang python",
    ),
) -> None:
    text = load_explain_text(source)
    engine = get_engine_for_explain(text=text, lang=lang)

    if engine is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    diagnosis = engine.diagnose(text)

    if diagnosis is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    render_engine_diagnosis(diagnosis)


@app.command("report")
def create_report(
    source: str = typer.Argument(
        "last",
        help='Use "last" or provide a path to a file with a traceback.',
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the Markdown report to a file.",
    ),
    show_raw: bool = typer.Option(
        True,
        "--show-raw/--no-raw",
        help="Include or exclude the raw traceback in the report.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        help="Force a language engine. Example: --lang python",
    ),
) -> None:
    try:
        markdown = build_markdown_report(source=source, include_raw=show_raw, lang=lang)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    if output:
        path = write_report(markdown, output)
        console.print(f"[green]Report written to:[/green] {path}")
        raise typer.Exit(code=0)

    console.print(markdown)


@app.command("paste")
def paste_error(
    lang: str | None = typer.Option(
        None,
        "--lang",
        help="Force a language engine. Example: --lang python",
    ),
) -> None:
    console.print("[bold]Paste a traceback below.[/bold]")
    console.print("Press Ctrl+D on Linux/macOS or Ctrl+Z then Enter on Windows when finished.")
    console.print()

    text = sys.stdin.read()
    engine = get_engine_for_explain(text=text, lang=lang)

    if engine is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    diagnosis = engine.diagnose(text)

    if diagnosis is None:
        render_no_python_error_found(text)
        raise typer.Exit(code=1)

    render_engine_diagnosis(diagnosis)


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


def load_explain_text(source: str) -> str:
    if source == "last":
        last_item = get_last_history_item()

        if not last_item:
            console.print("[yellow]No history found.[/yellow]")
            console.print('Run something first, for example: termdoctor run "python main.py"')
            raise typer.Exit(code=1)

        return last_item.get("stderr") or last_item.get("stdout") or ""

    path = Path(source)

    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")

    return source


def get_engine_for_explain(text: str, lang: str | None = None):
    if lang:
        from termdoctor.engines.registry import get_engine_by_language

        return get_engine_by_language(lang)

    return get_language_detector().detect_for_text(text)


def main() -> None:
    app()