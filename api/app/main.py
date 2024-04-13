import fastapi
import uvicorn
from alembic.command import upgrade
from alembic.config import Config
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_utils import create_database, database_exists
from starlette.middleware.gzip import GZipMiddleware

from app.database import SessionManager
from app.load_data import load_data
from app.router import (
    bank_router,
    model_router,
    source_router,
    text_result_router,
    text_router,
    views_router,
)
from app.settings import Settings

app = fastapi.FastAPI(
    title="Texts API",
    version="0.1.0",
    description="API for DB",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(text_router)
app.include_router(model_router)
app.include_router(text_result_router)
app.include_router(source_router)
app.include_router(bank_router)
app.include_router(views_router)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)


def run_upgrade(connection: AsyncEngine, cfg: Config) -> None:
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


@app.on_event("startup")
async def startup() -> None:
    settings = Settings()
    if not database_exists(settings.database_uri_sync):
        create_database(settings.database_uri_sync)
    # Base.metadata.create_all(bind=engine)
    config = Config("alembic.ini")
    config.attributes["configure_logger"] = False
    engine = SessionManager().engine
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)
    await load_data()


if __name__ == "__main__":
    uvicorn.run(app)
