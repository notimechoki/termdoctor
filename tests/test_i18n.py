import re

from termdoctor.engines.python.engine import PythonEngine
from termdoctor.i18n import normalize_locale, set_locale, tr


PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def test_locale_aliases():
    assert normalize_locale("rus") == "ru"
    assert normalize_locale("Russian") == "ru"
    assert normalize_locale("eng") == "en"


def test_russian_catalog_falls_back_and_formats():
    set_locale("ru")
    try:
        assert tr("run.success") == "Команда успешно выполнена"
        assert tr("report.written", path="report.md").endswith("report.md")
    finally:
        set_locale("en")


def test_every_python_rule_has_russian_translation_and_matching_placeholders():
    engine = PythonEngine()
    english = {rule.id: rule for rule in engine.load_rules("en")}
    russian = {rule.id: rule for rule in engine.load_rules("ru")}

    assert english.keys() == russian.keys()
    assert len(english) >= 100

    for rule_id, english_rule in english.items():
        russian_rule = russian[rule_id]
        assert russian_rule.title != english_rule.title, rule_id
        assert russian_rule.explanation != english_rule.explanation, rule_id
        english_texts = [english_rule.explanation, *english_rule.causes, *english_rule.fixes]
        russian_texts = [russian_rule.explanation, *russian_rule.causes, *russian_rule.fixes]
        assert len(english_rule.causes) == len(russian_rule.causes), rule_id
        assert len(english_rule.fixes) == len(russian_rule.fixes), rule_id
        for source, translated in zip(english_texts, russian_texts):
            assert set(PLACEHOLDER.findall(source)) == set(PLACEHOLDER.findall(translated)), rule_id
