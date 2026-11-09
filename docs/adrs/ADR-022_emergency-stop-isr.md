# ADR-022: Hardware Interrupt Emergency Stop

## Status
Accepted

## Context
Physical operators on-site require an instantaneous emergency stop mechanism during burst pipes or electrical faults.

## Decision
Bind hardwired normally-closed emergency stop switch to ESP32 GPIO 14 configured with falling-edge hardware ISR.

## Consequences
Sub-millisecond pump relay cutoff completely independent of FreeRTOS scheduler state.