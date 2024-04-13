import json
import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from banki_ru.database import BankiRuBase
from banki_ru.queries import get_bank_list
from banki_ru.requests_ import get_page_from_url, send_get_request
from banki_ru.schemes import BankiRuBaseScheme, BankTypes
from common import api
from common.base_parser import BaseParser
from common.schemes import (
    ApiBank,
    PatchSource,
    Source,
    SourceRequest,
    SourceTypes,
    Text,
    TextRequest,
)


def bank_exists(bank: BankiRuBaseScheme, bank_list: list[ApiBank]) -> bool:
    for bank_db in bank_list:
        if bank_db.licence == bank.bank_id:
            return True
    return False


class BankiBase(BaseParser):
    bank_site: BankTypes
    source_type: SourceTypes

    def __init__(self) -> None:
        self.bank_list = get_bank_list(self.bank_site)
        self.source = self.create_source()
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list(self.bank_site)

    def create_source(self) -> Source:
        create_source = SourceRequest(site=self.bank_site, source_type=self.source_type)
        self.logger.debug(f"Creating source {create_source}")
        return api.send_source(create_source)

    def load_bank_list(self) -> None:
        raise NotImplementedError

    def get_pages_num_html(self, url: str, params: dict[str, Any] | None = None) -> int | None:
        response = send_get_request(url, params)
        if response.status_code != 200:
            return None
        page = BeautifulSoup(response.text, "html.parser")
        items_num_text = page.find("div", class_="ui-pagination__description")
        if items_num_text is None:
            return 0
        items_num = [int(num) for num in re.findall("\\d+", items_num_text.text)]
        # items num text pattern 1-10 из 100 -> [1, 10, 100] -> 100 / (10 - 1)
        total_pages = items_num[2] // (items_num[1] - items_num[0] + 1) + 1
        return total_pages if items_num[2] > 25 else 1

    def parse(self) -> None:
        self.logger.info(f"start parse banki.ru {self.source_type} {self.bank_site}")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_pages_num(bank)
            if total_page is None or total_page == 0:
                continue
            for i in range(start, total_page + 1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time)
                if reviews_list is None:
                    break
                if len(reviews_list) == 0:
                    break

                api.send_texts(
                    TextRequest(
                        items=reviews_list,
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info(f"finish parse {self.source_type} {self.bank_site}")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore

    def get_pages_num(self, bank: BankiRuBase) -> int | None:
        raise NotImplementedError

    def get_page_bank_reviews(self, bank: BankiRuBase, page_num: int, parsed_time: datetime) -> list[Text] | None:
        raise NotImplementedError

    def get_reviews_from_url(
        self, url: str, bank: BankiRuBase, parsed_time: datetime, params: dict[str, Any] | None = None
    ) -> list[Text]:
        if params is None:
            params = {}
        soup = get_page_from_url(url, params=params)
        if soup is None:
            return []
        texts = []
        for review in soup.find_all("article"):
            title_elem = review.find("a", class_="header-h3")
            title = title_elem.text
            link = "https://www.banki.ru" + title_elem["href"]
            text = review.find(
                "div",
                {"class": "responses__item__message markup-inside-small markup-inside-small--bullet", "data-full": ""},
            ).text.strip()
            date_elem = review.find("time", {"data-test": "responses-datetime"})
            comment_count = review.find("span", class_="responses__item__comment-count")
            text = Text(
                date=date_elem.text,
                title=title,
                text=text,
                link=link,
                comment_count=comment_count.text if comment_count else None,
                source_id=self.source.id,
                bank_id=bank.bank_id,
            )
            if text.date < parsed_time:
                continue
            texts.append(text)
        return texts
