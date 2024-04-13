import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query.bank import create_insurance_type


class InsuranceParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_ssd.xlsx"
    SKIP_ROWS = 2
    REG_NUM = "Рег. Номер"
    NAME = "Наименование субъекта страхового дела"
    TYPES = {REG_NUM: str}

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create_bank_type(self) -> BankType:
        return await create_insurance_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        df = df[[self.NAME, self.REG_NUM]].dropna()
        return [
            Bank(licence=row[self.REG_NUM], bank_name=row[self.NAME], bank_type_id=self.bank_type.id)
            for index, row in df.iterrows()
        ]
