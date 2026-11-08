# TerraNexus — Requirements Traceability Matrix (RTM)

**Document Reference**: TNX-QA-RTM-001  
**Version**: 1.0.0  
**Specification Baseline**: `TNX-ARCH-001`, `TNX-DATA-001`, `TNX-SYNC-001`, `TNX-UI-001`, Hardware Guide  

---

## Traceability Mapping Table

| Requirement ID | Specification Source | Requirement Description | Automated Test Suite | Test Case ID(s) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-CORE-001** | TNX-ARCH-001 §2.1 | Liveness probe returns `200 OK` and readiness probe checks DB status | `test_qa_auth_rbac_security.py` | `TC-CORE-001`, `TC-CORE-002` | **VERIFIED** |
| **REQ-AUTH-001** | TNX-ARCH-001 §11.1 | Password hashing using PBKDF2-HMAC-SHA256 with cryptographic salt | `test_qa_auth_rbac_security.py` | `TC-AUTH-001` | **VERIFIED** |
| **REQ-AUTH-002** | TNX-ARCH-001 §11.2 | JWT Bearer token generation with expiry and cryptographic signature | `test_qa_auth_rbac_security.py` | `TC-AUTH-002`, `TC-AUTH-003` | **VERIFIED** |
| **REQ-AUTH-003** | TNX-ARCH-001 §11.3 | RBAC role enforcement (Admin, Agronomist, Operator) on protected routes | `test_qa_auth_rbac_security.py` | `TC-AUTH-004`, `TC-AUTH-005` | **VERIFIED** |
| **REQ-FARM-001** | TNX-DATA-001 §3.1 | Farm spatial boundary registration with GeoJSON / PostGIS coordinates | `test_qa_farms_and_spatial.py` | `TC-FARM-001` | **VERIFIED** |
| **REQ-FARM-002** | TNX-DATA-001 §3.2 | Field plot creation, area calculation, and parent farm association | `test_qa_farms_and_spatial.py` | `TC-FARM-002`, `TC-FARM-003` | **VERIFIED** |
| **REQ-FARM-003** | TNX-DATA-001 §3.3 | Soil texture profile attachment (Field Capacity, Permanent Wilting Point) | `test_qa_farms_and_spatial.py` | `TC-FARM-004` | **VERIFIED** |
| **REQ-FARM-004** | TNX-DATA-001 §3.4 | Field scouting observations with GPS location and photo metadata | `test_qa_farms_and_spatial.py` | `TC-FARM-005` | **VERIFIED** |
| **REQ-AGRI-001** | TNX-DATA-001 §4.1 | Crop registry with FAO-56 dual crop coefficient growth stages ($K_{cb}$) | `test_qa_agriculture_and_crops.py` | `TC-AGRI-001` | **VERIFIED** |
| **REQ-AGRI-002** | TNX-DATA-001 §4.2 | Growing season management with start and end date validation | `test_qa_agriculture_and_crops.py` | `TC-AGRI-002` | **VERIFIED** |
| **REQ-AGRI-003** | TNX-DATA-001 §4.3 | Field planting allocation tracking with expected harvest calculation | `test_qa_agriculture_and_crops.py` | `TC-AGRI-003` | **VERIFIED** |
| **REQ-DEV-001** | TNX-ARCH-001 §3.1 | Hardware edge device registry with MAC address and hardware profile | `test_qa_devices_and_telemetry.py` | `TC-DEV-001` | **VERIFIED** |
| **REQ-DEV-002** | TNX-ARCH-001 §3.2 | Device provisioning workflow and cryptographic token issuance | `test_qa_devices_and_telemetry.py` | `TC-DEV-002` | **VERIFIED** |
| **REQ-DEV-003** | TNX-DATA-001 §5.2 | Sensor channels configuration with calibration slope and intercept | `test_qa_devices_and_telemetry.py` | `TC-DEV-003` | **VERIFIED** |
| **REQ-DEV-004** | TNX-ARCH-001 §3.3 | Durable device command dispatch with priority and execution state machine | `test_qa_devices_and_telemetry.py` | `TC-DEV-004`, `TC-DEV-005` | **VERIFIED** |
| **REQ-TELEM-001**| TNX-ARCH-001 §4.1 | Canonical JSON telemetry envelope ingestion (`event_id`, `schema_version`) | `test_qa_devices_and_telemetry.py` | `TC-TELEM-001` | **VERIFIED** |
| **REQ-TELEM-002**| TNX-DATA-001 §6.1 | Batch telemetry payload parsing and time-series measurement persistence | `test_qa_devices_and_telemetry.py` | `TC-TELEM-002` | **VERIFIED** |
| **REQ-TELEM-003**| TNX-DATA-001 §6.2 | Time-series query filtering by device, measurement type, and time window | `test_qa_devices_and_telemetry.py` | `TC-TELEM-003` | **VERIFIED** |
| **REQ-SAFE-001** | TNX-ARCH-001 §4.2 | Dual-layer actuation preflight check: water source capacity validation | `test_qa_irrigation_safety_critical.py` | `TC-SAFE-001` | **VERIFIED** |
| **REQ-SAFE-002** | TNX-ARCH-001 §4.3 | Dual-layer actuation preflight check: active pump and valid zone linkage | `test_qa_irrigation_safety_critical.py` | `TC-SAFE-002` | **VERIFIED** |
| **REQ-SAFE-003** | TNX-ARCH-001 §4.4 | Hardware watchdog duration enforcement ($\le 1800\text{ seconds}$) | `test_qa_irrigation_safety_critical.py` | `TC-SAFE-003` | **VERIFIED** |
| **REQ-SAFE-004** | TNX-ARCH-001 §4.5 | Hardwired Emergency Stop latch blocks all subsequent actuation dispatches | `test_qa_irrigation_safety_critical.py` | `TC-SAFE-004` | **VERIFIED** |
| **REQ-SAFE-005** | TNX-ARCH-001 §4.6 | Conflicting pump actuation rejection (prevents simultaneous overload) | `test_qa_irrigation_safety_critical.py` | `TC-SAFE-005` | **VERIFIED** |
| **REQ-OPS-001**  | TNX-DATA-001 §7.1 | Farm task lifecycle (CREATED $\to$ IN_PROGRESS $\to$ COMPLETED/CANCELLED) | `test_qa_operations_and_traceability.py`| `TC-OPS-001` | **VERIFIED** |
| **REQ-OPS-002**  | TNX-DATA-001 §7.2 | Equipment tracking and maintenance log records | `test_qa_operations_and_traceability.py`| `TC-OPS-002` | **VERIFIED** |
| **REQ-OPS-003**  | TNX-DATA-001 §7.3 | Inventory stock transactions with negative quantity prevention | `test_qa_operations_and_traceability.py`| `TC-OPS-003` | **VERIFIED** |
| **REQ-OPS-004**  | TNX-DATA-001 §7.4 | Harvest lot traceability linking yield quantity to specific field plot | `test_qa_operations_and_traceability.py`| `TC-OPS-004` | **VERIFIED** |
| **REQ-ALERT-001**| TNX-DATA-001 §8.1 | Alert rules evaluation with threshold conditions ($<$, $>$, $\le$, $\ge$) | `test_qa_monitoring_alerts.py` | `TC-ALERT-001` | **VERIFIED** |
| **REQ-ALERT-002**| TNX-DATA-001 §8.2 | Alert lifecycle state machine (ACTIVE $\to$ ACKNOWLEDGED $\to$ RESOLVED) | `test_qa_monitoring_alerts.py` | `TC-ALERT-002` | **VERIFIED** |
| **REQ-INTEL-001**| TNX-ARCH-001 §5.1 | FAO-56 Penman-Monteith crop water requirement calculation | `test_qa_intelligence_and_fao56.py` | `TC-INTEL-001` | **VERIFIED** |
| **REQ-INTEL-002**| TNX-ARCH-001 §5.2 | Agronomic irrigation recommendation with cited metric evidence | `test_qa_intelligence_and_fao56.py` | `TC-INTEL-002` | **VERIFIED** |
| **REQ-INTEL-003**| TNX-ARCH-001 §5.3 | Local QVAC LLM offline reasoning adapter with deterministic fallback | `test_qa_intelligence_and_fao56.py` | `TC-INTEL-003` | **VERIFIED** |
| **REQ-SYNC-001** | TNX-SYNC-001 §2.1 | Offline mobile client registration and cursor tracking | `test_qa_offline_sync_engine.py` | `TC-SYNC-001` | **VERIFIED** |
| **REQ-SYNC-002** | TNX-SYNC-001 §3.1 | Offline mutation push queue with client UUID idempotency | `test_qa_offline_sync_engine.py` | `TC-SYNC-002` | **VERIFIED** |
| **REQ-SYNC-003** | TNX-SYNC-001 §3.2 | Incremental pull synchronization using monotonic version cursors | `test_qa_offline_sync_engine.py` | `TC-SYNC-003` | **VERIFIED** |
| **REQ-SYNC-004** | TNX-SYNC-001 §4.1 | Deterministic conflict resolution (`server_wins` vs `client_wins`) | `test_qa_offline_sync_engine.py` | `TC-SYNC-004` | **VERIFIED** |
| **REQ-INTG-001** | TNX-DATA-001 §9.1 | Developer application keys issuance and scope enforcement | `test_qa_developer_integrations.py` | `TC-INTG-001` | **VERIFIED** |
| **REQ-INTG-002** | TNX-DATA-001 §9.2 | Webhook registration and HMAC-SHA256 payload signing | `test_qa_developer_integrations.py` | `TC-INTG-002` | **VERIFIED** |
| **REQ-SEC-001**  | TNX-ARCH-001 §11.4| SQL Injection resilience across all user input endpoints | `test_qa_security_injection.py` | `TC-SEC-001` | **VERIFIED** |
| **REQ-SEC-002**  | TNX-ARCH-001 §11.5| XSS payload sanitization on notes and text fields | `test_qa_security_injection.py` | `TC-SEC-002` | **VERIFIED** |
| **REQ-SEC-003**  | TNX-ARCH-001 §11.6| Multi-tenant data isolation enforcement across organisation boundaries | `test_qa_security_injection.py` | `TC-SEC-003` | **VERIFIED** |
| **REQ-PERF-001** | TNX-ARCH-001 §7.1 | High-throughput telemetry ingestion ($> 1000\text{ measurements/sec}$) | `test_qa_performance_stress.py` | `TC-PERF-001` | **VERIFIED** |
| **REQ-EDGE-001** | HARDWARE_GUIDE §3  | Dual-capacitive soil sensor ADC calibration curve conversion | `test_qa_firmware_harness.py` | `TC-EDGE-001` | **VERIFIED** |
| **REQ-EDGE-002** | HARDWARE_GUIDE §4  | SPIFFS circular buffer offline telemetry spooling upon WiFi disconnection | `test_qa_firmware_harness.py` | `TC-EDGE-002` | **VERIFIED** |
| **REQ-EDGE-003** | HARDWARE_GUIDE §5  | Hardware Watchdog countdown and GPIO 14 ISR Emergency Stop cutoffs | `test_qa_firmware_harness.py` | `TC-EDGE-003` | **VERIFIED** |
