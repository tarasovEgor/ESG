from datetime import datetime

import pytest

from banki_ru.database import BankiRuBase
from banki_ru.mfo_parser import BankiMfo
from banki_ru.queries import get_bank_list
from tests.mixins import TestMixin


class TestBankiRuMfo(TestMixin):
    mfo = BankiRuBase(id=1, bank_name="test", bank_id=1, bank_code=12345678)

    @pytest.fixture
    def setup_test_reviews(self, mock_source, mock_get_source_by_id, mock_text, mock_mfo_list):
        return mock_source

    @pytest.fixture
    def setup_insurance_page_with_header(self, setup_test_reviews, mock_banki_ru_mfo_list, mock_mfo_page):
        yield setup_test_reviews

    def test_load_bank(self, setup_insurance_page_with_header):
        mfo_reviews = BankiMfo()
        assert len(get_bank_list(mfo_reviews.bank_site)) == 3

    def test_page_num(self, setup_insurance_page_with_header):
        mfo_reviews = BankiMfo()
        num = mfo_reviews.get_pages_num(self.mfo)
        assert num == 3  # check page num bistrodengi

    def test_page_reviews(self, setup_insurance_page_with_header):
        mfo_reviews = BankiMfo()
        reviews = mfo_reviews.get_page_bank_reviews(self.mfo, 1, datetime.fromtimestamp(1))
        assert len(reviews) == 10
        review = reviews[0]
        assert review.bank_id == self.mfo.bank_id
        assert review.link == "https://www.banki.ru/microloans/responses/response/1/"
        assert review.date == datetime(2023, 1, 1)
        assert review.comments_num == 1
        assert review.source_id == 1
