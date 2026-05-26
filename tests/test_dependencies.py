from termdoctor.dependencies import (
    collect_dependency_info,
    dependency_exists,
    normalize_package_name,
    parse_pyproject_dependencies,
    parse_requirement_name,
    parse_requirements_txt,
)
from termdoctor.package_hints import get_install_name, get_package_hint


def test_normalize_package_name():
    assert normalize_package_name("PyYAML") == "pyyaml"
    assert normalize_package_name("python_dotenv") == "python-dotenv"


def test_parse_requirement_name():
    assert parse_requirement_name("requests==2.32.3") == "requests"
    assert parse_requirement_name("uvicorn[standard]>=0.29.0") == "uvicorn"
    assert parse_requirement_name("python-dotenv>=1.0.0") == "python-dotenv"
    assert parse_requirement_name("# comment") is None
    assert parse_requirement_name("-r base.txt") is None


def test_parse_requirements_txt(tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        """
            requests==2.32.3
            python-dotenv>=1.0.0
            uvicorn[standard]>=0.29.0
            # comment
        """,
        encoding="utf-8",
    )

    dependencies = parse_requirements_txt(requirements)

    assert "requests" in dependencies
    assert "python-dotenv" in dependencies
    assert "uvicorn" in dependencies


def test_parse_pyproject_dependencies(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
            [project]
            dependencies = [
                "typer>=0.12.0",
                "rich>=13.7.0",
                "PyYAML>=6.0.1"
            ]
        """,
        encoding="utf-8",
    )

    dependencies = parse_pyproject_dependencies(pyproject)

    assert "typer" in dependencies
    assert "rich" in dependencies
    assert "pyyaml" in dependencies


def test_collect_dependency_info(tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("requests==2.32.3\n", encoding="utf-8")

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
            [project]
            dependencies = [
                "typer>=0.12.0"
            ]
        """,
        encoding="utf-8",
    )

    info = collect_dependency_info(tmp_path)

    assert info.requirements_file is not None
    assert info.pyproject_file is not None
    assert "requests" in info.requirements_dependencies
    assert "typer" in info.pyproject_dependencies


def test_dependency_exists():
    assert dependency_exists("requests", ["requests", "rich"]) is True
    assert dependency_exists("python_dotenv", ["python-dotenv"]) is True
    assert dependency_exists("django", ["requests", "rich"]) is False


def test_package_hints():
    assert get_package_hint("dotenv") == "python-dotenv"
    assert get_install_name("dotenv") == "python-dotenv"
    assert get_install_name("requests") == "requests"