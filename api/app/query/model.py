from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.model import Model, ModelType
from app.schemes.model import PostModel


async def get_model_items(db: AsyncSession) -> list[Model]:
    return await db.scalars(select(Model).options(selectinload(Model.model_type)))  # type: ignore


async def create_model(db: AsyncSession, post_model: PostModel) -> int:
    model = await db.scalar(select(Model).filter(Model.name == post_model.model_name).limit(1))
    if model:
        return model.id

    model_type = await db.scalar(select(ModelType).filter(ModelType.model_type == post_model.model_type).limit(1))
    if model_type is None:
        model_type = ModelType(model_type=post_model.model_type)
    model = Model(name=post_model.model_name, model_type=model_type)
    db.add(model)
    await db.commit()
    return model.id


async def get_model_types_items(db: AsyncSession) -> list[ModelType]:
    return await db.scalars(select(ModelType))  # type: ignore
