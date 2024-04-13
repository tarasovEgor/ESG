from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.model import Model
    from app.database.models.text_sentence import TextSentence


class TextResult(Base):
    __tablename__ = "text_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text_sentence_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("text_sentence.id", ondelete="CASCADE"), index=True
    )
    text_sentence: Mapped["TextSentence"] = relationship("TextSentence", back_populates="text_results")
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("model.id"), index=True)
    model: Mapped["Model"] = relationship("Model", back_populates="text_results")
    result: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=True)
    is_processed: Mapped[bool] = mapped_column(default=True, index=True)

    def __repr__(self) -> str:
        return (
            f"TextResult(id={self.id}, text_sentence_id={self.text_sentence_id}, model_id={self.model_id},"
            f" result={self.result})"
        )

    def dict(self) -> dict[str, int | list[float] | bool]:
        return {
            "text_sentence_id": self.text_sentence_id,
            "model_id": self.model_id,
            "result": self.result,
            "is_processed": self.is_processed,
        }
