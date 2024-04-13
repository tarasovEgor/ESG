import os
from typing import Any


def relative_path(cwd: str, path: str) -> str:
    return os.path.join(cwd, path)


def path_params_to_url(params: dict[str, Any]) -> str:
    return "?" + "&".join(f"{key}={value}" for key, value in params.items())
