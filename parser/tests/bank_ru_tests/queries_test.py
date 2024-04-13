import pytest

from banki_ru.database import BankiRuBank, BankiRuBroker, BankiRuInsurance, BankiRuMfo
from banki_ru.queries import create_banks, get_bank_list
from banki_ru.schemes import BankTypes
from tests.mixins import TestMixin


class TestBankiRuQueries(TestMixin):
    def test_create_banks(self):
        bank = BankiRuBank(bank_id=1, bank_name="test", bank_code="test")
        broker = BankiRuBroker(bank_id=1, bank_name="test", bank_code="test")
        insurance = BankiRuInsurance(bank_id=1, bank_name="test", bank_code="test")
        mfo = BankiRuMfo(bank_id=1, bank_name="test", bank_code="test")

        create_banks([bank, broker, insurance, mfo])
        assert self.session.query(BankiRuBank).count() == 1
        assert self.session.query(BankiRuBroker).count() == 1
        assert self.session.query(BankiRuInsurance).count() == 1
        assert self.session.query(BankiRuMfo).count() == 1

    @pytest.fixture
    def setup_bank(self):
        self.test_create_banks()

    def test_get_bank_list(self, setup_bank):
        bank_list = get_bank_list(BankTypes.bank)
        assert len(bank_list) == 1
        assert type(bank_list[0]) == BankiRuBank
        assert bank_list[0].bank_id == 1
        assert bank_list[0].bank_name == "test"
        assert bank_list[0].bank_code == "test"

    def test_get_broker_list(self, setup_bank):
        broker_list = get_bank_list(BankTypes.broker)
        assert len(broker_list) == 1
        assert type(broker_list[0]) == BankiRuBroker
        assert broker_list[0].bank_id == 1
        assert broker_list[0].bank_name == "test"
        assert broker_list[0].bank_code == "test"

    def test_get_insurance_list(self, setup_bank):
        insurance_list = get_bank_list(BankTypes.insurance)
        assert len(insurance_list) == 1
        assert type(insurance_list[0]) == BankiRuInsurance
        assert insurance_list[0].bank_id == 1
        assert insurance_list[0].bank_name == "test"
        assert insurance_list[0].bank_code == "test"

    def test_get_mfo_list(self, setup_bank):
        mfo_list = get_bank_list(BankTypes.mfo)
        assert len(mfo_list) == 1
        assert type(mfo_list[0]) == BankiRuMfo
        assert mfo_list[0].bank_id == 1
        assert mfo_list[0].bank_name == "test"
        assert mfo_list[0].bank_code == "test"
