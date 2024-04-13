from datetime import date
from enum import Enum  # TODO in python 3.11 replace with StrEnum

from pydantic import BaseModel


class IndexTypeVal(str, Enum):
    index_base = "index_base"
    index_mean = "index_mean"
    index_std = "index_std"
    index_safe = "index_safe"


class SentenceCountAggregate(str, Enum):
    month = "month"
    quarter = "quarter"


class AggregateTextResultItem(BaseModel):
    year: int
    quarter: int
    date: date
    bank_name: str
    bank_id: int
    model_name: str
    source_type: str
    index: float | None
    index_10_percentile: float | None
    index_90_percentile: float | None

    def __repr__(self) -> str:
        return (
            f"AggregateTextResultItem(year={self.year}, quarter={self.quarter}, bank_name={self.bank_name},"
            f" model_name={self.model_name}, source_type={self.source_type}, index={self.index})"
        )


class AggregateTetResultResponse(BaseModel):
    items: list[AggregateTextResultItem]


class ReviewsCountItem(BaseModel):
    date: date
    source_site: str
    source_type: str
    count: int


class ReviewsCountResponse(BaseModel):
    items: list[ReviewsCountItem]
