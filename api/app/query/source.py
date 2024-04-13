from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.source import Source, SourceType
from app.schemes.source import CreateSource, PatchSource


async def get_source_items(db: AsyncSession) -> list[Source]:
    return await db.scalars(select(Source).options(selectinload(Source.source_type)))  # type: ignore


async def create_source(db: AsyncSession, model: CreateSource) -> Source:
    source = await db.scalar(
        select(Source)
        .join(Source.source_type)
        .filter(SourceType.name == model.source_type)
        .filter(Source.site == model.site)
    )
    if source:
        return source

    source_type = await db.scalar(select(SourceType).filter(SourceType.name == model.source_type))
    if source_type is None:
        source_type = SourceType(name=model.source_type)
    source = Source(site=model.site, source_type=source_type)
    db.add(source)
    await db.commit()
    return source


async def get_source_item_by_id(db: AsyncSession, source_id: int) -> Source | None:
    return await db.get(Source, source_id)


async def get_source_types_items(db: AsyncSession) -> list[SourceType]:
    return await db.scalars(select(SourceType))  # type: ignore


async def patch_source_by_id(db: AsyncSession, source_id: int, patch_source: PatchSource) -> Source | None:
    source = await get_source_item_by_id(db, source_id)
    if source is None:
        return None
    source.parser_state = patch_source.parser_state  # type: ignore
    source.last_update = patch_source.last_update  # type: ignore
    await db.commit()
    return source
