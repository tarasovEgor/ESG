from datetime import datetime

import pytest
import requests_mock

from banki_ru.database import BankiRuBase
from banki_ru.queries import get_bank_list
from banki_ru.reviews_parser import BankiReviews
from tests.mixins import TestMixin


class TestBankiRuReviews(TestMixin):
    bank = BankiRuBase(bank_id=1, bank_name="test", bank_code="unicreditbank")

    @pytest.fixture
    def setup_test_reviews(
        self, mock_source, mock_get_source_by_id, mock_text, mock_banki_ru_banks_list, mock_bank_list
    ) -> requests_mock.Mocker:
        return mock_source

    @pytest.fixture
    def setup_bank_page(self, setup_test_reviews, mock_bank_reviews_response) -> requests_mock.Mocker:
        yield setup_test_reviews

    @pytest.fixture
    def setup_bank_page_large_reviews(self, setup_test_reviews, bank_reviews_response) -> requests_mock.Mocker:
        v = bank_reviews_response[1]
        v["total"] = 4443
        setup_test_reviews.get(bank_reviews_response[0], status_code=200, json=v)
        yield setup_test_reviews

    @pytest.fixture
    def setup_reviews_difference_dates(self, setup_test_reviews, bank_reviews_response_freeze) -> requests_mock.Mocker:
        json = bank_reviews_response_freeze[1]
        json["data"][0]["dateCreate"] = datetime(2023, 1, 1).isoformat()
        json["data"][0]["title"] = "test"
        json["data"][0]["text"] = "test"
        json["data"][0]["commentCount"] = 1
        json["data"][0]["id"] = 1
        setup_test_reviews.get(bank_reviews_response_freeze[0], json=bank_reviews_response_freeze[1])
        yield setup_test_reviews

    def test_reviews(self, setup_test_reviews):
        banki_reviews = BankiReviews()
        assert len(get_bank_list(banki_reviews.bank_site)) == 3

    def test_bank_page_num(self, setup_bank_page_large_reviews):
        banki_reviews = BankiReviews()
        pages = banki_reviews.get_pages_num(self.bank)
        assert pages == 178

    def test_bank_page_reviews(self, setup_bank_page):
        banki_reviews = BankiReviews()
        reviews = banki_reviews.get_page_bank_reviews(self.bank, page_num=1, parsed_time=datetime.fromtimestamp(1))
        assert len(reviews) == 25

    def test_bank_page_reviews_diff_dates(self, setup_reviews_difference_dates):
        banki_reviews = BankiReviews()
        reviews = banki_reviews.get_page_bank_reviews(self.bank, page_num=1, parsed_time=datetime(2022, 1, 1))
        assert len(reviews) == 1
        review = reviews[0]
        assert review.bank_id == self.bank.bank_id
        assert review.text == "test"
        assert review.title == "test"
        assert review.link == "https://www.banki.ru/services/responses/bank/response/1"
        assert review.date == datetime(2023, 1, 1)
        assert review.source_id == 1
        assert review.comments_num == 1

    def test_parse(self, setup_bank_page):
        banki_reviews = BankiReviews()
        banki_reviews.get_pages_num = lambda x: 1
        banki_reviews.parse()
        text_post = [x for x in setup_bank_page.request_history if x.method == "POST" and x.path == "/text/"][0]
        request_json = text_post.json()
        assert len(request_json["items"]) == 25
