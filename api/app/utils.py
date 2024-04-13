from typing import Any

import pandas as pd
import requests
from fastapi.logger import logger


def send_get(url: str, headers: dict[str, str] | None = None) -> requests.Response | None:
    if headers is None:
        headers = {}
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        logger.error(response.url, response.status_code)
        return None
    return response


def get_dataframe(
    url: str, skip_rows: int = 3, index_col: str | int | None = None, types: dict[str, Any] | None = None
) -> pd.DataFrame | None:
    response = send_get(url)
    if response is None:
        return None

    dataframe = pd.read_excel(response.content, skiprows=skip_rows, index_col=index_col, dtype=types)
    return dataframe
