# ADR-017: Multi-Tenant RBAC

## Status
Accepted

## Context
Commercial farming operations involve owners, farm managers, agronomists, field operators, and external auditors.

## Decision
Implement granular role permissions scoped to organisations and farms (Owner, Admin, Manager, Agronomist, Operator, Viewer).

## Consequences
Strict tenant data isolation and zero cross-tenant observation leakage.