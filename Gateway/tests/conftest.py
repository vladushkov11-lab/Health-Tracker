import pytest
from fastapi.testclient import TestClient
from main import app
from httpx import AsyncClient, ASGITransport
import httpx
# ------------------ Базовые фикстуры----------------
@pytest.fixture()
async def async_client():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def test_app():
    return app

# ---------------Фикстуры для аутентификации-------------------

@pytest.fixture
async def client_auth_200(): #Заглушка клиена Auth с 200
    from auth.security import get_current_user
    def mock_auth_handler(request: httpx.Request):
        if "/auth/login" in str(request.url):
            return httpx.Response(
                status_code=200,
                json={
                    "access_token": "test_token",
                    "token_type": "bearer",
                    "user_id": "29495076532223560"
                }
            )
        elif "/auth/register" in str(request.url):
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Успешная регестрация",
                    "status": "ok"
                }
            )
        
        elif "/auth/logout" in str(request.url):
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Пользователь успешно вышел",
                    "status": "ok"
                }
            )
        
        elif "/auth/me" in str(request.url):
            return httpx.Response(
                
                json={
                    "id": "29495076532223560",
                    "email": "test@test.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "phone_number": "string"
                }
            )
        elif "/auth/delete_user" in str(request.url):
            return httpx.Response(status_code=200,
                json = {"message": "Пользователь успешно удален", "status": "ok"}
            )
        elif "/auth/update_user" in str(request.url):
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Пользователь успешно обновлен", "status": "ok"
                }
            )
        else:
            return httpx.Response(
                status_code=404
            )
        
    mock_transport = httpx.MockTransport(mock_auth_handler)
    import api.router_auth
    original_client = api.router_auth.client_auth
    mock_auth_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url="http://localhost:8000"
    )
    
    api.router_auth.client_auth = mock_auth_client
    
    async def override_get_current_user():
        return "29495076532223560"
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
    api.router_auth.client_auth = original_client
    await mock_auth_client.aclose()


@pytest.fixture
async def client_auth_401(): #Заглушка клиена Auth с 401
    from auth.security import get_current_user
    def mock_auth_handler(request: httpx.Request):
        if "auth/login" in str(request.url):
            return httpx.Response(
                status_code=401,
                json={
                    "detail": "Неверный логин или пароль"
                }
            )
        elif "/auth/me" in str(request.url):
            return httpx.Response(
                status_code=401,
                json={"detail": "Неверный токен"}
            )
        elif "/auth/delete_user" in str(request.url):
            return httpx.Response(status_code=401,
                json={
                    "message": "Пользователь не найден", "status": "error"
                }
            )
        elif "/auth/update_user" in str(request.url):
            return httpx.Response(
                status_code=401,
                json={
                    "message": "Пользователь не найден", "status": "error"
                }
            )
        else:
            return httpx.Response(status_code=404)
    mock_transport = httpx.MockTransport(mock_auth_handler)
    import api.router_auth
    original_client = api.router_auth.client_auth
    mock_auth_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url="http://localhost:8000"
    )
    api.router_auth.client_auth = mock_auth_client
    
    async def override_get_current_user():
        return "12345678909876453"
    app.dependency_overrides[get_current_user] = override_get_current_user
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()
    api.router_auth.client_auth = original_client
    await mock_auth_client.aclose()

@pytest.fixture
async def client_auth_503(): #Заглушка клиена Auth с 503
    from auth.security import get_current_user
    def mock_auth_handler(request: httpx.Request):
        return httpx.Response(
            status_code=503,
            json={"detail": "Сервис временно недоступен"}
        )
    mock_transport = httpx.MockTransport(mock_auth_handler)
    import api.router_auth
    original_client = api.router_auth.client_auth
    mock_auth_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url="http://localhost:8000"
    )
    api.router_auth.client_auth = mock_auth_client
    async def override_get_current_user():
        return "12345678909876453"
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()
    api.router_auth.client_auth = original_client
    await mock_auth_client.aclose()

@pytest.fixture
def test_data_user():
    """Тестовые данные пользователя"""
    return {
        "email": "test@test.com",
        "password": "test_password",
        "password_check": "test_password",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "79001234567"
    }

@pytest.fixture
def test_data_user_invalid():
    """Невалидные данные пользователя (для тестов валидации)"""
    return {
        "email": "invalid-email",
        "password": "123",
        "password_check": "123",
        "first_name": "",
        "last_name": "",
        "phone_number": "123"
    }

# ---------------Фикстуры для приложения-------------------
@pytest.fixture
async def client_app_200():
    from auth.security import get_current_user
    async def override_get_current_user():
        return "12345678909876453"
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    def mock_app_handler(request: httpx.Request):
        path = str(request.url)
        
        if "/app/get_profile" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "id": "12345678909876453",
                    "email": "test@test.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "phone_number": "79001234567"
                }
            )
        elif "/app/create_profile" in path:
            return httpx.Response(
                status_code=201,
                json={
                    "message": "Профиль успешно создан",
                    "status": "success"
                }
            )
        elif "/app/metrics/add_met" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Метрика успешно создана",
                    "status": "success"
                }
            )
        elif "/app/metrics/get_metrics" in path:
            return httpx.Response(
                status_code=200,
                json=[
                    {
                        "id": 1,
                        "name": "Счетчик 1",
                        "value": 100,
                        "created_at": "2024-01-01T00:00:00.000000Z",
                        "updated_at": "2024-01-01T00:00:00.000000Z"
                    }
                ]
            )
        elif "/app/metrics/update_metrics" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Метрика успешно обновлена",
                    "status": "success"
                }
            )
        
        elif "/app/metrics/delete_metrics" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "message": "Метрика успешно удалена",
                    "status": "success"
                }
            )
        
        elif "/app/stats/get_stats" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "steps": 100,
                    "calories": 50,
                    "calories_intake": 250
                }
            )
        elif "/app/stats/get_stats_detail" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "days": 30,
                    "data": [
                        {"date": "2024-01-01", "value": 100},
                        {"date": "2024-01-02", "value": 120}
                    ]
                }
            )
        elif "/app/stats/get_metric_detail" in path:
            return httpx.Response(
                status_code=200,
                json={
                    "metric_type": "clicks",
                    "total": 500,
                    "avg": 50
                }
            )
        else:
            return httpx.Response(
                status_code=404,
                json={"detail": "Endpoint not found"}
            )
    mock_transport = httpx.MockTransport(mock_app_handler)
    import api.router_app
    original_client = api.router_app.client_auth
    mock_app_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url="http://localhost:8002"
    )
    api.router_app.client_auth = mock_app_client
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()
    api.router_app.client_auth = original_client
    await mock_app_client.aclose()

@pytest.fixture
async def client_app_503():
    from auth.security import get_current_user
    
    def mock_app_handler(request: httpx.Request):
        return httpx.Response(
            status_code=503,
            json={"detail": "APP Service временно недоступен"}
        )
    
    mock_transport = httpx.MockTransport(mock_app_handler)
    
    import api.router_app
    original_client = api.router_app.client_auth
    
    mock_app_client = httpx.AsyncClient(
        transport=mock_transport,
        base_url="http://localhost:8002"
    )
    api.router_app.client_auth = mock_app_client
    
    async def override_get_current_user():
        raise Exception("APP Service unavailable")
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()
    api.router_app.client_auth = original_client
    await mock_app_client.aclose()