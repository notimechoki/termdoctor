from termdoctor.engines.python.matcher import find_rule
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

def test_find_rule_for_unbound_local_error():
    parsed = ParsedError(
        error_type="UnboundLocalError",
        message="cannot access local variable 'count' where it is not associated with a value",
        raw_text="UnboundLocalError: cannot access local variable 'count' where it is not associated with a value",
        extracted={"name": "count"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "UnboundLocalError"


def test_find_rule_for_assertion_error():
    parsed = ParsedError(
        error_type="AssertionError",
        message="",
        raw_text="AssertionError",
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.error == "AssertionError"

def test_find_rule_for_django_no_reverse_match():
    parsed = ParsedError(
        error_type="NoReverseMatch",
        message="Reverse for 'missing-route' not found",
        raw_text="django.urls.exceptions.NoReverseMatch: Reverse for 'missing-route' not found",
        extracted={"full_error_type": "django.urls.exceptions.NoReverseMatch"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.id == "django_no_reverse_match"


def test_find_rule_for_fastapi_response_validation_error():
    parsed = ParsedError(
        error_type="ResponseValidationError",
        message="1 validation errors",
        raw_text="fastapi.exceptions.ResponseValidationError: 1 validation errors",
        extracted={"full_error_type": "fastapi.exceptions.ResponseValidationError"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.id == "fastapi_response_validation_error"


def test_find_rule_for_sqlalchemy_operational_error():
    parsed = ParsedError(
        error_type="OperationalError",
        message="connection refused",
        raw_text="sqlalchemy.exc.OperationalError: connection refused",
        extracted={"full_error_type": "sqlalchemy.exc.OperationalError"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.id == "sqlalchemy_operational_error"


def test_find_rule_for_aiogram_bad_request():
    parsed = ParsedError(
        error_type="TelegramBadRequest",
        message="Bad Request: can't parse entities",
        raw_text="aiogram.exceptions.TelegramBadRequest: Bad Request: can't parse entities",
        extracted={"full_error_type": "aiogram.exceptions.TelegramBadRequest"},
    )

    rule = find_rule(parsed)

    assert rule is not None
    assert rule.id == "aiogram_telegram_bad_request"