import pytest

from app.dataloader.bank_parser import BankParser
from app.query.bank import get_bank_count


class TestCBRParser:
    @pytest.fixture(autouse=True)
    def get_cbr_page(self, session, get_cbr_bank_page_mock, get_cbr_bank_file_mock):
        self.session = session
        self.cbr = BankParser(session)

    async def test_get_dataframe_url(self, get_cbr_bank_page):
        _, page = get_cbr_bank_page
        assert (
            self.cbr.get_dataframe_url(page).split("?")[0]
            == "https://www.cbr.ru/Queries/UniDbQuery/DownloadExcel/98547"
        )

    async def test_get_page(self):
        await self.cbr.load_banks()
        assert await get_bank_count(self.session, self.cbr.bank_type.id) > 300
