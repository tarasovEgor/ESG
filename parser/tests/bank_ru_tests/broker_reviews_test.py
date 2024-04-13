from datetime import datetime

import pytest

from banki_ru.broker_parser import BankiBroker
from banki_ru.database import BankiRuBase
from banki_ru.queries import get_bank_list
from tests.mixins import TestMixin


class TestBankiRuBroker(TestMixin):
    broker = BankiRuBase(id=1, bank_name="test", bank_id=1, bank_code=12345678)

    @pytest.fixture
    def setup_test_reviews(self, mock_source, mock_get_source_by_id, mock_text, mock_broker_list):
        return mock_source

    @pytest.fixture
    def setup_broker_page_with_header(self, setup_test_reviews, mock_banki_ru_brokers_license, mock_broker_page):
        yield setup_test_reviews

    def test_bank_list(self, setup_broker_page_with_header):
        broker_reviews = BankiBroker()
        assert len(get_bank_list(broker_reviews.bank_site)) == 3

    def test_page_num(self, setup_broker_page_with_header):
        broker_reviews = BankiBroker()
        num = broker_reviews.get_pages_num(self.broker)
        assert num == 14  # check page num https://www.banki.ru/investment/responses/company/broker/alfa-direkt/

    def test_page_reviews(self, setup_broker_page_with_header):
        broker_reviews = BankiBroker()
        reviews = broker_reviews.get_page_bank_reviews(self.broker, 1, datetime.fromtimestamp(1))
        assert len(reviews) == 25
        review = reviews[0]
        assert review.bank_id == self.broker.bank_id
        assert review.link == "https://www.banki.ru/investment/responses/company/response/29144/"
        assert review.date.date() == datetime(2023, 1, 4).date()
        assert review.comments_num is None
        assert review.source_id == 1
