import pytest

from tests.mixins import TestMixin
from vk_parser.database import VkBank, VkOtherIndustries
from vk_parser.queries import create_banks, get_bank_list
from vk_parser.schemes import VKType


class TestVKQueries(TestMixin):
    def test_create_banks(self):
        bank = VkBank(vk_id=1, name="test", domain="test")
        bank_2 = VkOtherIndustries(real_id=1, vk_id=1, name="test", domain="test")

        create_banks([bank, bank_2])
        assert self.session.query(VkBank).count() == 1
        assert self.session.query(VkOtherIndustries).count() == 1

    @pytest.fixture
    def setup_bank(self):
        self.test_create_banks()

    def test_get_vk_banki(self, setup_bank):
        bank_list = get_bank_list(VKType.bank)
        assert len(bank_list) == 1
        bank = bank_list[0]
        assert type(bank) == VkBank
        assert bank.vk_id == 1
        assert bank.name == "test"
        assert bank.domain == "test"
        assert bank.id == 1

    def test_get_vk_other(self, setup_bank):
        bank_list = get_bank_list(VKType.other)
        assert len(bank_list) == 1
        bank = bank_list[0]
        assert type(bank) == VkOtherIndustries
        assert bank.vk_id == 1
        assert bank.name == "test"
        assert bank.domain == "test"
