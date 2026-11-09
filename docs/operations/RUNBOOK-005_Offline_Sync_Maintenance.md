# RUNBOOK-005: Offline Sync Queue Drain

1. Inspect dead-letter sync queue via `/api/v1/sync/status`.
2. Review rejected client mutations.
3. Replay valid idempotent operations.
4. Reset client sync cursors.
