from sqlalchemy import Column, Integer, String

from common.database import Base
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
        )
