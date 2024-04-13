import json

import pandas as pd

from app.database.models.bank import Bank, BankType
from app.dataloader.base_parser import BaseParser
from app.query import bank as query
from app.query.bank import create_mfo_type
from app.utils import send_get


class MFOParser(BaseParser):
    URL = "https://www.cbr.ru/vfs/finmarkets/files/supervision/list_MFO.xlsx"
    SHEETS = {
        "Действующие": {"skiprows": 4, "index_col": 0},
        "Исключенные": {"skiprows": 2, "index_col": 0},
    }
    TYPES = {
        "Регистрационный номер записи": str,
        "Unnamed: 2": str,
        "Unnamed: 3": str,
        "Unnamed: 4": str,
        "Unnamed: 5": str,
    }  # TYPES for register number, because if contains leading zeros

    async def create_bank_type(self) -> BankType:
        return await create_mfo_type(self.db)

    def get_bank_list(self, df: pd.DataFrame) -> list[Bank]:
        self.logger.info("start parse broker list")
        df["Регистрационный номер записи"] = df["Регистрационный номер записи"].fillna("0")
        df["licence"] = (
            df["Регистрационный номер записи"]
            + df["Unnamed: 2"]
            + df["Unnamed: 3"]
            + df["Unnamed: 4"]
            + df["Unnamed: 5"]
        )
        return [
            Bank(
                licence=row["licence"],
                bank_name=row["Полное наименование"],
                bank_type_id=self.bank_type.id,
                description=json.dumps(
                    {
                        "ogrn": row["Основной государственный регистрационный номер"],
                        # some sites may not contain licence or several companies may have one licence
                        "short_name": row["Сокращенное наименование"],
                    }
                ),
            )
            for index, row in df.iterrows()
        ]

    async def parse(self) -> None:
        self.logger.info("start download bank list")
        response = send_get(self.URL)
        if response is None:
            self.logger.error("Download failed")
            raise Exception("Download failed")
        excel_file = pd.ExcelFile(response.content)
        if not any(sheet in excel_file.sheet_names for sheet in self.SHEETS):
            self.logger.error("Sheets not found")
            raise Exception("Sheets not found")

        for sheet, settings in self.SHEETS.items():
            df = excel_file.parse(sheet, dtype=self.TYPES, **settings)
            banks = self.get_bank_list(df)
            await query.load_banks(self.db, banks)
