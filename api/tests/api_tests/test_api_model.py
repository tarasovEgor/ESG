import pytest
from fastapi import status

from tests.conftest import APITestMixin


class TestModel(APITestMixin):
    async def test_post_model(self):
        response = await self.client.post("/model/", json={"model_name": "test_model", "model_type": "test_type"})
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["model_id"] == 1

    @pytest.mark.parametrize(
        "data", [{"model_name": "test_model"}, {"model_type": "test_type"}, {"model_name": 1, "qwer": "test_type"}]
    )
    async def test_post_model_422(self, data):
        response = await self.client.post("/model/", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    async def test_get_model_200(self, add_model):
        response = await self.client.get("/model")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {"items": [{"id": 1, "name": "test_model", "model_type_id": 1, "model_type": "test_type"}]}

    async def test_get_model_empty(self):
        response = await self.client.get("/model")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {"items": []}

    async def test_get_model_type_200(self, add_model):
        response = await self.client.get("/model/type")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {"items": [{"id": 1, "model_type": "test_type"}]}

    async def test_get_model_type_empty(self):
        response = await self.client.get("/model/type")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {"items": []}

    async def test_post_existing_model(self):
        model = {"model_name": "test_model", "model_type": "test_type"}
        response = await self.client.post("/model/", json=model)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["model_id"] == 1
        response = await self.client.post("/model/", json=model)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["model_id"] == 1
