from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.dependencies import Session
from app.exceptions import IdNotFoundError
from app.query.text import create_text_sentences, get_text_sentences
from app.schemes.text import GetTextSentences, PostTextItem

router = APIRouter(prefix="/text", tags=["text"])


@router.get(
    "/sentences",
    response_model=GetTextSentences,
    response_model_by_alias=False,
    responses={400: {"description": "Sources cannot be empty"}},
)
async def get_sentences(
    db: Session,
    sources: Annotated[list[str], Query(example=["example.com"])],
    model_id: Annotated[int, Query()],
    limit: Annotated[int, Query(description="total values")] = 100,
) -> GetTextSentences | JSONResponse:
    if len(sources) == 0 or sources[0] == "":
        raise HTTPException(status_code=400, detail="Sources cannot be empty")
    sentences = await get_text_sentences(db, model_id, sources, limit)

    return GetTextSentences(items=sentences)


@router.post(
    "/",
    responses={
        201: {"description": "ok"},
        400: {"description": "Model id cannot be empty"},
        404: {"description": "Model not found"},
    },
)
async def post_text(texts: PostTextItem, db: Session) -> JSONResponse:
    try:
        await create_text_sentences(db, texts)
    except IdNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=201, content={"message": "ok"})
