# TerraNexus Platform — Master QA Test Plan (IEEE 829 Standard)

**Document Reference**: TNX-QA-MTP-001  
**Version**: 1.0.0 (Production Release Gate)  
**Classification**: Engineering Quality Assurance Specification  
**System**: TerraNexus Open Agricultural Intelligence & Operations Platform  

---

## 1. Executive Summary & Purpose

The purpose of this Master Test Plan (MTP) is to define the holistic quality assurance strategy, test architecture, verification methods, risk management framework, and release acceptance criteria for the TerraNexus platform.

TerraNexus integrates physical edge hardware (ESP32 microcontrollers, relays, solenoids, capacitive sensors), a Python FastAPI modular monolith, PostGIS spatial data stores, local AI inference engines (QVAC), and offline-first mobile and web clients. Because actuation commands directly control high-power water pumps and agricultural field infrastructure, software quality directly impacts physical safety, crop preservation, and electrical/mechanical equipment protection.

This plan details the testing approach spanning:
- Unit & Module Isolation Testing
- Functional & Contract API Testing
- End-to-End System Flow Verification
- Critical Physical Safety Boundary & Hardware Interlock Assurance
- Offline-First Synchronization & Conflict Resolution Rig
- Edge Node & Firmware Logic Emulation
- Security Penetration & Vulnerability Testing (OWASP API Top 10)
- Performance, Scalability & Stress Profiling

---

## 2. Test Strategy & Architectural Scope

```
+----------------------------------------------------------------------------------+
|                             TERRANEXUS TEST PYRAMID                              |
+----------------------------------------------------------------------------------+
|                                                                                  |
|                                     / \                                          |
|                                    /   \                                         |
|                                   / E2E \  --> 22 Subsystem Automated Rig        |
|                                  /-------\                                       |
|                                 / Security\ --> OWASP API Top 10 & DAST Injections|
|                                /-----------\                                     |
|                               / Performance \ --> Concurrency & Ingestion Loads |
|                              /---------------\                                   |
|                             / Physical Safety \ --> Actuation Preflights & Watchdog|
|                            /-------------------\                                 |
|                           / Integration & Sync  \ --> Offline Push/Pull & Conflicts|
|                          /-----------------------\                               |
|                         /   Component & API Tests  \ --> 14 Domain Modules       |
|                        /-----------------------------\                           |
|                       /    Unit & Logic Validation    \ --> FAO-56 & Calibrations|
|                      +---------------------------------+                         |
+----------------------------------------------------------------------------------+
```

### 2.1 Modules In-Scope
1. **Core Infrastructure**: Database connection management, SQLite/PostgreSQL failover, PBKDF2 password security, RFC 7807 problem details error handling, request ID tracing.
2. **Identity & Access Management**: JWT token issuance, session validation, Role-Based Access Control (RBAC: Admin, Agronomist, Operator), multi-tenant organisation isolation.
3. **Farms & Spatial Assets**: PostGIS geospatial boundaries, field plot partitioning, soil texture profiles (AWC, field capacity, wilting point), field scouting observations.
4. **Agriculture & Crop Science**: Crop varieties, FAO-56 growth stages ($K_{cb}$, $K_{c\text{ mid}}$, $K_{c\text{ end}}$), seasonal plantings, yield records.
5. **Edge Device Registry & Lifecycle**: Device enrollment, hardware cryptographic tokens, provisioning state machine, sensor channel calibration curves, command dispatch & receipt acknowledgement.
6. **High-Throughput Telemetry Pipeline**: Canonical JSON envelope validation, out-of-range sensor screening, duplicate suppression, time-series storage, MQTT bridge consumer.
7. **Physical Irrigation Safety & Actuation Rig**: Dual-layer preflight interlocks, hardware watchdog enforcement ($\le 1800\text{s}$), hardwired Emergency Stop override, pump conflict avoidance, water source capacity depletion guards.
8. **Operations & Maintenance**: Farm tasks state machine, equipment maintenance intervals, inventory stock tracking with negative balance guards, harvest lot traceability.
9. **Monitoring & Real-Time Alert Engine**: Rule evaluations, multi-level alert thresholds (INFO, WARNING, CRITICAL), state progression (ACTIVE $\to$ ACKNOWLEDGED $\to$ RESOLVED), delivery receipts.
10. **Agronomic Intelligence & Local QVAC Reasoning**: Daily evapotranspiration ($ET_0$) calculation, soil moisture depletion percentage, irrigation volume advisory generation, local offline LLM reasoning fallback.
11. **Offline-First Synchronization Engine (TNX-SYNC-001)**: Client registration, vector cursor tracking, push mutation batch queue, idempotent upserts, conflict resolution policies (`server_wins`, `client_wins`).
12. **Developer APIs & Integrations**: Application registration, scoped API key authentication (`tnx_live_...`), HMAC-SHA256 webhook signatures.
13. **Reporting & Auditing**: Aggregated operational farm analytics, water efficiency metrics, tamper-evident audit logs.
14. **Firmware Logic & Safety**: ESP32 ADC calibration, circular flash spooling (SPIFFS), hardware watchdog timers, active-LOW relay fail-safe states.

---

## 3. Test Levels & Methodology

| Test Level | Scope | Primary Tools | Execution Frequency | Target Pass Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Unit Testing** | Individual classes, mathematical algorithms (FAO-56, calibrations), security hashing | `pytest` | Continuous | 100% |
| **API Contract** | All 14 REST module routers, HTTP status codes, JSON schema schemas | `pytest`, `fastapi.testclient` | Every build | 100% |
| **Safety Interlock** | Preflight checks, hardware watchdog limit, emergency stop latch | `pytest` dedicated safety rig | Every build | 100% (Zero-tolerance) |
| **Integration** | DB transactions, SQLite/PostGIS schema execution, MQTT consumer | `pytest`, `paho-mqtt` | Every build | 100% |
| **Offline Sync** | Mobile offline mutation queues, cursor updates, conflict policies | `pytest` sync rig | Every build | 100% |
| **Security & DAST**| SQL injection, XSS vectors, token tampering, broken object authorization | Custom security test suite | Release gate | 100% (Zero vulnerabilities) |
| **Performance** | Telemetry ingestion load (1,000 pts/sec), P50/P95/P99 latency | Custom multi-threaded benchmark | Release gate | P95 < 50ms |
| **End-to-End** | 22-step full lifecycle verification script | `scripts/verify_e2e.py` | Release gate | 22/22 Passing |

---

## 4. Defect Severity & Priority Classification

### 4.1 Severity Levels
- **S1 (Blocker / Critical Safety)**: Any failure in the physical safety interlock (e.g., pump fails to shut down on emergency stop, watchdog timeout ignored, actuation allowed without water source check), data corruption in authoritative storage, or critical security bypass (unauthenticated access to admin endpoints).
- **S2 (Major)**: Functional failure in primary business workflow (e.g., offline sync batch dropped, telemetry ingestion failing for valid schema, recommendation generation crash).
- **S3 (Minor)**: Non-blocking functional defect with an operational workaround (e.g., minor UI rendering glitch, non-critical field observation filter error).
- **S4 (Trivial)**: Cosmetic defect, typo in documentation or log message formatting.

### 4.2 Priority Levels
- **P1 (Immediate)**: Must be resolved prior to any release or physical field test deployment.
- **P2 (High)**: Must be resolved before general production availability.
- **P3 (Medium)**: Scheduled for next minor sprint release.
- **P4 (Low)**: Backlog improvement item.

---

## 5. Release Entry & Exit Gates

### 5.1 Entry Criteria to QA Validation
1. Backend modular monolith starts without syntax or dependency errors.
2. All 8 database migration scripts apply sequentially without error.
3. Seed dataset loads successfully into the local and authoritative databases.
4. Firmware compiles cleanly using PlatformIO.
5. Frontend compiles cleanly with `vite build` without TypeScript errors.

### 5.2 Release Exit Criteria (Sign-Off Gates)
1. **100% Pass Rate** on all automated Pytest functional and integration test suites.
2. **Zero S1 or S2 defects** remaining open.
3. **100% Safety Compliance**: All physical safety preflights and emergency interlocks verified.
4. **Offline Sync Integrity**: 100% data consistency verified across push/pull cycles with zero unhandled conflict states.
5. **Security Validation**: Zero high or critical OWASP vulnerabilities detected.
6. **Performance Verified**: Telemetry ingestion sustains $> 1000\text{ metrics/second}$ with $P_{95} \le 50\text{ms}$.
7. **22/22 Subsystems Passing** on `scripts/verify_e2e.py`.
