import pytest
import requests
import requests_mock
import vcr

from tests.request_data import PROJECT_PATH, settings

my_vcr = vcr.VCR(
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    serializer="yaml",
    cassette_library_dir=f"{PROJECT_PATH}/vcr_cassettes/vk",
    match_on=("method", "scheme", "host", "port", "path"),
)

base_params = {
    "access_token": settings.vk_token,
    "v": "5.131",
    "count": 100,
    "owner_id": -22522055,
}


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def group_page():
    params = base_params.copy() | {"offset": 0}
    url = "https://api.vk.com/method/wall.get"
    js = requests.get(url, params=params).json()
    js["response"]["count"] = 101
    js["response"]["items"] = js["response"]["items"][:1]
    return (
        url,
        js,
    )


@pytest.fixture
def mock_wall(mock_request, group_page) -> requests_mock.Mocker:
    mock_request.get(group_page[0], json=group_page[1])
    yield mock_request


@pytest.fixture(scope="session")
@my_vcr.use_cassette
def post_comments():
    params = base_params.copy() | {
        "post_id": 2125420,
        "start_comment_id": None,
        "sort": "desc",
        "thread_items_count": 10,
    }
    url = "https://api.vk.com/method/wall.getComments"
    js = requests.get(url, params=params).json()
    js["response"]["count"] = 101
    js["response"]["items"] = js["response"]["items"][:1]
    js["response"]["items"][0]["text"] *= 10
    return (
        url,
        js,
    )


@pytest.fixture
def mock_post_comments(mock_request, post_comments) -> requests_mock.Mocker:
    mock_request.get(post_comments[0], json=post_comments[1])
    yield mock_request
