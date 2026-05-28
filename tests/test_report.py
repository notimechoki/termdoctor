from pathlib import Path

import pytest

from termdoctor.report import build_markdown_report, load_report_source, write_report


def test_build_markdown_report_from_raw_text():
    text = """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            print(username)
        NameError: name 'username' is not defined
        """

    report = build_markdown_report(text)

    assert "# TermDoctor Report" in report
    assert "NameError" in report
    assert "Raw traceback" in report
    assert "username" in report


def test_build_markdown_report_without_raw_traceback():
    text = """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            print(username)
        NameError: name 'username' is not defined
        """

    report = build_markdown_report(text, include_raw=False)

    assert "# TermDoctor Report" in report
    assert "NameError" in report
    assert "Raw traceback" not in report


def test_build_markdown_report_from_file(tmp_path):
    traceback_file = tmp_path / "error.txt"
    traceback_file.write_text(
        """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            import missing_demo
        ModuleNotFoundError: No module named 'missing_demo'
        """,
        encoding="utf-8",
    )

    report = build_markdown_report(str(traceback_file))

    assert "ModuleNotFoundError" in report
    assert "missing_demo" in report


def test_write_report(tmp_path):
    output = tmp_path / "reports" / "report.md"

    path = write_report("# Demo Report\n", str(output))

    assert path == output
    assert output.read_text(encoding="utf-8") == "# Demo Report\n"


def test_report_raises_for_invalid_text():
    with pytest.raises(ValueError):
        build_markdown_report("this is not a python traceback")