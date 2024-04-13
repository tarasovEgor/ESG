from time import sleep
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import ConnectTimeout, JSONDecodeError, SSLError

from utils.logger import get_logger

logger = get_logger(__name__)


def send_get_request(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> requests.Response:
    if params is None:
        params = {}
    if header is None:
        header = {}
    response = Response()
    log_params = params.copy()
    if "access_token" in log_params.keys():
        log_params["access_token"] = "..."
    for _ in range(5):
        header |= {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
        try:
            logger.debug(f"send request to {url} with {log_params=}")
            response = requests.get(url, headers=header, params=params)
        except (SSLError, ConnectTimeout) as error:
            logger.warning(f"{type(error)} when request {response.url} {error=}")
            sleep(30)
        except Exception as error:
            logger.warning(f"{type(error)} when request {response.url} {error=}")
            sleep(30)
        if response.status_code == 200:
            break
        sleep(2)
    return response


def get_json(response: Response) -> dict[str, Any] | None:
    if response.status_code != 200:
        logger.warning(f"response status code is {response.status_code}")
        logger.warning(response.text)
        return None
    try:
        json_response = response.json()  # type: dict[str, Any]
    except JSONDecodeError as error:
        logger.warning(f"Bad json on {response.url} {error=} {response.text=}")
        return None
    except Exception as error:
        logger.warning(f"Bad json on {response.url} {error=} {response.text=}")
        return None
    if type(json_response) is not list and "error" in json_response.keys() and json_response["error"] is not None:  # type: ignore
        logger.warning(f"Error in json {json_response} Error: {response.json()['error']}")
        sleep(5)
        return None
    return json_response


def get_json_from_url(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    response = send_get_request(url, params, header)
    return get_json(response)


def get_page_from_url(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> BeautifulSoup | None:
    response = send_get_request(url, params, header)
    try:
        page = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.warning(f"{e} on {url}")
        return None
    return page
