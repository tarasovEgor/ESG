from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text


class SourceType(Base):
    __tablename__ = "source_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="source_type")

    def __repr__(self) -> str:
        return f"SourceType(id={self.id}, name={self.name})"


class Source(Base):
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True)
    site: Mapped[str] = mapped_column(index=True, unique=True)
    source_type_id: Mapped[int] = mapped_column(ForeignKey("source_type.id"), index=True)
    source_type: Mapped["SourceType"] = relationship("SourceType", back_populates="sources")
    parser_state: Mapped[str] = mapped_column(nullable=True)
    last_update: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    texts: Mapped[list["Text"]] = relationship("Text", back_populates="source")

    def __repr__(self) -> str:
        return (
            f"Source(id={self.id}, site={self.site}, source_type_id={self.source_type_id},"
            f" parser_state={self.parser_state}, last_update={self.last_update})"
        )
