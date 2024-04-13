import requests_mock


def check_used_paths(mock: requests_mock.Mocker, method: str, path: str):
    return len([x for x in mock.request_history if x.method == method and x.path == path])
