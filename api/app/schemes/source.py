from datetime import datetime
from enum import Enum  # TODO in python 3.11 replace with StrEnum

from pydantic import BaseModel


class SourceTypesEnum(str, Enum):
    reviews = "reviews"
    news = "news"
    vk = "vk.com"


class SourceSitesEnum(str, Enum):
    banki_ru_reviews = "banki.ru"
    banki_ru_brokers = "banki.ru/broker"
    banki_ru_news = "banki.ru/news"
    banki_ru_insurance = "banki.ru/insurance"
    banki_ru_mfo = "banki.ru/mfo"
    irecommend = "irecommend.ru"
    sravni_ru = "sravni.ru"
    sravni_mfo = "sravni.ru/mfo"
    sravni_insurance = "sravni.ru/insurance"
    vk_comments = "vk.com/comments"
    vk_other = "vk.com/other"


class SourceModel(BaseModel):
    id: int
    site: str
    source_type_id: int
    parser_state: str | None
    last_update: datetime | None

    class Config:
        orm_mode = True


class GetSourceItemModel(SourceModel):
    source_type: str


class GetSource(BaseModel):
    items: list[SourceModel]


class CreateSource(BaseModel):
    site: str
    source_type: str


class PostSourceResponse(BaseModel):
    source_id: int


class SourceTypesModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetSourceTypes(BaseModel):
    items: list[SourceTypesModel]


class PatchSource(BaseModel):
    parser_state: str | None
    last_update: datetime | None
