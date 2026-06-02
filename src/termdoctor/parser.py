import re

from termdoctor.models import ParsedError


ERROR_LINE_PATTERN = re.compile(
    r"^(?P<full_error_type>"
    r"(?:[A-Za-z_][A-Za-z0-9_]*\.)*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Warning)"
    r"|KeyboardInterrupt|SystemExit|StopIteration|StopAsyncIteration|MemoryError"
    r"|ImproperlyConfigured|NoReverseMatch|TemplateDoesNotExist|FixtureLookupError"
    r"|TelegramBadRequest|TelegramUnauthorized|TelegramForbidden|TelegramNotFound"
    r"|TelegramConflict|TelegramRetryAfter|TelegramMigrateToChat|TelegramNetworkError))"
    r"(?::\s*(?P<message>.*))?$"
)

FILE_LINE_PATTERN = re.compile(
    r'File "(?P<file_path>.+?)", line (?P<line_number>\d+)'
)

IGNORED_TRACEBACK_LINES = (
    "Traceback (most recent call last):",
    "During handling of the above exception, another exception occurred:",
    "The above exception was the direct cause of the following exception:",
)


def parse_python_error(text: str) -> ParsedError | None:
    cleaned_text = text.strip()

    if not cleaned_text:
        return None

    file_path = None
    line_number = None

    file_matches = list(FILE_LINE_PATTERN.finditer(cleaned_text))

    if file_matches:
        last_file_match = file_matches[-1]
        file_path = last_file_match.group("file_path")
        line_number = int(last_file_match.group("line_number"))

    error_type = None
    full_error_type = None
    message = ""

    lines = cleaned_text.splitlines()

    for line in reversed(lines):
        stripped_line = line.strip()

        if should_skip_line(stripped_line):
            continue

        match = ERROR_LINE_PATTERN.match(stripped_line)

        if match:
            full_error_type = match.group("full_error_type")
            error_type = normalize_error_type(full_error_type)
            message = match.group("message") or ""
            break

    if not error_type:
        return None

    extracted = extract_details(error_type=error_type, message=message, raw_text=cleaned_text)

    if full_error_type and full_error_type != error_type:
        extracted["full_error_type"] = full_error_type

    return ParsedError(
        error_type=error_type,
        message=message,
        raw_text=cleaned_text,
        file_path=file_path,
        line_number=line_number,
        extracted=extracted,
    )


def should_skip_line(line: str) -> bool:
    if not line:
        return True

    if line.startswith("^"):
        return True

    if set(line) == {"~"}:
        return True

    if set(line) == {"-"}:
        return True

    return line in IGNORED_TRACEBACK_LINES


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
        )

        if not name_match:
            name_match = re.search(
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

    if error_type in {"FileNotFoundError", "IsADirectoryError", "NotADirectoryError"}:
        file_match = re.search(r": ['\"](?P<path>[^'\"]+)['\"]", message)

        if file_match:
            extracted["path"] = file_match.group("path")

    if error_type == "AttributeError":
        attr_match = re.search(r"has no attribute ['\"](?P<attribute>[^'\"]+)['\"]", message)

        if attr_match:
            extracted["attribute"] = attr_match.group("attribute")

    if error_type == "IndexError":
        extracted["index_hint"] = "The index is outside the available range."

    if error_type == "JSONDecodeError":
        extracted["json_hint"] = "The input is not valid JSON."

    if error_type in {"OperationalError", "IntegrityError", "ProgrammingError", "DatabaseError"}:
        relation_match = re.search(r'relation ["\']?(?P<relation>[A-Za-z0-9_\.]+)["\']? does not exist', raw_text)

        if relation_match:
            extracted["relation"] = relation_match.group("relation")

    if error_type in {"ValidationError", "ResponseValidationError"}:
        field_match = re.search(r"(?:field required|Field required).*?(?P<field>[A-Za-z_][A-Za-z0-9_]*)", raw_text, re.IGNORECASE)

        if field_match:
            extracted["field"] = field_match.group("field")

    return extracted