import re
from datetime import datetime

from banki_ru.banki_base_parser import BankiBase, bank_exists
from banki_ru.database import BankiRuBase, BankiRuInsurance
from banki_ru.queries import create_banks
from banki_ru.requests_ import get_page_from_url
from banki_ru.schemes import BankiRuInsuranceScheme, BankTypes
from common import api
from common.schemes import SourceTypes, Text


class BankiInsurance(BankiBase):
    bank_site = BankTypes.insurance
    source_type = SourceTypes.reviews
    url = "https://www.banki.ru/insurance/responses/company/"

    def __init__(self) -> None:
        super().__init__()

    def get_pages_num_insurance_list(self, url: str) -> int:
        page = get_page_from_url(url)
        if page is None:
            return 0
        total_page_elem = page.find("div", {"data-module": "ui.pagination"})
        if total_page_elem is None or total_page_elem["data-options"] is None:  # type: ignore[index]
            return 1
        # currentPageNumber: 1; itemsPerPage: 15; totalItems: 157; title: Страховых компаний
        total_page = int(re.search("(?<=totalItems:\\s)\\d+(?=;)", total_page_elem["data-options"]).group())  # type: ignore
        per_page = int(re.search("(?<=itemsPerPage:\\s)\\d+(?=;)", total_page_elem["data-options"]).group())  # type: ignore
        return total_page // per_page + 1

    def load_bank_list(self) -> None:
        insurances = []
        # TODO change to https://www.banki.ru/insurance/company/list/
        existing_insurances = api.get_insurance_list()
        url = "https://www.banki.ru/insurance/companies/"
        total_pages = self.get_pages_num_insurance_list(url)
        for pages in range(1, total_pages + 1):
            soup = get_page_from_url(url, params={"page": pages})
            if soup is None:
                raise Exception("Can't get page")
            for row in soup.find_all("tr", {"data-test": "list-row"}):
                bank_text_url = row.find("a", class_="widget__link")
                license_text = row.find(
                    "div",
                    class_=(
                        "inline-elements inline-elements--x-small font-size-small color-gray-blue margin-top-xx-small"
                    ),
                )
                insurance = BankiRuInsuranceScheme(
                    bank_id=license_text.text,
                    bank_name=bank_text_url.text,
                    bank_code=bank_text_url["href"].split("/")[-2],
                )
                if bank_exists(insurance, existing_insurances):
                    insurances.append(BankiRuInsurance.from_pydantic(insurance))
        self.logger.info("finish download bank list")
        create_banks(insurances)  # type: ignore[arg-type]

    def get_pages_num(self, bank: BankiRuBase) -> int | None:
        url = f"{self.url}{bank.bank_code}"
        return self.get_pages_num_html(url)

    def get_page_bank_reviews(self, bank: BankiRuBase, page_num: int, parsed_time: datetime) -> list[Text] | None:
        url = f"{self.url}{bank.bank_code}"
        texts = self.get_reviews_from_url(url, bank, parsed_time, params={"page": page_num, "isMobile": 0})
        return texts
