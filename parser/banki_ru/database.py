from sqlalchemy import BigInteger, Column, Integer, String

from banki_ru import schemes
from common.database import Base


class BankiRuBase(Base):
    __abstract__ = True

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id: int = Column(Integer, index=True)  # some ids are not unique
    bank_name: str = Column(String)
    bank_code: str = Column(String)

    def __repr__(self) -> str:
        return (
            f"<BankiRuBase(id={self.id}, bank_id={self.bank_id}, bank_name={self.bank_name},"
            f" bank_code={self.bank_code})>"
        )

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBaseScheme) -> "BankiRuBase":
        raise NotImplementedError


class BankiRuBank(BankiRuBase):
    __tablename__ = "banki_ru"

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBaseScheme) -> "BankiRuBank":
        return BankiRuBank(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )

    def __repr__(self) -> str:
        return (
            f"<BankiRuBank(id={self.id}, bank_id={self.bank_id}, bank_name={self.bank_name},"
            f" bank_code={self.bank_code})>"
        )


class BankiRuInsurance(BankiRuBase):
    __tablename__ = "banki_ru_insurance"

    def __repr__(self) -> str:
        return (
            f"<BankiRuInsurance(id={self.id}, bank_id={self.bank_id}, bank_name={self.bank_name},"
            f" bank_code={self.bank_code})>"
        )

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBaseScheme) -> "BankiRuInsurance":
        return BankiRuInsurance(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )


class BankiRuMfo(BankiRuBase):
    __tablename__ = "banki_ru_mfo"

    bank_id = Column(BigInteger, index=True)

    def __repr__(self) -> str:
        return (
            f"<BankiRuMfo(id={self.id}, bank_id={self.bank_id}, bank_name={self.bank_name},"
            f" bank_code={self.bank_code})>"
        )

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBaseScheme) -> "BankiRuMfo":
        return BankiRuMfo(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )


class BankiRuBroker(BankiRuBase):
    __tablename__ = "banki_ru_broker"

    bank_id = Column(BigInteger, index=True)

    def __repr__(self) -> str:
        return (
            f"<BankiRuBroker(id={self.id}, bank_id={self.bank_id}, bank_name={self.bank_name},"
            f" bank_code={self.bank_code})>"
        )

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBaseScheme) -> "BankiRuBroker":
        return BankiRuBroker(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )
