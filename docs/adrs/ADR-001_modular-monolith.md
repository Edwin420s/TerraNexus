# ADR-001: Modular Monolith Architecture

## Status
Accepted

## Context
To balance rapid feature evolution with clean domain boundaries, TerraNexus adopts a modular monolith pattern rather than microservices.

## Decision
Organize modules by business domains (identity, farms, agriculture, devices, telemetry, irrigation, operations, intelligence, sync, finance) with isolated schemas and shared core.

## Consequences
Zero network latency between domain boundaries while enabling independent schema evolution.