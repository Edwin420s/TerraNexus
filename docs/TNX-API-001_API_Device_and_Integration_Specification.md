TerraNexus — TNX-API-001
COMPLETE API, DEVICE, TELEMETRY, COMMAND, SYNCHRONISATION AND INTEGRATION SPECIFICATION · VERSION 1.0
This document establishes the technical contract between the TerraNexus web application, mobile application, backend modules, database, IoT devices, external data providers and physical equipment.
It builds on the decisions already established:
Architecture: modular monolith first.
Primary database: PostgreSQL + PostGIS as the source of truth.
Backend direction: Python FastAPI.
Device communication: MQTT and HTTPS, with Bluetooth or gateway-assisted provisioning where needed.
Mobile operation: offline-first, with controlled synchronisation.
Physical control: independent safety and device-control boundaries.
Intelligence: recommendations are evidence-based; AI cannot bypass operational authorisation or equipment safety.
One important distinction: this is a proposed engineering contract, not a claim that every endpoint, device protocol or safety threshold has already been validated against production hardware. Exact hardware limits, provider-specific formats and deployment parameters must be confirmed before implementation.
TERRANEXUS
Complete API, Device and Integration Specification
Document ID: TNX-API-001
Version: 1.0
Status: Proposed engineering baseline
Product: Open Agricultural Intelligence and Operations Platform
API prefix: /api/v1
Primary backend: Python / FastAPI
Primary database: PostgreSQL + PostGIS
Messaging: MQTT
Architecture: Modular monolith with independently deployable infrastructure adapters and device-control boundaries

PART I — SYSTEM CONTRACT AND ARCHITECTURE
1. Purpose
TNX-API-001 defines how all TerraNexus components communicate.
It covers:
Web and mobile application APIs.
Authentication and authorisation.
Organisation and farm management.
Field and crop management.
Device registration and provisioning.
Sensor and telemetry ingestion.
Agricultural measurements.
Data import and export.
Weather and external data integrations.
Monitoring and alerts.
Farm operations and tasks.
Irrigation and physical equipment control.
Agricultural intelligence and recommendations.
Dataset and research workflows.
Notifications and collaboration.
Reporting.
Developer applications and webhooks.
Offline synchronisation.
Security, observability and reliability.
Testing and deployment.
The document is intended to be the implementation contract between frontend developers, backend developers, embedded engineers, data engineers and infrastructure engineers.
2. Core architecture decisions
Area
Initial decision
Backend
FastAPI modular monolith
API style
REST/JSON
API version
/api/v1
Database
PostgreSQL
Spatial data
PostGIS
Cache
Redis
Background work
Celery or equivalent worker system
Device messaging
MQTT
Broker
Mosquitto initially; EMQX as an alternative
File storage
S3-compatible object storage
Web client
React + Vite
Mobile client
React Native + Expo
Authentication
OIDC-compatible identity provider
Telemetry
MQTT and HTTPS
Real-time updates
WebSocket or Server-Sent Events where justified
Documentation
OpenAPI
Containerisation
Docker
Initial deployment
Docker Compose
Observability
Prometheus, Grafana, structured logs and error tracking

These choices are initial engineering decisions, not mandatory commitments to every named vendor.
3. Architectural boundaries
TerraNexus begins as a modular monolith. Its modules are logically isolated, but share one application deployment and one PostgreSQL database initially.
                        TERRANEXUS CLIENTS
             ┌──────────────────────────────────┐
             │ Web App │ Mobile App │ Developer │
             └─────────────────┬────────────────┘
                               │ HTTPS
                               ▼
                     ┌───────────────────┐
                     │ API Gateway /     │
                     │ Reverse Proxy      │
                     └─────────┬─────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ FastAPI Application      │
                  │                          │
                  │ Identity & Access        │
                  │ Organisation             │
                  │ Farm & Field             │
                  │ Crop & Season            │
                  │ Device & Sensor           │
                  │ Telemetry & Data          │
                  │ Monitoring & Alerts      │
                  │ Operations                │
                  │ Irrigation                │
                  │ Intelligence              │
                  │ Integrations              │
                  │ Reporting                 │
                  │ Administration            │
                  └───────┬──────────┬───────┘
                          │          │
                          ▼          ▼
                  ┌────────────┐ ┌───────────┐
                  │ PostgreSQL │ │   Redis   │
                  │ + PostGIS  │ │ Cache/Jobs│
                  └────────────┘ └─────┬─────┘
                                      │
                                      ▼
                              Background Workers
                                      │
                     ┌────────────────┼─────────────────┐
                     ▼                ▼                 ▼
                 Data Jobs        Notifications    Intelligence
                 Imports          Integrations     Model Runs
                 Exports          Reports          Forecasts

       IoT DEVICES                       EXTERNAL DATA PROVIDERS
 ┌──────────────────────┐             ┌────────────────────────┐
 │ ESP32 / Sensors      │             │ Weather APIs           │
 │ Gateways             │             │ Satellite providers    │
 │ Pumps / Relays       │             │ Soil datasets          │
 │ Other controllers    │             │ Agricultural systems   │
 └──────────┬───────────┘             └───────────┬────────────┘
            │ MQTT / HTTPS                        │ HTTPS / Files
            ▼                                     ▼
       ┌────────────┐                      Integration adapters
       │ MQTT Broker│                              │
       └──────┬─────┘                              │
              ▼                                    │
       ┌───────────────────────────────────────────┘
       │ Device Connectivity and Ingestion Adapter
       ▼
       Telemetry Validation → Normalisation → Persistence

       PHYSICAL CONTROL BOUNDARY
       ┌─────────────────────────────────────────┐
       │ Authorisation / Policy / Command Service │
       │ Device Controller                       │
       │ Local Safety Logic                      │
       │ Interlocks / Manual Override             │
       └─────────────────────────────────────────┘
4. Module ownership
Each module owns its domain rules and public service interface.
Module
Owns
Identity
Users, sessions, authentication integration
Organisation
Tenants, memberships, roles, permissions
Farm
Farms, fields, boundaries, farm membership
Crop
Crop catalogue, varieties, seasons, assignments
Device
Device identities, gateways, provisioning, configuration
Sensor
Sensor channels, calibration and measurement definitions
Telemetry
Ingestion, validation, deduplication, normalisation
Data
Datasets, sources, imports, exports, quality
Monitoring
Monitoring views, thresholds and alert evaluation
Operations
Tasks, activities, equipment, inventory
Irrigation
Zones, water sources, plans and operational workflows
Control
Command authorisation, dispatch, acknowledgements and safety
Intelligence
Models, forecasts, recommendations and evidence
Integration
External providers, credentials, synchronisation
Notification
Delivery preferences and notification dispatch
Reporting
Report definitions, generation and schedules
Collaboration
Comments, assignments and shared activity
Administration
Platform configuration, audit and system management

Boundary rules
A module must not modify another module's tables directly through arbitrary SQL.
Cross-module interactions must use explicit service interfaces or documented domain events.
Database transactions must remain within well-defined boundaries.
Long-running work must be delegated to background jobs.
Physical-control functions must not depend on the AI module.
A recommendation is not an equipment command.
A device's reported state is not automatically proof that an action occurred successfully.
5. Request and response flow
A normal API request follows this path:
Reverse proxy receives the request.
Request ID is assigned or validated.
Authentication is verified.
Tenant context is resolved.
Permissions are checked.
Input is validated.
The owning module executes domain logic.
Database changes are committed.
Relevant events are recorded.
A response is returned.
For asynchronous operations, the API returns a job or resource identifier and exposes a status endpoint.

PART II — API STANDARDS
6. API base URL and versioning
Development:
http://localhost:8000/api/v1
Staging:
https://staging-api.example.com/api/v1
Production:
https://api.example.com/api/v1
The example domains are placeholders and must be replaced with verified TerraNexus domains.
Versioning rules
Breaking changes require a new major API version.
Additive optional fields may be introduced within the existing version.
Deprecated endpoints must publish a removal timeline.
API changes must be documented in OpenAPI.
Clients must not assume that unknown response fields are errors.
7. Request headers
Header
Purpose
Authorization
Bearer access token
Content-Type
Request content type
Accept
Expected response format
X-Request-ID
Request correlation
Idempotency-Key
Safe retry of supported write operations
If-Match
Optimistic concurrency control
If-None-Match
Conditional retrieval
Accept-Language
Language preference
X-Client-Version
Client version
X-Client-Platform
Web, Android, iOS or other supported client

Tenant identification should primarily be resolved through authenticated membership and resource ownership. A client-provided organisation ID must never be trusted as proof of access.
8. Standard response format
Successful single-resource response:
{
  "data": {
    "id": "uuid",
    "name": "North Farm"
  },
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-11-08T10:30:00Z"
  }
}
Collection response:
{
  "data": [
    {
      "id": "uuid-1",
      "name": "North Farm"
    }
  ],
  "meta": {
    "request_id": "req_01J...",
    "pagination": {
      "page": 1,
      "page_size": 25,
      "total_items": 1,
      "total_pages": 1
    }
  }
}
The API may use cursor pagination for high-volume telemetry and activity feeds.
9. Error contract
Errors should follow a consistent machine-readable structure based on the Problem Details approach.
{
  "type": "https://docs.example.com/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "code": "VALIDATION_ERROR",
  "detail": "One or more fields are invalid.",
  "request_id": "req_01J...",
  "errors": [
    {
      "field": "area_hectares",
      "code": "OUT_OF_RANGE",
      "message": "Area must be greater than zero."
    }
  ]
}
Standard HTTP status codes
Status
Meaning
200
Successful retrieval or operation
201
Resource created
202
Accepted for asynchronous processing
204
Successful operation without response body
400
Invalid request
401
Authentication required
403
Authenticated but not authorised
404
Resource unavailable or not found
409
Conflict
410
Resource or endpoint permanently gone
412
Conditional request failed
413
Payload too large
415
Unsupported media type
422
Semantic validation error
423
Resource locked where applicable
429
Rate limit exceeded
500
Internal server error
502
Upstream provider error
503
Service unavailable
504
Upstream timeout

Do not leak stack traces, SQL statements, credentials or internal infrastructure details.
10. Pagination, filtering and sorting
Example:
GET /api/v1/farms?page=1&page_size=25&sort=-created_at&status=active
Rules:
Default page size: 25.
Proposed maximum: 100 for ordinary collections.
High-volume telemetry uses cursor pagination.
Sort fields must be explicitly allowed.
Filter fields must be documented.
Dates use ISO 8601.
Time ranges must state whether boundaries are inclusive.
Example:
GET /api/v1/measurements?field_id={uuid}&type=soil_moisture&from=2026-11-01T00:00:00Z&to=2026-11-08T23:59:59Z
11. Date, time and units
Store timestamps in UTC.
Store the user's preferred timezone separately.
Preserve the original observation timestamp and ingestion timestamp.
Return timestamps as ISO 8601.
Use explicit units for every physical quantity.
Never assume all devices report the same unit.
Initial standard units:
Measurement
Unit
Temperature
°C
Relative humidity
% RH
Soil moisture
% or calibrated volumetric water content
Rainfall
mm
Wind speed
m/s
Pressure
hPa
pH
dimensionless
Electrical conductivity
µS/cm or mS/cm
Water volume
L or m³
Area
m² or hectares
Flow rate
L/min or m³/h

Unit conversion must be explicit and recorded. A raw ADC reading is not a percentage of soil moisture unless a valid calibration transformation exists.

PART III — AUTHENTICATION, TENANCY AND PERMISSIONS
12. Authentication
Use an OIDC-compatible identity system.
Recommended flow:
User authenticates through the identity provider.
Identity provider issues access and refresh tokens.
Client sends access token to the API.
API validates signature, issuer, audience and expiry.
API resolves user and organisation memberships.
API checks resource-level permissions.
Access tokens should be short-lived. Refresh tokens should be protected, rotated and revocable.
Never store plain-text passwords or long-lived secrets in frontend storage.
13. Authentication endpoints
Method
Endpoint
Purpose
GET
/auth/me
Current user profile
GET
/auth/sessions
List sessions
DELETE
/auth/sessions/{id}
Revoke session
POST
/auth/logout
End session
POST
/auth/mfa/enrol
Begin MFA setup
POST
/auth/mfa/verify
Verify MFA
POST
/auth/mfa/disable
Disable MFA with reauthentication
POST
/auth/password/change
Change password
POST
/auth/account/export
Request account export
POST
/auth/account/deletion
Request account deletion

Registration, email verification, password recovery and primary sign-in may be handled by the identity provider rather than duplicated in the application API.
14. Organisation and tenant endpoints
Method
Endpoint
Purpose
GET
/organisations
List memberships
POST
/organisations
Create organisation
GET
/organisations/{id}
Get organisation
PATCH
/organisations/{id}
Update organisation
GET
/organisations/{id}/members
List members
POST
/organisations/{id}/invitations
Invite member
GET
/organisations/{id}/invitations
List invitations
POST
/organisations/{id}/invitations/{inviteId}/resend
Resend invitation
DELETE
/organisations/{id}/members/{userId}
Remove member
PATCH
/organisations/{id}/members/{userId}
Change membership
GET
/roles
List available roles
GET
/permissions
List permissions

15. Authorisation model
Use RBAC combined with resource-level access checks.
Proposed roles:
Platform administrator.
Organisation owner.
Organisation administrator.
Farm manager.
Farm worker.
Agronomist.
Extension officer.
Researcher.
Service provider.
Read-only auditor.
Permissions should be action-oriented.
Examples:
farm.read
farm.create
farm.update
field.read
field.update
device.register
device.configure
telemetry.read
task.assign
irrigation.plan.create
irrigation.approve
device.command.request
device.command.approve
report.export
organisation.member.manage
Authorisation rules
A user can belong to multiple organisations.
Organisation access does not automatically grant access to every farm if farm-level restrictions apply.
Device commands require additional permissions.
Emergency-stop permissions must be defined explicitly.
API keys have scopes and organisation boundaries.
Platform administrators should not receive unrestricted access to private farm data by default.
All sensitive access and changes must be audited.

PART IV — CORE AGRICULTURAL API CONTRACTS
16. Farms
Method
Endpoint
Purpose
GET
/farms
List authorised farms
POST
/farms
Create farm
GET
/farms/{farmId}
Farm details
PATCH
/farms/{farmId}
Update farm
DELETE
/farms/{farmId}
Archive farm
GET
/farms/{farmId}/fields
List fields
GET
/farms/{farmId}/members
List farm members
POST
/farms/{farmId}/members
Add farm member
DELETE
/farms/{farmId}/members/{userId}
Remove member
GET
/farms/{farmId}/summary
Farm summary

Create farm request
{
  "name": "North Farm",
  "description": "Demonstration farm",
  "location": {
    "country_code": "KE",
    "locality": "Kerugoya"
  },
  "boundary": {
    "type": "Polygon",
    "coordinates": [
      [
        [37.0, -0.5],
        [37.001, -0.5],
        [37.001, -0.501],
        [37.0, -0.501],
        [37.0, -0.5]
      ]
    ]
  },
  "area_hectares": 2.5
}
This coordinate set is illustrative, not a real farm boundary.
Server rules:
Validate GeoJSON.
Enforce the supported coordinate reference system.
Validate polygon geometry.
Check that the polygon is not self-intersecting.
Calculate area from the geometry.
Do not blindly trust client-supplied area.
Preserve the original geometry and calculated area where required.
17. Fields
Method
Endpoint
Purpose
GET
/fields
List fields
POST
/fields
Create field
GET
/fields/{fieldId}
Field details
PATCH
/fields/{fieldId}
Update field
DELETE
/fields/{fieldId}
Archive field
GET
/fields/{fieldId}/history
Field history
GET
/fields/{fieldId}/observations
Observations
POST
/fields/{fieldId}/observations
Create observation
GET
/fields/{fieldId}/measurements
Field measurements
GET
/fields/{fieldId}/summary
Field summary

Create field request
{
  "farm_id": "uuid",
  "name": "Field A",
  "code": "FIELD-A",
  "boundary": {
    "type": "Polygon",
    "coordinates": []
  },
  "soil_profile_id": null
}
The empty geometry above is a placeholder; actual requests must contain a valid polygon or follow an explicitly supported geometry-optional workflow.
18. Crops and growing seasons
Method
Endpoint
Purpose
GET
/crops
Crop catalogue
POST
/crops
Create authorised catalogue entry
GET
/crops/{cropId}
Crop details
GET
/crop-varieties
List varieties
POST
/crop-varieties
Create variety
GET
/seasons
List seasons
POST
/seasons
Create season
GET
/seasons/{seasonId}
Season details
PATCH
/seasons/{seasonId}
Update season
POST
/fields/{fieldId}/crop-assignments
Assign crop
GET
/fields/{fieldId}/crop-assignments
List crop assignments
PATCH
/crop-assignments/{assignmentId}
Update assignment

Crop assignments must preserve historical information. A new season should not overwrite previous crop history.
19. Farm operations
Method
Endpoint
Purpose
GET
/tasks
List tasks
POST
/tasks
Create task
GET
/tasks/{taskId}
Task details
PATCH
/tasks/{taskId}
Update task
POST
/tasks/{taskId}/complete
Complete task
POST
/tasks/{taskId}/cancel
Cancel task
POST
/tasks/{taskId}/comments
Add comment
GET
/activities
List activities
POST
/activities
Record activity
GET
/equipment
List equipment
POST
/equipment
Register equipment
PATCH
/equipment/{equipmentId}
Update equipment
GET
/inventory/items
List inventory
POST
/inventory/items
Create inventory item
POST
/inventory/transactions
Record stock movement
GET
/inspections
List inspections
POST
/inspections
Create inspection
GET
/harvest-records
List harvest records
POST
/harvest-records
Create harvest record

Inventory must use transaction records. Updating a displayed stock balance directly must not bypass its transaction history.

PART V — DEVICE AND SENSOR API
20. Device identity
Every device must have a globally unique immutable identity.
Example:
tnx_dev_01JABC...
Required attributes:
Device ID.
Manufacturer.
Model.
Hardware revision.
Firmware version.
Serial number where available.
Organisation.
Farm.
Field, if assigned.
Gateway, if used.
Connectivity protocol.
Provisioning status.
Operational status.
Security status.
Last-seen timestamp.
A device may move between fields, but the assignment history must be preserved.
21. Device endpoints
Method
Endpoint
Purpose
GET
/devices
List devices
POST
/devices
Register device
GET
/devices/{deviceId}
Device details
PATCH
/devices/{deviceId}
Update metadata
POST
/devices/{deviceId}/provision
Provision device
POST
/devices/{deviceId}/activate
Activate device
POST
/devices/{deviceId}/deactivate
Deactivate device
POST
/devices/{deviceId}/revoke
Revoke device credentials
GET
/devices/{deviceId}/status
Device status
GET
/devices/{deviceId}/events
Device events
GET
/devices/{deviceId}/configuration
Current configuration
PUT
/devices/{deviceId}/configuration
Submit new configuration
GET
/devices/{deviceId}/commands
Command history
GET
/devices/{deviceId}/sensors
Associated sensors

22. Device registration request
{
  "manufacturer": "Example Manufacturer",
  "model": "ESP32 Agricultural Node",
  "hardware_revision": "1.0",
  "serial_number": "ESP32-001",
  "farm_id": "uuid",
  "field_id": "uuid",
  "protocol": "mqtt",
  "capabilities": [
    "telemetry",
    "configuration",
    "relay_control"
  ]
}
Capabilities are declarations, not proof that a function is safe or supported. The server must compare them with the registered device profile.
23. Device provisioning lifecycle
REGISTERED
    │
    ▼
PROVISIONING_PENDING
    │
    ▼
CREDENTIALS_ISSUED
    │
    ▼
CONNECTIVITY_TEST
    │
    ▼
TELEMETRY_VERIFIED
    │
    ▼
ACTIVE
Possible failure or terminal states:
Provisioning expired.
Provisioning rejected.
Revoked.
Quarantined.
Decommissioned.
Provisioning requirements
Generate a device identity.
Associate it with an organisation.
Generate a unique device credential.
Set credential expiry and rotation rules.
Provide broker or HTTPS endpoint configuration.
Verify device connection.
Verify telemetry signature or authenticated connection.
Activate device.
Record provisioning audit event.
Never place shared fleet-wide credentials in firmware images.
24. Sensor endpoints
Method
Endpoint
Purpose
GET
/sensors
List sensors
POST
/sensors
Register sensor
GET
/sensors/{sensorId}
Sensor details
PATCH
/sensors/{sensorId}
Update metadata
GET
/sensors/{sensorId}/measurements
Sensor readings
GET
/sensors/{sensorId}/calibrations
Calibration history
POST
/sensors/{sensorId}/calibrations
Record calibration
POST
/sensors/{sensorId}/verify
Record verification

A sensor definition must include:
Measurement type.
Unit.
Sensor model.
Channel identifier.
Validity rules.
Calibration information.
Expected reporting interval.
Accuracy information where known.
25. Sensor channel model
One physical device may expose multiple sensors and multiple channels.
Example:
Device: ESP32 Node 001
│
├── Soil moisture sensor
│   └── Channel: soil_moisture_1
│
├── DHT11
│   ├── Channel: air_temperature
│   └── Channel: relative_humidity
│
├── Rain sensor
│   └── Channel: rain_raw
│
└── Relay
    └── Capability: pump_control
Do not treat a relay as a measurement sensor.

PART VI — TELEMETRY CONTRACT
26. Telemetry principles
Telemetry is an observation received from a device.
A telemetry message must preserve:
Originating device.
Sensor or channel.
Measurement type.
Original value.
Original unit.
Observation time.
Reception time.
Sequence or event identifier.
Quality metadata.
Firmware information.
A reading received by the server at 10:05 but measured at 09:55 must retain both timestamps.
27. Canonical telemetry schema
{
  "schema_version": "1.0",
  "message_id": "01JTNXABC123",
  "device_id": "tnx_dev_001",
  "boot_id": "boot_001",
  "sequence": 1024,
  "observed_at": "2026-11-08T10:00:00Z",
  "sent_at": "2026-11-08T10:00:02Z",
  "firmware_version": "0.6.1",
  "measurements": [
    {
      "channel_id": "soil_moisture_1",
      "measurement_type": "soil_moisture",
      "value": 42.6,
      "unit": "percent",
      "raw_value": 1830,
      "quality": "unverified"
    },
    {
      "channel_id": "air_temperature",
      "measurement_type": "air_temperature",
      "value": 25.4,
      "unit": "Cel",
      "quality": "valid"
    },
    {
      "channel_id": "relative_humidity",
      "measurement_type": "relative_humidity",
      "value": 64.0,
      "unit": "percent",
      "quality": "valid"
    }
  ],
  "location": {
    "latitude": -0.5,
    "longitude": 37.0,
    "accuracy_m": null
  },
  "device_status": {
    "battery_voltage": 4.9,
    "rssi_dbm": -68,
    "uptime_seconds": 86400
  }
}
Values and location above are illustrative. They are not calibrated readings or actual device coordinates.
Required validation
Message ID must be unique within the defined device scope.
Device must be registered and authorised.
Channel must belong to that device or an authorised attached sensor.
Measurement type must match the channel definition.
Unit must be supported.
Value must be numeric or a valid typed value.
Timestamp must be parseable.
Sequence information must be checked.
Invalid observations must not silently enter trusted analytics.
28. Measurement quality states
Use a controlled vocabulary:
Status
Meaning
valid
Passed configured validation
suspect
Unusual but not conclusively invalid
invalid
Failed validation
missing
Expected observation not received
stale
Observation older than freshness policy
uncalibrated
Sensor has no required calibration
estimated
Derived or estimated value
corrected
Value changed through documented correction
manually_verified
Reviewed by an authorised user
unverified
Not yet sufficiently assessed

Quality status must be preserved in analysis and export.
29. Soil moisture handling
Resistive soil moisture sensors commonly return raw analogue readings.
The system must distinguish:
Raw ADC reading.
Calibrated moisture estimate.
Volumetric water content, if properly calibrated.
Soil-specific interpretation.
Do not label a raw ADC value as volumetric water content.
Calibration records should include:
Sensor identity.
Soil type or calibration context.
Dry reference.
Wet reference.
Method.
Date.
Operator.
Calibration version.
Validation evidence.
30. Telemetry ingestion endpoint
POST /api/v1/ingestion/telemetry
Alternative bulk endpoint:
POST /api/v1/ingestion/telemetry/batch
Example response:
{
  "data": {
    "accepted": 3,
    "rejected": 0,
    "duplicates": 0,
    "batch_id": "batch_001"
  },
  "meta": {
    "request_id": "req_001",
    "timestamp": "2026-11-08T10:00:03Z"
  }
}
A batch may return partial acceptance. The response must identify failed records without implying the whole batch succeeded.
31. Telemetry processing pipeline
Device Message
      │
      ▼
Authenticate Device
      │
      ▼
Validate Schema
      │
      ▼
Validate Device / Channel
      │
      ▼
Check Duplicate ID
      │
      ▼
Validate Timestamp / Unit
      │
      ▼
Assign Server Received Time
      │
      ▼
Persist Original Observation
      │
      ▼
Normalise / Derive Values
      │
      ▼
Update Monitoring State
      │
      ▼
Evaluate Alert Rules
      │
      ▼
Publish Domain Events
      │
      ▼
Update Analytics / Dashboards
Raw observations should remain immutable. Corrections and derived measurements should be separate, traceable records.
32. Device health telemetry
In addition to agricultural readings, devices should report:
Battery voltage or charge state where available.
Signal strength.
Uptime.
Firmware.
Last successful transmission.
Sensor health.
Memory/storage status where supported.
Boot reason where supported.
Communication errors.
This data supports device-health monitoring and helps distinguish actual farm conditions from sensor failures.

PART VII — MQTT TOPICS AND DEVICE MESSAGING
33. MQTT architecture
MQTT is the preferred lightweight messaging protocol for connected devices.
Use:
TLS.
Per-device authentication.
Per-device authorisation.
Unique client IDs.
Explicit topic permissions.
Message expiry where supported.
Retained messages only for appropriate state/configuration topics.
QoS according to message criticality.
34. Topic structure
Proposed topic namespace:
tnx/v1/org/{org_id}/device/{device_id}/telemetry
tnx/v1/org/{org_id}/device/{device_id}/status
tnx/v1/org/{org_id}/device/{device_id}/events
tnx/v1/org/{org_id}/device/{device_id}/config
tnx/v1/org/{org_id}/device/{device_id}/config/ack
tnx/v1/org/{org_id}/device/{device_id}/commands
tnx/v1/org/{org_id}/device/{device_id}/commands/ack
tnx/v1/org/{org_id}/device/{device_id}/commands/result
tnx/v1/org/{org_id}/device/{device_id}/heartbeat
These are application topic names, not broker credentials or access-control policies.
35. Topic permissions
Topic
Device permission
Telemetry
Publish
Status
Publish
Events
Publish
Heartbeat
Publish
Configuration
Subscribe
Configuration acknowledgement
Publish
Commands
Subscribe
Command acknowledgement
Publish
Command result
Publish

A device must not subscribe to another device's commands or publish under another device's identity.
36. QoS policy
Message type
Suggested QoS
Reason
Periodic telemetry
1
Reliable delivery with deduplication
Heartbeat
0 or 1
Depends on criticality
Device events
1
Event preservation
Configuration
1
Reliable configuration delivery
Commands
1
Reliable delivery request
Command acknowledgements
1
Reliable acknowledgement
Emergency stop signalling
1 plus independent local mechanism
MQTT is not the only safety path

QoS 2 is not automatically necessary. Delivery guarantees do not eliminate the need for application-level idempotency.
37. MQTT telemetry example
Topic:
tnx/v1/org/org_001/device/tnx_dev_001/telemetry
Payload:
{
  "schema_version": "1.0",
  "message_id": "msg_001",
  "observed_at": "2026-11-08T10:00:00Z",
  "sequence": 100,
  "measurements": [
    {
      "channel_id": "soil_1",
      "measurement_type": "soil_moisture",
      "value": 42.6,
      "unit": "percent",
      "quality": "unverified"
    }
  ]
}
The server derives the organisation and device identity from the authenticated broker connection. It must not rely exclusively on organisation identifiers embedded in untrusted payloads.
38. Device heartbeat
Topic:
tnx/v1/org/org_001/device/tnx_dev_001/heartbeat
{
  "schema_version": "1.0",
  "message_id": "heartbeat_001",
  "observed_at": "2026-11-08T10:00:00Z",
  "uptime_seconds": 3600,
  "battery_voltage": 4.9,
  "rssi_dbm": -68,
  "firmware_version": "0.6.1",
  "status": "healthy"
}
Heartbeat frequency must be configurable according to power and connectivity constraints.
39. MQTT retained messages
Appropriate uses:
Current device availability snapshot.
Current configuration version, where designed safely.
Do not retain:
One-time pump-start commands.
Emergency-stop commands as ordinary retained control messages.
Sensitive credentials.
Large historical telemetry batches.
Retained configuration messages must have a version and expiry policy.

PART VIII — DEVICE COMMANDS AND PHYSICAL CONTROL
40. Command architecture
Physical-control requests must pass through a separate command-control boundary.
User / Approved Workflow
        │
        ▼
API Permission Check
        │
        ▼
Command Request
        │
        ▼
Command Policy Validation
        │
        ▼
Resource / Device Validation
        │
        ▼
Safety Interlock Validation
        │
        ▼
Approval, if required
        │
        ▼
Command Dispatch
        │
        ▼
MQTT Broker
        │
        ▼
Device Local Controller
        │
        ▼
Local Safety Checks
        │
        ▼
Actuator Execution
        │
        ▼
Acknowledgement
        │
        ▼
Execution Result
        │
        ▼
Server Reconciliation and Audit
The cloud API, user interface and AI services must not directly energise a relay or motor.
41. Command endpoints
Method
Endpoint
Purpose
POST
/devices/{deviceId}/commands
Request command
GET
/commands/{commandId}
Command details
GET
/commands
List commands
POST
/commands/{commandId}/approve
Approve command
POST
/commands/{commandId}/reject
Reject command
POST
/commands/{commandId}/cancel
Cancel command
POST
/commands/{commandId}/retry
Request eligible retry
GET
/commands/{commandId}/events
Command timeline
POST
/commands/{commandId}/acknowledgements
Record acknowledgement
POST
/commands/{commandId}/results
Record result

Device-originated acknowledgement and result endpoints must require device authentication. They must not be available as ordinary unauthenticated public endpoints.
42. Command request schema
{
  "command_type": "pump.start",
  "target": {
    "device_id": "tnx_dev_001",
    "actuator_id": "relay_1"
  },
  "parameters": {
    "maximum_runtime_seconds": 300
  },
  "reason": "Approved irrigation plan",
  "source": {
    "type": "irrigation_plan",
    "id": "plan_001"
  },
  "expires_at": "2026-11-08T10:05:00Z"
}
The server must calculate or validate all operational limits. The client cannot choose arbitrary limits outside the approved policy.
43. Command state machine
REQUESTED
    │
    ▼
VALIDATING
    │
    ├── REJECTED
    │
    ▼
PENDING_APPROVAL
    │
    ├── REJECTED
    ├── EXPIRED
    ▼
APPROVED
    │
    ▼
DISPATCHED
    │
    ├── DELIVERY_FAILED
    ▼
DELIVERED
    │
    ▼
ACKNOWLEDGED
    │
    ▼
EXECUTING
    │
    ├── FAILED
    ├── TIMED_OUT
    ├── CANCELLED
    ▼
SUCCEEDED
Additional terminal or exceptional states:
SAFETY_BLOCKED
CANCELLED
EXPIRED
UNKNOWN
PARTIALLY_SUCCEEDED
RECONCILIATION_REQUIRED
A command's lifecycle must be recorded as events, not just a mutable status field.
44. Command payload
Topic:
tnx/v1/org/org_001/device/tnx_dev_001/commands
{
  "schema_version": "1.0",
  "command_id": "cmd_001",
  "command_type": "pump.start",
  "issued_at": "2026-11-08T10:00:00Z",
  "expires_at": "2026-11-08T10:05:00Z",
  "target": {
    "actuator_id": "relay_1"
  },
  "parameters": {
    "maximum_runtime_seconds": 300
  },
  "configuration_version": 12
}
The device must reject expired, malformed, duplicated or unsupported commands.
45. Acknowledgement payload
{
  "schema_version": "1.0",
  "command_id": "cmd_001",
  "device_id": "tnx_dev_001",
  "acknowledged_at": "2026-11-08T10:00:01Z",
  "status": "accepted",
  "reason": null
}
Acknowledgement means the device accepted the command. It does not prove that the physical operation succeeded.
46. Execution result
{
  "schema_version": "1.0",
  "command_id": "cmd_001",
  "device_id": "tnx_dev_001",
  "started_at": "2026-11-08T10:00:02Z",
  "completed_at": "2026-11-08T10:04:55Z",
  "status": "succeeded",
  "actuator_state": "off",
  "runtime_seconds": 293,
  "safety_events": []
}
Physical success should be supported by the available feedback mechanisms. Relay state alone may not prove water flow. Where water-flow or pressure sensors exist, their observations should be associated with the operation.
47. Independent safety requirements
The device must have local safety logic that can operate without the cloud.
Mandatory design requirements for applicable control devices:
Local maximum runtime.
Local command expiry check.
Duplicate command prevention.
Manual override.
Physical emergency-stop mechanism where the equipment risk assessment requires one.
Safe default actuator state on reboot.
Power-loss handling.
Pump dry-run protection where supported.
Water availability checks where supported.
Overcurrent or overload protection where required.
Watchdog and fault recovery.
Hardware-rated relay or contactor.
Isolation and suitable electrical protection.
Local event logging where feasible.
No automatic restart after an unsafe fault without an explicit recovery policy.
Software controls must not substitute for appropriate electrical, mechanical and hydraulic safety engineering.
48. Irrigation-specific API
Method
Endpoint
Purpose
GET
/irrigation/zones
List zones
POST
/irrigation/zones
Create zone
GET
/irrigation/zones/{zoneId}
Zone details
PATCH
/irrigation/zones/{zoneId}
Update zone
GET
/water-sources
List water sources
POST
/water-sources
Register water source
GET
/irrigation/plans
List plans
POST
/irrigation/plans
Create plan
GET
/irrigation/plans/{planId}
Plan details
POST
/irrigation/plans/{planId}/approve
Approve plan
POST
/irrigation/plans/{planId}/execute
Request execution
POST
/irrigation/plans/{planId}/cancel
Cancel plan
GET
/irrigation/events
Irrigation history
GET
/irrigation/safety/status
Current safety state

Irrigation plan request
{
  "farm_id": "farm_001",
  "field_id": "field_001",
  "zone_id": "zone_001",
  "water_source_id": "water_001",
  "target": {
    "duration_seconds": 300
  },
  "schedule": {
    "mode": "manual_approval",
    "requested_start_at": "2026-11-08T10:00:00Z"
  },
  "reason": "Field moisture assessment"
}
A plan is not automatically an execution command.
49. Irrigation safety checks
Before dispatch, evaluate:
User authorisation.
Plan approval.
Device identity and status.
Actuator compatibility.
Command expiry.
Current device state.
Local and server-side operating limits.
Water-source availability where measurable.
Pump health where measurable.
Conflicting operations.
Maintenance lock.
Emergency-stop state.
Device connectivity.
Required acknowledgements.
Some checks can only be enforced locally. The server must know which checks are confirmed, unknown or unavailable.
If a required safety condition cannot be verified, the system must block the action or require the specifically approved safe operating procedure. It must not silently assume the condition is safe.

PART IX — CONFIGURATION AND FIRMWARE
50. Device configuration endpoints
Method
Endpoint
Purpose
GET
/devices/{deviceId}/configuration
Current configuration
POST
/devices/{deviceId}/configuration
Create new configuration version
GET
/devices/{deviceId}/configuration/history
Configuration history
POST
/devices/{deviceId}/configuration/{version}/publish
Publish configuration
POST
/devices/{deviceId}/configuration/{version}/rollback
Request rollback

Configuration schema
{
  "version": 13,
  "sampling": {
    "interval_seconds": 60
  },
  "reporting": {
    "interval_seconds": 300
  },
  "sensors": {
    "soil_moisture_1": {
      "enabled": true
    },
    "air_temperature": {
      "enabled": true
    }
  },
  "network": {
    "mode": "wifi"
  }
}
Configuration parameters must be defined by hardware profiles. A generic device must not accept arbitrary unsupported parameters.
51. Firmware management
Endpoints:
GET /firmware/releases
POST /firmware/releases
GET /firmware/releases/{releaseId}
POST /devices/{deviceId}/firmware-updates
GET /firmware-updates/{updateId}
POST /firmware-updates/{updateId}/cancel
Firmware release metadata:
Release ID.
Version.
Hardware compatibility.
Checksum.
Signature.
File reference.
Release notes.
Security advisory.
Rollback policy.
Firmware images must be signed and verified by the device bootloader where hardware supports secure boot. A firmware download must never be treated as proof of successful installation.

PART X — DATA, OBSERVATIONS AND DATASETS
52. Measurement API
Method
Endpoint
Purpose
GET
/measurements
Query measurements
GET
/measurements/{measurementId}
Measurement details
GET
/measurements/aggregations
Aggregated data
GET
/measurements/latest
Latest readings
POST
/measurements/manual
Record authorised manual measurement
POST
/measurements/{measurementId}/corrections
Record correction

Manual measurements must retain the user who entered them, entry time, observation time and verification state.
53. Observation API
GET /observations
POST /observations
GET /observations/{observationId}
PATCH /observations/{observationId}
POST /observations/{observationId}/attachments
Observations may include:
Crop condition.
Pest observation.
Disease symptoms.
Soil condition.
Weather observation.
Irrigation condition.
Field inspection.
Other documented field observations.
A farmer's observation should not be overwritten by an AI interpretation.
54. Dataset API
Method
Endpoint
Purpose
GET
/datasets
List datasets
POST
/datasets
Create dataset metadata
GET
/datasets/{datasetId}
Dataset details
PATCH
/datasets/{datasetId}
Update metadata
GET
/datasets/{datasetId}/versions
Version history
POST
/datasets/{datasetId}/versions
Create version
POST
/datasets/{datasetId}/access-requests
Request access
POST
/datasets/{datasetId}/publish
Publish if authorised
GET
/data-sources
Source catalogue

Dataset metadata must include:
Name.
Description.
Owner.
Source.
Licence.
Geographic coverage.
Temporal coverage.
Schema.
Update frequency.
Quality information.
Access level.
Version.
55. Data import
Endpoints:
POST /imports
GET /imports/{importId}
POST /imports/{importId}/validate
POST /imports/{importId}/preview
POST /imports/{importId}/execute
POST /imports/{importId}/cancel
Import lifecycle:
UPLOADED
   │
   ▼
FORMAT_DETECTION
   │
   ▼
SCHEMA_MAPPING
   │
   ▼
VALIDATION
   │
   ├── FAILED
   ▼
PREVIEW
   │
   ▼
APPROVED
   │
   ▼
PROCESSING
   │
   ├── PARTIAL
   ├── FAILED
   ▼
COMPLETED
The import process must report accepted, rejected, skipped and duplicate records.
56. Data export
Endpoints:
POST /exports
GET /exports/{exportId}
GET /exports/{exportId}/download
POST /exports/{exportId}/cancel
Export formats:
CSV.
JSON.
GeoJSON.
Supported spreadsheet formats.
Exports must enforce tenant and field-level access. Download links should be short-lived and scoped.
57. File and attachment handling
Endpoints:
POST /files/upload-sessions
POST /files/{fileId}/complete
GET /files/{fileId}
DELETE /files/{fileId}
Use direct-to-object-storage uploads for large files where possible.
Requirements:
File size limits.
Allowed file types.
Content validation.
Malware scanning where applicable.
Ownership checks.
Retention policy.
Signed download URLs.
Attachment-to-resource relationships.
Upload interruption recovery.
Do not trust file extensions as proof of file type.

PART XI — WEATHER, SOIL AND EXTERNAL DATA
58. External provider integration architecture
Each external provider must have an adapter.
External Provider
       │
       ▼
Provider Adapter
       │
       ▼
Authentication
       │
       ▼
Provider Schema Validation
       │
       ▼
Normalisation
       │
       ▼
Provenance and Licence Metadata
       │
       ▼
Data Quality Checks
       │
       ▼
TerraNexus Canonical Data Model
       │
       ▼
Storage / Analytics / UI
External provider records must retain the source and retrieval time.
59. Weather endpoints
GET /weather/current
GET /weather/forecast
GET /weather/history
GET /weather/sources
POST /weather/refresh
Weather query parameters:
Latitude.
Longitude.
Farm or field ID.
Time range.
Provider preference where supported.
Do not return a forecast without its issue time, source and valid period.
60. Soil data endpoints
GET /soil/profiles
POST /soil/profiles
GET /soil/samples
POST /soil/samples
GET /soil/observations
POST /soil/observations
GET /soil/maps
Soil information should distinguish:
Laboratory sample.
Sensor observation.
External dataset.
Model-derived estimate.
Manually entered value.
61. Satellite and remote sensing
Potential endpoints:
GET /remote-sensing/sources
POST /remote-sensing/requests
GET /remote-sensing/requests/{requestId}
GET /remote-sensing/products
GET /remote-sensing/products/{productId}
Potential data:
Vegetation indices.
Land-surface information.
Surface temperature where supported.
Land cover.
Soil moisture estimates where a validated product exists.
Every product must state spatial resolution, temporal resolution, source, coverage, quality and processing method.

PART XII — MONITORING, ALERTS AND NOTIFICATIONS
62. Monitoring API
GET /monitoring/overview
GET /monitoring/live
GET /monitoring/devices
GET /monitoring/fields
GET /monitoring/charts
Live endpoints must expose the observation timestamp and freshness state.
63. Alert endpoints
Method
Endpoint
Purpose
GET
/alerts
List alerts
POST
/alerts/rules
Create rule
GET
/alerts/rules
List rules
PATCH
/alerts/rules/{ruleId}
Update rule
DELETE
/alerts/rules/{ruleId}
Disable/archive rule
GET
/alerts/{alertId}
Alert details
POST
/alerts/{alertId}/acknowledge
Acknowledge
POST
/alerts/{alertId}/resolve
Resolve
POST
/alerts/{alertId}/assign
Assign
GET
/alerts/{alertId}/history
Alert history

64. Alert rule schema
{
  "name": "Low soil moisture",
  "scope": {
    "farm_id": "farm_001",
    "field_id": "field_001"
  },
  "condition": {
    "measurement_type": "soil_moisture",
    "operator": "lt",
    "threshold": 25,
    "unit": "percent",
    "minimum_consecutive_observations": 2
  },
  "severity": "warning",
  "enabled": true
}
The threshold is illustrative. Actual thresholds must be crop-, soil-, sensor- and context-aware.
Rules should support:
Minimum consecutive observations.
Duration.
Hysteresis.
Data freshness requirements.
Sensor quality requirements.
Suppression periods.
Re-evaluation.
Escalation.
A stale or uncalibrated sensor should not silently generate a trusted crop-condition alert.
65. Notifications
Endpoints:
GET /notifications
POST /notifications/{notificationId}/read
POST /notifications/read-all
GET /notification-preferences
PATCH /notification-preferences
GET /notification-deliveries
Channels:
In-app.
Email.
Push.
SMS where available and configured.
Notification delivery failure must not delete the underlying alert or operational event.

PART XIII — INTELLIGENCE AND RECOMMENDATIONS
66. Intelligence API
GET /intelligence/overview
GET /recommendations
GET /recommendations/{recommendationId}
POST /recommendations/{recommendationId}/accept
POST /recommendations/{recommendationId}/reject
POST /recommendations/{recommendationId}/defer
POST /recommendations/{recommendationId}/feedback
GET /forecasts
GET /models
GET /models/{modelId}
POST /models/{modelId}/runs
GET /model-runs/{runId}
67. Recommendation schema
{
  "recommendation_type": "irrigation_review",
  "farm_id": "farm_001",
  "field_id": "field_001",
  "title": "Review field moisture",
  "summary": "Recent readings suggest the field may require inspection.",
  "proposed_action": {
    "type": "create_inspection_task"
  },
  "evidence": [
    {
      "type": "measurement",
      "reference_id": "measurement_001",
      "observed_at": "2026-11-08T09:00:00Z"
    },
    {
      "type": "weather_forecast",
      "reference_id": "forecast_001"
    }
  ],
  "confidence": {
    "value": 0.78,
    "method": "model_specific"
  },
  "limitations": [
    "Sensor calibration has not been confirmed."
  ],
  "expires_at": "2026-11-08T18:00:00Z"
}
The confidence example is illustrative. It must not be interpreted as a universally comparable probability.
68. Recommendation governance
Every recommendation must record:
Source data.
Data freshness.
Model or ruleset version.
Generation time.
Intended user.
Limitations.
Expiry.
Review decision.
Decision-maker.
Resulting task or plan.
Actual outcome where captured.
AI output must never be treated as verified agricultural fact by default.
69. Model lifecycle
DEVELOPMENT
    │
    ▼
EVALUATION
    │
    ▼
APPROVED
    │
    ▼
STAGING
    │
    ▼
DEPLOYED
    │
    ▼
MONITORED
    │
    ├── SUSPENDED
    ├── ROLLBACK
    ▼
RETIRED
Model metadata:
Name.
Version.
Task.
Training dataset.
Evaluation dataset.
Metrics.
Limitations.
Approval.
Deployment target.
Monitoring.
Rollback history.
Quantum computing experiments must be isolated as research workflows. They must be benchmarked against suitable classical baselines and must not be represented as having an advantage without evidence.

PART XIV — OFFLINE-FIRST SYNCHRONISATION
70. Offline architecture
Mobile and supported edge devices must be able to operate during intermittent connectivity.
Mobile User
     │
     ▼
Local Application
     │
     ├── Local Database
     ├── Pending Operations
     ├── Cached Reference Data
     ├── Attachments
     └── Sync Manager
              │
              ▼
        Connectivity Available
              │
              ▼
        Authentication Refresh
              │
              ▼
        Sync Handshake
              │
              ▼
        Upload Pending Changes
              │
              ▼
        Server Validation
              │
              ▼
        Download Changes
              │
              ▼
        Conflict Detection
              │
              ▼
        Local Reconciliation
71. Sync endpoints
Method
Endpoint
Purpose
POST
/sync/handshake
Establish sync session
GET
/sync/changes
Fetch changes since cursor
POST
/sync/push
Submit local changes
GET
/sync/status
View sync status
GET
/sync/conflicts
List conflicts
POST
/sync/conflicts/{id}/resolve
Resolve conflict
POST
/sync/attachments
Register attachment sync

72. Sync operation schema
{
  "sync_id": "sync_001",
  "client_id": "mobile_001",
  "operations": [
    {
      "operation_id": "op_001",
      "entity_type": "field_observation",
      "entity_id": "local_obs_001",
      "operation": "create",
      "client_revision": 1,
      "client_timestamp": "2026-11-08T08:00:00Z",
      "payload": {
        "field_id": "field_001",
        "observation_type": "crop_condition",
        "notes": "Leaves showing visible damage."
      }
    }
  ]
}
73. Sync response schema
{
  "data": {
    "accepted": [
      {
        "operation_id": "op_001",
        "server_entity_id": "obs_001",
        "status": "accepted"
      }
    ],
    "rejected": [],
    "conflicts": []
  },
  "meta": {
    "sync_cursor": "cursor_001",
    "completed_at": "2026-11-08T10:00:00Z"
  }
}
74. Synchronisation rules
Create operations
Use unique operation IDs.
Use idempotency keys.
Preserve original client timestamp.
Assign server ID after acceptance.
Prevent duplicate creation on retry.
Updates
Use entity version or revision.
Support If-Match where appropriate.
Reject stale updates when required.
Return conflict metadata.
Deletes
Prefer archive or tombstone records for synchronised entities where historical integrity matters.
Append-only observations
Observations and measurements should be appended rather than overwritten. Corrections should create traceable records.
Physical commands
Offline users may prepare a plan or record a proposed action, but a physical-control command must be freshly validated when connectivity returns.
An expired offline command must never execute simply because it eventually synchronises.
75. Conflict resolution
Entity
Resolution
Field observation
Preserve distinct observations; reconcile duplicates
Measurement
Deduplicate by event identity
Farm profile
Version conflict; user review if needed
Task description
Field-level merge where safe
Task status
Apply domain transition rules
Crop assignment
Validate overlapping assignments
Irrigation plan
Require revalidation
Device command
Never blindly replay
Inventory transaction
Preserve transaction ledger
User preferences
Last accepted revision may be used

76. Sync cursor and change tracking
The server must maintain a reliable change feed.
A sync cursor should be opaque and scoped to:
Authenticated user or device.
Organisation.
Permitted resources.
Sync version.
The cursor must not allow one tenant to retrieve another tenant's changes.
The server must retain deletion tombstones long enough for supported clients to synchronise them.
77. Offline data security
Encrypt sensitive local data at rest where platform support permits.
Protect authentication tokens.
Restrict access to cached records.
Expire data according to retention policy.
Allow remote session revocation.
Do not cache credentials or unnecessary sensitive records.
Do not store physical-control credentials in general-purpose mobile storage.

PART XV — REAL-TIME UPDATES AND EVENTS
78. WebSocket endpoints
Optional endpoint:
/api/v1/realtime
Possible event types:
measurement.created
device.status.changed
alert.created
task.updated
command.status.changed
irrigation.event.created
sync.completed
WebSocket access must use authenticated sessions and enforce tenant/resource permissions.
For simpler use cases, Server-Sent Events may be sufficient.
Real-time delivery is a convenience layer, not the system of record. Clients must be able to recover missed events through ordinary API retrieval.
79. Domain event envelope
{
  "event_id": "evt_001",
  "event_type": "device.status.changed",
  "event_version": "1.0",
  "occurred_at": "2026-11-08T10:00:00Z",
  "organisation_id": "org_001",
  "resource": {
    "type": "device",
    "id": "tnx_dev_001"
  },
  "data": {
    "previous_status": "offline",
    "new_status": "online"
  },
  "correlation_id": "req_001"
}
80. Event delivery
Use a transactional outbox pattern:
Commit domain change and outbox event in the same database transaction.
Background worker reads pending events.
Worker publishes event.
Worker records delivery state.
Consumers deduplicate by event ID.
This prevents lost events caused by committing a database update but failing to publish its notification.

PART XVI — INTEGRATIONS, WEBHOOKS AND DEVELOPER API
81. Integration endpoints
GET /integrations
POST /integrations
GET /integrations/{integrationId}
PATCH /integrations/{integrationId}
POST /integrations/{integrationId}/test
POST /integrations/{integrationId}/sync
GET /integrations/{integrationId}/logs
POST /integrations/{integrationId}/disable
Credentials must be stored in a secure secrets facility, not ordinary integration configuration JSON.
82. Webhook endpoints
GET /webhooks
POST /webhooks
PATCH /webhooks/{webhookId}
DELETE /webhooks/{webhookId}
POST /webhooks/{webhookId}/test
GET /webhooks/{webhookId}/deliveries
POST /webhooks/{webhookId}/deliveries/{deliveryId}/retry
Webhook security
Sign payloads using a secret.
Include timestamp and event ID.
Support secret rotation.
Require HTTPS.
Validate destination URLs.
Prevent server-side request forgery.
Apply delivery retry limits.
Support idempotent consumers.
Example signature header:
X-TNX-Signature: sha256=<signature>
The signature must be calculated over the exact transmitted payload using the agreed signing procedure.
83. API applications and keys
GET /developer/applications
POST /developer/applications
GET /developer/applications/{applicationId}
POST /developer/applications/{applicationId}/keys
POST /developer/api-keys/{keyId}/rotate
DELETE /developer/api-keys/{keyId}
Keys must:
Have explicit scopes.
Be associated with an organisation or application.
Have expiry where appropriate.
Support revocation.
Be stored as hashes or secure credentials where feasible.
Be rate-limited.
Never be displayed again after initial issuance.

PART XVII — REPORTING, COLLABORATION AND ADMINISTRATION
84. Reporting endpoints
GET /reports
POST /reports
GET /reports/{reportId}
POST /reports/{reportId}/generate
GET /report-runs/{runId}
GET /report-runs/{runId}/download
GET /scheduled-reports
POST /scheduled-reports
PATCH /scheduled-reports/{scheduleId}
DELETE /scheduled-reports/{scheduleId}
Long-running reports must execute asynchronously.
85. Collaboration endpoints
GET /comments
POST /comments
PATCH /comments/{commentId}
DELETE /comments/{commentId}
POST /mentions
GET /collaboration/activity
Comments must be linked to an authorised resource and inherit its access controls.
86. Administration endpoints
GET /admin/overview
GET /admin/tenants
GET /admin/users
GET /admin/audit-logs
GET /admin/system/health
GET /admin/system/metrics
GET /admin/security/events
GET /admin/jobs
POST /admin/jobs/{jobId}/retry
Administrative actions must be restricted and audited.

PART XVIII — DATABASE AND API CONSISTENCY
87. Core resource relationships
Organisation
  │
  ├── Memberships ── Users
  │
  └── Farms
        │
        ├── Fields
        │    │
        │    ├── Crop Assignments
        │    ├── Observations
        │    ├── Measurements
        │    ├── Tasks
        │    ├── Irrigation Zones
        │    └── Recommendations
        │
        ├── Devices
        │    │
        │    ├── Sensors
        │    ├── Channels
        │    ├── Measurements
        │    ├── Events
        │    ├── Configurations
        │    └── Commands
        │
        ├── Operations
        ├── Water Sources
        ├── Datasets
        └── Reports
88. Data integrity rules
All tenant-owned records must have organisation ownership.
Farm-owned records must reference an authorised farm.
Field-owned records must reference a valid field.
Device-owned measurements must reference a valid device and channel.
Crop assignments must reference a valid crop and season.
Irrigation events must reference valid operational resources.
Commands must reference a valid target and authorisation context.
Dataset access must be checked independently of dataset discovery.
Deletion must respect historical and audit requirements.
89. Optimistic concurrency
Mutable resources should expose a version or ETag.
Example:
ETag: "resource-v12"
Client update:
If-Match: "resource-v12"
If the resource changed, return 412 Precondition Failed or a documented conflict response.
This prevents two users from silently overwriting each other's changes.
90. Idempotency
Require idempotency for:
Resource creation where clients may retry.
Telemetry batches.
Inventory transactions.
Irrigation plan execution requests.
Physical commands.
Payments, if introduced.
File completion.
Offline sync operations.
An idempotency key must be scoped to the authenticated principal and operation. Reuse with a different request payload must return a conflict.

PART XIX — SECURITY AND PRIVACY
91. API security requirements
TLS for all external traffic.
Strong authentication.
MFA for privileged accounts.
Tenant isolation.
Resource-level authorisation.
Input validation.
Output filtering.
Rate limiting.
Secure secret storage.
Audit logging.
Dependency scanning.
Secure file uploads.
Device credential rotation.
MQTT topic access control.
Protection against replay.
Protection against injection.
CSRF protection where cookie authentication is used.
CORS restrictions.
Security headers.
Incident response procedures.
92. Device security
Unique device identity.
Unique credentials.
TLS-authenticated communication where supported.
No shared default passwords.
No credentials committed to firmware source.
Secure provisioning.
Credential revocation.
Signed firmware.
Device quarantine.
Replay-resistant command handling.
Local safe-state logic.
Where hardware cannot support strong security capabilities, the risk must be documented and compensating controls applied.
93. Data protection
The platform must support:
Data ownership and access policies.
Consent where required.
Purpose limitation.
Export.
Correction.
Deletion requests.
Retention.
Organisation exit.
Audit.
Anonymisation or aggregation where appropriate.
For Kenya operations, assess the Kenya Data Protection Act, 2019 and applicable regulations. International deployments require jurisdiction-specific review.

PART XX — RELIABILITY AND PERFORMANCE
94. Reliability targets
Initial proposed service objectives:
Area
Proposed target
API availability
99.5% initial target
Normal API response
p95 below 500 ms for common reads
Write response
p95 below 800 ms for ordinary writes
Device ingestion
Accepted messages processed promptly, with backlog visibility
Command acknowledgement
Measured by device/network conditions, not guaranteed by API
Backup
Automated daily baseline plus appropriate continuous recovery strategy
Restore
Tested restoration procedure
Audit
Durable and queryable
Sync
Resumable and idempotent

These are planning targets, not guaranteed service commitments. They must be revisited after load testing and operational measurements.
95. Failure handling
Database unavailable
Reject writes safely.
Do not claim persistence.
Queue only where the relevant workflow explicitly supports it.
Recover through retry and reconciliation.
MQTT broker unavailable
Devices buffer telemetry locally.
Commands remain undispatched.
Physical safety remains local.
Show device and command uncertainty.
Redis unavailable
Core database operations should not become dependent on cache availability.
Background jobs may pause.
Degrade non-essential features safely.
External provider unavailable
Retain last known data with freshness indicators.
Do not present old forecasts as current.
Retry with backoff.
Worker failure
Track job state.
Retry idempotent work.
Dead-letter repeated failures.
Provide administrative inspection.
96. Backup and disaster recovery
Required:
Database backups.
Point-in-time recovery where available.
Object storage backups/versioning.
Secrets recovery procedures.
Configuration backups.
Restore tests.
Recovery documentation.
Incident communication.
Define RPO and RTO after deployment requirements and budget are established. Do not assume daily backups alone are sufficient for all production scenarios.

PART XXI — OBSERVABILITY AND OPERATIONS
97. Logging
Use structured logs with:
Timestamp.
Level.
Service/module.
Request ID.
Correlation ID.
User or device identifier where appropriate.
Organisation identifier where appropriate.
Operation.
Result.
Duration.
Error code.
Never log:
Passwords.
Access tokens.
Device secrets.
API keys.
Private keys.
Unnecessary personal data.
98. Metrics
Track:
API latency.
API error rate.
Database connection health.
Database query performance.
MQTT connection count.
Telemetry ingestion rate.
Rejected telemetry.
Duplicate telemetry.
Device offline duration.
Command delivery latency.
Command success/failure.
Safety blocks.
Sync failures.
Worker queue length.
Integration errors.
Report generation duration.
Storage usage.
99. Tracing
Use correlation IDs across:
API requests.
Database transactions.
Worker jobs.
MQTT ingestion.
Command dispatch.
External integrations.
Notifications.
A command should be traceable from the user's original request to its device acknowledgement and final result.

PART XXII — TESTING AND ACCEPTANCE
100. API testing
Schema validation.
Authentication tests.
Authorisation tests.
Tenant-isolation tests.
Resource ownership tests.
CRUD tests.
Pagination tests.
Filtering tests.
Idempotency tests.
Concurrency tests.
Rate-limit tests.
Error contract tests.
API version tests.
101. Device testing
Provisioning.
Invalid credentials.
Duplicate telemetry.
Delayed telemetry.
Out-of-order telemetry.
Clock drift.
Network interruption.
Broker restart.
Power interruption.
Sensor disconnection.
Invalid sensor readings.
Firmware mismatch.
Configuration rejection.
Command expiry.
Duplicate command.
Failed acknowledgement.
102. Physical-control testing
Test on a controlled test rig before connecting real pumps or other operational equipment.
Cases:
User lacks permission.
Device offline.
Command expired.
Water source unavailable.
Pump fault.
Dry-run condition.
Emergency stop active.
Conflicting command.
Controller reboot.
Relay failure.
No flow feedback.
Communication lost during execution.
Unexpected actuator state.
The acceptance criterion is safe behaviour, not merely successful message delivery.
103. Offline testing
Create observation offline.
Edit task offline.
Upload attachments after reconnection.
Retry after partial upload.
Duplicate sync.
Conflict resolution.
Expired credentials.
Device buffer overflow.
App termination during sync.
Server interruption.
Long offline period.
104. Security testing
Cross-tenant access attempts.
Broken object-level authorisation.
Privilege escalation.
Token replay.
Credential leakage.
MQTT topic abuse.
Malicious upload.
Webhook SSRF.
Rate-limit bypass.
SQL injection.
XSS.
CSRF where applicable.
Secrets in logs.
Firmware authenticity.
105. End-to-end acceptance scenarios
Scenario A: Farm creation
A user creates an organisation, registers a farm, defines its boundary and adds fields.
Expected:
Valid database records.
Correct tenant ownership.
Correct spatial geometry.
Correct role-based visibility.
Scenario B: Device telemetry
A provisioned device sends soil moisture and temperature readings.
Expected:
Authenticated device.
Valid channel association.
Deduplication.
Immutable observation.
Quality metadata.
Measurement visible in authorised field views.
Scenario C: Alert creation
A valid sequence of readings crosses an approved threshold.
Expected:
Alert generated.
Evidence linked.
Duplicate alert suppression works.
User notification delivered according to preference.
Scenario D: Irrigation request
An authorised user submits an approved irrigation plan.
Expected:
Safety checks executed.
Command recorded.
Device validates command.
Acknowledgement recorded.
Result reconciled.
Audit history complete.
Scenario E: Offline observation
A user records an observation without connectivity and later reconnects.
Expected:
Local record retained.
Sync operation uniquely identified.
Server record created once.
Attachments associated.
User informed of completion.

PART XXIII — IMPLEMENTATION AND DEPLOYMENT CONTRACT
106. Proposed repository structure
terranexus/
│
├── apps/
│   ├── web/
│   └── mobile/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── modules/
│   │   │   ├── identity/
│   │   │   ├── organisations/
│   │   │   ├── farms/
│   │   │   ├── fields/
│   │   │   ├── crops/
│   │   │   ├── devices/
│   │   │   ├── sensors/
│   │   │   ├── telemetry/
│   │   │   ├── data/
│   │   │   ├── monitoring/
│   │   │   ├── operations/
│   │   │   ├── irrigation/
│   │   │   ├── control/
│   │   │   ├── intelligence/
│   │   │   ├── integrations/
│   │   │   ├── notifications/
│   │   │   ├── reports/
│   │   │   └── administration/
│   │   ├── workers/
│   │   └── main.py
│   │
│   ├── migrations/
│   └── tests/
│
├── firmware/
│   ├── device-profiles/
│   ├── esp32-node/
│   ├── shared/
│   └── tests/
│
├── infrastructure/
│   ├── docker/
│   ├── mqtt/
│   ├── monitoring/
│   ├── deployment/
│   └── backups/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── devices/
│   ├── security/
│   └── operations/
│
└── README.md
107. Deployment environments
Local development
FastAPI.
PostgreSQL + PostGIS.
Redis.
MQTT broker.
Object storage emulator or local storage adapter.
Worker process.
Web application.
Device simulator.
Testing
Isolated database.
Simulated device clients.
Test broker.
Fake external provider responses.
Automated integration tests.
Staging
Production-like configuration.
Test credentials.
Hardware test rig.
Monitoring.
Migration validation.
Production
TLS reverse proxy.
Application deployment.
Database.
Redis.
MQTT.
Workers.
Object storage.
Secrets management.
Backups.
Observability.
Incident response.
108. Migration rules
Use versioned database migrations.
Test migrations on representative data.
Back up before risky changes.
Avoid destructive schema changes without migration plans.
Keep application and migration versions compatible.
Preserve measurement and command history.
Test rollback or forward-recovery procedures.
109. API documentation requirements
Every endpoint must document:
Method.
URL.
Purpose.
Authentication.
Permissions.
Request schema.
Response schema.
Error responses.
Pagination.
Idempotency behaviour.
Rate limits.
Side effects.
Audit behaviour.
Example request.
Example response.
OpenAPI should be generated from the actual application contracts and reviewed for accuracy.

PART XXIV — COMPLETE API CATALOGUE AND TRACEABILITY
110. Domain endpoint inventory
The following is the minimum initial endpoint inventory. Individual endpoint schemas and validation rules must be implemented and maintained in OpenAPI.
Domain
Endpoint groups
Authentication
/auth/*
Organisations
/organisations/*
Memberships
/memberships/*
Roles
/roles/*
Farms
/farms/*
Fields
/fields/*
Crops
/crops/*
Varieties
/crop-varieties/*
Seasons
/seasons/*
Crop assignments
/crop-assignments/*
Observations
/observations/*
Devices
/devices/*
Gateways
/gateways/*
Sensors
/sensors/*
Calibration
/calibrations/*
Telemetry
/ingestion/*
Measurements
/measurements/*
Data sources
/data-sources/*
Datasets
/datasets/*
Imports
/imports/*
Exports
/exports/*
Processing
/data-processing/*
Monitoring
/monitoring/*
Alerts
/alerts/*
Notifications
/notifications/*
Tasks
/tasks/*
Activities
/activities/*
Equipment
/equipment/*
Inventory
/inventory/*
Inspections
/inspections/*
Harvest
/harvest-records/*
Irrigation
/irrigation/*
Water
/water-sources/*
Commands
/commands/*
Configuration
/configurations/*
Firmware
/firmware/*
Intelligence
/intelligence/*
Recommendations
/recommendations/*
Forecasts
/forecasts/*
Models
/models/*
Model runs
/model-runs/*
Integrations
/integrations/*
Webhooks
/webhooks/*
Files
/files/*
Reports
/reports/*
Collaboration
/comments/*
Sync
/sync/*
Realtime
/realtime
Developer
/developer/*
Administration
/admin/*
Health
/health/*

111. Cross-document traceability
Earlier design
API responsibility
TNX-UI-001: Dashboard
Farm summary, monitoring and alerts
TNX-UI-001: Farm overview
Farm and field APIs
TNX-UI-001: Device details
Device, sensor, event and telemetry APIs
TNX-UI-001: Measurements explorer
Measurement and dataset APIs
TNX-UI-001: Irrigation control
Plan, command, acknowledgement and safety APIs
TNX-UI-001: Recommendations
Intelligence and evidence APIs
TNX-UI-001: Research workspace
Dataset, import, model and export APIs
TNX-UI-001: Offline mobile
Sync and attachment APIs
TNX-UI-001: Administration
Tenant, permission, audit and health APIs

The UI must not invent its own domain rules. Backend contracts remain authoritative.

PART XXV — ADDITIONAL REQUIREMENTS THAT MUST NOT BE OMITTED
112. Device and sensor lifecycle
The platform must support:
Registration.
Provisioning.
Activation.
Assignment.
Reassignment.
Maintenance.
Calibration.
Credential rotation.
Quarantine.
Revocation.
Decommissioning.
Historical record retention.
113. Data lifecycle
The platform must support:
Collection.
Validation.
Normalisation.
Storage.
Quality assessment.
Correction.
Aggregation.
Export.
Retention.
Archiving.
Deletion where legally and operationally permitted.
114. Agricultural reference data
Do not hardcode agricultural knowledge throughout the application.
Create managed reference catalogues for:
Crop types.
Varieties.
Growth stages.
Measurement types.
Units.
Soil classifications.
Irrigation methods.
Activity types.
Alert types.
Device capabilities.
Quality states.
Reference records should be versioned where changes affect historical interpretation.
115. Localisation
Support:
Multiple languages.
Local date and number formats.
Timezones.
Local units where appropriate.
Regional agricultural terminology.
Local currency for applicable commercial features.
Store canonical data independently of the language used to display it.
116. Commercial and subscription boundaries
Potential future features:
Subscription plans.
Usage metering.
Storage limits.
Device limits.
Premium integrations.
Paid reports.
Organisation billing.
Do not make billing a dependency of basic safety, data integrity or user access to their own permitted records.
117. Support and incident workflows
Support systems must include:
Ticket creation.
Device issue reporting.
Integration failure reporting.
Incident categorisation.
Severity.
Assignment.
Resolution.
User communication.
Internal audit trail.
118. Research and experimental capabilities
The platform may support:
Local AI inference.
QVAC integration.
Quantum computing experiments using Qiskit.
Blockchain-backed provenance verification.
Advanced optimisation.
These must remain optional, independently governed modules. They must not be required for basic farm management, telemetry, data access or safe equipment operation.
119. Interoperability
Design adapters around established standards where useful:
MQTT.
REST.
OpenAPI.
JSON.
CSV.
GeoJSON.
OGC SensorThings API concepts.
OGC API standards.
ISO 19115 metadata concepts.
Relevant agricultural data exchange standards.
Do not claim compliance merely because the platform uses a similar JSON structure. Formal conformance requires implementation and testing against the relevant specification.
120. Accessibility and usability
The API must support the UI's accessibility requirements:
Localised labels where appropriate.
Human-readable validation errors.
Stable resource identifiers.
Clear status codes.
Predictable pagination.
Consistent empty responses.
Accessible chart data exports.
No unnecessary reliance on real-time connectivity.

PART XXVI — IMPLEMENTATION PHASES
121. Phase 0 — Contract and schema validation
Deliver:
API conventions.
Database mapping.
Authentication model.
Device identity model.
Telemetry schema.
Command safety contract.
Sync contract.
OpenAPI skeleton.
Test fixtures.
Exit condition: frontend, backend and firmware teams agree on the core contracts.
122. Phase 1 — Core platform API
Deliver:
Identity.
Organisations.
Farms.
Fields.
Crops.
Seasons.
Tasks.
Observations.
Permissions.
Audit.
Exit condition: a user can create and manage an authorised farm workspace.
123. Phase 2 — Device connectivity
Deliver:
Device registry.
Provisioning.
MQTT broker integration.
Sensor registry.
Telemetry ingestion.
Measurement storage.
Device status.
Data-quality pipeline.
Exit condition: a real test device sends authenticated, correctly associated measurements.
124. Phase 3 — Monitoring and offline workflows
Deliver:
Monitoring.
Charts.
Alerts.
Notifications.
Mobile local database.
Sync manager.
Conflict handling.
Attachments.
Exit condition: a field user can capture records offline and reliably synchronise them.
125. Phase 4 — Irrigation and safe control
Deliver:
Irrigation zones.
Water sources.
Plans.
Approval.
Command service.
Device acknowledgement.
Local safety.
Physical test rig.
Audit and reconciliation.
Exit condition: safe controlled operation is demonstrated on a test rig under normal and failure conditions.
126. Phase 5 — Intelligence and external integrations
Deliver:
Weather.
Soil data.
Recommendations.
Model registry.
Evaluation.
Integration adapters.
Dataset catalogue.
Reporting.
Exit condition: recommendations show traceable evidence and validated limitations.
127. Phase 6 — Ecosystem and scale
Deliver:
External API applications.
Webhooks.
Multi-organisation governance.
Research tools.
Advanced analytics.
Scale and resilience improvements.
Exit condition: independently developed integrations can use documented, secure contracts.

PART XXVII — FINAL ENGINEERING ACCEPTANCE
128. TNX-API-001 completion criteria
The specification is ready for implementation planning when:
Every module has an owner.
API naming and versioning are agreed.
Authentication and tenant boundaries are approved.
Core request and response schemas are defined.
Database relationships match the API.
Telemetry schemas are agreed with firmware engineering.
MQTT topic permissions are defined.
Device provisioning is specified.
Command lifecycle is approved.
Physical safety requirements are reviewed.
Offline sync behaviour is defined.
Conflict handling is agreed.
External integration rules are documented.
Audit and event requirements are defined.
Security review is completed.
Testing strategy is approved.
Deployment and backup plans exist.
UI routes are mapped to API operations.
OpenAPI documentation is generated and reviewed.
129. Outstanding implementation decisions
The following must be resolved before production implementation:
Final identity provider.
Final MQTT broker.
Final object-storage provider.
Device provisioning mechanism for each hardware family.
Exact ESP32 pin mapping and firmware protocol.
Sensor calibration procedures.
Supported actuator hardware and electrical protections.
Water-flow and pump feedback availability.
Device reporting intervals and power constraints.
Final mobile local database and encryption approach.
Sync retention and conflict policies.
Data retention and legal requirements.
Weather and satellite provider contracts.
Hosting provider and deployment topology.
Production performance and recovery targets.
Commercial and billing scope.
These are not reasons to stop architectural work. They are explicit decisions to validate before locking implementation details.
130. Definition of done
A TerraNexus API feature is complete only when:
Its business purpose is documented.
Its data ownership is clear.
Its permission rules are enforced.
Its request and response schemas are defined.
Its error behaviour is documented.
Its audit behaviour is defined.
Its idempotency and concurrency behaviour are considered.
Its security requirements are tested.
Its offline behaviour is specified where relevant.
Its frontend contract is documented.
Its automated tests pass.
Its operational metrics exist.
Its documentation is updated.
Its failure and recovery behaviour is verified.

Document status: TNX-API-001 establishes the proposed API, device, telemetry, MQTT, command, irrigation safety, offline synchronisation, integration, security and operational contracts for TerraNexus.
Important: This is the complete proposed contract baseline, not a finished implementation or formal hardware safety certification. Production endpoint schemas, hardware-specific limits, provider integrations, security controls and operational targets must be verified during engineering and field validation.
What this adds to the TerraNexus master specification
The three documents now have distinct responsibilities:
Document
Responsibility
Status
