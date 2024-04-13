import json
from datetime import datetime
from math import ceil
from typing import Any

from common import api
from common.base_parser import BaseParser
from common.requests_ import get_json_from_url
from common.schemes import ApiBank, PatchSource, SourceRequest, Text, TextRequest
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import get_bank_list
from sravni_reviews.schemes import SravniRuBaseScheme


def bank_exists(bank: SravniRuBaseScheme, bank_list: list[ApiBank]) -> bool:
    for bank_db in bank_list:
        if bank_db.licence == bank.bank_id:
            return True
    return False


class BaseSravniReviews(BaseParser):
    site: str
    organization_type: str
    tag: str | None = None

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        source_create = SourceRequest(site=self.site, source_type="reviews")
        self.source = api.send_source(source_create)
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def request_bank_list(self) -> dict[str, Any] | None:
        params = {"active": True, "limit": 400, "organizationType": self.organization_type, "skip": 0}
        return get_json_from_url("https://www.sravni.ru/proxy-organizations/organizations", params=params)

    def get_bank_reviews(
        self, bank_info: SravniBankInfo, page_num: int = 0, page_size: int = 1000
    ) -> dict[str, Any] | None:
        params = {
            "filterBy": "withRates",
            "isClient": False,
            "locationRoute": None,
            "newIds": True,
            "orderBy": "byDate",
            "pageIndex": page_num,
            "pageSize": page_size,
            "reviewObjectId": bank_info.sravni_id,
            "reviewObjectType": self.organization_type,
            "specificProductId": None,
            "tag": self.tag,
            "withVotes": True,
        }
        json_response = get_json_from_url("https://www.sravni.ru/proxy-reviews/reviews", params=params)
        if not json_response:
            self.logger.warning(f"error for {bank_info.alias}")
        return json_response

    def get_num_reviews(self, bank_info: SravniBankInfo) -> int:
        json_response = self.get_bank_reviews(bank_info, page_size=1)
        if json_response is None or not json_response['items']:
            return 0
        reviews_total = int(json_response["total"])
        return ceil(reviews_total / 1000)

    def load_bank_list(self) -> None:
        raise NotImplementedError

    def parse_reviews(
        self, reviews_array: list[dict[str, str]], last_date: datetime, bank: SravniBankInfo
    ) -> list[Text]:
        reviews = []
        for review in reviews_array:
            parsed_review = Text(
                source_id=self.source.id,
                bank_id=bank.bank_id,
                link=self.get_review_link(bank, review),
                date=review["createdToMoscow"],
                title=review["title"],
                text=review["text"],
                comments_num=review["commentsCount"],
            )
            if last_date > parsed_review.date.replace(tzinfo=None):
                continue
            reviews.append(parsed_review)
        return reviews

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_array = []
        page_num = self.get_num_reviews(bank_info)
        for i in range(page_num):
            self.logger.debug(f"[{i + 1}/{page_num}] download page {i + 1} for {bank_info.alias}")
            reviews_json = self.get_bank_reviews(bank_info, i)
            if reviews_json is None or len(reviews_json.get("items", [])) == 0:
                break
            reviews_json_items = reviews_json["items"]
            parsed_reviews = self.parse_reviews(reviews_json_items, parsed_time, bank_info)
            reviews_array.extend(parsed_reviews)
            times = [review.date for review in parsed_reviews]
            if len(times) == 0 or min(times).replace(tzinfo=None) <= parsed_time:
                break
        return reviews_array

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        raise NotImplementedError

    def parse(self) -> None:
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        _, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for i, bank_info in enumerate(self.bank_list):
            self.logger.info(f"[{i + 1}/{len(self.bank_list)}] download reviews for {bank_info.alias}")
            if bank_info.bank_id <= parsed_bank_id:
                continue
            reviews = self.get_reviews(parsed_time, bank_info)
            time = datetime.now()
            api.send_texts(
                TextRequest(
                    items=reviews, parsed_state=json.dumps({"bank_id": bank_info.bank_id}), last_update=parsed_time
                )
            )
            self.logger.debug(f"Time for {bank_info.alias} send reviews: {datetime.now() - time}")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
