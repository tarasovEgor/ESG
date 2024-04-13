import requests

from app.dto import ResultSentence, Sentence
from app.logger import get_logger
from app.settings import API_URL

logger = get_logger(__name__)


def post_model(model_name: str) -> int:
    data = {
        "model_name": model_name,
        "model_type": "mdf",
    }
    logger.info(f"Posting model {model_name} to {API_URL}")
    response = requests.post(API_URL + "/model", json=data)
    return int(response.json()["model_id"])


def post_results(model_id: int, result_sentences: list[ResultSentence]) -> None:
    data = [
        {
            "model_id": model_id,
            "text_sentence_id": result_sentence.sentence_id,
            "text_result": result_sentence.result,
        }
        for result_sentence in result_sentences
    ]
    logger.info(f"Posting results to {API_URL} sentences {len(data)}")
    response = requests.post(API_URL + "/text_result/", json={"items": data})
    if response.status_code != 200:
        logger.error(f"Error posting results: {response.text}")


def get_sentences(sources: list[str], model_id: int, limit: int = 1000) -> list[Sentence]:
    logger.info(f"Getting texts from {API_URL}")
    params = {
        "sources": sources,
        "model_id": model_id,
        "limit": limit,
    }
    response = requests.get(API_URL + "/text/sentences", params=params)  # type: ignore
    return [Sentence(**text) for text in response.json()["items"]]
