from datetime import datetime

from banki_ru.banki_base_parser import BankiBase, bank_exists
from banki_ru.database import BankiRuBase, BankiRuBroker
from banki_ru.queries import create_banks
from banki_ru.schemes import BankiRuBrokerScheme, BankTypes
from common import api
from common.requests_ import get_json_from_url
from common.schemes import SourceTypes, Text


class BankiBroker(BankiBase):
    bank_site = BankTypes.broker
    source_type = SourceTypes.reviews

    def get_broker_licence_from_url(self, url: str) -> str | None:
        broker_json = get_json_from_url(url)
        if broker_json is None or "data" not in broker_json.keys():
            return None
        broker_license_str: str = broker_json["data"]["broker"]["licence"]
        return broker_license_str

    def load_bank_list(self) -> None:
        self.logger.info("start download bank list")
        existing_brokers = api.get_broker_list()
        brokers_json: list[dict[str, str]] = get_json_from_url("https://www.banki.ru/investment/brokers/list/")  # type: ignore
        if brokers_json is None:
            return None
        brokers = []
        for i, broker in enumerate(brokers_json):
            name_arr = broker["name"].split()
            if len(name_arr) == 0 or name_arr[0] == "Заявка":
                # remove Заявка на консультацию по инвестициям
                continue
            broker_scheme = BankiRuBrokerScheme(
                bank_name=broker["name"],
                bank_code=broker["url"],
                bank_id=broker["license"],
            )

            if bank_exists(broker_scheme, existing_brokers):
                brokers.append(broker_scheme)
        self.logger.info("finish download broker list")
        banks_db: list[BankiRuBase] = [BankiRuBroker.from_pydantic(bank) for bank in brokers]
        create_banks(banks_db)

    def get_page_bank_reviews(self, bank: BankiRuBase, page_num: int, parsed_time: datetime) -> list[Text] | None:
        url = f"https://www.banki.ru/investment/responses/company/broker/{bank.bank_code}/"
        texts = self.get_reviews_from_url(url, bank, parsed_time, params={"page": page_num, "isMobile": 0})
        return texts

    def get_pages_num(self, bank: BankiRuBase) -> int | None:
        params = {"page": 1, "isMobile": 0}
        total_pages = self.get_pages_num_html(
            f"https://www.banki.ru/investment/responses/company/broker/{bank.bank_code}/", params=params
        )
        return total_pages
