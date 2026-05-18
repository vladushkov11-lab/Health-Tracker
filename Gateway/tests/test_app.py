import pytest

class TestProfile:
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client_app_200):
        response = await client_app_200.get("/app/get_profile")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
    
    @pytest.mark.asyncio
    async def test_get_profile_no_auth(self, async_client):
        response = await async_client.get("/app/get_profile")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_profile_success(self, client_app_200, test_data_user):
        response = await client_app_200.post(
            "/app/profile_update",
            json={
                "email": test_data_user["email"],
                "first_name": test_data_user["first_name"],
                "last_name": test_data_user["last_name"],
                "phone_number": test_data_user["phone_number"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
    @pytest.mark.asyncio
    async def test_create_profile_no_auth(self, async_client, test_data_user):
        response = await async_client.post(
            "/app/profile_update",
            json={
                "email": test_data_user["email"],
                "first_name": test_data_user["first_name"],
                "last_name": test_data_user["last_name"],
                "phone_number": test_data_user["phone_number"]
            }
        )
        assert response.status_code == 401

class TestMetrics:
    @pytest.mark.asyncio
    async def test_create_metrics_success(self, client_app_200):
        response = await client_app_200.post(
            "/app/create_metrics",
        json={
                "date_of_metrics": "2000-01-01",
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
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
    @pytest.mark.asyncio
    async def test_get_metrics_success(self, client_app_200):
        response = await client_app_200.get("/app/get_metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    @pytest.mark.asyncio
    async def test_update_metrics_success(self, client_app_200):
        response = await client_app_200.patch(
            "app/update_metrics/",
        params={"metric_id": 1},
        json={
                "date_of_metrics": "2000-01-01",
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
        )
        assert response.status_code == 307

    @pytest.mark.asyncio
    async def test_delete_metrics_success(self, client_app_200):
        response = await client_app_200.delete("/app/delete_metrics/",
                                                params={"metric_id": 1})
        assert response.status_code == 307
    
    @pytest.mark.asyncio
    async def test_metrics_no_auth(self, async_client):
        response = await async_client.get("/app/get_metrics")
        assert response.status_code == 401
    
class TestStats:
    @pytest.mark.asyncio
    async def test_get_stats_success(self, client_app_200):
        response = await client_app_200.get("/app/stats")
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_get_stats_detail_success(self, client_app_200):
        response = await client_app_200.get("/app/stats/detail?days=30")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_stats_no_auth(self, async_client):
        response = await async_client.get("/app/stats")
        assert response.status_code == 401

class TestFlowApp:
    @pytest.mark.asyncio
    async def test_metric_then_stat(self, client_app_200):
        metric_response = await client_app_200.post(
            "/app/create_metrics",
            json={
                "date_of_metrics": "2000-01-01",
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
        )
        assert metric_response.status_code == 201
        
        stats_response = await client_app_200.get(
            "/app/stats"
        )
        assert stats_response.status_code == 200

