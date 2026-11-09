# ADR-005: Hardware Watchdog Countdown

## Status
Accepted

## Context
Irrigation runs must be guaranteed to terminate regardless of firmware hangs or network loss.

## Decision
Implement ESP32 hardware timer countdown capped at 1800s. Relays cut out automatically if not refreshed by valid authenticated heartbeat.

## Consequences
Zero risk of uncontrolled field flooding or water reservoir depletion.