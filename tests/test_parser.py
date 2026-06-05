from termdoctor.engines.python.parser import parse_python_error


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


def test_parse_json_decode_error_with_dotted_path():
    text = """
        Traceback (most recent call last):
        File "main.py", line 5, in <module>
            json.loads("")
        json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "JSONDecodeError"
    assert parsed.extracted["full_error_type"] == "json.decoder.JSONDecodeError"


def test_parse_file_not_found_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 1, in <module>
            open("missing.txt")
        FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
    """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "FileNotFoundError"
    assert parsed.extracted["path"] == "missing.txt"


def test_parse_attribute_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 4, in <module>
            user.name
        AttributeError: 'NoneType' object has no attribute 'name'
    """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "AttributeError"
    assert parsed.extracted["attribute"] == "name"


def test_parse_index_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 2, in <module>
            items[10]
        IndexError: list index out of range
    """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "IndexError"


def test_parse_chained_exception_takes_last_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 3, in <module>
            int("abc")
        ValueError: invalid literal for int() with base 10: 'abc'

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
        File "main.py", line 5, in <module>
            print(username)
        NameError: name 'username' is not defined
    """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "NameError"
    assert parsed.extracted["name"] == "username"
    assert parsed.line_number == 5


def test_returns_none_for_random_text():
    text = "hello world"

    parsed = parse_python_error(text)

    assert parsed is None


def test_parse_unbound_local_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 5, in <module>
            show_count()
        File "main.py", line 2, in show_count
            print(count)
        UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "UnboundLocalError"
    assert parsed.extracted["name"] == "count"


def test_parse_assertion_error_without_message():
    text = """
        Traceback (most recent call last):
        File "main.py", line 4, in <module>
            assert actual == expected
        AssertionError
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "AssertionError"


def test_parse_is_a_directory_error_path():
    text = """
        Traceback (most recent call last):
        File "main.py", line 3, in <module>
            open("demo_folder")
        IsADirectoryError: [Errno 21] Is a directory: 'demo_folder'
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "IsADirectoryError"
    assert parsed.extracted["path"] == "demo_folder"

def test_parse_django_no_reverse_match():
    text = """
        Traceback (most recent call last):
        File "views.py", line 10, in <module>
            reverse("missing-route")
        django.urls.exceptions.NoReverseMatch: Reverse for 'missing-route' not found.
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "NoReverseMatch"
    assert parsed.extracted["full_error_type"] == "django.urls.exceptions.NoReverseMatch"


def test_parse_fastapi_response_validation_error():
    text = """
        Traceback (most recent call last):
        File "main.py", line 20, in <module>
            raise ResponseValidationError(errors=[])
        fastapi.exceptions.ResponseValidationError: 1 validation errors
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "ResponseValidationError"
    assert parsed.extracted["full_error_type"] == "fastapi.exceptions.ResponseValidationError"


def test_parse_aiogram_telegram_bad_request():
    text = """
        Traceback (most recent call last):
        File "bot.py", line 15, in handler
            await message.answer("<b>broken")
        aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't parse entities
        """

    parsed = parse_python_error(text)

    assert parsed is not None
    assert parsed.error_type == "TelegramBadRequest"
    assert parsed.extracted["full_error_type"] == "aiogram.exceptions.TelegramBadRequest"