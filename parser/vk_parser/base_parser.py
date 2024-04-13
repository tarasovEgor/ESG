import json
import os
import re
from datetime import datetime, timedelta
from math import ceil
from typing import Any

import numpy as np

from common import api
from common.base_parser import BaseParser
from common.schemes import PatchSource, Source, SourceRequest, Text, TextRequest
from common.settings import Settings
from utils import relative_path
from utils.logger import get_logger
from vk_parser.database import VkBank, VKBaseDB
from vk_parser.queries import create_banks, get_bank_list
from vk_parser.schemes import VKType
from vk_parser.vk_api import VKApi


def clean_text_from_vk_url(match: re.Match[str]) -> str:
    group = match.group()
    return group.split("|")[1][:-1]


emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F1F2-\U0001F1F4"  # Macau flag
    "\U0001F1E6-\U0001F1FF"  # flags
    "\U0001F600-\U0001F64F"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U0001F1F2"
    "\U0001F1F4"
    "\U0001F620"
    "\u200d"
    "\u2640-\u2642"
    "\u1F91D"
    "]+",
    flags=re.UNICODE,
)


class VKBaseParser(BaseParser):
    logger = get_logger(__name__, Settings().logger_level)
    vk_api = VKApi()
    file: str
    type: VKType

    def __init__(self) -> None:
        self.logger.info("init vk parser")
        source_create = SourceRequest(site=f"vk.com/{self.type}", source_type="vk.com")
        self.source = api.send_source(source_create)
        self.bank_list = get_bank_list(self.type)
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list(self.type)

    def load_bank_list(self) -> None:
        path = relative_path(os.path.dirname(__file__), self.file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{self.file} not found")
        bank_arr = np.load(path, allow_pickle=True)
        db_banks: list[VKBaseDB] = [
            VkBank(id=bank[0], name=bank[1], vk_id=bank[2], domain=bank[3]) for bank in bank_arr
        ]
        create_banks(db_banks)
        self.logger.info("bank list loaded")

    def json_to_comment_text(self, domain: str, comment: dict[str, Any], bank_id: int, is_thread: bool = False) -> Text:
        if is_thread:
            url = f"https://vk.com/wall{comment['owner_id']}_{comment['post_id']}?reply={comment['id']}&thread={comment['parents_stack'][0]}"
        else:
            url = f"https://vk.com/{domain}?w=wall{comment['owner_id']}_{comment['post_id']}_r{comment['id']}"
        comment_text = re.sub(r"\[.+?\|.+?]", clean_text_from_vk_url, comment["text"])
        comment_text = emoji_pattern.sub("", comment_text)
        return Text(
            date=comment["date"], text=comment_text, link=url, source_id=self.source.id, title="", bank_id=bank_id
        )

    def get_post_comments(
        self, domain: str, owner_id: str, post_id: str, comments_num: int, bank_id: int
    ) -> list[Text]:
        comments_pages = ceil(comments_num / 100)
        comments = []
        for i in range(comments_pages):
            comments_json = self.vk_api.get_comments(owner_id, post_id, offset=i * 100)
            if comments_json is None:
                continue
            for comment in comments_json["response"]["items"]:
                if comment["text"] != "":
                    json_comment = self.json_to_comment_text(domain, comment, bank_id)
                    comments.append(json_comment)
                for thread_comment in comment["thread"]["items"]:
                    if thread_comment["text"] != "":
                        json_comment = self.json_to_comment_text(domain, thread_comment, bank_id)
                        comments.append(json_comment)
        return comments

    def get_vk_source_params(self, source: Source) -> tuple[int, int, int, datetime]:
        page_num, parsed_bank_id, parsed_time = super().get_source_params(source)
        parsed_state = {}
        if source.parser_state is not None:
            parsed_state = json.loads(source.parser_state)
        post_id = int(parsed_state.get("post_id", "0"))
        return page_num, parsed_bank_id, post_id, parsed_time

    def parse(self) -> None:
        self.logger.info("start parse VK")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        page_num, parsed_bank_id, post_id, parsed_time = self.get_vk_source_params(current_source)
        for bank_iter, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_iter+1}/{len(self.bank_list)}] start parse {bank.name}")
            if bank.id < parsed_bank_id:  # type: ignore
                continue
            response_json = self.vk_api.get_wall(bank.vk_id, 0, count=1)  # type: ignore # get total number of posts
            if response_json is None:
                continue
            num_page = ceil(response_json["response"]["count"] / 100)
            for i in range(num_page):
                self.logger.info(f"Start parse {bank.name} page [{i+1}/{num_page}]")
                if i <= page_num:
                    continue
                response_json = self.vk_api.get_wall(bank.vk_id, i * 100)  # type: ignore
                if response_json is None:
                    continue
                posts_dates = [post["date"] for post in response_json["response"]["items"]]
                look_up_date = max((parsed_time - timedelta(days=7)).timestamp(), 0)
                if max(posts_dates) < look_up_date:  # if all posts are older than 7 days
                    break
                for post in response_json["response"]["items"]:
                    if (
                        post.get("owner_id", None) is None
                        or post.get("id", None) is None
                        or post.get("comments", None) is None
                        or post["comments"].get("count", None) is None
                    ):
                        continue
                    comments = self.get_post_comments(
                        bank.domain, post["owner_id"], post["id"], post["comments"]["count"], bank.id  # type: ignore
                    )
                    if len(comments) == 0:
                        continue
                    comments_date = [comment.date for comment in comments]
                    if max(comments_date).replace(tzinfo=None) < parsed_time:
                        break
                    long_comments = []
                    for comment in comments:
                        if len(comment.text) > 100 and comment.date.replace(tzinfo=None) > parsed_time:
                            long_comments.append(comment)
                    api.send_texts(
                        TextRequest(
                            items=long_comments,
                            parsed_state=json.dumps({"bank_id": bank.id, "page_num": i, "post_id": post["id"]}),
                            last_update=parsed_time,
                        )
                    )
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
