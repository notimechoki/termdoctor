from importlib import resources

import yaml

from termdoctor.models import ErrorRule


def load_python_rules() -> list[ErrorRule]:
    rules_file = resources.files("termdoctor").joinpath("rules/python_errors.yml")

    with rules_file.open("r", encoding="utf-8") as file:
        raw_rules = yaml.safe_load(file) or []

    rules: list[ErrorRule] = []

    for raw_rule in raw_rules:
        rules.append(ErrorRule.from_dict(raw_rule))

    return rules