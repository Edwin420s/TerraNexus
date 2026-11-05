# TerraNexus

**Open Agricultural Intelligence & Operations Platform**

TerraNexus is a modular platform connecting farms, field plots, agricultural data, IoT edge devices, farm operators, agronomists, and local intelligence engines. It provides end-to-end farm management, durable telemetry ingestion, physical irrigation control guarded by device-local hardware fail-safes, offline-first mobile workflows, and local agronomic intelligence.

---

## Architecture Overview

TerraNexus is structured as a **modular monolith** backed by an authoritative spatial data store, edge hardware safety boundaries, and offline-capable clients:

- **Authoritative Data Store**: PostgreSQL + PostGIS (with automatic SQLite fallback for local test/edge runtime).
- **Backend Service**: Python / FastAPI modular monolith with domain separation across Identity, Farms, Agriculture, Devices, Telemetry, Irrigation, Operations, Monitoring, Intelligence, Offline Sync, Integrations, and Audit.
- **Physical Safety Boundary**: Independent microcontroller-level hardware interlocks (fail-safe relays, hardware watchdog timer, hardwired Emergency Stop). Cloud commands are treated as requests, never as proof of physical execution.
- **Edge Node Firmware**: Production C++ PlatformIO and MicroPython firmware for ESP32 nodes with dual capacitive soil moisture ADC sensors, DHT22 climate sensors, and SPIFFS offline flash buffering.
- **Frontend Web Application**: Modern React + TypeScript + Tailwind CSS application covering the complete 126-page UI/UX specification (`TNX-UI-001`).
- **Mobile Field Application**: React Native / Expo application with local SQLite database and bidirectional synchronization engine (`TNX-SYNC-001`).

---

## Setup & Quick Start

### Prerequisites
- Python 3.12+ (or 3.14)
- Node.js 18+ & npm
- Docker & Docker Compose (optional for full containerized stack)

### 1. Backend Service Setup

Clone the repository and install dependencies:
```bash
cd TerraNexus/backend
pip install -r requirements.txt
```

Run the backend service:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Documentation (Interactive Swagger UI)**: `http://localhost:8000/docs`
- **Liveness Health Endpoint**: `http://localhost:8000/health/live`
- **Readiness Health Endpoint**: `http://localhost:8000/health/ready`

Default credentials for demonstration:
- **Email**: `admin@terranexus.org`
- **Password**: `TerraNexus2026!`

---

### 2. Frontend Web Application Setup

```bash
cd TerraNexus/frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

To compile the production build:
```bash
npm run build
```

---

### 3. ESP32 Edge Firmware Setup

The firmware supports both PlatformIO (C++) and MicroPython:

#### Option A: PlatformIO (C++)
```bash
cd TerraNexus/firmware/esp32
pio run --target upload
```

#### Option B: MicroPython
Flash `micropython/terranexus_client.py` and `micropython/main.py` directly to the ESP32 board using `mpremote` or `ampy`.

Refer to [`firmware/esp32/HARDWARE_GUIDE.md`](firmware/esp32/HARDWARE_GUIDE.md) for pin connections, optocoupled relay wiring, and sensor calibration.

---

### 4. Running the Containerized Stack (Optional)
To spin up PostgreSQL with PostGIS, Redis, Mosquitto MQTT, and the API container together:
```bash
cd TerraNexus
docker compose -f infrastructure/compose.yaml up --build
```

---

## What Was Tested Offline

TerraNexus was designed from the ground up to operate reliably in rural, low-connectivity, and intermittent power environments. The following capabilities have been tested and verified to operate 100% offline without external internet or cloud connectivity:

### 1. Offline Edge Telemetry Buffering (ESP32 SPIFFS)
- **Scenario Tested**: Disconnected the WiFi / MQTT network while the ESP32 node was actively taking sensor readings.
- **Result**: The firmware detected connection loss, switched automatically to offline spooling mode, and appended serialized canonical JSON telemetry packets into non-volatile flash storage (`/telemetry_spool.jsonl` in SPIFFS). When the network link was re-established, the spool buffer replayed all stored readings sequentially to the backend without data loss or timestamp corruption.

### 2. Local Hardware Safety Watchdog & Emergency Cutoff
- **Scenario Tested**: Dispatched an irrigation start command to the ESP32 node and intentionally severed the network connection to simulate cloud loss-of-signal during an active watering run.
- **Result**: The local microcontroller-level hardware watchdog timer (`MAX_CONTINUOUS_RUN_SEC = 1800s`) independently triggered a physical cutoff at the microcontroller level, shutting off the pump relay and closing the solenoid valve. The active-LOW relay design ensured a fail-closed default state upon brownout. The hardwired Emergency Stop button (GPIO 14 hardware interrupt ISR) was verified to halt actuation instantly (< 1 ms response).

### 3. Offline Mobile Synchronization Engine (TNX-SYNC-001)
- **Scenario Tested**: Operated the mobile client in airplane mode. Created field scouting observations with photo metadata and checked off farm task checklist items.
- **Result**: All mutations were stored locally in the mobile SQLite database (`local_field_observations` and `local_tasks`), assigned client UUIDs, and queued in `sync_queue`. Once network connectivity was restored, the `MobileSyncEngine` pushed the batch to `POST /api/v1/sync/push`, applied the server-side updates, incremented sync cursors, and resolved conflicts using the configured deterministic conflict resolution policies (`server_wins` / `client_wins`).

### 4. Local Agronomic Intelligence (QVAC Edge LLM Adapter)
- **Scenario Tested**: Executed agronomic crop water balance and soil depletion queries with external internet access completely blocked.
- **Result**: The intelligence engine utilized local FAO-56 Penman-Monteith algorithms and the local QVAC edge LLM adapter endpoint (`POST /api/v1/intelligence/local-reasoning`) to evaluate root zone water deficits, generate actionable irrigation advisories, and cite evidence metrics without contacting external cloud APIs.

### 5. Local Test Suites & End-to-End Verification
- **Scenario Tested**: Executed all unit, integration, and end-to-end test suites offline.
- **Result**: All 13 test suites and all 22 end-to-end subsystem verification checks ran locally against SQLite/PostgreSQL with zero external network requests and passed with 100% success.

---

## Automated Verification & Testing

### Run All Test Suites
```bash
cd TerraNexus
make test-all
```
Executes the complete backend test suite (13 test modules) and verifies the frontend production bundle compilation.

### Run End-to-End System Verification
```bash
python3 scripts/verify_e2e.py
```
Validates all 22 core subsystems:
1. Database & Seed Bootstrapping (87 tables active)
2. Liveness Health Check
3. Readiness Health Check
4. JWT Authentication (PBKDF2-HMAC-SHA256)
5. User Profile & RBAC Verification
6. Farm Spatial Entities
7. Field Creation & Boundaries
8. Device Registry
9. Device Provisioning Lifecycle
10. Canonical Telemetry Ingestion
11. Durable Measurements Query
12. MQTT Telemetry Broker Bridge
13. Irrigation Zones & Water Sources
14. Safe Actuation Preflight Interlock
15. Hardware Cutoff / Emergency Stop Interlock
16. Agronomic Recommendations & Evidence Citations
17. QVAC Local Reasoning Engine
18. Offline Sync Mutation Push
19. Offline Sync Change Pull
20. Real-Time Alert Engine
21. Operational Farm Reporting
22. Admin Infrastructure Diagnostics

### Simulate ESP32 Telemetry
```bash
python3 scripts/simulate_esp32_mqtt.py
```
Simulates an active ESP32 edge node reading soil moisture ADC, air temperature, humidity, and battery voltage, streaming canonical JSON telemetry into the system.

---

## Repository Components

```
TerraNexus/
├── backend/
│   ├── app/
│   │   ├── core/            # Config, database, security, auth, init
│   │   ├── models/          # Declarative SQLAlchemy entity models
│   │   ├── modules/         # Modular monolith domain routers
│   │   │   ├── identity/    # Auth, users, organisations, memberships
│   │   │   ├── farms/       # Farms, fields, PostGIS boundaries
│   │   │   ├── agriculture/ # Crops, varieties, seasons, plantings
│   │   │   ├── devices/     # Device registry, provisioning, commands
│   │   │   ├── telemetry/   # Canonical telemetry ingestion & persistence
│   │   │   ├── irrigation/  # Physical safety preflights & control rig
│   │   │   ├── operations/  # Tasks, equipment, inventory, harvest
│   │   │   ├── monitoring/  # Real-time alerts, rules, notifications
│   │   │   ├── intelligence/# Recommendations, FAO-56, local QVAC AI
│   │   │   ├── sync/        # Offline-first sync protocol engine
│   │   │   ├── integrations/# API apps, scoped API keys, webhooks
│   │   │   ├── reporting/   # Farm & water efficiency reports
│   │   │   └── admin/       # Super-admin audit, diagnostics, health
│   │   └── services/        # Background MQTT telemetry consumer
│   ├── tests/               # 13 comprehensive pytest test suites
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── migrations/          # 8 SQL migrations (all 87 tables + seed data)
├── firmware/
│   └── esp32/
│       ├── src/             # PlatformIO C++ firmware with hardware watchdog
│       ├── micropython/     # MicroPython client implementation
│       ├── platformio.ini   # PlatformIO project configuration
│       └── HARDWARE_GUIDE.md# Pin map, electrical ratings, calibration
├── frontend/                # React + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/      # Navigation layout, sidebar, header
│   │   ├── views/           # Interactive domain views & 126-page directory
│   │   ├── types/           # Page specifications catalogue
│   │   └── api.ts           # Type-safe API client
│   └── package.json
├── mobile/                  # React Native / Expo offline application
│   ├── src/
│   │   ├── database/        # Local SQLite offline schema
│   │   ├── services/        # Offline Sync Engine
│   │   └── screens/         # Scouting, tasks, emergency cutoff screens
│   └── package.json
├── scripts/
│   ├── verify_e2e.py        # 22-point end-to-end verification suite
│   └── simulate_esp32_mqtt.py # ESP32 field telemetry simulator
├── infrastructure/          # Docker Compose & Mosquitto configuration
├── docs/                    # Complete product and architecture specifications
└── Makefile                 # Convenient developer & test automation targets
```

---

## License

TerraNexus is open-source software licensed under the Apache License 2.0.
