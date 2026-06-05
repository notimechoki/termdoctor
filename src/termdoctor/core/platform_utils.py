import platform
from pathlib import Path


def get_activation_command(venv_path: str | None) -> str | None:
    if not venv_path:
        return None

    path = Path(venv_path)
    system_name = platform.system().lower()

    if system_name == "windows":
        return f"{path}\\Scripts\\Activate.ps1"

    return f"source {path}/bin/activate"