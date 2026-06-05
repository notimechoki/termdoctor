from termdoctor.core.project import find_project_root, has_project_marker


def test_has_project_marker_with_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    assert has_project_marker(tmp_path) is True


def test_find_project_root_from_nested_directory(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    nested = tmp_path / "app" / "services"
    nested.mkdir(parents=True)

    assert find_project_root(nested) == tmp_path.resolve()


def test_find_project_root_falls_back_to_current_directory(tmp_path):
    assert find_project_root(tmp_path) == tmp_path.resolve()