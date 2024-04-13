from datetime import datetime

import pytest
from fastapi import status

from tests.conftest import APITestMixin


class TestSource(APITestMixin):
    @pytest.mark.parametrize(
        "data",
        [
            {"site": "example.com", "source_type": "review"},
        ],
    )
    async def test_post_source_200(self, data):
        response = await self.client.post(
            "/source/",
            json=data,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["id"] == 1

    @pytest.mark.parametrize(
        "data",
        [
            {"site": "example.com"},
            {"source_type": "example.com"},
            {"sitea": 1, "source_type": "review"},
        ],
    )
    async def test_post_source_422(self, data):
        response = await self.client.post(
            "/source/",
            json=data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    async def test_get_source_200(self, add_source):
        response = await self.client.get("/source")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {
            "items": [{"id": 1, "site": "example.com", "source_type_id": 1, "last_update": None, "parser_state": None}]
        }

    async def test_get_source_item_200(self, add_source):
        response = await self.client.get("/source/item/1")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {
            "id": 1,
            "site": "example.com",
            "source_type_id": 1,
            "last_update": None,
            "parser_state": None,
        }

    async def test_get_source_404(self):
        response = await self.client.get("/source")
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == {"items": []}

    async def test_get_source_item_404(self):
        response = await self.client.get("/source/item/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text

    async def test_get_source_type(self, add_source):
        response = await self.client.post(
            "/source/",
            json={"site": "example2.com", "source_type": "news"},
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        response = await self.client.get("/source/type")
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == {
            "items": [
                {"id": 1, "name": "review"},
                {"id": 2, "name": "news"},
            ]
        }

    async def test_post_existing_source(self):
        source = {"site": "example.com", "source_type": "review"}
        response = await self.client.post(
            "/source/",
            json=source,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["id"] == 1
        response = await self.client.post(
            "/source/",
            json=source,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["id"] == 1

    @pytest.mark.parametrize(
        "data",
        [
            {"parser_state": "test"},
            {"last_update": datetime.now().isoformat()},
            {"parser_state": "test", "last_update": datetime.now().isoformat()},
        ],
    )
    async def test_patch_source_200(self, add_source, data):
        response = await self.client.patch(
            "/source/item/1",
            json=data,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["site"] == "example.com"
        assert response_data["source_type_id"] == 1
        assert response_data["parser_state"] == data.get("parser_state", None)
        assert response_data["last_update"] == data.get("last_update", None)

    async def test_patch_source_404(self, add_source):
        response = await self.client.patch(
            "/source/item/2",
            json={"parser_state": "test"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text

    @pytest.mark.parametrize("data", [{"last_update": "test"}, {"last_update": "2021-01-01"}])
    async def test_patch_source_422(self, add_source, data):
        response = await self.client.patch(
            "/source/item/1",
            json=data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.parametrize(
        "data",
        [
            {},
            {"parser_state": None, "last_update": None},
        ],
    )
    async def test_patch_source_400(self, add_source, data):
        response = await self.client.patch(
            "/source/item/1",
            json=data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
