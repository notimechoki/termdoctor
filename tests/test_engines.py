from termdoctor.engines.detector import LanguageDetector
from termdoctor.engines.python.engine import PythonEngine, command_to_parts
from termdoctor.engines.registry import get_default_registry, get_engine_by_language


def test_python_engine_detects_python_command():
    engine = PythonEngine()

    assert engine.can_handle_command(["python", "main.py"])
    assert engine.can_handle_command("python main.py")
    assert engine.can_handle_command(["pytest"])


def test_python_engine_detects_python_traceback():
    engine = PythonEngine()
    text = """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            print(username)
        NameError: name 'username' is not defined
        """

    assert engine.can_handle_text(text)


def test_language_detector_detects_python_from_command():
    detector = LanguageDetector([PythonEngine()])
    engine = detector.detect_for_command(["python", "main.py"])

    assert engine is not None
    assert engine.language == "python"


def test_language_detector_detects_python_from_text():
    detector = LanguageDetector([PythonEngine()])
    text = "NameError: name 'username' is not defined"
    engine = detector.detect_for_text(text)

    assert engine is not None
    assert engine.language == "python"


def test_python_engine_diagnose_returns_diagnosis():
    engine = PythonEngine()
    text = """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            print(username)
        NameError: name 'username' is not defined
        """

    diagnosis = engine.diagnose(text)

    assert diagnosis is not None
    assert diagnosis.language == "python"
    assert diagnosis.display_name == "Python"
    assert diagnosis.parsed_error.error_type == "NameError"
    assert diagnosis.rule is not None


def test_registry_returns_python_engine():
    engines = get_default_registry()

    assert len(engines) == 1
    assert engines[0].language == "python"
    assert get_engine_by_language("python") is not None
    assert get_engine_by_language("Python") is not None


def test_command_to_parts_handles_string_and_list():
    assert command_to_parts("python main.py") == ["python", "main.py"]
    assert command_to_parts(["python", "main.py"]) == ["python", "main.py"]