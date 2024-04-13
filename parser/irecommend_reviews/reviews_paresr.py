import json
import os
from datetime import datetime
from time import sleep

import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException

from common import api
from common.base_parser import BaseParser
from common.schemes import PatchSource, Source, SourceRequest, Text, TextRequest
from irecommend_reviews.database import IRecommend
from irecommend_reviews.queries import create_banks, get_bank_list
from irecommend_reviews.schemes import IRecommendItem
from utils import get_browser, relative_path


# noinspection PyMethodMayBeStatic
class IRecommendReviews(BaseParser):
    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        self.source = self.create_source()
        if len(self.bank_list) < 90:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def create_source(self) -> Source:
        source_create = SourceRequest(site="irecommend.ru", source_type="reviews")
        return api.send_source(source_create)

    def load_bank_list(self) -> None:
        path = relative_path(os.path.dirname(__file__), "irecommend.npy")
        if not os.path.exists(path):
            raise FileNotFoundError("irecommend.npy not found")
        bank_arr = np.load(path, allow_pickle=True)
        db_banks = [IRecommend(bank_id=bank[0], name=bank[1], domain=bank[2]) for bank in bank_arr]
        create_banks(db_banks)
        self.logger.info("bank list loaded")

    def setup_browser(self) -> webdriver.Firefox | webdriver.Remote:
        browser = get_browser()
        _ = self.get_page("https://irecommend.ru", browser)
        browser.add_cookie({"name": "ss_uid", "value": "16657360693968717"})
        browser.add_cookie(
            {
                "name": "stats_u_a",
                "value": "2FwvdtyzJLp9avMj9v1UDmg%2FFm0UI%2FXBW%2FsyM1AaEAw3T%2B4TNNXo5lfkEHoCwRfjzJGxf%2B8kFi7JSYfhs9N1Y7fNh6VCLOvq",
            }
        )
        browser.add_cookie({"name": "ab_var", "value": "7"})
        browser.add_cookie(
            {"name": "stats_s_a", "value": "xFaamZkIWvN9rPje0Yyp%2FQ3JHeijRMZodVCSo0G%2FXRxy9IMakAA1QAIUJJmDZ1qw"}
        )
        browser.add_cookie({"name": "statsactivity", "value": "36"})
        browser.add_cookie({"name": "statstimer", "value": "486"})
        browser.add_cookie({"name": "v", "value": "63"})
        browser.add_cookie({"name": "ss_hid", "value": "31135198"})
        return browser

    def get_page(self, url: str, browser: webdriver.Firefox | webdriver.Remote) -> BeautifulSoup | None:
        try:
            browser.get(url)
        except TimeoutException:
            pass
        try:
            page = BeautifulSoup(browser.page_source, "html.parser")
        except WebDriverException:
            self.logger.warning(f"page {url} not found")
            return None
        if page.find("h1", class_="not-found-title") is not None:
            self.logger.error(f"page {url} not found")
            return None
        return page

    def get_pages_num(self, bank: IRecommendItem, browser: webdriver.Firefox | webdriver.Remote) -> int:
        page = self.get_page(bank.domain + "?new=1", browser)
        if page is None:
            return 0
        pages = 1
        if page.find("ul", {"class": "pager"}) is not None:
            pages = int(page.find("ul", {"class": "pager"}).find("li", {"class": "pager-last"}).text)  # type: ignore
        return pages

    def get_review(
        self, review_url: str, bank: IRecommendItem, browser: webdriver.Firefox | webdriver.Remote
    ) -> Text | None:
        page = self.get_page(review_url, browser)
        if page is None or page.find("meta", {"itemprop": "datePublished"}) is None:
            self.logger.warning(f"review {review_url} not found")
            return None
        date = page.find("meta", {"itemprop": "datePublished"})["content"]  # type: ignore

        text = page.find("div", {"class": "description hasinlineimage", "itemprop": "reviewBody"}).text  # type: ignore
        title = page.find("h2", class_="reviewTitle").text  # type: ignore
        return Text(
            source_id=self.source.id,
            bank_id=bank.bank_id,
            title=title,
            text=text,
            date=date,
            link=review_url,
        )

    def get_page_bank_reviews(
        self, bank: IRecommendItem, i: int, parsed_time: datetime, browser: webdriver.Firefox | webdriver.Remote
    ) -> list[Text] | None:
        page = self.get_page(f"{bank.domain}?new=1&page={i}", browser)
        if page is None:
            return None
        reviews_urls = []
        if page.find("div", id="block-quicktabs-3") is not None:
            for elem in page.find("div", id="block-quicktabs-3").findAll("div", {"class": "reviewTextSnippet"}):  # type: ignore
                reviews_urls.append("https://irecommend.ru" + elem.find("a", recursive=False)["href"])
        elif page.find("h1", class_="not-found-title") is not None:
            return None
        texts = []
        for i, review_url in enumerate(reviews_urls):
            self.logger.debug(f"parsing review {review_url} [{i + 1}/{len(reviews_urls)}]")
            text = self.get_review(review_url, bank, browser)
            if text is None:
                continue
            if text.date.replace(tzinfo=None) < parsed_time:
                break
            texts.append(text)
            sleep(2)
        return texts

    def parse(self) -> None:
        self.logger.info("start parse irecommend reviews")
        start_time = datetime.now()
        browser = self.setup_browser()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank_pydantic in enumerate(self.bank_list):
            bank = IRecommendItem.from_orm(bank_pydantic)
            self.logger.info(f"[{bank_index + 1}/{len(self.bank_list)}] Start parse bank {bank.name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 0
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_pages_num(bank, browser)
            for i in range(start, total_page):
                self.logger.info(f"[{i}/{total_page-1}] start parse {bank.name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time, browser)
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

        self.logger.info("finish parse bank reviews")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore
        browser.close()
