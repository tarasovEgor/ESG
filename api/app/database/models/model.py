from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text_result import TextResult


class ModelType(Base):
    __tablename__ = "model_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    model_type: Mapped[str] = mapped_column(index=True)
    models: Mapped[list["Model"]] = relationship("Model", back_populates="model_type")

    def __repr__(self) -> str:
        return f"ModelType(id={self.id}, model_type={self.model_type})"


class Model(Base):
    __tablename__ = "model"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    model_type_id: Mapped[int] = mapped_column(ForeignKey("model_type.id"), index=True)
    model_type: Mapped["ModelType"] = relationship("ModelType", back_populates="models")
    text_results: Mapped[list["TextResult"]] = relationship("TextResult", back_populates="model")

    def __repr__(self) -> str:
        return f"Model(id={self.id}, name={self.name}, model_type_id={self.model_type_id})"
