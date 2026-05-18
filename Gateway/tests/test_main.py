import pytest
from fastapi.testclient import TestClient
from main import app

class TestMain:
    @pytest.mark.asyncio
    async def test_read_root(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_service_error(self, async_client):
        response = await async_client.get("/service_error")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_service(self, async_client):
        response = await async_client.get("/api/v1/me")
        assert response.status_code == 401