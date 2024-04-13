import pytest


class TestMixin:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, session, mocker):
        self.session = session
        mocker.patch("common.requests_.sleep", return_value=None)
        mocker.patch("vk_parser.vk_api.sleep", return_value=None)
