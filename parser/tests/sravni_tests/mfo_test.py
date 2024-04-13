from datetime import datetime

import pytest
import requests_mock

from sravni_reviews.database import SravniBankInfo
from sravni_reviews.mfo_parser import SravniMfoReviews
from sravni_reviews.queries import get_bank_list
from tests.mixins import TestMixin


class TestSravniMfo(TestMixin):
    mfo = SravniBankInfo(
        bank_id=1,
        sravni_id=1,
        sravni_old_id=1,
        alias="test",
        bank_name="test",
        bank_full_name="test",
        bank_official_name="test",
    )

    @pytest.fixture
    def setup_test_reviews(self, mock_source, mock_get_source_by_id, mock_text, mock_mfo_list) -> requests_mock.Mocker:
        return mock_source

    @pytest.fixture
    def setup_bank_page(
        self, setup_test_reviews, mock_sravni_mfo_list, mock_sravni_mfo_reviews_response
    ) -> requests_mock.Mocker:
        yield setup_test_reviews

    def test_reviews(self, setup_bank_page):
        SravniMfoReviews()
        assert len(get_bank_list()) == 3

    def test_bank_page_reviews(self, setup_bank_page):
        banki_reviews = SravniMfoReviews()
        reviews = banki_reviews.get_reviews(parsed_time=datetime.fromtimestamp(1), bank_info=self.mfo)
        assert len(reviews) == 10
        review = reviews[0]
        assert review.bank_id == 1
        assert review.source_id == 1
        assert review.link == "https://www.sravni.ru/zaimy/test/otzyvy/1"
        assert review.date == datetime(2023, 1, 1)
        assert review.title == "test"
        assert review.text == "test"
        assert review.comments_num == 1

    def test_parse(self, setup_bank_page):
        banki_reviews = SravniMfoReviews()
        banki_reviews.parse()
        text_post = [x for x in setup_bank_page.request_history if x.method == "POST" and x.path == "/text/"][0]
        request_json = text_post.json()
        assert len(request_json["items"]) == 10
