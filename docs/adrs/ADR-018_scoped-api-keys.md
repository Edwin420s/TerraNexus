# ADR-018: Scoped API Keys

## Status
Accepted

## Context
Third-party drone scouting and ERP services require programmatic API access without sharing user credentials.

## Decision
Provide developer applications with SHA256 hashed API keys scoped by granular read/write permissions.

## Consequences
Secure API ecosystem enablement with instantaneous revocation capabilities.