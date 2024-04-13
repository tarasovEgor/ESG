import argparse
from enum import Enum

import numpy as np
from sklearn.preprocessing import LabelEncoder


class Datasets(Enum):
    bow = "bow.npz"
    tfidf = "tfidf.npz"
    fast_text = "fasttext.npz"
    word_2_vec = "w2v.npz"
    word_2_vec_navec = "w2v_navec.npz"
    rubert_base_sentence = "rubert_base_cased_sentence.npz"
    rubert_base_parsed = "rubert_base_cased_parsed.npz"
    rubert_reviews_sentence = "rubert_base_cased_sentiment_rurewiews_sentence.npz"
    rubert_reviews_parsed = "rubert_base_cased_sentiment_rurewiews_parsed.npz"
    rubert_base_unfreeze_one_last = "DeepPavlovrubert-base-casedUnfreeze last layer.npz"
    rubert_base_unfreeze_two_last = "DeepPavlovrubert-base-casedUnfreeze last 2 layers.npz"


def get_dataset(args: argparse.Namespace) -> str:
    dataset = args.dataset
    return Datasets[dataset].value


def load_data(path: str) -> np.ndarray | np.ndarray:
    encoder = LabelEncoder()
    x, y = np.load(f"../data/{path}", allow_pickle=True).values()
    y = encoder.fit_transform(y)
    return x, y  # type: ignore


def parse_args() -> str | np.ndarray | np.ndarray:
    parser = argparse.ArgumentParser(description="CLI for dataset selection")
    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        choices=[dataset.name for dataset in Datasets],
        help="select dataset for training",
        # default=Datasets.bow.name,
        required=True,
    )
    path = get_dataset(parser.parse_args())
    x, y = load_data(path)
    return path.split(".")[0], x, y  # type: ignore
