import nltk
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.text_sentence import TextSentence

# from . import celery_app

tokenizer = nltk.data.load("tokenizers/punkt/russian.pickle")


# @celery_app.task
async def transform_texts(texts_ids: list[int], texts: list[str], db: AsyncSession) -> None:
    text_sentences = []
    for text_id, text in zip(texts_ids, texts):
        sentences = tokenizer.tokenize(text)
        for i, sentence in enumerate(sentences, 1):
            if len(sentence) < 5:
                # sometimes triple symbols reconstructed as two sentences
                continue
            text_sentences.append(
                TextSentence(
                    text_id=text_id,
                    sentence=sentence.strip(),
                    sentence_num=i,
                )
            )
    db.add_all(text_sentences)
    await db.commit()
