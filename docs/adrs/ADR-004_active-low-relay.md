# ADR-004: Active-LOW Relay Topology

## Status
Accepted

## Context
Upon microcontroller power-on, reset, or brownout, GPIO pins float high or tri-state. A HIGH-triggered relay would inadvertently pulse pumps.

## Decision
Mandate active-LOW optically isolated relay modules where ground sinks are required for coil energization.

## Consequences
Fail-safe physical closed state upon processor boot or brownout event.