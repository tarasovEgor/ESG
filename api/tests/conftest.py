import asyncio
from datetime import datetime
from os import environ
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import requests_mock
from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.database import (
    Model,
    ModelType,
    Source,
    SourceType,
    Text,
    TextResult,
    TextSentence,
)
from app.database.models.bank import Bank, BankType
from app.main import app
from app.schemes.bank_types import BankTypeVal
from app.settings import Settings
from tests.utils import make_alembic_config


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:
    settings = Settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    cmd_options = SimpleNamespace(config="app/database/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine(postgres):
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    return create_async_engine(postgres, echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def engine_async(postgres, migrated_postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine_async, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


def relative_path(path: str) -> str:
    return f"{Path(__file__).parent}/{path}"


@pytest.fixture
async def add_banks(session) -> list[Bank]:
    # bank type for banks created in migrations
    bank_type_id = await session.scalar(select(BankType.id).filter(BankType.name == BankTypeVal.bank))
    if bank_type_id is None:
        bank_type = BankType(name=BankTypeVal.bank)
        session.add(bank_type)
        await session.commit()
        bank_type_id = bank_type.id
    banks = [
        Bank(id=1, bank_name="unicredit", licence="1", bank_type_id=bank_type_id),
        Bank(id=1000, bank_name="vtb", licence="1000", bank_type_id=bank_type_id),
    ]
    session.add_all(banks)
    await session.commit()
    return banks


@pytest.fixture
async def client(session, add_banks) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        yield client


@pytest.fixture
async def add_source(session: AsyncSession) -> Source:
    source = Source(site="example.com", source_type=SourceType(name="review"))
    session.add(source)
    await session.commit()
    assert source.id == 1
    assert source.source_type_id == 1
    return source


@pytest.fixture
async def add_model(session) -> Model:
    model = Model(name="test_model", model_type=ModelType(model_type="test_type"))
    session.add(model)
    await session.commit()
    assert model.id == 1
    assert model.model_type_id == 1
    return model


@pytest.fixture
async def add_text(session, add_source, add_banks) -> list[Text]:
    texts = [
        Text(
            source=add_source,
            date=datetime(2022, 10, 2, 10, 12, 1),
            title="string",
            bank=add_banks[0],  # type: ignore
            text_sentences=[
                TextSentence(
                    sentence="string",
                    sentence_num=1,
                )
            ],
            link="string",
        ),
        Text(
            source=add_source,
            date=datetime(2022, 10, 2, 10, 12, 1),
            title="string",
            text_sentences=[
                TextSentence(
                    sentence="some text",
                    sentence_num=1,
                )
            ],
            bank=add_banks[1],  # type: ignore
            link="string",
        ),
    ]
    session.add_all(texts)
    await session.commit()
    return texts


@pytest.fixture
async def add_text_result(session, add_model, add_text) -> TextResult:
    text_result = TextResult(
        text_sentence=add_text[0].text_sentences[0],  # type: ignore
        model=add_model,
        result=[0.1, 1, 3],
    )
    session.add(text_result)
    await session.commit()
    return text_result


@pytest.fixture
def mock_request() -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield m


class APITestMixin:
    client: AsyncClient

    @pytest.fixture(autouse=True, scope="function")
    def use_api_client(self, client):
        self.client = client
