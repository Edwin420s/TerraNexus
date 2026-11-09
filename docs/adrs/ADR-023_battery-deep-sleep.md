# ADR-023: Battery Deep Sleep Management

## Status
Accepted

## Context
Solar-powered remote field nodes must operate throughout cloudy monsoon periods.

## Decision
Monitor 18650 LiFePO4 battery via 2:1 resistive divider and enter deep sleep (15uA) between 15-minute measurement cycles.

## Consequences
Continuous unattended field node autonomy exceeding 180 days on a 2200mAh cell.