import pytest

from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks, get_bank_list
from tests.mixins import TestMixin


class TestSravniQueries(TestMixin):
    def test_create_banks(self):
        bank = SravniBankInfo(
            id=1,
            bank_id=1,
            sravni_id="test",
            sravni_old_id=1,
            alias="test",
            bank_name="test",
            bank_full_name="test",
            bank_official_name="test",
        )
        bank_2 = SravniBankInfo(
            id=2,
            bank_id=2,
            sravni_id="test",
            sravni_old_id=2,
            alias="test",
            bank_name="test",
            bank_full_name="test",
            bank_official_name="test",
        )

        create_banks([bank, bank_2])
        assert self.session.query(SravniBankInfo).count() == 2

    @pytest.fixture
    def setup_bank(self):
        self.test_create_banks()

    def test_get_bank_list(self, setup_bank):
        bank_list = get_bank_list()
        assert len(bank_list) == 2
        bank = bank_list[0]
        assert type(bank) == SravniBankInfo
        assert bank.bank_id == 1
        assert bank.sravni_id == "test"
        assert bank.sravni_old_id == 1
        assert bank.alias == "test"
        assert bank.bank_name == "test"
        assert bank.bank_full_name == "test"
        assert bank.bank_official_name == "test"
        assert bank.id == 1
