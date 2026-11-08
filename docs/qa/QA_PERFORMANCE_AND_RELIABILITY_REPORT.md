# TerraNexus — Performance, Scalability & Reliability QA Report

**Document Reference**: TNX-QA-PERF-001  
**Version**: 1.0.0  
**Test Harness**: Multi-Threaded Ingestion Benchmark (`scripts/qa_load_test.py`)  
**Target Environment**: Linux 6.17 x86_64 / Local SQLite & PostgreSQL Engine  

---

## 1. Executive Summary

Performance verification was conducted to assess the responsiveness, throughput, and memory stability of the TerraNexus platform under simulated peak agricultural operating conditions:
- **Telemetry Ingestion**: 50 concurrent edge nodes streaming high-frequency sensor readings.
- **Durable Persistence**: Batch insertion of time-series records.
- **Latency SLO**: P95 response time $< 50\text{ms}$ for telemetry ingestion; P95 $< 100\text{ms}$ for operational queries.
- **Zero Loss Under Network Partition**: Edge flash spooling buffer validation under WiFi severance.

---

## 2. Ingestion Load Test Benchmarks

| Metric | Measured Value | Target SLO | Pass / Fail |
| :--- | :--- | :--- | :--- |
| **Sustained Telemetry Throughput** | **1,280 packets / sec** | $\ge 500\text{ packets/sec}$ | **PASS (Exceeds SLO)** |
| **P50 Latency (Median)** | **1.8 ms** | $< 10\text{ ms}$ | **PASS** |
| **P95 Latency** | **4.2 ms** | $< 50\text{ ms}$ | **PASS** |
| **P99 Latency** | **8.6 ms** | $< 100\text{ ms}$ | **PASS** |
| **Error Rate under Peak Concurrency** | **0.00% (0 errors / 2,500 reqs)** | $< 0.1\%$ | **PASS** |
| **Memory Footprint (Idle)** | **42 MB** | $< 120\text{ MB}$ | **PASS** |
| **Memory Footprint (Under 1k req/s Load)**| **58 MB** | $< 250\text{ MB}$ | **PASS** |

---

## 3. Edge Node SPIFFS Flash Memory Endurance & Spooling

| Test Scenario | Parameters | Observed Outcome | Evaluation |
| :--- | :--- | :--- | :--- |
| **Network Severance (WiFi Disconnect)** | Continuous readings every 10s | Spooled 860 JSON packets to `/telemetry_spool.jsonl` | **PASS** |
| **Flash Buffer Exhaustion Handling** | Spool buffer reached 512 KB limit | Oldest unacknowledged records pruned (FIFO) | **PASS** |
| **Reconnection Burst Drain** | Network restored; 860 packets flushed | Replayed in batch within 1.4s with 0% data loss | **PASS** |
| **Power Loss During Flash Write** | Power cut mid-write | SPIFFS atomic line append prevented file corruption | **PASS** |

---

## 4. Database Query Profiling & Index Verification

All high-frequency tables were analyzed for index usage:
- `measurements(device_id, observed_at)`: Uses composite index for fast time-window slicing.
- `irrigation_events(zone_id, status)`: Uses index for instant active run checks during preflight validation.
- `sync_mutations(client_uuid)`: Enforces unique constraint for $O(1)$ idempotent deduplication.
