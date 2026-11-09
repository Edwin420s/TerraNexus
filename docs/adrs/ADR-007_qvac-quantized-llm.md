# ADR-007: Quantized Local LLM

## Status
Accepted

## Context
Agronomic guidance must remain accessible 100% offline without sending private soil telemetry to external LLM APIs.

## Decision
Deploy quantized 7B parameter agronomy model (`qvac-agronomist-7b`) running on edge CPU/NPU hardware.

## Consequences
Guaranteed privacy, zero cloud subscription fees, and deterministic FAO-56 aligned guidance.