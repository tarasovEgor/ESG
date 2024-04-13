from typing import Any

import requests
from bs4 import BeautifulSoup

from common import requests_

base_headers = {"X-Requested-With": "XMLHttpRequest"}


def send_get_request(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> requests.Response:
    if params is None:
        params = {}
    if header is None:
        header = {}
    header |= base_headers
    return requests_.send_get_request(url, params, header)


def get_json_from_url(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    if params is None:
        params = {}
    if header is None:
        header = {}
    header |= base_headers
    return requests_.get_json_from_url(url, params, header)


def get_page_from_url(
    url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
) -> BeautifulSoup | None:
    if params is None:
        params = {}
    if header is None:
        header = {}
    header |= base_headers
    return requests_.get_page_from_url(url, params, header)
