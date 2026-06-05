from termdoctor.engines.python.engine import PythonEngine
from termdoctor.models import ErrorRule, ParsedError


def find_rule(parsed_error: ParsedError) -> ErrorRule | None:
    return PythonEngine().find_rule(parsed_error)