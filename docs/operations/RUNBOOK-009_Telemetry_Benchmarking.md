# RUNBOOK-009: Telemetry Stress Benchmark

1. Launch `python3 scripts/qa_load_test.py`.
2. Simulate 50 concurrent edge nodes publishing at 5Hz.
3. Verify measurement ingestion latency p95 < 25ms.
4. Check SQLite/PostgreSQL write lock duration.
