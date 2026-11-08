# TerraNexus — Formal QA Test Cases Specification

**Document Reference**: TNX-QA-TCS-001  
**Version**: 1.0.0  
**Scope**: Full End-to-End Functional, Safety, Security, Offline Sync, and Performance Verification  

---

## 1. Authentication, Identity & RBAC Test Cases

### TC-AUTH-001: Cryptographic Password Hash Verification
- **Description**: Verify user passwords are encrypted using PBKDF2-HMAC-SHA256 with random salt, never stored in plaintext.
- **Preconditions**: Clean database session.
- **Inputs**: User registration with password `"ComplexPass2026!"`.
- **Expected Results**: Stored password hash matches `$pbkdf2-sha256$...`, salt length $\ge 16$ bytes, plaintext password not found anywhere in database.
- **Severity**: S1 | **Priority**: P1

### TC-AUTH-002: JWT Token Lifecycle & Expiration
- **Description**: Verify JWT access tokens expire after configured TTL (60 minutes) and expired tokens are rejected with `401 Unauthorized`.
- **Preconditions**: Valid user registered.
- **Inputs**: Request `/api/v1/auth/me` with an expired JWT token.
- **Expected Results**: HTTP 401 Unauthorized with RFC 7807 problem details message `"Token has expired"`.
- **Severity**: S1 | **Priority**: P1

### TC-AUTH-003: Tampered JWT Signature Rejection
- **Description**: Verify tampering with JWT payload or signature is detected and rejected.
- **Preconditions**: Valid token generated for user `operator@terranexus.org`.
- **Inputs**: Mutate token payload to change role to `"super_admin"` while keeping signature.
- **Expected Results**: HTTP 401 Unauthorized with `"Could not validate credentials"`.
- **Severity**: S1 | **Priority**: P1

### TC-AUTH-004: Role-Based Access Control (RBAC) Enforcement
- **Description**: Verify Farm Operator role cannot access Super Admin endpoints (`/api/v1/admin/audit`).
- **Preconditions**: Authenticated user with role `"operator"`.
- **Inputs**: `GET /api/v1/admin/audit` with Operator Bearer token.
- **Expected Results**: HTTP 403 Forbidden with `"Insufficient permissions"`.
- **Severity**: S1 | **Priority**: P1

---

## 2. Geospatial Assets & Field Management Test Cases

### TC-FARM-001: Farm Spatial Multi-Polygon Validation
- **Description**: Create farm with valid GeoJSON coordinates and verify area calculation.
- **Preconditions**: Authenticated Farm Admin.
- **Inputs**: `POST /api/v1/farms` with boundary coordinates enclosing 25.5 hectares in Nakuru, Kenya.
- **Expected Results**: HTTP 201 Created with valid UUID, spatial geometry persisted, status active.
- **Severity**: S2 | **Priority**: P2

### TC-FARM-002: Field Plot Partitioning & Soil Attachment
- **Description**: Attach field plot to farm with specific soil texture profile (Clay Loam).
- **Preconditions**: Farm `farm_id` exists.
- **Inputs**: `POST /api/v1/fields` with soil parameters: `field_capacity: 0.32`, `wilting_point: 0.18`.
- **Expected Results**: HTTP 201 Created, field bound to farm, Available Water Capacity (AWC) calculated as $0.14\text{ m}^3/\text{m}^3$.
- **Severity**: S2 | **Priority**: P2

---

## 3. IoT Edge Device & Telemetry Pipeline Test Cases

### TC-DEV-001: Device Provisioning State Machine
- **Description**: Transition edge device from REGISTERED $\to$ PROVISIONING $\to$ ACTIVE upon initial handshake.
- **Preconditions**: Device record created with MAC `A4:CF:12:89:FE:01`.
- **Inputs**: `POST /api/v1/devices/{device_id}/provision` with device public key.
- **Expected Results**: HTTP 200 OK, device status transitions to `active`, device auth token issued.
- **Severity**: S2 | **Priority**: P1

### TC-TELEM-001: Canonical Telemetry Envelope Validation
- **Description**: Ingest standard canonical JSON telemetry packet from field node.
- **Preconditions**: Active device `dev-esp32-001`.
- **Inputs**: `POST /api/v1/telemetry` with measurements: soil moisture (28.4%), ambient temp (23.5°C), humidity (65%).
- **Expected Results**: HTTP 202 Accepted, telemetry ingested, measurements queryable via `GET /api/v1/measurements`.
- **Severity**: S1 | **Priority**: P1

### TC-TELEM-002: Out-of-Range Sensor Value Handling
- **Description**: Ingest sensor reading with out-of-physical-range data (soil moisture -15% or 180%).
- **Preconditions**: Active device.
- **Inputs**: `POST /api/v1/telemetry` with `soil_moisture: -15.0`.
- **Expected Results**: Value flagged with quality tag `SUSPECT` or rejected with `422 Unprocessable Entity`; does not corrupt agronomic calculations.
- **Severity**: S2 | **Priority**: P2

---

## 4. Physical Irrigation Safety & Interlock Test Cases (Critical)

### TC-SAFE-001: Water Source Depletion Preflight Guard
- **Description**: Attempt to start irrigation when water source capacity is below critical safety threshold (< 10%).
- **Preconditions**: Water reservoir level at 5% capacity.
- **Inputs**: `POST /api/v1/irrigation/control/start` for Zone 1 linked to depleted reservoir.
- **Expected Results**: HTTP 400 Bad Request, actuation rejected with `"Preflight failed: Water source capacity below safety reserve limit"`. Pump remains OFF.
- **Severity**: S1 | **Priority**: P1

### TC-SAFE-002: Inactive / Faulted Pump Interlock
- **Description**: Attempt to start irrigation when assigned borehole pump is in MAINTENANCE or FAULT state.
- **Preconditions**: Borehole Pump status set to `FAULT`.
- **Inputs**: `POST /api/v1/irrigation/control/start` targeting Zone 1.
- **Expected Results**: HTTP 400 Bad Request with `"Preflight failed: Assigned pump is faulted or offline"`.
- **Severity**: S1 | **Priority**: P1

### TC-SAFE-003: Hardware Watchdog Duration Cap Enforcement
- **Description**: Enforce maximum continuous run duration ($\le 1800\text{ seconds}$) on cloud commands.
- **Preconditions**: Safe operational state.
- **Inputs**: `POST /api/v1/irrigation/control/start` requesting duration `3600` seconds.
- **Expected Results**: HTTP 400 Bad Request or automatically clamped to 1800s with safety warning logged.
- **Severity**: S1 | **Priority**: P1

### TC-SAFE-004: Hardwired Emergency Stop Override Verification
- **Description**: When emergency stop button is latched, all pending and active actuation commands must be aborted immediately and new start requests blocked.
- **Preconditions**: Emergency Stop triggered on farm.
- **Inputs**: `POST /api/v1/irrigation/control/start` while E-Stop is active.
- **Expected Results**: HTTP 400/409 Conflict with `"Actuation blocked: Emergency stop is active"`.
- **Severity**: S1 | **Priority**: P1

---

## 5. Offline-First Mobile Sync Engine (TNX-SYNC-001) Test Cases

### TC-SYNC-001: Batch Mutation Push & Deduplication
- **Description**: Push offline scouting observations and task completions with client-generated UUIDs.
- **Preconditions**: Client device registered with sync cursor.
- **Inputs**: `POST /api/v1/sync/push` containing 10 offline mutations. Replay exact same payload a second time.
- **Expected Results**: First push applies all 10 records. Second push detects duplicate `client_uuid`s, processes idempotently without duplicating entities, returns 200 OK.
- **Severity**: S1 | **Priority**: P1

### TC-SYNC-002: Deterministic Conflict Resolution
- **Description**: Resolve concurrent mutations on same task status using `server_wins` and `client_wins` policies.
- **Preconditions**: Task exists on server with status `in_progress`.
- **Inputs**: Client pushes update setting status to `cancelled` with resolution policy `server_wins`.
- **Expected Results**: Server preserves authoritative state, records conflict record in `sync_conflicts` table, notifies client with current server entity.
- **Severity**: S1 | **Priority**: P1

---

## 6. Agronomic Intelligence & Local FAO-56 Test Cases

### TC-INTEL-001: FAO-56 Water Deficit Calculation
- **Description**: Calculate root zone depletion and daily water requirement for Maize at mid-season ($K_c = 1.2$).
- **Preconditions**: Field planted with Maize at Day 65, $ET_0 = 4.8\text{ mm/day}$, soil moisture at 18% (PWP = 15%, FC = 30%).
- **Inputs**: `GET /api/v1/intelligence/recommendations` for field.
- **Expected Results**: Recommendation generated with status `pending`, recommended irrigation depth $\approx 18.5\text{ mm}$, evidence metrics cited.
- **Severity**: S2 | **Priority**: P2

### TC-INTEL-002: Local QVAC Reasoning Offline Fallback
- **Description**: Query local AI reasoning endpoint when cloud network is completely unavailable.
- **Preconditions**: External internet connection blocked.
- **Inputs**: `POST /api/v1/intelligence/local-reasoning` with prompt and sensor context.
- **Expected Results**: HTTP 200 OK returned with deterministic local agronomic reasoning explanation, citing soil moisture trend and weather outlook.
- **Severity**: S2 | **Priority**: P2

---

## 7. Security Penetration & DAST Test Cases

### TC-SEC-001: SQL Injection Probing
- **Description**: Inject SQL injection payloads (`' OR '1'='1`, `'; DROP TABLE users; --`) into query parameters and JSON fields.
- **Inputs**: Filter parameters on `/api/v1/measurements?device_id=' OR 1=1--`.
- **Expected Results**: Parameterized queries prevent injection, returns empty result or HTTP 422, zero syntax errors exposed.
- **Severity**: S1 | **Priority**: P1

### TC-SEC-002: XSS Vector Neutralization
- **Description**: Submit stored Cross-Site Scripting (XSS) payloads in field observation notes.
- **Inputs**: Observation note containing `<script>alert('XSS')</script>`.
- **Expected Results**: Content stored safely as plain string, HTML-escaped upon serialization, script execution prevented.
- **Severity**: S2 | **Priority**: P1

---

## 8. Performance & Stress Test Cases

### TC-PERF-001: High-Volume Telemetry Ingestion Rate
- **Description**: Ingest 1,000 telemetry packets in rapid succession across 50 simulated edge devices.
- **Inputs**: Concurrent HTTP POST requests to `/api/v1/telemetry`.
- **Expected Results**: Sustained throughput $> 500\text{ packets/second}$, error rate $0.0\%$, $P_{95}\text{ latency} < 50\text{ms}$.
- **Severity**: S2 | **Priority**: P2
