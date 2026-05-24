import re

from termdoctor.models import ParsedError


ERROR_LINE_PATTERN = re.compile(
    r"^(?P<error_type>[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Warning)|KeyboardInterrupt|SystemExit|StopIteration|StopAsyncIteration)"
    r"(?::\s*(?P<message>.*))?$"
)

FILE_LINE_PATTERN = re.compile(
    r'File "(?P<file_path>.+?)", line (?P<line_number>\d+)'
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
    message = ""

    lines = cleaned_text.splitlines()

    for line in reversed(lines):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith("^"):
            continue

        match = ERROR_LINE_PATTERN.match(stripped_line)

        if match:
            error_type = match.group("error_type")
            message = match.group("message") or ""
            break

    if not error_type:
        return None

    extracted = extract_details(error_type=error_type, message=message)

    return ParsedError(
        error_type=error_type,
        message=message,
        raw_text=cleaned_text,
        file_path=file_path,
        line_number=line_number,
        extracted=extracted,
    )


def extract_details(error_type: str, message: str) -> dict[str, str]:
    extracted: dict[str, str] = {}

    if error_type == "ModuleNotFoundError":
        module_match = re.search(r"No module named ['\"](?P<module>[^'\"]+)['\"]", message)

        if module_match:
            extracted["module"] = module_match.group("module")

    if error_type == "NameError":
        name_match = re.search(r"name ['\"](?P<name>[^'\"]+)['\"] is not defined", message)

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

    if error_type == "FileNotFoundError":
        file_match = re.search(r"No such file or directory: ['\"](?P<path>[^'\"]+)['\"]", message)

        if file_match:
            extracted["path"] = file_match.group("path")

    if error_type == "AttributeError":
        attr_match = re.search(r"has no attribute ['\"](?P<attribute>[^'\"]+)['\"]", message)

        if attr_match:
            extracted["attribute"] = attr_match.group("attribute")

    return extracted