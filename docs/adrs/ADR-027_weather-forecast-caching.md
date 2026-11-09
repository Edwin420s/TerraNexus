# ADR-027: Weather Forecast Caching

## Status
Accepted

## Context
Irrigation planning incorporates forecasted precipitation and evapotranspiration (ET0).

## Decision
Fetch Open-Meteo agricultural forecast with 3-hour TTL caching and deterministic fallback models for offline operation.

## Consequences
Reliable irrigation scheduling even when third-party weather APIs are temporarily unreachable.