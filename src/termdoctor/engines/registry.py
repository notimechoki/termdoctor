from termdoctor.engines.base import BaseEngine
from termdoctor.engines.detector import LanguageDetector
from termdoctor.engines.python.engine import PythonEngine


def get_default_registry() -> list[BaseEngine]:
    return [PythonEngine()]


def get_language_detector() -> LanguageDetector:
    return LanguageDetector(get_default_registry())


def get_engine_by_language(language: str) -> BaseEngine | None:
    normalized = language.strip().lower()

    for engine in get_default_registry():
        if engine.language == normalized or engine.display_name.lower() == normalized:
            return engine

    return None