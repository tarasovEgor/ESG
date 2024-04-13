import logging
from time import sleep
from typing import Any

import requests

from common.settings import get_settings
from utils.logger import get_logger


class VKApi:
    TOKEN = get_settings().vk_token
    logger = get_logger(__name__, get_settings().logger_level)

    def __init__(self, version: str = "5.131"):
        self.VERSION = version

    def get_comments(
        self,
        owner_id: str,
        post_id: str,
        offset: int,
        count: int = 100,
        sort: str = "desc",
        thread_items_count: int = 10,
        start_comment_id: int | None = None,
    ) -> dict[str, Any] | None:
        response = self.get(
            "wall.getComments",
            owner_id=owner_id,
            post_id=post_id,
            count=count,
            offset=offset,
            sort=sort,
            thread_items_count=thread_items_count,
            start_comment_id=start_comment_id,
        )
        if response:
            return response.json()  # type: ignore
        return None

    def get_wall(self, owner_id: int, offset: int, count: int = 100) -> dict[str, Any] | None:
        response = self.get(
            "wall.get",
            owner_id=owner_id,
            count=count,
            offset=offset,
        )
        if response:
            return response.json()  # type: ignore
        return None

    def groups_get_by_id(self, group_ids: str) -> dict[str, Any] | None:
        response = self.get(
            "groups.getById",
            group_ids=group_ids,
        )
        if response:
            return response.json()  # type: ignore
        return None

    def get(self, url: str, **params: str | int | None) -> requests.Response | None:
        default_params = {
            "access_token": self.TOKEN,
            "v": self.VERSION,
        }
        self.logger.info(f"GET {url} {params}")
        for _ in range(5):
            response = requests.get(f"https://api.vk.com/method/{url}", params=default_params | params)  # type: ignore
            if response.json().get("error", None) is None:
                # https://vk.com/dev/api_requests limited to 3 rps for user token, and for two parsers in ~0.5s
                sleep(0.51)
                return response
            logging.warning(f"VK API error: {response.json()}")
            sleep(1)
        return None
