# ADR-020: GeoJSON Spatial Boundaries

## Status
Accepted

## Context
Farms and fields represent physical geometric parcels requiring coordinate verification.

## Decision
Store WGS-84 (EPSG:4326) GeoJSON polygons with spatial centroid calculation and area hectares validation.

## Consequences
Enables field scouting geotagging and spatial overlap detection.