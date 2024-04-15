from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from common.database import Base
# from datetime import datetime
from sravni_reviews.schemes import SravniRuBaseScheme


class SravniBankInfo(Base):
    __tablename__ = "sravni_bank_info"

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id: int = Column(Integer, index=True)
    sravni_id: str = Column(String)
    sravni_old_id: int = Column(Integer)
    alias: str = Column(String)
    bank_name: str = Column(String)
    bank_full_name: str = Column(String)
    bank_official_name: str = Column(String)
    # time_created: datetime = Column(DateTime(timezone=True), server_default=func.now())


    @staticmethod
    def from_pydantic(bank: SravniRuBaseScheme) -> "SravniBankInfo":
        return SravniBankInfo(
            sravni_id=bank.sravni_id,
            sravni_old_id=bank.sravni_old_id,  # type: ignore
            alias=bank.alias,
            bank_name=bank.bank_name,
            bank_full_name=bank.bank_full_name,
            bank_official_name=bank.bank_official_name,
            bank_id=bank.bank_id,
            # time_created=bank.time_created
        )
