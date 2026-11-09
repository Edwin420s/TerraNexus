# ADR-019: HMAC-SHA256 Signed Webhooks

## Status
Accepted

## Context
External ERP and farm management software need real-time push notifications of irrigation and harvest events.

## Decision
Deliver webhook HTTP POST payloads signed with `X-TerraNexus-Signature` containing HMAC-SHA256 digests.

## Consequences
Receivers verify payload authenticity and prevent replay or spoofing attacks.