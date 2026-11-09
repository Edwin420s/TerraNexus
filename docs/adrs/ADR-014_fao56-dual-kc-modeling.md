# ADR-014: FAO-56 Dual Kc Transpiration Modeling

## Status
Accepted

## Context
Estimating water demand requires separating soil evaporation (Ke) from crop transpiration (Kcb).

## Decision
Adopt FAO-56 Penman-Monteith reference evapotranspiration (ET0) multiplied by stage-specific Kc curves.

## Consequences
Prevents over-irrigation during early vegetative stages when soil cover is incomplete.