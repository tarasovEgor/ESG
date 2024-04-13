from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class TextSentenceCount(Base):
    __tablename__ = "text_reviews_count"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    quarter: Mapped[int] = mapped_column(index=True)
    source_site: Mapped[str] = mapped_column(index=True)
    source_type: Mapped[str] = mapped_column(index=True)
    count_reviews: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return (
            f"TextSentenceCount(date={self.date}, quarter={self.quarter}, source_site={self.source_site},"
            f" source_type={self.source_type}, count={self.count_reviews})"
        )
