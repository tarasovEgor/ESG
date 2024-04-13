from typing import Any

from common import api
from common.schemes import ApiMfo
from sravni_reviews.base_parser import BaseSravniReviews
from sravni_reviews.database import SravniBankInfo
from sravni_reviews.queries import create_banks
from sravni_reviews.schemes import SravniRuMfoScheme


def bank_exists(mfo: SravniRuMfoScheme, existing_mfos: list[ApiMfo]) -> int | None:
    for existing_bank in existing_mfos:
        if existing_bank.licence == mfo.bank_id or existing_bank.ogrn == mfo.bank_ogrn:
            return existing_bank.id
    return None


class SravniMfoReviews(BaseSravniReviews):
    site: str = "sravni.ru/mfo"
    organization_type = "mfo"
    tag = "microcredits"

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        sravni_mfo_json_full = self.request_bank_list()
        if sravni_mfo_json_full is None:
            return None
        sravni_mfo_json = sravni_mfo_json_full["items"]
        self.logger.info("finish download bank list")
        existing_mfos = api.get_mfo_list()
        sravni_bank_list = []
        for sravni_mfo in sravni_mfo_json:
            mfo = SravniRuMfoScheme(
                sravni_id=sravni_mfo["id"],
                alias=sravni_mfo["alias"],
                bank_id=sravni_mfo["license"],
                bank_name=sravni_mfo["name"],
                bank_full_name=sravni_mfo["fullName"],
                bank_official_name=sravni_mfo["genitiveName"],
                bank_ogrn=sravni_mfo["requisites"]["ogrn"],
            )
            if (existing_mfo_id := bank_exists(mfo, existing_mfos)) is not None:
                mfo.bank_id = existing_mfo_id
                sravni_bank_list.append(mfo)
        banks_db = [SravniBankInfo.from_pydantic(bank) for bank in sravni_bank_list]
        create_banks(banks_db)
        self.logger.info("create table for sravni banks")

    def get_review_link(self, bank_info: SravniBankInfo, review: dict[str, Any]) -> str:
        return f"https://www.sravni.ru/zaimy/{bank_info.alias}/otzyvy/{review['id']}"
