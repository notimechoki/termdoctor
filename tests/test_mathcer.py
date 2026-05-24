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


def test_find_rule_returns_none_for_unknown_error():
    parsed = ParsedError(
        error_type="VeryStrangeError",
        message="Something strange happened",
        raw_text="VeryStrangeError: Something strange happened",
    )

    rule = find_rule(parsed)

    assert rule is None