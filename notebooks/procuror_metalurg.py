import ast
from enum import Enum

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import BertConfig, BertModel, BertTokenizerFast, get_scheduler
from transformers.optimization import get_linear_schedule_with_warmup


class SentencesDataset(Dataset):
    def __init__(
        self,
        metalurgi,
        prokuror,
        prokuror_col,
        data_size=None,
        close_sent_dist=1,
        far_sent_dist=10,
    ):
        self.metalurgi = metalurgi
        self.prokuror = prokuror
        self.prokuror_col = prokuror_col
        self.exsist_inn = self.prokuror.loc[
            self.prokuror["INN"].isin(self.metalurgi["INN"]), "INN"
        ].unique()
        self.data_size = (
            data_size
            if data_size is not None
            else min(self.metalurgi.shape[0], self.prokuror.shape[0])
        )
        self.close_sent_dist = close_sent_dist
        self.far_sent_dist = far_sent_dist

    def __len__(self):
        return self.data_size

    def __getitem__(self, idx: int):
        first, second = 0, 0
        label = idx % 2

        if idx % 2:
            first_sentence, second_sentence = self.get_positive_example()
        else:
            first_sentence, second_sentence = self.get_negative_example()

        examples = {
            "sentence1": first_sentence,
            "sentence2": second_sentence,
            "label": label,
        }

        return examples

    def get_positive_example(self):
        second_sentence = None
        while second_sentence is None or pd.isnull(second_sentence):
            inn = np.random.choice(self.exsist_inn)
            first_id = np.random.choice(
                self.metalurgi[self.metalurgi["INN"] == inn].index
            )
            first_sentence = self.metalurgi.at[first_id, "line"]
            second_id = np.random.choice(
                self.prokuror[self.prokuror["INN"] == inn].index
            )
            second_sentence = self.prokuror.at[second_id, "line"]
        return first_sentence, second_sentence

    def get_negative_example(self):
        second_sentence = None
        while second_sentence is None or pd.isnull(second_sentence):
            first_id = np.random.choice(self.metalurgi.shape[0])
            second_id = np.random.choice(self.prokuror.shape[0])
            while (
                self.metalurgi.iloc[first_id]["INN"]
                == self.prokuror.iloc[second_id]["INN"]
            ):
                second_id = np.random.choice(self.prokuror.shape[0])
            first_sentence = self.metalurgi.iloc[first_id]["line"]
            second_sentence = self.prokuror.iloc[second_id]["line"]
        return first_sentence, second_sentence


class ProbModel(nn.Module):
    def __init__(self, bert, custom_bert):
        super().__init__()
        self.bert = bert
        self.custom_bert = custom_bert
        self.dense = nn.Linear(768, 768)
        self.probability = Probability()

    def forward(self, sentence1: Tensor, sentence2: Tensor):
        a = self.get_embedding(sentence1)
        b = self.get_embedding(sentence2, True)

        p = self.probability(a, b)

        return p

    def get_embedding(self, sentence, custom_model=False):
        device = self.probability.device()
        anchor_ids = sentence["input_ids"]  # .to(device)
        anchor_mask = sentence["attention_mask"]  # .to(device)
        if custom_model:
            a = self.custom_bert(anchor_ids, attention_mask=anchor_mask)[0][:, 0]
        else:
            with torch.no_grad():
                a = self.bert(anchor_ids, attention_mask=anchor_mask)[0][:, 0]
        a = self.dense(a)

        return a
