# ADR-012: MQTT Telemetry Message Envelope

## Status
Accepted

## Context
Heterogeneous sensors require a uniform ingestion protocol across LoRaWAN, Cellular, and Wi-Fi gateways.

## Decision
Standardize `tnx/<org>/farm/<farm>/device/<device>/telemetry` topic hierarchy with ISO-8601 timestamps and typed measurement arrays.

## Consequences
High throughput schema validation and seamless Kafka/MQTT bridge processing.