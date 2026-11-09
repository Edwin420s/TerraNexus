# ADR-030: Immutable Audit Logging

## Status
Accepted

## Context
Critical operations (pump activations, financial approvals, user role elevations) require non-repudiation.

## Decision
Log all state modifications in `audit_logs` table with user ID, client IP, action, entity name, and before/after JSON diffs.

## Consequences
Comprehensive forensic traceability and compliance with agricultural safety auditing standards.