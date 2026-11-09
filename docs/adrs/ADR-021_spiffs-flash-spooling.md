# ADR-021: Non-Volatile Flash Spooling

## Status
Accepted

## Context
Remote farm edge nodes experience cellular outages lasting hours or days.

## Decision
Allocate circular JSON Lines spool buffer in SPIFFS flash memory storing up to 10,000 telemetry packets.

## Consequences
Zero telemetry loss during extended telecommunication infrastructure failures.