import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommendations_and_reasoning():
    # Fetch recommendations
    rec_resp = client.get("/api/v1/intelligence/recommendations")
    assert rec_resp.status_code == 200
    recs = rec_resp.json()
    assert len(recs) > 0
    rec_id = recs[0]["id"]

    # Accept recommendation
    accept_resp = client.post(f"/api/v1/intelligence/recommendations/{rec_id}/accept")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["new_status"] == "accepted"

    # Test local reasoning engine
    reason_resp = client.post("/api/v1/intelligence/local-reasoning", json={
        "prompt": "Evaluate soil water deficit for tomato block in mid-season."
    })
    assert reason_resp.status_code == 200
    r_data = reason_resp.json()
    assert "reasoning" in r_data
    assert len(r_data["suggested_actions"]) > 0

def test_offline_sync():
    client_uuid = f"test-client-{uuid.uuid4()}"
    
    # Push offline observation
    push_resp = client.post("/api/v1/sync/push", json={
        "client_uuid": client_uuid,
        "operations": [
            {
                "operation_id": str(uuid.uuid4()),
                "operation_type": "create",
                "entity_name": "field_observation",
                "entity_id": str(uuid.uuid4()),
                "client_timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "field_id": "d0000000-0000-0000-0000-000000000001",
                    "observation_type": "pest_scouting",
                    "description": "Offline scouting noted no fall armyworm on maize whorls.",
                    "severity": "low"
                }
            }
        ]
    })
    assert push_resp.status_code == 200
    p_data = push_resp.json()
    assert p_data["applied_count"] == 1

    # Pull server changes
    pull_resp = client.post("/api/v1/sync/pull", json={
        "client_uuid": client_uuid,
        "since_cursor": 0
    })
    assert pull_resp.status_code == 200
    assert len(pull_resp.json()["changes"]) > 0
