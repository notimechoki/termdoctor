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

    searchable_text = build_searchable_text(parsed_error)

    for rule in exact_error_rules:
        if not rule.match:
            continue

        for phrase in rule.match:
            if phrase.lower() in searchable_text:
                return rule

    for rule in exact_error_rules:
        if not rule.match:
            return rule

    return exact_error_rules[0]


def build_searchable_text(parsed_error: ParsedError) -> str:
    parts = [
        parsed_error.error_type,
        parsed_error.message,
        parsed_error.raw_text,
    ]

    full_error_type = parsed_error.extracted.get("full_error_type")

    if full_error_type:
        parts.append(full_error_type)

    return "\n".join(parts).lower()