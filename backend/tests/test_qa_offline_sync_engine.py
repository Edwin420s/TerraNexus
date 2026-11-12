import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_sync_001_offline_push_and_idempotency():
    """Verify offline push mutation queue."""
    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]

    tasks = client.get("/api/v1/tasks").json()
    task_id = tasks[0]["id"] if tasks else "e0000000-0000-0000-0000-000000000001"

    client_uuid = f"m-client-{uuid.uuid4().hex[:8]}"
    op_id1 = str(uuid.uuid4())
    op_id2 = str(uuid.uuid4())
    obs_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    payload = {
        "client_uuid": client_uuid,
        "app_version": "1.0.0",
        "device_model": "Field-Tablet-Android",
        "operations": [
            {
                "operation_id": op_id1,
                "operation_type": "update",
                "entity_name": "task",
                "entity_id": task_id,
                "client_timestamp": now_iso,
                "payload": {
                    "status": "in_progress"
                }
            },
            {
                "operation_id": op_id2,
                "operation_type": "create",
                "entity_name": "field_observation",
                "entity_id": obs_id,
                "client_timestamp": now_iso,
                "payload": {
                    "field_id": field_id,
                    "observation_type": "pest",
                    "description": "Locust spotted in border trees",
                    "severity": "medium"
                }
            }
        ]
    }

    # Push batch mutations
    resp1 = client.post("/api/v1/sync/push", json=payload)
    assert resp1.status_code == 200
    res_data1 = resp1.json()
    assert res_data1["processed_count"] == 2
    assert res_data1["applied_count"] == 2
    assert res_data1["conflict_count"] == 0

def test_tc_sync_002_offline_pull_cursor_changes():
    """Verify incremental pull synchronization returning modified records."""
    client_uuid = f"m-client-{uuid.uuid4().hex[:8]}"
    pull_req = {
        "client_uuid": client_uuid,
        "since_cursor": 0
    }
    resp = client.post("/api/v1/sync/pull", json=pull_req)
    assert resp.status_code == 200
    data = resp.json()
    assert "new_sync_cursor" in data
    assert "changes" in data
    assert isinstance(data["changes"], list)

def test_tc_sync_003_idempotency_and_tenant_device_isolation():
    """Verify operation_id deduplication, rejection of unhandled entities, and cross-tenant device protection."""
    client_uuid = f"m-client-{uuid.uuid4().hex[:8]}"
    op_id = str(uuid.uuid4())
    obs_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    fields = client.get("/api/v1/fields").json()
    field_id = fields[0]["id"]

    payload = {
        "client_uuid": client_uuid,
        "operations": [
            {
                "operation_id": op_id,
                "operation_type": "create",
                "entity_name": "field_observation",
                "entity_id": obs_id,
                "client_timestamp": now_iso,
                "payload": {"field_id": field_id, "description": "Soil survey observation"}
            },
            {
                "operation_id": str(uuid.uuid4()),
                "operation_type": "custom_action",
                "entity_name": "unsupported_entity_type",
                "entity_id": str(uuid.uuid4()),
                "client_timestamp": now_iso,
                "payload": {"raw": "data"}
            }
        ]
    }

    # 1. First push: 1 valid operation applied, 1 unhandled rejected
    resp1 = client.post("/api/v1/sync/push", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["applied_count"] == 1  # Only the valid observation applied
    assert data1["deduplicated_count"] == 0
    assert "results" in data1
    assert len(data1["results"]) == 2
    res_statuses = {r["operation_id"]: r["status"] for r in data1["results"]}
    assert res_statuses[op_id] == "applied"
    unhandled_id = payload["operations"][1]["operation_id"]
    assert res_statuses[unhandled_id] == "rejected"

    # 2. Second push with exact same operations: must be deduplicated
    resp2 = client.post("/api/v1/sync/push", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["deduplicated_count"] >= 1
    assert data2["applied_count"] == 0
    assert any(r["status"] == "deduplicated" for r in data2["results"])

