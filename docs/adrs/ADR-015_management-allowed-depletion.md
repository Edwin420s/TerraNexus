# ADR-015: Dynamic MAD Triggers

## Status
Accepted

## Context
Different crops tolerate different levels of root zone depletion before experiencing yield penalties.

## Decision
Configure crop-specific MAD thresholds (e.g. Maize = 0.50, Tomato = 0.40, Avocado = 0.30) dynamically adjusted by daily ET0.

## Consequences
Optimal irrigation timing that prevents moisture stress while conserving water reserves.