from datetime import datetime

import pytest
import requests_mock

from tests.mixins import TestMixin
from vk_parser.bank_parser import VKBankParser
from vk_parser.database import VkBank
from vk_parser.queries import get_bank_list
from vk_parser.schemes import VKType


class TestVKParser(TestMixin):
    bank = VkBank(id=100, name="test", vk_id=1, domain="test")

    @pytest.fixture
    def setup_test_reviews(self, mock_source, mock_get_source_by_id, mock_text, mock_bank_list) -> requests_mock.Mocker:
        return mock_source

    @pytest.fixture
    def setup_bank_page(self, setup_test_reviews, mock_post_comments, mock_wall) -> requests_mock.Mocker:
        yield setup_test_reviews

    def test_get_bank_reviews(self, setup_test_reviews):
        VKBankParser()
        assert len(get_bank_list(VKType.bank)) == 156

    def test_json_to_comment(self, setup_test_reviews):
        parser = VKBankParser()
        comment = {
            "id": 2132706,
            "from_id": 258041371,
            "date": 1673447440,
            "text": "Ну оооочень приятный процент по [123|кредиту]!☠️😂",
            "post_id": 2132702,
            "owner_id": -22522055,
            "thread": {
                "count": 2,
                "items": [],
            },
        }

        text = parser.json_to_comment_text(self.bank.domain, comment, self.bank.id)
        assert text.text == "Ну оооочень приятный процент по кредиту!"
        assert (
            text.link
            == f"https://vk.com/{self.bank.domain}?w=wall{comment['owner_id']}_{comment['post_id']}_r{comment['id']}"
        )

    def test_json_to_comment_thread(self, setup_test_reviews):
        parser = VKBankParser()
        comment = {
            "id": 2132706,
            "from_id": 258041371,
            "date": 1673447440,
            "text": "Ну оооочень приятный процент по [123|кредиту]!☠️😂",
            "post_id": 2132702,
            "owner_id": -22522055,
            "parents_stack": {0: 123},
            "thread": {
                "count": 2,
                "items": [],
            },
        }

        text = parser.json_to_comment_text(self.bank.domain, comment, self.bank.id, is_thread=True)
        assert text.text == "Ну оооочень приятный процент по кредиту!"
        assert (
            text.link
            == f"https://vk.com/wall{comment['owner_id']}_{comment['post_id']}?reply={comment['id']}&thread={comment['parents_stack'][0]}"
        )
        assert text.date == datetime.fromtimestamp(comment["date"])
        assert text.comments_num is None
        assert text.bank_id == self.bank.id

    def test_get_post_comment(self, setup_bank_page):
        parser = VKBankParser()
        texts = parser.get_post_comments(self.bank.domain, "123", "2132702", 1, self.bank.id)
        assert len(texts) == 6

    def test_parse(self, setup_bank_page):
        parser = VKBankParser()
        parser.bank_list = [self.bank]
        parser.parse()

        text_post = [x for x in setup_bank_page.request_history if x.method == "POST" and x.path == "/text/"][0]
        request_json = text_post.json()
        assert len(request_json["items"]) == 2
