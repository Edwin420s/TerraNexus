# RUNBOOK-004: Database Snapshot Recovery

1. Execute `pg_dump` with PostGIS extension preservation.
2. Encrypt snapshot with AES-256.
3. Push to cold secondary backup bucket.
4. Verify restore integrity on test cluster.
