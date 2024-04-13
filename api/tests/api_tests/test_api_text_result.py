import pytest
from fastapi import status

from tests.conftest import APITestMixin


class TestTextResult(APITestMixin):
    async def test_post_text_result_201(self, add_model, add_text):
        response = await self.client.post(
            "/text_result/",
            json={
                "items": [{"text_result": [0.1, 1, 3], "text_sentence_id": 1, "model_id": 1}],
            },
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data == {"message": "OK"}

    @pytest.mark.parametrize(
        "data",
        [
            {"items": [{"text_result": "test", "text_sentence_id": 1, "model_id": 1}]},
            {"items": [{"text_result": [0.1, 1, 3], "text_sentence_id": 1}]},
            {"items": [{"text_result": [0.1, 1, 3], "model_id": 1}]},
        ],
    )
    async def test_post_text_result_422(self, data, add_text, add_model):
        response = await self.client.post(
            "/text_result/",
            json=data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.skip(reason="logic changed")
    @pytest.mark.parametrize(
        "data",
        [
            {"items": [{"text_result": [0.1, 1, 3], "text_sentence_id": 1, "model_id": 2}]},
            {"items": [{"text_result": [0.1, 1, 3], "text_sentence_id": 100, "model_id": 1}]},
        ],
    )
    async def test_post_text_result_400(self, data, add_text, add_model):
        response = await self.client.post(
            "/text_result/",
            json=data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    async def test_get_text_result_200(self, add_text_result):
        response = await self.client.get("/text_result/item/1")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data == {
            "items": [
                {
                    "id": 1,
                    "text_sentence_id": 1,
                    "result": [0.1, 1.0, 3.0],
                    "model_id": 1,
                },
            ]
        }

    async def post_text_result(self, items: dict):
        for item in items:
            response = await self.client.post(
                "/text_result/",
                json={
                    "items": [{"text_result": [0.1, 1, 3], "text_sentence_id": item["id"], "model_id": 1}],
                },
            )
            assert response.status_code == status.HTTP_201_CREATED, response.text

    async def test_several_sources_and_models(self):
        for i in range(3):
            response = await self.client.post(
                "/source/",
                json={"site": f"example{i}.com", "source_type": "review"},
            )
            assert response.status_code == status.HTTP_200_OK, response.text
            response = await self.client.post(
                "/model/", json={"model_name": f"test_model{i}", "model_type": "test_type"}
            )
            assert response.status_code == status.HTTP_200_OK, response.text
            for j in range(10):
                response = await self.client.post(
                    "/text/",
                    json={
                        "items": [
                            {
                                "source_id": i + 1,
                                "date": "2022-10-02T10:12:01.154Z",
                                "title": "string",
                                "text": "string",
                                "bank_id": 1000,
                                "link": "string",
                                "comments_num": 0,
                            }
                        ]
                    },
                )
                assert response.status_code == status.HTTP_201_CREATED, response.text
        response = await self.client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1&limit=5")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        await self.post_text_result(data["items"])
        for j in range(10):
            response = await self.client.post(
                "/text/",
                json={
                    "items": [
                        {
                            "source_id": 1,
                            "date": "2022-10-02T10:12:01.154Z",
                            "title": "string",
                            "text": "string",
                            "bank_id": 1000,
                            "link": "string",
                            "comments_num": 0,
                        }
                    ]
                },
            )
            assert response.status_code == status.HTTP_201_CREATED, response.text
        response = await self.client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert len(data["items"]) == 15
        await self.post_text_result(data["items"])
        response = await self.client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1&limit=20")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert len(data["items"]) == 10
        await self.post_text_result(data["items"])
        response = await self.client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=1&limit=20")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert len(data["items"]) == 0
        await self.post_text_result(data["items"])
        response = await self.client.get("text/sentences?sources=example0.com&sources=example1.com&model_id=2")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert len(data["items"]) == 30
