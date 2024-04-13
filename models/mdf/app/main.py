from time import sleep

from app.api import get_sentences, post_results
from app.args_parser import parse_args
from app.dto import ResultSentence, Sentence
from app.logger import get_logger
from app.models.base_mdf import BaseMDF

logger = get_logger(__name__)


def parse_sentences(model: BaseMDF, sentences: list[Sentence]) -> list[ResultSentence]:
    return [
        ResultSentence(
            sentence_id=sentence.id,
            result=model.compute_scores(sentence.sentence),
        )
        for sentence in sentences
    ]


def main() -> None:
    logger.info("Starting main")
    model_class = parse_args()
    logger.info(f"Using model {model_class.name}")
    while True:
        for _ in range(1_000_000):
            sources = [
                "banki.ru/broker",
                "banki.ru/mfo",
                "banki.ru/insurance",
                "vk.com/other",
                "vk.com/comments",
                "banki.ru",
                "sravni.ru",
                "banki.ru/news",
                "sravni.ru/insurance",
                "sravni.ru/mfo",
            ]
            sentences = get_sentences(sources, model_class.model_id)
            result_sentences = parse_sentences(model_class, sentences)
            post_results(model_class.model_id, result_sentences)
        sleep(60 * 60 * 24)  # 24 hours


if __name__ == "__main__":
    main()
