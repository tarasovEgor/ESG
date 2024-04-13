from sqlalchemy import BigInteger, Float, Integer, cast, func, select, update
from sqlalchemy.orm import Session

from app.database.models import AggregateTableModelResult as TextResultAgg
from app.misc.logger import get_logger

logger = get_logger(__name__)


def update_indexes(session: Session) -> None:
    calculate_index_base(session)
    calculate_index_mean(session)
    calculate_index_std(session)
    calculate_index_safe(session)


def calculate_index_base(session: Session) -> None:
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(index_base=cast((TextResultAgg.positive - TextResultAgg.negative), Float) / TextResultAgg.total)
    )
    session.commit()
    logger.info("Calculated index base")


def calculate_index_mean(session: Session) -> None:
    select_mean = select(
        TextResultAgg.id,
        func.avg(TextResultAgg.index_base)
        .over(partition_by=[TextResultAgg.source_type, TextResultAgg.model_name])  # type: ignore
        .label("avg"),
    ).subquery("select_mean")
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.id == select_mean.c.id)
        .values(
            index_mean=select_mean.c.avg,
        )
    )
    session.commit()
    logger.info("Calculated index mean")


def calculate_index_std(session: Session) -> None:
    # TODO test for big numbers
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(
            # (((POS * (TOTAL - POS)) / TOTAL**3) + ((NEG * (TOTAL - NEG)) / TOTAL**3))**0.5
            index_std=func.sqrt(
                (
                    cast(TextResultAgg.positive, BigInteger)
                    * (cast(TextResultAgg.total, BigInteger) - cast(TextResultAgg.positive, BigInteger))
                    / func.power(cast(TextResultAgg.total, BigInteger), 3)
                )
                + (
                    cast(TextResultAgg.negative, BigInteger)
                    * (cast(TextResultAgg.total, BigInteger) - cast(TextResultAgg.negative, BigInteger))
                    / func.power(cast(TextResultAgg.total, BigInteger), 3)
                )
            )
        )
    )
    session.commit()
    logger.info("Calculated index std")


def calculate_index_safe(session: Session) -> None:
    # (2 * ((index_base - index_mean) > 0) - 1) * (max(abs(index_base - index_mean) - index_std, 0))
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.total > 0)
        .values(
            index_safe=(
                (
                    2
                    * cast(
                        (TextResultAgg.index_base - TextResultAgg.index_mean) > 0,
                        Integer,
                    )
                    - 1
                )
                * func.greatest(
                    func.abs(TextResultAgg.index_base - TextResultAgg.index_mean) - TextResultAgg.index_std,
                    0,
                )
            )
        )
    )
    session.commit()
    logger.info("Calculated index safe")


def calculate_percentiles(session: Session) -> None:
    base_1 = "base_1"
    base_9 = "base_9"
    mean_1 = "mean_1"
    mean_9 = "mean_9"
    safe_1 = "safe_1"
    safe_9 = "safe_9"
    std_1 = "std_1"
    std_9 = "std_9"
    p_year = "p_year"
    p_quarter = "p_quarter"
    percentiles_query = select(
        func.percentile_disc(0.1).within_group(TextResultAgg.index_base).label(base_1),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.9).within_group(TextResultAgg.index_base).label(base_9),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.1).within_group(TextResultAgg.index_mean).label(mean_1),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.9).within_group(TextResultAgg.index_mean).label(mean_9),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.1).within_group(TextResultAgg.index_std).label(std_1),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.9).within_group(TextResultAgg.index_std).label(std_9),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.1).within_group(TextResultAgg.index_safe).label(safe_1),  # type: ignore[no-untyped-call]
        func.percentile_disc(0.9).within_group(TextResultAgg.index_safe).label(safe_9),  # type: ignore[no-untyped-call]
        TextResultAgg.year.label(p_year),
        TextResultAgg.quater.label(p_quarter),
    ).group_by(TextResultAgg.year, TextResultAgg.quater)
    session.execute(
        update(TextResultAgg)
        .where(TextResultAgg.year == percentiles_query.c.p_year)
        .where(TextResultAgg.quater == percentiles_query.c.p_quarter)
        .values(
            index_base_10_percentile=percentiles_query.c.base_1,
            index_base_90_percentile=percentiles_query.c.base_9,
            index_mean_10_percentile=percentiles_query.c.mean_1,
            index_mean_90_percentile=percentiles_query.c.mean_9,
            index_std_10_percentile=percentiles_query.c.std_1,
            index_std_90_percentile=percentiles_query.c.std_9,
            index_safe_10_percentile=percentiles_query.c.safe_1,
            index_safe_90_percentile=percentiles_query.c.safe_9,
        )
    )
    session.commit()
    logger.info("Calculated percentiles")
