import os
import re

import pandas as pd

from app.api import post_model
from app.logger import get_logger

logger = get_logger(__name__)


class BaseMDF:
    name: str
    model_id: int
    file_path: str

    def __init__(self) -> None:
        self.model_id = post_model(self.name)
        data = self.load_data()
        self.positive_pattern = self.create_pattern(data[data["positive"]]["word"])
        self.negative_pattern = self.create_pattern(data[~data["positive"]]["word"])

    def get_path(self) -> str:
        path = os.path.join(os.path.dirname(__file__)+"/../../data/", self.file_path)
        return path

    def load_data(self) -> pd.DataFrame:
        logger.info(f"Loading data from {self.file_path}")
        words = pd.read_csv(self.get_path(), compression="zip")
        words["positive"] = words["positive"].astype(bool)
        return words

    def create_pattern(self, words: pd.Series) -> re.Pattern[str]:
        return re.compile("(" + "|".join(words) + ")")

    def word_count(self, sentence: str) -> tuple[int, int]:
        positive = len(self.positive_pattern.findall(sentence))
        negative = len(self.negative_pattern.findall(sentence))
        return positive, negative

    def compute_scores(self, sentence: str) -> tuple[float, float]:
        positive, negative = self.word_count(sentence)
        not_neutral = positive + negative
        if not_neutral == 0:
            return 0, 0
        return positive / not_neutral, negative / not_neutral
