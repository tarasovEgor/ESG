from datetime import datetime

import pytest
import requests
import requests_mock
import vcr

from tests.request_data import PROJECT_PATH

my_vcr = vcr.VCR(
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    serializer="yaml",
    cassette_library_dir=f"{PROJECT_PATH}/vcr_cassettes/sravni_ru",
)

reviews_url = "https://www.sravni.ru/proxy-reviews/reviews"
organizations_url = "https://www.sravni.ru/proxy-organizations/organizations"

reviews_params = {
    "filterBy": "withRates",
    "isClient": False,
    "locationRoute": None,
    "newIds": True,
    "orderBy": "byDate",
    "pageIndex": 1,
    "pageSize": 10,
    "specificProductId": None,
    "tag": None,
    "withVotes": True,
}
organizations_params = {"active": True, "limit": 400, "organizationType": "bank", "skip": 0}


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def sravni_banks_list() -> tuple[str, dict]:
    params = organizations_params.copy() | {"organizationType": "bank"}
    return (
        organizations_url,
        requests.get(organizations_url, params=params).json(),
    )


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def bank_sravni_reviews_response() -> tuple[str, dict]:
    params = reviews_params.copy() | {"reviewObjectId": "5bb4f768245bc22a520a6115", "reviewObjectType": "bank"}
    return (
        reviews_url,
        requests.get(reviews_url, params=params).json(),
    )


@pytest.fixture
def mock_sravni_bank_reviews_response(mock_request, bank_sravni_reviews_response) -> requests_mock.Mocker:
    json = bank_sravni_reviews_response[1]
    json["items"][0]["id"] = "1"
    json["items"][0]["createdToMoscow"] = datetime(2023, 1, 1).isoformat()
    json["items"][0]["title"] = "test"
    json["items"][0]["text"] = "test"
    json["items"][0]["commentsCount"] = 1
    mock_request.get(bank_sravni_reviews_response[0], json=json)
    yield mock_request


@pytest.fixture
def mock_sravni_banks_list(mock_request, sravni_banks_list) -> requests_mock.Mocker:
    mock_request.get(sravni_banks_list[0], json=sravni_banks_list[1])
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def sravni_insurance_list() -> tuple[str, dict]:
    params = organizations_params.copy() | {"organizationType": "insuranceCompany"}
    return (
        organizations_url,
        requests.get(organizations_url, params=params).json(),
    )


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def insurance_sravni_reviews_response() -> tuple[str, dict]:
    params = reviews_params.copy() | {"reviewObjectId": "126810", "reviewObjectType": "insuranceCompany"}
    return (
        reviews_url,
        requests.get(reviews_url, params=params).json(),
    )


@pytest.fixture
def mock_sravni_insurance_reviews_response(mock_request, insurance_sravni_reviews_response) -> requests_mock.Mocker:
    json = insurance_sravni_reviews_response[1]
    json["items"][0]["id"] = "1"
    json["items"][0]["createdToMoscow"] = datetime(2023, 1, 1).isoformat()
    json["items"][0]["title"] = "test"
    json["items"][0]["text"] = "test"
    json["items"][0]["commentsCount"] = 1
    mock_request.get(insurance_sravni_reviews_response[0], json=json)
    yield mock_request


@pytest.fixture
def mock_sravni_insurance_list(mock_request, sravni_insurance_list) -> requests_mock.Mocker:
    mock_request.get(sravni_insurance_list[0], json=sravni_insurance_list[1])
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def sravni_mfo_list() -> tuple[str, dict]:
    params = organizations_params.copy() | {"organizationType": "mfo"}
    return (
        organizations_url,
        requests.get(organizations_url, params=params).json(),
    )


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def mfo_sravni_reviews_response() -> tuple[str, dict]:
    params = reviews_params.copy() | {"reviewObjectId": "5e95c820380d2c001c873e36", "reviewObjectType": "mfo"}
    return (
        reviews_url,
        requests.get(reviews_url, params=params).json(),
    )


@pytest.fixture
def mock_sravni_mfo_list(mock_request, sravni_mfo_list) -> requests_mock.Mocker:
    mock_request.get(sravni_mfo_list[0], json=sravni_mfo_list[1])
    yield mock_request


@pytest.fixture
def mock_sravni_mfo_reviews_response(mock_request, mfo_sravni_reviews_response) -> requests_mock.Mocker:
    json = mfo_sravni_reviews_response[1]
    json["items"][0]["id"] = "1"
    json["items"][0]["createdToMoscow"] = datetime(2023, 1, 1).isoformat()
    json["items"][0]["title"] = "test"
    json["items"][0]["text"] = "test"
    json["items"][0]["commentsCount"] = 1
    mock_request.get(mfo_sravni_reviews_response[0], json=json)
    yield mock_request
