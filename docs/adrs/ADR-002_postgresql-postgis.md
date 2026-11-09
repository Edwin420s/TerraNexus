# ADR-002: Dual Database Strategy

## Status
Accepted

## Context
Requires enterprise spatial querying in cloud deployments while enabling edge gateways to run zero-dependency SQLite.

## Decision
Support PostgreSQL with PostGIS for authoritative cloud cluster and dynamic SQLite compatibility for embedded test and local deployments.

## Consequences
Ensures maximum portability across edge Raspberry Pi gateways and cloud Kubernetes environments.