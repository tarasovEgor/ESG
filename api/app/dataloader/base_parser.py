from typing import Any

import pandas as pd
from fastapi.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.bank import Bank, BankType
from app.query import bank as query
from app.utils import get_dataframe


class BaseParser:
    logger = logger
    bank_type: BankType
    URL = ""
    SKIP_ROWS = 0
    INDEX_COL = None
    TYPES: dict[str, Any] = {}

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def load_banks(self) -> None:
        self.bank_type = await self.create_bank_type()
        count = await query.get_bank_count(self.db, self.bank_type.id)
        if count == 0:
            await self.parse()
        self.logger.info(f"finish download {self.bank_type.name} list")

    async def create_bank_type(self) -> BankType:
        raise NotImplementedError

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        raise NotImplementedError

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        df = get_dataframe(self.URL, skip_rows=self.SKIP_ROWS, index_col=self.INDEX_COL, types=self.TYPES)
        if df is None:
            self.logger.error("cbr.ru 403 error")
            raise Exception("cbr.ru 403 error")
        banks = self.get_bank_list(df)
        await query.load_banks(self.db, banks)
