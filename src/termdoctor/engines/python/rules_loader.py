from termdoctor.engines.python.engine import PythonEngine
from termdoctor.models import ErrorRule


def load_python_rules() -> list[ErrorRule]:
    return PythonEngine().load_rules()