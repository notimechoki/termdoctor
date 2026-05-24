from termdoctor.parser import parse_python_error


def test_parse_module_not_found_error():
    text = """
            Traceback (most recent call last):
            File "main.py", line 1, in <module>
                import requests_fake
            ModuleNotFoundError: No module named 'requests_fake'
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "ModuleNotFoundError"
    assert parsed.extracted["module"] == "requests_fake"
    assert parsed.file_path == "main.py"
    assert parsed.line_number == 1


def test_parse_name_error():
    text = """
            Traceback (most recent call last):
            File "main.py", line 3, in <module>
                print(username)
            NameError: name 'username' is not defined
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "NameError"
    assert parsed.extracted["name"] == "username"


def test_parse_key_error():
    text = """
            Traceback (most recent call last):
            File "main.py", line 5, in <module>
                print(user["name"])
            KeyError: 'name'
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "KeyError"
    assert parsed.extracted["key"] == "name"


def test_returns_none_for_random_text():
    text = "hello world"

    parsed = parse_python_error(text)

    assert parsed is None