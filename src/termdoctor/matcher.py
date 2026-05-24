from termdoctor.models import ErrorRule, ParsedError
from termdoctor.rules_loader import load_python_rules


def find_rule(parsed_error: ParsedError) -> ErrorRule | None:
    rules = load_python_rules()

    exact_error_rules: list[ErrorRule] = []

    for rule in rules:
        if rule.error == parsed_error.error_type:
            exact_error_rules.append(rule)

    if not exact_error_rules:
        return None

    for rule in exact_error_rules:
        if not rule.match:
            continue

        for phrase in rule.match:
            if phrase.lower() in parsed_error.message.lower():
                return rule

    return exact_error_rules[0]