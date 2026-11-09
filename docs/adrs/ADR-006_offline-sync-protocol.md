# ADR-006: Offline Sync Protocol

## Status
Accepted

## Context
Mobile farm operators collect field scouting notes in remote plots without mobile broadband.

## Decision
Adopt client-generated UUIDv4 keys, incremental server mutation cursors, and deterministic conflict resolution.

## Consequences
Flawless bidirectional sync without key collisions upon reconnection.