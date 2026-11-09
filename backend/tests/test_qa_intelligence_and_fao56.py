import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_intel_001_weather_feed():
    """Verify local weather conditions feed returns climate metrics."""
    weather_resp = client.get("/api/v1/intelligence/weather")
    assert weather_resp.status_code == 200
    data = weather_resp.json()
    assert "current" in data or "daily" in data or "temperature_2m" in str(data)

def test_tc_intel_002_recommendations_and_evidence():
    """Verify agronomic recommendations listing, evidence metrics, and accept/reject."""
    recs_resp = client.get("/api/v1/intelligence/recommendations")
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert len(recs) > 0
    rec = recs[0]
    rec_id = rec["id"]
    assert "summary" in rec
    assert "evidence" in rec

    # Fetch specific recommendation
    single_resp = client.get(f"/api/v1/intelligence/recommendations/{rec_id}")
    assert single_resp.status_code == 200
    assert single_resp.json()["id"] == rec_id

    # Accept recommendation (no body)
    accept_resp = client.post(f"/api/v1/intelligence/recommendations/{rec_id}/accept")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "ok"

def test_tc_intel_003_recommendation_rejection():
    """Verify rejection of agronomic recommendation with documented reason."""
    recs = client.get("/api/v1/intelligence/recommendations").json()
    rec_id = recs[-1]["id"]

    reject_resp = client.post(f"/api/v1/intelligence/recommendations/{rec_id}/reject?reason=Rain+expected")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "ok"

def test_tc_intel_004_local_qvac_reasoning_offline_fallback():
    """Verify local offline reasoning engine adapter returns agronomic guidance in qvac_local_hardware mode."""
    req_payload = {
        "prompt": "Evaluate irrigation necessity for maize at mid season given 18% soil moisture.",
        "context_data": {
            "crop": "Maize",
            "growth_stage": "mid_season",
            "soil_moisture_pct": 18.2
        },
        "model_name": "qvac-agronomist-7b"
    }
    resp = client.post("/api/v1/intelligence/local-reasoning", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "reasoning" in data
    assert "suggested_actions" in data
    assert data["model"] == "qvac-agronomist-7b"
    assert data["execution_mode"] == "qvac_local_hardware"
    assert "Maize" in data["reasoning"]

def test_tc_intel_005_wifi_off_offline_hardware_reasoning():
    """Verify 100% offline local hardware execution when all external network is severed."""
    req_payload = {
        "prompt": "Evaluate Tomato greenhouse soil moisture at 16.2% with root zone depletion assessment."
    }
    resp = client.post("/api/v1/intelligence/local-reasoning", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["execution_mode"] == "qvac_local_hardware"
    assert "Tomato" in data["reasoning"]
    assert "DEFICIT_TRIGGERED" in data["reasoning"]
