#!/usr/bin/env python3
"""
TerraNexus QA Load & Concurrency Benchmark Runner
Simulates multi-node concurrent telemetry ingestion and benchmarks throughput & latency percentiles.
"""

import sys
import os
import time
import uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

# Add backend directory to sys.path so we can run directly
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

def run_load_benchmark(total_packets=200, workers=8):
    print("=" * 70)
    print("TERRANEXUS QA BENCHMARK: HIGH-THROUGHPUT TELEMETRY INGESTION")
    print(f"Target: {total_packets} packets | Concurrency: {workers} workers")
    print("=" * 70)

    client = TestClient(app)

    # 1. Fetch or ensure a test device exists
    dev_resp = client.get("/api/v1/devices")
    if dev_resp.status_code == 200 and dev_resp.json():
        device_id = dev_resp.json()[0]["id"]
    else:
        create_resp = client.post("/api/v1/devices", json={
            "device_eui": f"LOAD-{uuid.uuid4().hex[:8].upper()}",
            "name": "Benchmark Load Device",
            "hardware_profile": "ESP32-STRESS-NODE"
        })
        device_id = create_resp.json()["id"]

    print(f"Using target device: {device_id}")

    latencies = []
    successes = 0
    failures = 0

    def send_one(i):
        nonlocal successes, failures
        event_id = str(uuid.uuid4())
        payload = {
            "event_id": event_id,
            "schema_version": "1.0",
            "device_id": device_id,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "sequence": i,
            "measurements": [
                {"type": "soil_moisture", "value": 25.0 + (i % 20) * 0.5, "unit": "%", "depth_cm": 15.0},
                {"type": "ambient_temp", "value": 24.1 + (i % 5) * 0.2, "unit": "°C"},
                {"type": "battery_voltage", "value": 3.88, "unit": "V"}
            ]
        }
        t0 = time.perf_counter()
        resp = client.post("/api/v1/telemetry", json=payload)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        if resp.status_code == 202:
            return elapsed_ms, True
        else:
            return elapsed_ms, False

    print("Beginning load generation...")
    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(send_one, range(total_packets)))
    t_end = time.perf_counter()

    total_time = t_end - t_start
    latencies = [r[0] for r in results]
    successes = sum(1 for r in results if r[1])
    failures = len(results) - successes

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg_latency = sum(latencies) / len(latencies)
    throughput = total_packets / total_time

    print("\n" + "=" * 70)
    print("BENCHMARK EXECUTION RESULTS")
    print("=" * 70)
    print(f"Total Packets Processed: {total_packets}")
    print(f"Total Time:              {total_time:.3f} seconds")
    print(f"Throughput:              {throughput:.1f} packets/second")
    print(f"Success Rate:            {(successes/total_packets)*100:.2f}% ({successes} passed, {failures} failed)")
    print(f"Average Latency:         {avg_latency:.2f} ms")
    print(f"P50 (Median) Latency:    {p50:.2f} ms")
    print(f"P90 Latency:             {p90:.2f} ms")
    print(f"P95 Latency:             {p95:.2f} ms")
    print(f"P99 Latency:             {p99:.2f} ms")
    print("=" * 70)

    if failures == 0 and p95 < 1000.0:
        print(">> QA VERDICT: PASS (Meets all performance and reliability SLOs)")
        return 0
    else:
        print(">> QA VERDICT: FAIL (Exceeded latency thresholds or encountered dropped packets)")
        return 1

if __name__ == "__main__":
    sys.exit(run_load_benchmark())
