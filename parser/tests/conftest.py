import asyncio
from os import environ
from uuid import uuid4

import pytest
import requests_mock
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from common.database import Base
from common.settings import Settings
from tests.request_data import (
    api_bank,
    api_broker,
    api_get_source_by_id,
    api_insurance,
    api_mfo,
    api_source,
    settings,
)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:
    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_url
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_url
    finally:
        drop_database(tmp_url)


@pytest.fixture
def engine(postgres: str) -> Engine:
    engine = create_engine(postgres, echo=True)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session(session_factory) -> Session:
    with session_factory() as session:
        yield session


@pytest.fixture
def mock_request() -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mock_source(mock_request) -> requests_mock.Mocker:
    mock_request.post(api_source()[0], status_code=200, json=api_source()[1])
    yield mock_request


@pytest.fixture
def mock_get_source_by_id(mock_request) -> requests_mock.Mocker:
    mock_request.get(api_get_source_by_id()[0], status_code=200, json=api_get_source_by_id()[1])
    mock_request.patch(api_get_source_by_id()[0], status_code=200, json=api_get_source_by_id()[1])
    yield mock_request


@pytest.fixture
def mock_text(mock_request) -> requests_mock.Mocker:
    mock_request.post(f"{Settings().api_url}/text/", status_code=200, json={"data": "ok"})
    yield mock_request


@pytest.fixture
def mock_bank_list(mock_request) -> requests_mock.Mocker:
    mock_request.get(api_bank()[0], status_code=200, json=api_bank()[1])
    yield mock_request


@pytest.fixture
def mock_broker_list(mock_request) -> requests_mock.Mocker:
    mock_request.get(api_broker()[0], status_code=200, json=api_broker()[1])
    yield mock_request


@pytest.fixture
def mock_insurance_list(mock_request) -> requests_mock.Mocker:
    mock_request.get(api_insurance()[0], status_code=200, json=api_insurance()[1])
    yield mock_request


@pytest.fixture
def mock_mfo_list(mock_request) -> requests_mock.Mocker:
    mock_request.get(api_mfo()[0], status_code=200, json=api_mfo()[1])
    yield mock_request
