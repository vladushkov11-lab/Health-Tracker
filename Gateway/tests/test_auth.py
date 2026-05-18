import httpx
import pytest
from fastapi import Depends
class TestAuth:
    @pytest.mark.asyncio
    async def test_auth_login(self, client_auth_200, test_data_user):
        response = await client_auth_200.post(
            "/api/v1/login",
            json = {
                "email": test_data_user["email"],
                "password": test_data_user["password"],
                "password_check": test_data_user["password_check"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
    @pytest.mark.asyncio
    async def test_login_invalid_data(self, client_auth_401, test_data_user_invalid):
        response = await client_auth_401.post(
            "/api/v1/login",
            json = {
                "email": test_data_user_invalid["email"],
                "password": test_data_user_invalid["password"],
                "password_check": test_data_user_invalid["password_check"]
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_without_email(self, async_client, test_data_user):
        response = await async_client.post(
            "/api/v1/login",
            json = {
                "password": test_data_user["password"],
                "password_check": test_data_user["password_check"]
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_without_password(self, async_client, test_data_user):
        response = await async_client.post(
            "/api/v1/login",
            json = {
                "email": test_data_user["email"],
                "password_check": test_data_user["password_check"]
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_empty_body(self, async_client):
        response = await async_client.post(
            "/api/v1/login",
            json = {}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_service(self, client_auth_503, test_data_user):
        response = await client_auth_503.post(
            "/api/v1/login",
            json = {
                "email": test_data_user["email"],
                "password": test_data_user["password"],
                "password_check": test_data_user["password_check"]
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_invalid_json(self, async_client):
        response = await async_client.post(
            "/api/v1/login",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self, client_auth_200, test_data_user):
        response = await client_auth_200.post(
            "/api/v1/register",
            json = test_data_user
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_register_invalid_password(self, async_client, test_data_user_invalid):
        response = await async_client.post(
            "/api/v1/register",
            json = test_data_user_invalid
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_mismatch(self, async_client, test_data_user):
        response = await async_client.post(
            "/api/v1/register",
            json = {
                "email": test_data_user["email"],
                "password": test_data_user["password"],
                "password_check": "test"
            }
        )
        assert response.status_code == 422
    @pytest.mark.asyncio
    async def test_register_invalid_json(self, async_client):
        response = await async_client.post(
            "/api/v1/register",
            json = {
                "email": "",
                "password": "",
                "password_check": ""
            })
            
        assert response.status_code == 422
    @pytest.mark.asyncio
    async def test_register_auth_service_unavailable(self, client_auth_503, test_data_user):
        response = await client_auth_503.post(
            "/api/v1/register",
            json=test_data_user
        )
        assert response.status_code == 400

class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_success(self, client_auth_200):
        response = await client_auth_200.get("/api/v1/logout")
        assert response.status_code == 200
    
class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_success(self, client_auth_200):
        response = await client_auth_200.delete("/api/v1/delete_user")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_delete_invalid_user(self, client_auth_401):
        response = await client_auth_401.delete("/api/v1/delete_user")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Неверные данные"
    
class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_success(self, client_auth_200, test_data_user):
        response = await client_auth_200.patch(
            "/api/v1/update_user",
            json={
                "email": test_data_user["email"],
                "first_name": test_data_user["first_name"],
                "last_name": test_data_user["last_name"],
                "phone_number": test_data_user["phone_number"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_update_invalid_user(self, client_auth_401):
        response = await client_auth_401.patch(
            "/api/v1/update_user",
            json={
                "email": "test@test.com",
                "first_name": "test",
                "last_name": "test",
                "phone_number": "test"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Неверные данные"
class TestAuthFlow:
    @pytest.mark.asyncio
    async def test_register_then_login(self, client_auth_200, test_data_user):
        register_response = await client_auth_200.post(
            "/api/v1/register",
            json=test_data_user
        )
        assert register_response.status_code == 200
        login_response = await client_auth_200.post(
            "/api/v1/login",
            json={
                "email": test_data_user["email"],
                "password": test_data_user["password"],
            }
        )
        assert login_response.status_code == 200
    


