from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.database import TextSentenceCount
from app.database.models import AggregateTableModelResult as TextResultAgg
from app.schemes.source import SourceSitesEnum
from app.schemes.views import (
    AggregateTextResultItem,
    IndexTypeVal,
    ReviewsCountItem,
    SentenceCountAggregate,
)


def get_index(
    index_type: IndexTypeVal,
) -> tuple[InstrumentedAttribute[Any], InstrumentedAttribute[Any], InstrumentedAttribute[Any]]:
    match index_type:
        case IndexTypeVal.index_base:
            return (
                TextResultAgg.index_base,
                TextResultAgg.index_base_10_percentile,
                TextResultAgg.index_base_90_percentile,
            )
        case IndexTypeVal.index_std:
            return TextResultAgg.index_std, TextResultAgg.index_std_10_percentile, TextResultAgg.index_std_90_percentile
        case IndexTypeVal.index_mean:
            return (
                TextResultAgg.index_mean,
                TextResultAgg.index_mean_10_percentile,
                TextResultAgg.index_mean_90_percentile,
            )
        case IndexTypeVal.index_safe:
            return (
                TextResultAgg.index_safe,
                TextResultAgg.index_safe_10_percentile,
                TextResultAgg.index_safe_90_percentile,
            )
        case _:
            raise ValueError


def aggregate_columns(aggregate_by_year: bool) -> list[InstrumentedAttribute[Any]]:
    if aggregate_by_year:
        aggregate_cols = [TextResultAgg.year, TextResultAgg.quater]
    else:
        aggregate_cols = [TextResultAgg.quater, TextResultAgg.year]
    aggregate_cols.extend(
        [
            TextResultAgg.source_type.name,
            TextResultAgg.model_name.name,
            TextResultAgg.bank_name.name,
            TextResultAgg.bank_id.name,
        ]
    )
    return aggregate_cols


async def aggregate_text_result(
    session: AsyncSession,
    start_year: int,
    end_year: int,
    bank_ids: list[int],
    model_names: list[str],
    source_types: list[str],
    aggregate_by_year: bool,
    index_type: IndexTypeVal,
) -> list[AggregateTextResultItem]:
    index_val, index_10_percentile, index_90_percentile = get_index(index_type)
    aggregate_cols = aggregate_columns(aggregate_by_year)
    query = (
        select(
            TextResultAgg.year,
            TextResultAgg.quater,
            TextResultAgg.bank_name,
            TextResultAgg.bank_id,
            TextResultAgg.model_name,
            TextResultAgg.source_type,
            func.sum(index_val).label("index"),
            func.avg(index_10_percentile).label("index_10_percentile"),
            func.avg(index_90_percentile).label("index_90_percentile"),
        )
        .where(
            TextResultAgg.year.between(start_year, end_year),
            TextResultAgg.model_name.in_(model_names),
            TextResultAgg.source_type.in_(source_types),
            TextResultAgg.bank_id.in_(bank_ids),
        )
        .group_by(*aggregate_cols)
        .order_by(TextResultAgg.year, TextResultAgg.quater)
    )
    return [
        AggregateTextResultItem.construct(  # don't validate data
            _fields_set=AggregateTextResultItem.__fields_set__,
            year=year,
            quarter=quarter,
            date=date(year, quarter * 3, 1),
            bank_id=bank_id,
            bank_name=bank_name,
            model_name=model_name,
            source_type=source_type,
            index=index,
            index_10_percentile=index_10,
            index_90_percentile=index_90,
        )
        for (
            year,
            quarter,
            bank_name,
            bank_id,
            model_name,
            source_type,
            index,
            index_10,
            index_90,
        ) in await session.execute(query)
    ]


async def text_reviews_count(
    session: AsyncSession,
    start_date: date,
    end_date: date,
    source_sites: list[SourceSitesEnum] | None,
    # sources_types: list[SourceTypesEnum],
    aggregate_by_year: SentenceCountAggregate,
) -> list[ReviewsCountItem]:
    date_label = "date_"
    match aggregate_by_year:
        case SentenceCountAggregate.month:
            query = select(
                TextSentenceCount.date.label(date_label),
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
                TextSentenceCount.count_reviews,
            )
        case SentenceCountAggregate.quarter:
            query = select(
                func.date_trunc("quarter", TextSentenceCount.date).label(date_label),
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
                func.sum(TextSentenceCount.count_reviews).label("count_reviews"),
            ).group_by(
                date_label,
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
            )
        case _:
            raise ValueError
    query = query.where(TextSentenceCount.date.between(start_date, end_date))
    if source_sites:
        query = query.where(TextSentenceCount.source_site.in_(source_sites))
    return [
        ReviewsCountItem.construct(  # don't validate data
            _fields_set=ReviewsCountItem.__fields_set__,
            date=date_,
            source_site=source_site,
            source_type=source_type,
            count=count_reviews,
        )
        for (date_, source_site, source_type, count_reviews) in await session.execute(query)
    ]
