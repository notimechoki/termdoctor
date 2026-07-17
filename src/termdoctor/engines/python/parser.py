from __future__ import annotations

import re
from pathlib import Path

from termdoctor.models import ParsedError, TracebackFrame


ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
FILE_LINE_PATTERN = re.compile(
    r'^\s*File\s+["\'](?P<file_path>.+?)["\'],\s+line\s+(?P<line_number>\d+)'
    r'(?:,\s+in\s+(?P<function_name>.+))?\s*$'
)

ERROR_LINE_PATTERN = re.compile(
    r"^(?P<full_error_type>(?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Za-z_][A-Za-z0-9_]*)"
    r"(?::\s*(?P<message>.*))?$"
)
KNOWN_EXCEPTION_NAMES = {
    "KeyboardInterrupt",
    "SystemExit",
    "GeneratorExit",
    "StopIteration",
    "StopAsyncIteration",
    "MemoryError",
    "ExceptionGroup",
    "BaseExceptionGroup",
    "ImproperlyConfigured",
    "NoReverseMatch",
    "TemplateDoesNotExist",
    "ObjectDoesNotExist",
    "DoesNotExist",
    "MultipleObjectsReturned",
    "FixtureLookupError",
    "Failed",
    "Skipped",
    "NoResultFound",
    "MultipleResultsFound",
    "BadRequest",
    "BadParameter",
    "ClickException",
    "TelegramBadRequest",
    "TelegramUnauthorized",
    "TelegramForbidden",
    "TelegramNotFound",
    "TelegramConflict",
    "TelegramRetryAfter",
    "TelegramMigrateToChat",
    "TelegramNetworkError",
    "ApiTelegramException",
    "CommandError",
    "ValidationError",
    "ResponseValidationError",
    "RequestValidationError",
    "CancelledError",
    "TimeoutExpired",
    "CalledProcessError",
    "ArgumentError",
    "FrozenInstanceError",
    "PydanticUserError",
    "Timeout",
    "HTTPError",
    "URLError",
    "AxisError",
    "ParserError",
    "DecodeError",
    "ExpiredSignatureError",
    "YAMLError",
    "TOMLDecodeError",
    "PackageNotFoundError",
    "Error",
}
IGNORED_TRACEBACK_LINES = {
    "Traceback (most recent call last):",
    "During handling of the above exception, another exception occurred:",
    "The above exception was the direct cause of the following exception:",
}


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text)


def parse_python_error(text: str) -> ParsedError | None:
    cleaned_text = strip_ansi(text).strip()
    if not cleaned_text:
        return None

    lines = cleaned_text.splitlines()
    frames = parse_traceback_frames(lines)
    has_traceback_evidence = bool(frames) or "Traceback (most recent call last):" in cleaned_text
    exception_lines: list[tuple[str, str]] = []

    for line in lines:
        stripped_line = normalize_exception_line(line)
        if should_skip_line(stripped_line):
            continue
        match = ERROR_LINE_PATTERN.match(stripped_line)
        if not match:
            continue

        full_error_type = match.group("full_error_type")
        error_type = normalize_error_type(full_error_type)
        message = match.group("message") or ""
        if not looks_like_exception(error_type, full_error_type, has_traceback_evidence):
            continue
        exception_lines.append((full_error_type, message))

    if not exception_lines:
        return None

    full_error_type, message = exception_lines[-1]
    error_type = normalize_error_type(full_error_type)
    extracted = extract_details(error_type=error_type, message=message, raw_text=cleaned_text)
    if full_error_type != error_type:
        extracted["full_error_type"] = full_error_type

    file_path = frames[-1].file_path if frames else None
    line_number = frames[-1].line_number if frames else None
    exception_chain = [normalize_error_type(item[0]) for item in exception_lines]

    return ParsedError(
        error_type=error_type,
        message=message,
        raw_text=cleaned_text,
        file_path=file_path,
        line_number=line_number,
        full_error_type=full_error_type,
        frames=frames,
        exception_chain=exception_chain,
        extracted=extracted,
    )


def normalize_exception_line(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^[|+\- ]+(?=[A-Za-z_])", "", stripped)
    return stripped


def parse_traceback_frames(lines: list[str]) -> list[TracebackFrame]:
    frames: list[TracebackFrame] = []
    for index, line in enumerate(lines):
        match = FILE_LINE_PATTERN.match(strip_ansi(line))
        if not match:
            continue
        code_line = None
        if index + 1 < len(lines):
            candidate = strip_ansi(lines[index + 1]).strip()
            if candidate and not FILE_LINE_PATTERN.match(candidate) and candidate not in IGNORED_TRACEBACK_LINES:
                code_line = candidate
        frames.append(
            TracebackFrame(
                file_path=match.group("file_path"),
                line_number=int(match.group("line_number")),
                function_name=(match.group("function_name") or "").strip() or None,
                code_line=code_line,
            )
        )
    return frames


def attach_source_context(parsed_error: ParsedError, cwd: Path | None = None, radius: int = 2) -> None:
    base = (cwd or Path.cwd()).resolve()
    selected_path: Path | None = None
    selected_frame: TracebackFrame | None = None

    for frame in reversed(parsed_error.frames):
        candidate = Path(frame.file_path)
        if not candidate.is_absolute():
            candidate = base / candidate
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if not resolved.is_file():
            continue
        lowered_parts = {part.lower() for part in resolved.parts}
        is_dependency = bool({"site-packages", "dist-packages"} & lowered_parts)
        try:
            is_project_file = resolved.is_relative_to(base)
        except AttributeError:
            is_project_file = str(resolved).startswith(str(base))
        if is_project_file and not is_dependency:
            selected_path, selected_frame = resolved, frame
            break
        if selected_path is None:
            selected_path, selected_frame = resolved, frame

    if selected_path is None or selected_frame is None:
        return

    try:
        source_lines = selected_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return

    parsed_error.file_path = selected_frame.file_path
    parsed_error.line_number = selected_frame.line_number
    target_index = selected_frame.line_number - 1
    start = max(0, target_index - radius)
    end = min(len(source_lines), target_index + radius + 1)
    parsed_error.source_context = [
        f"{'> ' if index == target_index else '  '}{index + 1:4d} | {source_lines[index]}"
        for index in range(start, end)
    ]


def should_skip_line(line: str) -> bool:
    if not line:
        return True
    if line.startswith("^"):
        return True
    if set(line) <= {"~", "-", "+", "|", " "}:
        return True
    return line in IGNORED_TRACEBACK_LINES


def looks_like_exception(error_type: str, full_error_type: str, has_traceback_evidence: bool) -> bool:
    if error_type in KNOWN_EXCEPTION_NAMES:
        return True
    if error_type.endswith(("Error", "Exception", "Warning")):
        return True
    if "." in full_error_type and has_traceback_evidence:
        return True
    return has_traceback_evidence and error_type[:1].isupper()


def normalize_error_type(error_type: str) -> str:
    return error_type.split(".")[-1]


def extract_details(error_type: str, message: str, raw_text: str = "") -> dict[str, str]:
    extracted: dict[str, str] = {}

    if error_type == "ModuleNotFoundError":
        module_match = re.search(r"No module named ['\"](?P<module>[^'\"]+)['\"]", message)
        if module_match:
            extracted["module"] = module_match.group("module")

    if error_type == "NameError":
        name_match = re.search(r"name ['\"](?P<name>[^'\"]+)['\"] is not defined", message)
        if name_match:
            extracted["name"] = name_match.group("name")

    if error_type == "UnboundLocalError":
        name_match = re.search(
            r"(?:local variable|free variable) ['\"](?P<name>[^'\"]+)['\"]",
            message,
        ) or re.search(
            r"cannot access local variable ['\"](?P<name>[^'\"]+)['\"]",
            message,
        )
        if name_match:
            extracted["name"] = name_match.group("name")

    if error_type == "ImportError":
        import_match = re.search(r"cannot import name ['\"](?P<name>[^'\"]+)['\"]", message)
        if import_match:
            extracted["name"] = import_match.group("name")

    if error_type == "KeyError":
        key_match = re.search(r"['\"](?P<key>[^'\"]+)['\"]", message)
        if key_match:
            extracted["key"] = key_match.group("key")

    if error_type in {"FileNotFoundError", "IsADirectoryError", "NotADirectoryError", "FileExistsError"}:
        file_match = re.search(r": ['\"](?P<path>[^'\"]+)['\"]", message)
        if file_match:
            extracted["path"] = file_match.group("path")

    if error_type == "AttributeError":
        attr_match = re.search(r"has no attribute ['\"](?P<attribute>[^'\"]+)['\"]", message)
        if attr_match:
            extracted["attribute"] = attr_match.group("attribute")

    if error_type in {"OperationalError", "IntegrityError", "ProgrammingError", "DatabaseError"}:
        relation_match = re.search(
            r'relation ["\']?(?P<relation>[A-Za-z0-9_.]+)["\']? does not exist',
            raw_text,
        )
        if relation_match:
            extracted["relation"] = relation_match.group("relation")

    if error_type in {"ValidationError", "ResponseValidationError", "RequestValidationError"}:
        field_match = re.search(
            r"(?:field required|Field required).*?(?P<field>[A-Za-z_][A-Za-z0-9_]*)",
            raw_text,
            re.IGNORECASE,
        )
        if field_match:
            extracted["field"] = field_match.group("field")

    return extracted
