from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import Session
from app.query.views import aggregate_text_result, text_reviews_count
from app.schemes.source import SourceSitesEnum
from app.schemes.views import (
    AggregateTetResultResponse,
    IndexTypeVal,
    ReviewsCountResponse,
    SentenceCountAggregate,
)

router = APIRouter(prefix="/views", tags=["aggregate"])


@router.get(
    "/aggregate_text_result",
    response_model=AggregateTetResultResponse,
    responses={400: {"description": "Start year cannot be greater than end year"}},
)
async def get_aggregate_text_result(
    db: Session,
    bank_ids: Annotated[list[int], Query(description="Список id банков", example=[1])],
    model_names: Annotated[list[str], Query(description="Список названий моделей", example=["model"])],
    source_type: Annotated[list[str], Query(description="Список типов источников", example=["review"])],
    start_year: Annotated[
        int,
        Query(
            ge=datetime.fromtimestamp(1).year,
            le=datetime.now().year,
            description="Первый год рассматриваемого периода",
        ),
    ] = datetime.fromtimestamp(1).year,
    end_year: Annotated[
        int,
        Query(
            ge=datetime.fromtimestamp(1).year,
            le=datetime.now().year,
            description="Последний год рассматриваемого периода",
        ),
    ] = datetime.now().year,
    aggregate_by_year: Annotated[bool, Query(description="Типы агрегации год/квартал")] = False,
    index_type: Annotated[IndexTypeVal, Query(description="Тип индекса")] = IndexTypeVal.index_safe,
) -> AggregateTetResultResponse:
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="Start year cannot be greater than end year")
    if any([model == "" for model in model_names]):
        raise HTTPException(status_code=400, detail="Model names cannot be empty")
    if any([source == "" for source in source_type]):
        raise HTTPException(status_code=400, detail="Source types cannot be empty")
    data = await aggregate_text_result(
        db,
        start_year,
        end_year,
        bank_ids,
        model_names,
        source_type,
        aggregate_by_year,
        index_type,
    )
    return AggregateTetResultResponse(items=data)


@router.get(
    "/reviews_count",
    response_model=ReviewsCountResponse,
    responses={400: {"description": "Start date cannot be greater than end date"}},
)
async def get_reviews_count(
    source_sites: Annotated[list[SourceSitesEnum] | None, Query(description="Список сайтов")],
    session: Session,
    start_date: Annotated[
        date,
        Query(
            description="Начальная дата рассматриваемого периода",
        ),
    ] = datetime.fromtimestamp(1).date(),
    end_date: Annotated[
        date,
        Query(
            description="Конечная дата рассматриваемого периода",
        ),
    ] = datetime.now().date(),
    aggregate_by: Annotated[SentenceCountAggregate, Query(description="Тип агрегации")] = SentenceCountAggregate.month,
) -> ReviewsCountResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be greater than end date")
    if start_date < datetime.fromtimestamp(1).date() or end_date < datetime.fromtimestamp(1).date():
        raise HTTPException(status_code=400, detail="Date cannot be less than 1970")
    if start_date > datetime.now().date() or end_date > datetime.now().date():
        raise HTTPException(status_code=400, detail="Date cannot be greater than now")
    data = await text_reviews_count(session, start_date, end_date, source_sites, aggregate_by)
    return ReviewsCountResponse(items=data)
