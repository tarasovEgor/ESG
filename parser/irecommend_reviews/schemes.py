from pydantic import BaseModel


class IRecommendItem(BaseModel):
    bank_id: int
    name: str
    domain: str

    class Config:
        orm_mode = True
