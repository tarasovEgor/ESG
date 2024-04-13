from sqlalchemy import Column, Integer, String

from common.database import Base


class IRecommend(Base):
    __tablename__ = "irecommend_bank_list"

    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer)
    name = Column(String)
    domain = Column(String)
