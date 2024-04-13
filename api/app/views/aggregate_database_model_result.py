from sqlalchemy import (
    Boolean,
    and_,
    case,
    cast,
    delete,
    extract,
    func,
    insert,
    select,
    text,
)
from sqlalchemy.orm import Session

from app.database import (
    AggregateTableModelResult,
    Bank,
    Model,
    Source,
    SourceType,
    Text,
    TextResult,
    TextSentence,
)
from app.misc.logger import get_logger

logger = get_logger(__name__)


def recalculate_aggregate_table(session: Session) -> None:
    session.execute(delete(AggregateTableModelResult))
    session.execute(text("ALTER SEQUENCE aggregate_table_model_result_id_seq RESTART WITH 1"))


def aggregate_database_sentiment(session: Session) -> None:
    """
    INSERT INTO aggregate_table_model_result (bank_id, bank_name, quater, year, model_name, source_site, source_type,
                                              positive, neutral, negative, total)
    SELECT bank.id,
           bank.bank_name,
           EXTRACT(quarter FROM anon_1.date)                       AS quarter,
           EXTRACT(year FROM anon_1.date)                          AS year,
           model.name,
           source.site,
           source_type.name                                        AS name_1,
           sum(anon_1.positive)                                    AS positive,
           sum(anon_1.neutral)                                     AS neutral,
           sum(anon_1.negative)                                    AS negative,
           sum(anon_1.positive + anon_1.neutral + anon_1.negative) AS total
    FROM (SELECT anon_14.model_id  AS model_id,
                 anon_14.source_id AS source_id,
                 anon_14.bank_id   AS bank_id,
                 anon_14.date      AS date,
                 CASE
                     WHEN (anon_14.log_positive > anon_14.log_neutral AND anon_14.log_positive > anon_14.log_negative)
                         THEN 1
                     ELSE 0 END    AS positive,
                 CASE
                     WHEN (anon_14.log_neutral > anon_14.log_positive AND anon_14.log_neutral > anon_14.log_negative)
                         THEN 1
                     ELSE 0 END    AS neutral,
                 CASE
                     WHEN (anon_14.log_negative > anon_14.log_neutral AND anon_14.log_negative > anon_14.log_positive)
                         THEN 1
                     ELSE 0 END    AS negative
          FROM (SELECT text.source_id                          AS source_id,
                       text.bank_id                            AS bank_id,
                       text_result.model_id                    AS model_id,
                       text.date                               AS date,
                       sum(log(text_result.result[1] + 0.001)) AS log_neutral,
                       sum(log(text_result.result[2] + 0.001)) AS log_positive,
                       sum(log(text_result.result[3] + 0.001)) AS log_negative
                FROM text_result
                         JOIN text_sentence ON text_sentence.id = text_result.text_sentence_id
                         JOIN text ON text.id = text_sentence.text_id
                WHERE text_result.model_id = 1
                GROUP BY text_result.model_id, text.bank_id, text.source_id, text.date) AS anon_14) AS anon_1
             JOIN bank
                  ON bank.id = anon_1.bank_id
             JOIN model ON model.id = anon_1.model_id
             JOIN source ON source.id = anon_1.source_id
             JOIN source_type ON source_type.id = source.source_type_id
    GROUP BY year, quarter, bank.id, bank.bank_name, source_type.name, source.site, model.name
    """
    eps = 1e-7

    select_log_result = (
        select(
            Text.source_id,
            Text.bank_id,
            TextResult.model_id,
            Text.date,
            func.sum(func.log(TextResult.result[1] + eps)).label("log_neutral"),
            func.sum(func.log(TextResult.result[2] + eps)).label("log_positive"),
            func.sum(func.log(TextResult.result[3] + eps)).label("log_negative"),
        )
        .where(TextResult.model_id == 1)
        .select_from(TextResult)
        .join(TextSentence)
        .join(Text)
        .group_by(TextResult.model_id, Text.bank_id, Text.source_id, Text.date)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.model_id,
        select_log_result.c.source_id,
        select_log_result.c.bank_id,
        select_log_result.c.date,
        case(
            (
                and_(
                    select_log_result.c.log_positive > select_log_result.c.log_neutral,
                    select_log_result.c.log_positive > select_log_result.c.log_negative,
                ),
                1,
            ),
            else_=0,
        ).label("positive"),
        case(
            (
                and_(
                    select_log_result.c.log_neutral > select_log_result.c.log_positive,
                    select_log_result.c.log_neutral > select_log_result.c.log_negative,
                ),
                1,
            ),
            else_=0,
        ).label("neutral"),
        case(
            (
                and_(
                    select_log_result.c.log_negative > select_log_result.c.log_neutral,
                    select_log_result.c.log_negative > select_log_result.c.log_positive,
                ),
                1,
            ),
            else_=0,
        ).label("negative"),
    ).subquery()
    query = (
        select(
            Bank.id,
            Bank.bank_name,
            extract("quarter", select_pos_neut_neg.c.date).label("quarter"),
            extract("year", select_pos_neut_neg.c.date).label("year"),
            Model.name,
            Source.site,
            SourceType.name,
            func.sum(select_pos_neut_neg.c.positive).label("positive"),
            func.sum(select_pos_neut_neg.c.neutral).label("neutral"),
            func.sum(select_pos_neut_neg.c.negative).label("negative"),
            func.sum(
                select_pos_neut_neg.c.positive + select_pos_neut_neg.c.neutral + select_pos_neut_neg.c.negative
            ).label("total"),
        )
        .select_from(select_pos_neut_neg)
        .join(Bank)
        .join(Model)
        .join(Source)
        .join(SourceType)
        .group_by(
            "year",
            "quarter",
            Bank.id,
            Bank.bank_name,
            SourceType.name,
            Source.site,
            Model.name,
        )
    )
    session.execute(
        insert(AggregateTableModelResult).from_select(
            [
                AggregateTableModelResult.bank_id.name,
                AggregateTableModelResult.bank_name.name,
                AggregateTableModelResult.quater.name,
                AggregateTableModelResult.year.name,
                AggregateTableModelResult.model_name.name,
                AggregateTableModelResult.source_site.name,
                AggregateTableModelResult.source_type.name,
                AggregateTableModelResult.positive.name,
                AggregateTableModelResult.neutral.name,
                AggregateTableModelResult.negative.name,
                AggregateTableModelResult.total.name,
            ],
            query,
        )
    )
    session.commit()
    logger.info("AggregateTableModelResult table updated sentiment")


def aggregate_database_mdf(session: Session, model_name: str) -> None:
    eps = 1e-7
    model_id = select(Model.id).where(Model.name == model_name).limit(1).subquery()
    select_log_result = (
        select(
            Text.source_id,
            Text.bank_id,
            TextResult.model_id,
            Text.date,
            func.sum(func.log(TextResult.result[1] + eps)).label("log_positive"),
            func.sum(func.log(TextResult.result[2] + eps)).label("log_negative"),
        )
        .select_from(TextResult)
        .join(TextSentence)
        .join(Text)
        .where(TextResult.model_id == model_id)
        .group_by(TextResult.model_id, Text.source_id, Text.bank_id, Text.date)
        .subquery()
    )
    select_pos_neut_neg = select(
        select_log_result.c.model_id,
        select_log_result.c.source_id,
        select_log_result.c.bank_id,
        select_log_result.c.date,
        case(
            (
                cast(select_log_result.c.log_positive > select_log_result.c.log_negative, Boolean),
                1,
            ),
            else_=0,
        ).label("positive"),
        case(
            (
                cast(select_log_result.c.log_negative > select_log_result.c.log_positive, Boolean),
                1,
            ),
            else_=0,
        ).label("negative"),
    ).subquery()
    query = (
        select(
            Bank.id,
            Bank.bank_name,
            extract("quarter", select_pos_neut_neg.c.date).label("quarter"),
            extract("year", select_pos_neut_neg.c.date).label("year"),
            Model.name,
            Source.site,
            SourceType.name,
            func.sum(select_pos_neut_neg.c.positive).label("positive"),
            func.sum(select_pos_neut_neg.c.negative).label("negative"),
            func.sum(select_pos_neut_neg.c.positive + select_pos_neut_neg.c.negative).label("total"),
        )
        .select_from(select_pos_neut_neg)
        .join(Bank)
        .join(Model)
        .join(Source)
        .join(SourceType)
        .group_by(
            "year",
            "quarter",
            Bank.id,
            Bank.bank_name,
            SourceType.name,
            Source.site,
            Model.name,
        )
    )
    session.execute(
        insert(AggregateTableModelResult).from_select(
            [
                AggregateTableModelResult.bank_id.name,
                AggregateTableModelResult.bank_name.name,
                AggregateTableModelResult.quater.name,
                AggregateTableModelResult.year.name,
                AggregateTableModelResult.model_name.name,
                AggregateTableModelResult.source_site.name,
                AggregateTableModelResult.source_type.name,
                AggregateTableModelResult.positive.name,
                AggregateTableModelResult.negative.name,
                AggregateTableModelResult.total.name,
            ],
            query,
        )
    )
    session.commit()
    logger.info(f"AggregateTableModelResult table updated {model_name}")
