# ADR-016: PBKDF2 Password Hashing

## Status
Accepted

## Context
User authentication must adhere to NIST 800-63B standards without external cloud auth dependencies.

## Decision
Use PBKDF2-HMAC-SHA256 with 100,000 iterations and cryptographically secure random 16-byte salts.

## Consequences
Robust defense against brute-force attacks and zero external auth vendor lock-in.