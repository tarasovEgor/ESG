from fastapi import APIRouter

from app.dependencies import Session
from app.query.model import create_model, get_model_items, get_model_types_items
from app.schemes.model import (
    GetModel,
    GetModelItem,
    GetModelType,
    ModelTypeModel,
    PostModel,
    PostModelResponse,
)

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/", response_model=GetModel)
async def get_models(db: Session) -> GetModel:
    models = await get_model_items(db)
    return GetModel(
        items=[
            GetModelItem(
                id=model.id,
                name=model.name,
                model_type_id=model.model_type_id,
                model_type=model.model_type.model_type,
            )
            for model in models
        ]
    )


@router.post("/", response_model=PostModelResponse)
async def post_model(model: PostModel, db: Session) -> PostModelResponse:
    model_id = await create_model(db, model)
    return PostModelResponse(model_id=model_id)


@router.get("/type/", response_model=GetModelType)
async def get_model_types(db: Session) -> GetModelType:
    model_types = await get_model_types_items(db)
    get_model_type = GetModelType(items=[ModelTypeModel.from_orm(model_type) for model_type in model_types])
    return get_model_type
