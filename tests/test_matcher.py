from termdoctor.matcher import find_rule
from termdoctor.models import ParsedError


def test_find_rule_for_module_not_found():
    parsed = ParsedError(
        error_type="ModuleNotFoundError",
        message="No module named 'requests'",
        raw_text="ModuleNotFoundError: No module named 'requests'",
        extracted={"module": "requests"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "ModuleNotFoundError"


def test_find_rule_for_key_error():
    parsed = ParsedError(
        error_type="KeyError",
        message="'name'",
        raw_text="KeyError: 'name'",
        extracted={"key": "name"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "KeyError"


def test_find_rule_for_file_not_found():
    parsed = ParsedError(
        error_type="FileNotFoundError",
        message="[Errno 2] No such file or directory: 'missing.txt'",
        raw_text="FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'",
        extracted={"path": "missing.txt"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "FileNotFoundError"


def test_find_rule_for_json_decode_error():
    parsed = ParsedError(
        error_type="JSONDecodeError",
        message="Expecting value: line 1 column 1 (char 0)",
        raw_text="json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)",
        extracted={"full_error_type": "json.decoder.JSONDecodeError"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "JSONDecodeError"


def test_find_rule_returns_none_for_unknown_error():
    parsed = ParsedError(
        error_type="VeryStrangeError",
        message="Something strange happened",
        raw_text="VeryStrangeError: Something strange happened",
    )

    rule = find_rule(parsed)

    assert rule is None