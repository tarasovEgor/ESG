from sqlalchemy import delete, extract, func, insert, select, text
from sqlalchemy.orm import Session

from app.database import Source, SourceType, Text, TextSentenceCount
from app.misc.logger import get_logger

logger = get_logger(__name__)


def recalculate_count_sentences_table(session: Session) -> None:
    session.execute(delete(TextSentenceCount))
    session.execute(text("ALTER SEQUENCE text_reviews_count_id_seq RESTART WITH 1"))
    session.commit()


def aggregate_count_sentences(session: Session) -> None:
    query = (
        select(
            func.count(Text.id).label("reviews_count"),
            func.date_trunc("month", Text.date).label("month"),
            extract("quarter", Text.date).label("quarter"),
            SourceType.name,
            Source.site,
        )
        .select_from(Text)
        .join(Source)
        .join(SourceType)
        .group_by("month", "quarter", Source.site, SourceType.name)
    )
    session.execute(
        insert(TextSentenceCount).from_select(
            [
                TextSentenceCount.count_reviews.name,
                TextSentenceCount.date.name,
                TextSentenceCount.quarter.name,
                TextSentenceCount.source_type.name,
                TextSentenceCount.source_site.name,
            ],
            query,
        )
    )
    session.commit()
    logger.info("Counted sentences per day")
