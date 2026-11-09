# RUNBOOK-001: Cold System Boot

1. Initialize PostgreSQL PostGIS database.
2. Execute schema migrations.
3. Launch Mosquitto MQTT broker.
4. Start FastAPI backend service.
5. Verify `/health/live` and `/health/ready`.
