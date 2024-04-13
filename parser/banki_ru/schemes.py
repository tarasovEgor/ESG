import re
from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic.class_validators import validator


class BankiRuBaseScheme(BaseModel):
    bank_id: int
    bank_name: str
    bank_code: str

    class Config:
        orm_mode = True


class BankiRuBankScheme(BankiRuBaseScheme):
    @validator("bank_id", pre=True)
    def bank_id_validator(cls, v: str) -> int:
        if v == "—" or v == "" or v == "-":
            return -1
        license_id_str = v.split("-")[0]
        if license_id_str.isnumeric():
            return int(license_id_str)
        else:
            return int(license_id_str.split()[0])


class BankiRuBrokerScheme(BankiRuBaseScheme):
    @validator("bank_id", pre=True)
    def bank_id_validator(cls, v: str | None) -> int:
        if v is None:
            return -1
        broker_license_unparsed = re.sub("-", "", v)
        broker_license_arr = re.findall("\\d{8}100000|\\d{8}300000", broker_license_unparsed)
        if len(broker_license_arr) == 0:
            return -1
        return int(broker_license_arr[0])

    @validator("bank_code", pre=True)
    def bank_code_validator(cls, v: str) -> str:
        return v.split("/")[-2]


class BankiRuInsuranceScheme(BankiRuBaseScheme):
    @validator("bank_id", pre=True)
    def bank_id_validator(cls, v: Any) -> int:
        arr = re.findall("(?<=№\\s)\\d+(?=\\s)", v)
        if len(arr) == 1:
            return int(arr[0])
        return -1


class BankiRuMfoScheme(BankiRuBaseScheme):
    bank_ogrn: int

    def __hash__(self) -> int:
        return hash(self.bank_id) + hash(self.bank_ogrn) + hash(self.bank_code) + hash(self.bank_name)

    @validator("bank_id", pre=True)
    def license_validator(cls, v: str) -> int:
        if v.isnumeric():
            return int(v)
        return -1

    class Config:
        orm_mode = True


class BankTypes(str, Enum):
    bank = "banki.ru"
    news = "banki.ru/news"
    insurance = "banki.ru/insurance"
    mfo = "banki.ru/mfo"
    broker = "banki.ru/broker"
