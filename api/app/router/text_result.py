from fastapi import APIRouter, HTTPException

from app.dependencies import Session
from app.exceptions import IdNotFoundError
from app.query.text_result import create_text_results, get_text_result_items
from app.schemes.text import GetTextResult, GetTextResultItem, PostTextResult

router = APIRouter(prefix="/text_result", tags=["text_result"])


@router.get("/item/{text_id}", response_model=GetTextResult)
async def get_text_results(text_id: int, db: Session) -> GetTextResult:
    texts = await get_text_result_items(db, text_id)
    get_text_result = GetTextResult(
        items=[
            GetTextResultItem(
                id=text.id,
                text_sentence_id=text.text_sentence_id,
                result=text.result,
                model_id=text.model_id,
            )
            for text in texts
        ]
    )
    return get_text_result


@router.post("/", status_code=201, responses={400: {"description": "Text sentence or model not found"}})
async def post_text_result(texts: PostTextResult, db: Session) -> dict[str, str]:
    try:
        await create_text_results(db, texts.items)
    except IdNotFoundError:
        raise HTTPException(status_code=400, detail="Text sentence or model not found")
    return {"message": "OK"}
