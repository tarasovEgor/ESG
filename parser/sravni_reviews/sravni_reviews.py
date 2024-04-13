from typing import Any

from common import api
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuBankScheme


class SravniReviews(BaseSravniReviews):
    site: str = "sravni.ru"
    organization_type: str = "bank"

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/organizations")
        response_bank_list = self.request_bank_list()
        if response_bank_list is None:
            return None
        items = response_bank_list["items"]
        self.logger.info("finish download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        sravni_bank_list = []
        for item in items:
            sravni_bank = SravniRuBankScheme(
                sravni_id=item["_id"],
                sravni_old_id=item["oldId"],
                alias=item["alias"],
                bank_id=item["license"],
                bank_name=item["name"],
                bank_full_name=item["prepositionalName"],
                bank_official_name=item["fullName"],
            )
            if sravni_bank.bank_id in banks_id:
                sravni_bank_list.append(sravni_bank)
        banks_db = [SravniBankInfo.from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        return f"https://www.sravni.ru/bank/{bank_info.alias}/otzyvy/{review['id']}"
