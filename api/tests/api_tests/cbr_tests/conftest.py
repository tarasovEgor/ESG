import pytest
import requests
import requests_mock
import vcr

from app.dataloader import BankParser, BrokerParser, InsuranceParser, MFOParser
from app.settings import ROOT_DIR

my_vcr = vcr.VCR(
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    serializer="yaml",
    cassette_library_dir=f"{ROOT_DIR}/../cassettes/",
    match_on=("method", "scheme", "host", "port", "path"),
)


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_bank_page() -> tuple[str, str]:
    data = requests.get(BankParser.BASE_PAGE_URL)
    return BankParser.BASE_PAGE_URL, data.text


@pytest.fixture
def get_cbr_bank_page_mock(
    mock_request: requests_mock.Mocker, get_cbr_bank_page: tuple[str, str]
) -> requests_mock.Mocker:
    url, page = get_cbr_bank_page
    mock_request.get(url, text=page)
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_bank_file(get_cbr_bank_page: tuple[str, str]) -> tuple[str, bytes]:
    _, page = get_cbr_bank_page
    file_url = BankParser.get_dataframe_url(page)
    data = requests.get(file_url)
    return file_url, data.content


@pytest.fixture
def get_cbr_bank_file_mock(
    mock_request: requests_mock.Mocker, get_cbr_bank_file: tuple[str, bytes]
) -> requests_mock.Mocker:
    url, content = get_cbr_bank_file
    mock_request.get(url, content=content)
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_broker_file() -> tuple[str, bytes]:
    data = requests.get(BrokerParser.URL)
    return BrokerParser.URL, data.content


@pytest.fixture
def get_cbr_broker_file_mock(mock_request, get_cbr_broker_file) -> requests_mock.Mocker:
    url, content = get_cbr_broker_file
    mock_request.get(url, content=content)
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_mfo_file() -> tuple[str, bytes]:
    data = requests.get(MFOParser.URL)
    return MFOParser.URL, data.content


@pytest.fixture
def get_cbr_mfo_file_mock(mock_request, get_cbr_mfo_file) -> requests_mock.Mocker:
    url, content = get_cbr_mfo_file
    mock_request.get(url, content=content)
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def get_cbr_insurance_file() -> tuple[str, bytes]:
    data = requests.get(InsuranceParser.URL)
    return InsuranceParser.URL, data.content


@pytest.fixture
def get_cbr_insurance_file_mock(mock_request, get_cbr_insurance_file) -> requests_mock.Mocker:
    url, content = get_cbr_insurance_file
    mock_request.get(url, content=content)
    yield mock_request
