from termdoctor.engines.base import BaseEngine


class LanguageDetector:
    def __init__(self, engines: list[BaseEngine]) -> None:
        self.engines = engines

    def detect_for_command(self, command: str | list[str], output_text: str = "") -> BaseEngine | None:
        for engine in self.engines:
            if engine.can_handle_command(command):
                return engine

        if output_text:
            return self.detect_for_text(output_text)

        return None

    def detect_for_text(self, text: str) -> BaseEngine | None:
        for engine in self.engines:
            if engine.can_handle_text(text):
                return engine

        return None