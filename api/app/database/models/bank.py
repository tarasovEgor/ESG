from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text


class BankType(Base):
    __tablename__ = "bank_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    banks: Mapped["Bank"] = relationship("Bank", back_populates="bank_type")

    def __repr__(self) -> str:
        return f"BankType(id={self.id}, name={self.name})"


class Bank(Base):
    __tablename__ = "bank"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    licence: Mapped[str] = mapped_column(index=True)
    bank_type_id: Mapped[int] = mapped_column(ForeignKey("bank_type.id"), index=True, nullable=True)
    bank_type: Mapped["BankType"] = relationship("BankType", back_populates="banks")
    bank_name: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    texts: Mapped[list["Text"]] = relationship("Text", back_populates="bank")

    def __repr__(self) -> str:
        return f"Bank(id={self.id}, license={self.licence} bank_name={self.bank_name}, description={self.description})"
