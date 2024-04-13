from dataclasses import dataclass
from enum import Enum


class ModelType(str, Enum):
    mdf = "mdf"
    mdf_adjusted = "mdf_adjusted"
    mdf_combined = "mdf_combined"


@dataclass(frozen=True)
class Sentence:
    id: int
    sentence: str


@dataclass(frozen=True)
class ResultSentence:
    sentence_id: int
    result: tuple[float, float]
