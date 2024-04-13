from fastapi import status

from tests.conftest import APITestMixin


class TestBankApi(APITestMixin):
    async def test_get_bank(self) -> None:
        response = await self.client.get("/bank/")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert len(data["items"]) > 0
        assert data["items"][0].get("id", None) is not None
        assert data["items"][0].get("bank_name", None) is not None
