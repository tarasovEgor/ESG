from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, extract, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.bank import Bank
    from app.database.models.source import Source
    from app.database.models.text_sentence import TextSentence


class Text(Base):
    __tablename__ = "text"
    __table_args__ = (
        Index("ix_text_date_extract_year", extract("year", "date")),  # type: ignore
        Index("ix_text_date_extract_quarter", extract("quarter", "date")),  # type: ignore
        Index("ix_text_date_trunc_month", func.date_trunc("month", "date")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    link: Mapped[str] = mapped_column(String)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("source.id"), index=True)
    source: Mapped["Source"] = relationship("Source", back_populates="texts")
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    title: Mapped[str] = mapped_column(String)
    bank_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank.id"), index=True)
    bank: Mapped["Bank"] = relationship("Bank", back_populates="texts")
    comment_num: Mapped[int] = mapped_column(Integer, nullable=True)
    text_sentences: Mapped[list["TextSentence"]] = relationship("TextSentence", back_populates="text")

    def __repr__(self) -> str:
        return (
            f"Text(id={self.id}, link={self.link}, source_id={self.source_id}, date={self.date}, title={self.title},"
            f" bank_id={self.bank_id}, comment_num={self.comment_num})"
        )
