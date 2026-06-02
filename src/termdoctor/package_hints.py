IMPORT_PACKAGE_MAP: dict[str, str] = {
    "dotenv": "python-dotenv",
    "PIL": "pillow",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "jwt": "PyJWT",
    "Crypto": "pycryptodome",
    "dateutil": "python-dateutil",
    "magic": "python-magic",
    "slugify": "python-slugify",
    "serial": "pyserial",
    "psycopg2": "psycopg2-binary",
    "multipart": "python-multipart",
    "decouple": "python-decouple",
    "environ": "django-environ",
    "mysql": "mysqlclient",
    "MySQLdb": "mysqlclient",
    "flask_sqlalchemy": "Flask-SQLAlchemy",
    "flask_migrate": "Flask-Migrate",
    "rest_framework": "djangorestframework",
    "corsheaders": "django-cors-headers",
    "telebot": "pyTelegramBotAPI",
    "aiogram": "aiogram",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "alembic",
}


def get_package_hint(import_name: str) -> str | None:
    return IMPORT_PACKAGE_MAP.get(import_name)


def get_install_name(import_name: str) -> str:
    return get_package_hint(import_name) or import_name