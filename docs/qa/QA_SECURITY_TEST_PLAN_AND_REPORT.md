# TerraNexus — Security Test Plan & Vulnerability Assessment (OWASP API Top 10)

**Document Reference**: TNX-QA-SEC-001  
**Version**: 1.0.0  
**Methodology**: OWASP API Security Top 10 (2023), STRIDE Threat Modeling, DAST Penetration Testing  
**Audit Scope**: All REST endpoints, WebSocket/MQTT brokers, Authentication mechanisms, Physical safety boundaries  

---

## 1. Threat Modeling & Attack Surfaces (STRIDE)

| Threat Category | Potential Attack Vector | TerraNexus Defense Architecture | Test Verification Case |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Rogue ESP32 device impersonating a registered node | Unique per-device pre-shared cryptographic tokens, MAC binding | `TC-DEV-002`, `TC-AUTH-003` |
| **Tampering** | Man-in-the-middle altering irrigation duration payload | Cryptographic JWT signatures, hardware-enforced 1800s watchdog | `TC-AUTH-003`, `TC-SAFE-003` |
| **Repudiation** | Operator denying triggering emergency shutdown or pump start | Append-only immutable `security_audit_log` with user UUID & IP | `TC-OPS-001`, `TC-SEC-003` |
| **Information Disclosure** | Unauthorized tenant reading another farm's soil & yield data | Multi-tenant organization scoping enforced on all database queries | `TC-SEC-003` |
| **Denial of Service** | Flooding telemetry ingestion endpoint to cause OOM | Async background queue, payload size limits, database pooling | `TC-PERF-001` |
| **Elevation of Privilege** | Farm worker attempting to invoke admin audit or wipe database | Strict RBAC matrix (`admin`, `agronomist`, `operator`) | `TC-AUTH-004` |

---

## 2. OWASP API Security Top 10 (2023) Assessment Results

### API1:2023 — Broken Object Level Authorization (BOLA)
- **Vulnerability Description**: An attacker manipulates an entity ID in an API request to view or edit another user's or farm's resources.
- **TerraNexus Implementation**: Every entity query explicitly joins or filters by the authenticated user's `organisation_id`.
- **Test Case**: User from Organisation A attempts to access `GET /api/v1/farms/{farm_b_id}`.
- **Result**: **PASS**. Returns `404 Not Found` or `403 Forbidden`. No cross-tenant data leakage.

### API2:2023 — Broken Authentication
- **Vulnerability Description**: Weak password hashing, predictable tokens, or flawed session management.
- **TerraNexus Implementation**: Password storage uses PBKDF2-HMAC-SHA256 with 100,000+ iterations and per-user cryptographic salts. JWTs are signed with HMAC-SHA256 and have explicit 60-minute expiration.
- **Test Case**: Weak password bruteforce simulation, expired token submission, tampered signature submission.
- **Result**: **PASS**. All unauthorized or tampered tokens rejected with HTTP 401.

### API3:2023 — Broken Object Property Level Authorization
- **Vulnerability Description**: Mass assignment vulnerabilities allowing users to overwrite sensitive fields (e.g. `is_superuser`, `role`).
- **TerraNexus Implementation**: Strict Pydantic input schemas separate creation/update schemas from internal entity models.
- **Test Case**: Non-admin user posts `{"role": "super_admin"}` to profile update endpoint.
- **Result**: **PASS**. Role mutation ignored or rejected.

### API4:2023 — Unrestricted Resource Consumption
- **Vulnerability Description**: DoS via unconstrained payload sizes, unbounded time-series queries, or excessive concurrent requests.
- **TerraNexus Implementation**: FastAPI request size limits, time-series query limits (`limit=100`, max 1000), pagination on all collections.
- **Test Case**: Query `GET /api/v1/measurements` with no limit; benchmark response payload size.
- **Result**: **PASS**. Capped cleanly with default pagination.

### API5:2023 — Broken Function Level Authorization
- **Vulnerability Description**: Missing access control checks on privileged management actions (e.g., audit logs, device wipe).
- **TerraNexus Implementation**: `get_current_admin_user` dependency guards all `/api/v1/admin/*` routes.
- **Test Case**: Standard operator requests `/api/v1/admin/audit`.
- **Result**: **PASS**. HTTP 403 Forbidden returned.

### API6:2023 — Unrestricted Access to Sensitive Business Flows
- **Vulnerability Description**: Automated botting of critical actuation actions (e.g. mass triggering irrigation solenoids).
- **TerraNexus Implementation**: Dual-layer preflight interlocks validate water source levels, pump health, and active emergency stop flags before queuing commands.
- **Test Case**: Scripted bursts of rapid start commands dispatched to same pump.
- **Result**: **PASS**. Interlocks prevent conflicting or duplicate runs; only one active run permitted per zone.

### API7:2023 — Server-Side Request Forgery (SSRF)
- **Vulnerability Description**: Supplying arbitrary URLs for webhooks to probe internal cloud network.
- **TerraNexus Implementation**: Webhook destination URLs are validated; internal network IP ranges (127.0.0.1, 169.254.169.254, RFC 1918) are blocked for non-admin setups.
- **Result**: **PASS**.

### API8:2023 — Security Misconfiguration
- **Vulnerability Description**: Exposed debug endpoints, stack traces in production error responses.
- **TerraNexus Implementation**: RFC 7807 problem details error responses with masked stack traces in production mode.
- **Result**: **PASS**. Clean JSON error objects returned.

### API9:2023 — Improper Inventory Management
- **Vulnerability Description**: Deprecated or unversioned APIs left exposed.
- **TerraNexus Implementation**: All endpoints explicitly versioned under `/api/v1/`.
- **Result**: **PASS**.

### API10:2023 — Unsafe Consumption of APIs
- **Vulnerability Description**: Blindly trusting third-party weather or satellite API responses.
- **TerraNexus Implementation**: Input validation schemas for all external weather connectors with fallback defaults.
- **Result**: **PASS**.

---

## 3. Physical Safety Security Assurance

Because TerraNexus interfaces with high-voltage 240V/415V three-phase pumps:
1. **Cloud Loss-of-Signal**: If the cloud connection drops during an active irrigation run, the local microcontroller hardware watchdog shuts down the pump at `1800s`.
2. **Hardwired Kill Switch**: Physical GPIO 14 hardware interrupt halts relays within $< 1\text{ ms}$, entirely bypassing software loops.
3. **Fail-Closed Relays**: Active-LOW optocoupled relays ensure that MCU reset or power failure leaves all valves CLOSED and pumps DE-ENERGIZED.
