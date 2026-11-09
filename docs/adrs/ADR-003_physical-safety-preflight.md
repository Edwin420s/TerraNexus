# ADR-003: Physical Safety Preflight

## Status
Accepted

## Context
Irrigation actuation controls high-pressure water pumps and solenoids. Software errors or cloud disconnections must never cause pump burnout.

## Decision
Enforce local hardware safety preflight checks: hardware watchdog timers, active-LOW optocoupled relays, and dry-run protection.

## Consequences
Guarantees safe physical actuation even during complete cloud network blackout.