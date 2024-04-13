from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text
    from app.database.models.text_result import TextResult


class TextSentence(Base):
    __tablename__ = "text_sentence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text_id: Mapped[int] = mapped_column(Integer, ForeignKey("text.id", ondelete="CASCADE"), index=True)
    text: Mapped["Text"] = relationship("Text", back_populates="text_sentences")
    sentence: Mapped[str]
    sentence_num: Mapped[int]
    text_results: Mapped[list["TextResult"]] = relationship("TextResult", back_populates="text_sentence")

    def __repr__(self) -> str:
        return (
            f"TextSentence(id={self.id}, text_id={self.text_id}, sentence={self.sentence},"
            f" sentence_num={self.sentence_num})"
        )
