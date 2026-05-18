import pytest
import httpx
import subprocess
import time
import os

@pytest.fixture(scope="session")
def base_url():
    return "http://gateway:8001"
@pytest.fixture
def integration_client(base_url):
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        yield client

@pytest.fixture
async def async_integration_client(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        yield client
        
@pytest.fixture
def test_user():
    return {
        "email": f"test_{int(time.time())}@test.com",
        "password": "test_password_123",
        "password_check": "test_password_123",
        "first_name": "Integration",
        "last_name": "Test",
        "phone_number": "79001234567"
    }

@pytest.fixture
def test_metrics_data():
    from datetime import date
    return {
        "date_of_metrics": date.today().isoformat(),
        "steps": 10000,
        "calories": 500,
        "distance": 5.5,
        "sleep_hours": 8,
        "sleep_score": 85,
        "calories_intake": 2000,
        "water_ml": 2500,
        "mood": 7,
        "stress_level": 3
    }
    