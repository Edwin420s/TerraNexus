import time
import uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tc_perf_001_concurrent_telemetry_ingestion():
    """Verify high-throughput concurrent telemetry ingestion under multi-node load."""
    devices = client.get("/api/v1/devices").json()
    device_id = devices[0]["id"]
    dev_uuid = str(uuid.UUID(device_id)) if "-" in device_id else str(uuid.uuid4())

    total_requests = 50
    concurrency = 8

    def send_packet(seq):
        t0 = time.perf_counter()
        payload = {
            "event_id": str(uuid.uuid4()),
            "schema_version": "1.0",
            "device_id": dev_uuid,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "sequence": 0,
            "measurements": [
                {"type": "soil_moisture", "value": 28.0 + (seq % 10) * 0.5, "unit": "%"}
            ]
        }
        resp = client.post("/api/v1/telemetry", json=payload)
        elapsed = (time.perf_counter() - t0) * 1000.0
        return resp.status_code, elapsed

    start_wall = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(send_packet, range(total_requests)))
    total_duration = time.perf_counter() - start_wall

    status_codes = [r[0] for r in results]
    latencies = sorted([r[1] for r in results])

    # Assert 100% success rate
    success_count = sum(1 for s in status_codes if s == 202)
    assert success_count == total_requests, f"Expected {total_requests} success, got {success_count}"

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    throughput = total_requests / total_duration

    print(f"\n[PERF RESULT] Ingested {total_requests} in {total_duration:.2f}s | Throughput: {throughput:.1f} req/s | P50: {p50:.2f}ms | P95: {p95:.2f}ms")
    assert p95 < 800.0, f"P95 latency {p95:.2f}ms exceeded 800ms limit"

def test_tc_perf_002_measurement_query_latency():
    """Verify time-series query response latency under filter constraints."""
    devices = client.get("/api/v1/devices").json()
    device_id = devices[0]["id"]

    t0 = time.perf_counter()
    resp = client.get(f"/api/v1/measurements?device_id={device_id}&limit=50")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert resp.status_code == 200
    assert elapsed_ms < 150.0, f"Query latency {elapsed_ms:.2f}ms exceeded 150ms SLO"
