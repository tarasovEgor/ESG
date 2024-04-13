from datetime import datetime

from pydantic import BaseModel, Field


class TextItem(BaseModel):
    source_id: int
    date: datetime
    title: str
    text: str
    bank_id: int
    link: str
    comments_num: int | None = None


class TextModel(BaseModel):
    id: int
    link: str
    source: str
    date: datetime
    title: str
    bank_id: int
    source_id: int
    comments_num: int | None = None

    class Config:
        orm_mode = True


class TextResultModel(BaseModel):
    id: int
    text_sentence_id: int
    model_id: int
    result: list[float]

    class Config:
        orm_mode = True


class TextSentenceModel(BaseModel):
    id: int
    text_id: int
    sentence: str
    sentence_num: int

    class Config:
        orm_mode = True


class PostTextItem(BaseModel):
    items: list[TextItem]
    parser_state: str | None
    date: datetime | None


class GetTextSentencesItem(BaseModel):
    id: int = Field(..., alias="sentence_id")
    sentence: str


class GetTextSentences(BaseModel):
    items: list[GetTextSentencesItem]


class GetTextResultItem(BaseModel):
    id: int
    text_sentence_id: int
    result: list[float]
    model_id: int


class GetTextResult(BaseModel):
    items: list[GetTextResultItem]


class PostTextResultItem(BaseModel):
    text_result: list[float]
    model_id: int
    text_sentence_id: int


class PostTextResult(BaseModel):
    items: list[PostTextResultItem]
