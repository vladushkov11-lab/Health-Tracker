import pytest
import time
import httpx

class TestFullRegistrationFlow:
    @pytest.mark.integration
    def test_full_registration_flow(self, integration_client, test_user, test_metrics_data):
        register_response = integration_client.post(
            "/api/v1/register",
            json=test_user
        )
        assert register_response.status_code == 200
        
        login_response = integration_client.post(
            "/api/v1/login",
            json ={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert login_response.status_code == 200
        
        me_response = integration_client.get("/api/v1/me")
        assert me_response.status_code == 200
        
        metrics_response = integration_client.post("/app/create_metrics", json=test_metrics_data)
        assert metrics_response.status_code == 201
        
        stats_response = integration_client.get("/app/stats")
        assert stats_response.status_code == 200
    
class TestAuthIntegration:
    @pytest.mark.integration
    def test_login_wrong_password(self, integration_client, test_user):
        integration_client.post("/api/v1/register", json=test_user)
        response = integration_client.post(
            "/api/v1/login",
            json={
                "email": test_user["email"],
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_register_duplicate_user(self, integration_client, test_user):
        response1 = integration_client.post("/api/v1/register", json=test_user)
        assert response1.status_code == 200
        
        response2 = integration_client.post("/api/v1/register", json=test_user)
        assert response2.status_code == 409
    
class TestAPPIntegration:
    @pytest.mark.integration
    def test_profile_crud_flow(self, integration_client, test_user):
        integration_client.post("/api/v1/register", json=test_user)
        integration_client.post(
            "/api/v1/login",
            json={"email": test_user["email"], "password": test_user["password"]}
        )
        
        profile_data = {
            "birth_date": "2000-01-01",
            "height": 175.5,
            "weight": 70.0,
            "gender": "male",
            "target_weight": 68.0,
            "daily_step_goal": 10000
        }
        create_response = integration_client.post(
            "/app/profile_update",
            json=profile_data
        )
        assert create_response.status_code == 201
    
        get_response = integration_client.get("/app/get_profile")
        assert get_response.status_code == 200
        
        update_response = integration_client.patch(
            "/app/profile_update",
            json={"height": 180.0}
        )
        assert update_response.status_code == 200
        
        get_response2 = integration_client.get("/app/get_profile")
        assert get_response2.status_code == 200