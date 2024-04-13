import requests

from common.settings import Settings


class Client:
    base_url = Settings().api_url

    def get(self, path: str):
        url = self.base_url + path
        return requests.get(url)

    def post(self, path: str, json: dict | None = None) -> requests.Response:
        if json is None:
            json = {}
        url = self.base_url + path
        return requests.post(url, json=json)

    def delete(self, path: str):
        url = self.base_url + path
        return requests.delete(url)

    def put(self, path: str, json: dict | None = None) -> requests.Response:
        if json is None:
            json = {}
        url = self.base_url + path
        return requests.put(url, json=json)
