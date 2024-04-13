import logging
import threading
from collections.abc import Callable

import schedule

from app.database import get_sync
from app.misc.logger import get_logger
from app.schemes.mdf_models import MdfModels
from app.views import (
    aggregate_count_sentences,
    aggregate_database_mdf,
    aggregate_database_sentiment,
    calculate_percentiles,
    recalculate_aggregate_table,
    recalculate_count_sentences_table,
    update_indexes,
)

logger = get_logger(__name__)


def calculate_aggregate_database_sentiment() -> None:
    with get_sync() as session:
        recalculate_aggregate_table(session)
        logger.info("start sentiment aggregate")
        aggregate_database_sentiment(session)
        for mdf_model_name in MdfModels:
            logger.info(f"start {mdf_model_name.value} aggregate")
            aggregate_database_mdf(session, mdf_model_name.value)
        update_indexes(session)
        calculate_percentiles(session)


def count_sentences() -> None:
    with get_sync() as session:
        recalculate_count_sentences_table(session)
        aggregate_count_sentences(session)


def run_threaded(job_func: Callable[[None], None]) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def setup() -> None:
    logger.info("Starting views")
    count_sentences()
    calculate_aggregate_database_sentiment()
    logging.getLogger("schedule")
    schedule.every().day.do(run_threaded, count_sentences)
    schedule.every().day.do(run_threaded, calculate_aggregate_database_sentiment)
    while True:
        schedule.run_pending()


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
