import pandas as pd

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query.bank import create_broker_type


class BrokerParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_brokers.xlsx"
    SKIP_ROWS = 3

    async def create_bank_type(self) -> BankType:
        return await create_broker_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        df["licence"] = df["№ лицензии"].str.replace("-", "")
        return [
            Bank(licence=row["licence"], bank_name=row["Наименование организации"], bank_type_id=self.bank_type.id)
            for index, row in df.iterrows()
        ]
