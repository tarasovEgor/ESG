from datetime import datetime

import pytest
import requests_mock

from banki_ru.database import BankiRuBase
from banki_ru.news_parser import BankiNews
from tests.mixins import TestMixin


class TestBankiRuNews(TestMixin):
    bank = BankiRuBase(id=1, bank_name="test", bank_id=1, bank_code=12345678)

    @pytest.fixture
    def setup_test_reviews(
        self, mock_source, mock_get_source_by_id, mock_text, mock_banki_ru_banks_list, mock_bank_list
    ) -> requests_mock.Mocker:
        return mock_source

    @pytest.fixture
    def setup_bank_page(self, setup_test_reviews, mock_news_page, mock_news_page_lenta) -> requests_mock.Mocker:
        yield setup_test_reviews

    def test_page_num(self, setup_bank_page):
        bank_news = BankiNews()
        num = bank_news.get_pages_num(self.bank)
        assert num == 101  # https://www.banki.ru/banks/bank/alfabank/news/

    def test_get_news_links(self, setup_bank_page):
        bank_news = BankiNews()
        links = bank_news.get_news_links(self.bank, datetime.fromtimestamp(1), 1)
        assert len(links) == 55

    def test_news_from_links(self, setup_bank_page):
        bank_news = BankiNews()
        news = bank_news.news_from_links(
            self.bank, ["https://www.banki.ru/news/lenta/?id=10978151/", "https://www.banki.ru/news/lenta/?id=10978151"]
        )
        assert len(news) == 2
        assert len(news[0].text) > 0
        assert len(news[0].title) > 0
        assert news[0].link == "https://www.banki.ru/news/lenta/?id=10978151/"
        assert news[0].bank_id == 1

    def test_page_reviews(self, setup_bank_page):
        bank_news = BankiNews()
        bank_news.get_news_links = lambda a, b, c: ["https://www.banki.ru/news/lenta/?id=10978151/"] * 3
        reviews = bank_news.get_page_bank_reviews(self.bank, 1, datetime.fromtimestamp(1))
        assert len(reviews) == 3
        review = reviews[0]
        assert review.bank_id == self.bank.bank_id
        assert review.link == "https://www.banki.ru/news/lenta/?id=10978151/"
        assert review.date.date() == datetime(2022, 12, 30).date()
        assert review.comments_num is None
        assert review.source_id == 1
