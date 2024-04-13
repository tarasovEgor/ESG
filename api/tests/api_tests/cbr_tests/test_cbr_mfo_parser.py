import pytest

from app.dataloader import MFOParser
from app.query.bank import get_bank_count


class TestCBRMFOParser:
    @pytest.fixture(autouse=True)
    def get_cbr_page(self, session, get_cbr_mfo_file_mock):
        self.session = session
        self.cbr = MFOParser(session)

    async def test_load(self):
        await self.cbr.load_banks()
        assert await get_bank_count(self.session, self.cbr.bank_type.id) > 300
