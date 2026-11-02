Document ID: TNX-ARCH-001
Version: 1.0
Status: Proposed architecture baseline
Product: Open Agricultural Intelligence & Operations Platform
Architecture approach: Modular, API-first, event-driven where appropriate, multi-tenant and offline-first
Implementation status: Design only

1. Architecture objectives
TerraNexus must provide a common technical foundation for multiple agricultural applications.
The architecture must support:
Multiple farms, fields, organisations and users.
Different agricultural devices and sensor manufacturers.
Real-time and historical agricultural data.
External agricultural data providers.
Farm operations and resource management.
Weather, soil and crop intelligence.
Agricultural analytics and machine learning.
Safe irrigation and equipment control.
Offline mobile and edge-device operation.
Data exchange and interoperability.
Research and third-party integrations.
Future expansion without rebuilding the foundation.
The architecture must distinguish between the platform's core infrastructure and the applications built on top of it.
1.1 Architectural principles
Principle
Architectural implication
Modular architecture
Independent, clearly defined business modules
API-first
Applications communicate through documented APIs
Multi-tenant
Strong separation between organisations
Event-driven
Asynchronous events for ingestion and background work
Offline-first
Local data and synchronisation mechanisms
Interoperable
External providers and devices use standard interfaces
Data provenance
Measurements retain their origin and processing history
Secure by design
Identity, authorisation and audit are foundational
AI optional
Core operations work without AI
Human oversight
Important agricultural decisions remain reviewable
Observable
Every critical subsystem exposes operational health
Extensible
New applications and providers can be integrated

2. Architecture style
2.1 Recommended approach: modular monolith with event-driven infrastructure
TerraNexus should initially use a modular backend architecture, not dozens of independently deployed microservices.
The backend will contain well-separated modules with explicit responsibilities and internal interfaces.
The following components can operate independently from the beginning where there is a strong technical reason:
MQTT broker.
Database.
Redis.
Background workers.
Object storage.
Web application.
Mobile application.
The main business backend can initially be deployed as one application with independently testable modules.
This gives TerraNexus:
Simpler development.
Easier transactions.
Less infrastructure overhead.
Clear module boundaries.
Easier debugging.
A path to independently scaling or extracting services later.
Important: A module should not directly modify another module's internal database tables. It should use its defined interface or publish/consume appropriate events.
2.2 Logical architecture
flowchart TB
    subgraph APPLICATIONS["APPLICATION LAYER"]
        A1["TerraNexus Web"]
        A2["TerraNexus Mobile"]
        A3["Agronomist Workspace"]
        A4["Research Workspace"]
        A5["Developer Portal"]
        A6["Admin Console"]
    end

    subgraph ACCESS["ACCESS AND SECURITY"]
        B1["API Gateway / Reverse Proxy"]
        B2["Backend for Frontend"]
        B3["Identity Provider"]
        B4["Authorisation Policies"]
        B5["Offline Synchronisation"]
    end

    subgraph CORE["CORE BUSINESS PLATFORM"]
        C1["Organisation"]
        C2["Farm and Field"]
        C3["Crop and Season"]
        C4["Device Management"]
        C5["Agricultural Data"]
        C6["Operations"]
        C7["Irrigation"]
        C8["Monitoring and Alerts"]
        C9["Reporting"]
        C10["Integration Management"]
    end

    subgraph INTELLIGENCE["INTELLIGENCE PLATFORM"]
        D1["Rules Engine"]
        D2["Analytics"]
        D3["Forecasting"]
        D4["ML Models"]
        D5["Recommendation Engine"]
        D6["Optional Local AI"]
    end

    subgraph CONNECTIVITY["CONNECTIVITY"]
        E1["MQTT Broker"]
        E2["REST Ingestion"]
        E3["External APIs"]
        E4["CSV / GeoJSON Import"]
        E5["IoT Gateways"]
        E6["ESP32 Devices"]
    end

    subgraph DATA["DATA INFRASTRUCTURE"]
        F1["PostgreSQL / PostGIS"]
        F2["Time-Series Storage"]
        F3["Redis"]
        F4["Object Storage"]
        F5["Event and Job Queue"]
        F6["Search Index"]
    end

    APPLICATIONS --> ACCESS
    ACCESS --> CORE
    CORE --> INTELLIGENCE
    CONNECTIVITY --> CORE
    CORE --> DATA
    INTELLIGENCE --> DATA
    INTELLIGENCE --> CORE
3. Application architecture
3.1 TerraNexus Web
Technology: React + Vite.
Responsibilities:
Main farm management interface.
Organisation management.
Monitoring.
Analytics.
Device administration.
Irrigation management.
Research interface.
Developer tools.
Administration.
The web application must consume backend APIs. It must not connect directly to the production database or MQTT broker.
Suggested internal structure:
web/
├── src/
│   ├── app/
│   │   ├── routing/
│   │   ├── providers/
│   │   ├── layouts/
│   │   └── permissions/
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── organisations/
│   │   ├── farms/
│   │   ├── fields/
│   │   ├── crops/
│   │   ├── devices/
│   │   ├── monitoring/
│   │   ├── data/
│   │   ├── operations/
│   │   ├── irrigation/
│   │   ├── intelligence/
│   │   ├── reports/
│   │   ├── integrations/
│   │   └── administration/
│   │
│   ├── components/
│   ├── design-system/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   ├── utilities/
│   └── assets/
│
└── tests/
Each module owns its:
Pages.
Components.
API client functions.
Validation schemas.
State management.
Tests.
Permissions.
Shared components belong in the design system rather than being duplicated.
3.2 TerraNexus Mobile
Recommended technology: React Native with Expo.
Primary users:
Farmers.
Farm managers.
Field workers.
Agronomists.
Extension officers.
Responsibilities:
View assigned farms.
Review field conditions.
Receive notifications.
Record field observations.
Capture photographs.
Create and update tasks.
Record agricultural activities.
View recent measurements.
Operate authorised offline workflows.
Synchronise when connectivity returns.
Mobile architecture:
mobile/
├── src/
│   ├── app/
│   ├── modules/
│   ├── components/
│   ├── navigation/
│   ├── offline/
│   ├── database/
│   ├── sync/
│   ├── notifications/
│   ├── permissions/
│   └── services/
│
└── tests/
The mobile application should use a local SQLite database for supported offline records.
It must not assume a constant internet connection.
3.3 Application-specific workspaces
TerraNexus should not force every user to use one complicated dashboard.
The same backend should provide different workspaces:
Workspace
Main users
Focus
Farmer
Farmers
Farm conditions and activities
Farm Operations
Farm managers
Tasks, equipment and resources
Agronomy
Agronomists
Field assessment and recommendations
Extension
Extension officers
Farmer and community support
Research
Researchers
Datasets and analysis
Organisation
Cooperatives
Multi-farm coordination
Developer
Integration partners
APIs and connectors
Administration
Platform operators
Governance and system health

These are different experiences over shared platform services.
4. Backend architecture
4.1 Backend technology
Recommended baseline:
Python.
FastAPI.
Pydantic.
SQLAlchemy.
Alembic.
PostgreSQL.
PostGIS.
Redis.
Celery.
MQTT broker.
4.2 Backend internal structure
backend/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   ├── permissions.py
│   │   └── observability.py
│   │
│   ├── modules/
│   │   ├── identity/
│   │   ├── organisations/
│   │   ├── memberships/
│   │   ├── farms/
│   │   ├── fields/
│   │   ├── crops/
│   │   ├── seasons/
│   │   ├── devices/
│   │   ├── sensors/
│   │   ├── ingestion/
│   │   ├── measurements/
│   │   ├── datasets/
│   │   ├── monitoring/
│   │   ├── alerts/
│   │   ├── tasks/
│   │   ├── activities/
│   │   ├── equipment/
│   │   ├── irrigation/
│   │   ├── intelligence/
│   │   ├── recommendations/
│   │   ├── integrations/
│   │   ├── notifications/
│   │   ├── reports/
│   │   ├── audit/
│   │   └── administration/
│   │
│   ├── shared/
│   │   ├── events/
│   │   ├── schemas/
│   │   ├── pagination/
│   │   ├── units/
│   │   └── utilities/
│   │
│   └── workers/
│
├── migrations/
├── tests/
├── scripts/
└── pyproject.toml
4.3 Module boundary specification
Module
Owns
Must not own
Identity
Users, sessions, authentication
Farm operations
Organisations
Tenants and membership
Sensor measurements
Farms
Farms, fields and boundaries
Device command execution
Crops
Crop catalogue and seasons
User authentication
Devices
Device identity and configuration
Agricultural recommendations
Ingestion
Incoming telemetry and validation
User interface state
Measurements
Agricultural observations
Physical equipment execution
Monitoring
Conditions, rules and alerts
Device credentials
Operations
Tasks and activity records
Sensor firmware
Irrigation
Water and irrigation workflows
Global identity
Intelligence
Models and recommendations
Direct uncontrolled equipment access
Integrations
External provider connections
Internal domain ownership
Notifications
Delivery and preferences
Business-domain ownership
Reporting
Report generation
Authoritative source records
Audit
Immutable activity records
Unrestricted modification

4.4 Internal module interface
A module should expose:
Service functions.
Request and response schemas.
Domain events.
Permission requirements.
Repository interfaces.
For example:
Irrigation Module
    create_plan()
    approve_plan()
    execute_plan()
    stop_irrigation()
    get_irrigation_history()

Device Module
    register_device()
    provision_device()
    get_device_status()
    queue_command()
    acknowledge_command()

Measurement Module
    ingest_measurement()
    validate_measurement()
    query_measurements()
    calculate_data_quality()
The irrigation module should request a device command through the device-control interface. It should not directly manipulate MQTT credentials or publish arbitrary messages.
5. Event-driven architecture
5.1 Why events are needed
Agricultural data arrives continuously and may trigger several different workflows.
For example, one sensor measurement may result in:
Historical storage.
Data-quality evaluation.
Updated monitoring indicators.
An alert.
A recommendation.
A notification.
These operations should not all block the original ingestion request.
5.2 Event infrastructure
Use:
Redis-backed jobs for initial background processing.
An event abstraction inside the application.
A transactional outbox pattern for important domain events.
MQTT for device communication.
A dedicated event streaming platform only when justified by actual throughput.
Do not use Redis as the sole permanent source of important business events.
5.3 Proposed domain events
user.registered
organisation.created
farm.created
field.created

device.registered
device.provisioned
device.connected
device.disconnected
device.telemetry_received
device.command_requested
device.command_acknowledged
device.command_failed

measurement.received
measurement.validated
measurement.rejected
measurement.quality_changed

alert.created
alert.acknowledged
alert.resolved

task.created
task.assigned
task.completed

irrigation.plan_created
irrigation.plan_approved
irrigation.started
irrigation.completed
irrigation.failed

recommendation.generated
recommendation.accepted
recommendation.rejected
recommendation.outcome_recorded

integration.failed
integration.recovered
report.generated
5.4 Event envelope
Every event should contain:
{
  "event_id": "uuid",
  "event_type": "measurement.received",
  "event_version": "1.0",
  "occurred_at": "2026-11-08T10:00:00Z",
  "producer": "measurement-ingestion",
  "organisation_id": "uuid",
  "correlation_id": "uuid",
  "causation_id": null,
  "payload": {}
}
Rules:
Events have unique IDs.
Consumers must tolerate duplicate delivery.
Events must be versioned.
Sensitive payloads should not be exposed unnecessarily.
Important events must be traceable.
Failed processing must be retryable or recoverable.
6. Data architecture boundaries
6.1 Primary transactional database
PostgreSQL + PostGIS
Stores:
Users and organisations.
Farms and fields.
Crops and seasons.
Devices and sensors.
Tasks and activities.
Irrigation plans.
Alerts.
Recommendations.
Data-source metadata.
Audit information.
Integration configuration.
PostgreSQL is the authoritative source for core business records.
6.2 Time-series storage
Initial strategy:
PostgreSQL measurement tables.
Time-based partitioning.
Appropriate composite indexes.
Retention and archival policies.
Evaluate TimescaleDB when:
Measurement volume becomes substantial.
Time-series queries become expensive.
Continuous aggregates materially improve performance.
Retention and compression features provide operational value.
The decision should follow performance testing.
6.3 Redis
Responsibilities:
Cache.
Short-lived state.
Rate limiting.
Background job broker.
Temporary processing state.
Distributed coordination where needed.
Redis must not become the only place where critical agricultural records exist.
6.4 Object storage
Use S3-compatible storage or MinIO for:
Crop images.
Field photographs.
Soil reports.
Imported datasets.
Export files.
Satellite imagery.
Documents.
Model artefacts.
Store metadata and permissions in PostgreSQL, with the file itself in object storage.
6.5 Search
Start with PostgreSQL full-text search.
Introduce OpenSearch if there is a genuine need for:
Complex cross-domain search.
Large-scale document indexing.
Advanced search analytics.
High-volume search workloads.
7. Integration architecture
7.1 Connector model
Every external data provider should implement a consistent connector interface.
Connector
    validate_configuration()
    authenticate()
    test_connection()
    fetch_data()
    normalise_data()
    validate_data()
    report_status()
    handle_failure()
Connector categories:
Weather.
Soil data.
Satellite and remote sensing.
Agricultural datasets.
IoT manufacturers.
Farm management platforms.
Equipment manufacturers.
Research datasets.
Optional financial and payment services.
7.2 Integration flow
flowchart LR
    PROVIDER["External Provider"]
    CONNECTOR["Connector"]
    NORMALISE["Normalisation"]
    VALIDATE["Validation"]
    INGEST["Ingestion"]
    STORE["Agricultural Data Store"]
    EVENT["Domain Event"]
    CONSUMERS["Monitoring / Analytics / Reports"]

    PROVIDER --> CONNECTOR
    CONNECTOR --> NORMALISE
    NORMALISE --> VALIDATE
    VALIDATE --> INGEST
    INGEST --> STORE
    STORE --> EVENT
    EVENT --> CONSUMERS
Each connector must support:
Authentication.
Credential management.
Rate limits.
Retry policies.
Provider outages.
Schema changes.
Data provenance.
Licence information.
Synchronisation status.
8. Intelligence architecture boundaries
The intelligence subsystem should not be a single AI service.
It should have distinct components.
Component
Responsibility
Rules engine
Deterministic agricultural and operational rules
Analytics engine
Statistical analysis and indicators
Forecasting service
Future-condition estimation
Model registry
Model versions and metadata
Model execution
Model inference
Recommendation engine
Evidence-based decision support
Evaluation service
Compare predictions and outcomes
Local AI adapter
Optional QVAC or other local inference
Optimisation service
Resource allocation and scheduling

8.1 Recommendation flow
flowchart TD
    START["Request Recommendation"]
    CONTEXT["Retrieve Farm and Field Context"]
    DATA["Retrieve Measurements and Weather"]
    QUALITY["Check Data Quality"]
    RULES["Evaluate Rules and Models"]
    EVIDENCE["Build Evidence"]
    RESULT["Generate Recommendation"]
    HUMAN["Human Review"]
    DECISION["Accept / Reject / Defer"]
    ACTION["Approved Operational Action"]
    OUTCOME["Record Outcome"]

    START --> CONTEXT
    CONTEXT --> DATA
    DATA --> QUALITY
    QUALITY --> RULES
    RULES --> EVIDENCE
    EVIDENCE --> RESULT
    RESULT --> HUMAN
    HUMAN --> DECISION
    DECISION --> ACTION
    ACTION --> OUTCOME
If required data is missing, the system should communicate that limitation rather than manufacture certainty.
8.2 AI execution boundary
The AI subsystem can:
Analyse authorised information.
Summarise records.
Explain results.
Produce forecasts.
Suggest actions.
It cannot independently bypass:
Access control.
Equipment safety.
Device command authorisation.
Human approval requirements.
Data-quality validation.
9. Device and edge architecture
9.1 Device integration model
Every device must be registered in the platform before being trusted.
A device record includes:
Device identity.
Manufacturer.
Hardware model.
Firmware version.
Supported protocols.
Capabilities.
Organisation.
Farm and field association.
Provisioning state.
Security credentials reference.
Last communication.
9.2 Device communication architecture
flowchart TB
    subgraph FIELD["FIELD"]
        S["Sensors"]
        ESP["ESP32"]
        P["Local Pump / Relay Control"]
        BUF["Persistent Local Buffer"]
    end

    subgraph CONNECTIVITY["CONNECTIVITY"]
        WIFI["Wi-Fi"]
        LORA["LoRaWAN Gateway"]
        CELL["Cellular Gateway"]
    end

    subgraph PLATFORM["TERRANEXUS"]
        MQTT["MQTT Broker"]
        REG["Device Registry"]
        ING["Telemetry Ingestion"]
        DB["Measurement Store"]
        CMD["Command Service"]
    end

    S --> ESP
    ESP --> P
    ESP --> BUF
    BUF --> WIFI
    BUF --> LORA
    BUF --> CELL
    WIFI --> MQTT
    LORA --> MQTT
    CELL --> MQTT
    MQTT --> ING
    REG --> CMD
    ING --> DB
    CMD --> MQTT
9.3 Hardware safety boundary
The device must retain local safety logic.
For example:
Maximum pump runtime.
Emergency stop.
Sensor fault handling.
Pump protection.
Command expiry.
Safe state on invalid control input.
The cloud platform must not be required to maintain electrical or physical safety.
9.4 Command path
User requests an operation.
Backend checks user permissions.
Irrigation module validates the requested operation.
Safety policy is evaluated.
Device command is created.
Command is published.
Device validates command and expiry.
Device executes only if local safety checks pass.
Device acknowledges.
Backend records the result.
User interface displays the outcome.
A timeout must not be displayed as a successful operation.
10. Offline architecture
10.1 Mobile offline subsystem
Components:
SQLite.
Local repository.
Pending operation queue.
Synchronisation manager.
Conflict resolver.
Attachment queue.
Sync-status interface.
10.2 Edge offline subsystem
Components:
Persistent telemetry buffer.
Local timestamps.
Sequence numbers.
Retry policy.
Local safety controller.
Reconnection manager.
10.3 Synchronisation service
Responsibilities:
Authenticate the client.
Validate operations.
Check permissions.
Deduplicate requests.
Resolve conflicts.
Preserve audit records.
Return accepted and rejected operations.
10.4 Conflict strategy
Data type
Strategy
Sensor observations
Append-only and deduplicated
Field observations
Preserve source and version
Tasks
Version-aware updates
Farm metadata
Conflict detection
Irrigation commands
Never replay stale commands automatically
Photos
Upload with metadata and unique IDs
Audit events
Preserve event history

11. Infrastructure and deployment architecture
11.1 Initial deployment
Use a containerised deployment.
Suggested production components:
Component
Initial deployment
Web application
Static hosting or web container
Mobile application
Distribution through mobile stores
Reverse proxy
Caddy or Nginx
Backend API
FastAPI container
Background workers
Celery containers
PostgreSQL
Managed or dedicated database
PostGIS
PostgreSQL extension
Redis
Managed or dedicated service
MQTT
Mosquitto or EMQX
Object storage
S3-compatible storage
Monitoring
Prometheus and Grafana
Logging
Loki or equivalent
Error tracking
Sentry or equivalent

11.2 Deployment diagram
flowchart TB
    INTERNET["Internet / Mobile Networks"]

    subgraph EDGE["EDGE ACCESS"]
        CDN["CDN / Static Hosting"]
        PROXY["Reverse Proxy / TLS"]
    end

    subgraph APP["APPLICATION ENVIRONMENT"]
        WEB["Web Application"]
        API["FastAPI"]
        WORKER["Background Workers"]
        SCHED["Scheduled Jobs"]
    end

    subgraph MESSAGING["MESSAGING"]
        MQTT["MQTT Broker"]
        REDIS["Redis"]
    end

    subgraph STORAGE["PERSISTENT DATA"]
        PG["PostgreSQL + PostGIS"]
        OBJ["Object Storage"]
        BACKUP["Encrypted Backups"]
    end

    subgraph ANALYTICS["INTELLIGENCE ENVIRONMENT"]
        RULE["Rules Engine"]
        ML["ML Workers"]
        LOCAL["Optional Local AI"]
    end

    subgraph OPERATIONS["OPERATIONS"]
        METRICS["Prometheus"]
        DASH["Grafana"]
        LOGS["Centralised Logs"]
        ERR["Error Tracking"]
    end

    INTERNET --> CDN
    INTERNET --> PROXY
    CDN --> WEB
    PROXY --> API
    API --> PG
    API --> REDIS
    API --> MQTT
    API --> OBJ
    REDIS --> WORKER
    WORKER --> PG
    WORKER --> OBJ
    WORKER --> RULE
    RULE --> ML
    RULE --> LOCAL
    PG --> BACKUP
    OBJ --> BACKUP
    API --> METRICS
    WORKER --> METRICS
    MQTT --> METRICS
    METRICS --> DASH
    API --> LOGS
    WORKER --> LOGS
    API --> ERR
11.3 Environment separation
Maintain four environments:
Development
Local development.
Test data.
Local containers.
Simulated devices.
Testing
Automated tests.
Integration testing.
Simulated external providers.
Hardware-in-the-loop tests where available.
Staging
Production-like infrastructure.
Release validation.
User acceptance testing.
Pilot preparation.
Production
Real users.
Real devices.
Production credentials.
Monitored data and operations.
Never share production credentials with local development.
11.4 Network boundaries
Use separate logical network zones:
Public access zone.
Application zone.
Database zone.
Messaging zone.
Administrative zone.
Database ports, Redis ports and internal management interfaces must not be exposed directly to the public internet.
MQTT access must use controlled authentication and authorisation.
Administrative interfaces should require elevated access.
12. Multi-tenancy architecture
12.1 Tenant model
The organisation is the primary tenant.
Platform
  └── Organisation
       ├── Members
       ├── Farms
       │    ├── Fields
       │    ├── Devices
       │    └── Activities
       ├── Integrations
       └── Data-sharing policies
Users may belong to multiple organisations.
A farm may have authorised external collaborators.
12.2 Isolation rules
Every tenant-owned record has an organisation association where appropriate.
API queries must enforce tenant access.
Cross-tenant access must be denied by default.
Background jobs must preserve tenant context.
Object-storage access must be authorised.
Reports must not leak data between organisations.
Device identities must be bound to their authorised scope.
Use PostgreSQL Row-Level Security as an additional defence where appropriate, alongside application-level authorisation.
13. Observability architecture
Every important component must expose health and operational information.
13.1 Metrics
Monitor:
API request volume.
API latency.
HTTP errors.
Database connections.
Database query latency.
Queue depth.
Background job failures.
MQTT connections.
Telemetry ingestion rate.
Invalid measurement rate.
Offline synchronisation failures.
Command acknowledgement delays.
Notification delivery failures.
Model execution duration.
13.2 Logs
Logs should include:
Timestamp.
Severity.
Service.
Request ID.
Correlation ID.
Organisation context where safe.
Event or operation.
Error information.
Never log passwords, raw credentials or unnecessary personal information.
13.3 Tracing
Use OpenTelemetry-compatible tracing to follow a workflow across:
API.
Database.
Queue.
Worker.
MQTT.
Intelligence services.
This is particularly important for investigating delayed telemetry and failed irrigation commands.
14. Reliability and disaster recovery
14.1 Backup strategy
Automated database backups.
Point-in-time recovery where available.
Object-storage versioning where appropriate.
Encrypted backup storage.
Backup access controls.
Regular restore testing.
Documented recovery procedures.
14.2 Initial recovery objectives
Provisional targets for planning, to be reviewed against cost and pilot needs:
System
Initial RPO target
Initial RTO target
Core database
15 minutes
4 hours
Object storage
24 hours or better
8 hours
Application services
Re-deployable from versioned releases
2 hours
Device telemetry
Local buffer-dependent
Depends on connectivity

These targets must be validated with the selected hosting and backup configuration.
14.3 Failure scenarios
The architecture must handle:
API unavailable.
Database unavailable.
MQTT broker unavailable.
Internet unavailable.
Device disconnected.
Sensor damaged.
Redis unavailable.
External weather provider unavailable.
Background worker failure.
Object-storage failure.
Model inference failure.
Mobile synchronisation conflict.
Equipment command timeout.
For every failure, define:
Detection.
User-visible status.
Retry policy.
Recovery.
Data-loss risk.
Escalation.
Audit behaviour.
15. Security architecture
15.1 Identity
Use OpenID Connect/OAuth 2.0-compatible authentication.
Evaluate Keycloak or a suitable managed identity provider.
15.2 Authorisation
Use role-based access control combined with resource-level policies.
A role alone should not grant access to every farm.
15.3 Device security
Unique device credentials.
Controlled provisioning.
Credential revocation.
Encrypted communication.
Command authorisation.
Replay protection.
Firmware integrity.
Device audit history.
15.4 Application security
Input validation.
Output encoding.
Secure sessions.
Rate limits.
CSRF protection where applicable.
CORS restrictions.
Dependency scanning.
Secrets management.
Database least privilege.
Security event logging.
Penetration testing.
15.5 Data governance
Define:
Ownership.
Access.
Consent.
Sharing.
Retention.
Export.
Correction.
Deletion.
Research access.
Third-party processing.
The design must be reviewed against Kenyan data-protection requirements and applicable laws in future deployment regions.
16. Technology decisions register
Decision
Current proposal
Status
Web frontend
React + Vite
Proposed
Mobile frontend
React Native + Expo
Proposed
Backend
Python + FastAPI
Proposed
Main database
PostgreSQL
Proposed
Geospatial
PostGIS
Proposed
Time-series
PostgreSQL partitioning initially
Proposed
Cache
Redis
Proposed
Job processing
Celery
Proposed
Device messaging
MQTT
Proposed
File storage
S3-compatible
Proposed
Identity
OIDC provider
To evaluate
AI/ML
Python ecosystem
Proposed
Local AI
Optional QVAC integration
Conditional
Deployment
Docker
Proposed
Orchestration
Not initially required
Deferred
Event streaming
Kafka/Redpanda if justified
Deferred
Search
PostgreSQL initially
Proposed

17. Architecture decisions requiring approval
Before implementation, the following must be confirmed:
Whether PostgreSQL is the final primary database.
Whether the backend remains a modular monolith for the initial releases.
Whether React Native is the preferred mobile approach.
Whether MQTT is required in the first device integration.
Whether identity will be self-hosted or managed.
Whether the initial deployment is cloud-hosted or hybrid.
Whether the initial data volume justifies a specialised time-series extension.
Whether the first pilot needs local edge gateway processing.
Which external data providers are approved.
Which device-control actions require mandatory human approval.
18. Architecture completion criteria
The architecture specification is ready for detailed implementation planning when:
Every application has a defined responsibility.
Every backend module has an explicit boundary.
Every important data flow is documented.
Device communication is defined.
Command safety is documented.
Offline behaviour is defined.
Tenant isolation is designed.
Data storage responsibilities are defined.
Integration boundaries are defined.
Security controls are mapped.
Deployment environments are specified.
Monitoring and recovery are designed.
Open decisions are recorded and approved.

19. Handoff to the next engineering document
This architecture is the foundation for the next specification.
Next document: TNX-DATA-001 — TerraNexus Complete Database and Data Architecture.
It must derive its structure from this architecture and include:
Complete entity-relationship diagram.
All entities and relationships.
Complete table definitions.
Field names and data types.
Primary and foreign keys.
Unique constraints.
Check constraints.
Index strategy.
Tenant isolation.
Geographic data types.
Measurement storage and partitioning.
Device and sensor schemas.
Events and audit tables.
Recommendations and model records.
Offline synchronisation records.
Database migration strategy.
Data retention and archival.
Example records and relationships.
Architecture status: Proposed baseline established. Final approval and validation remain outstanding. No implementation has been started or authorised by this document.
Architecture decision summary
There are three particularly important decisions in this design:
Modular monolith first: avoids unnecessary infrastructure complexity while keeping the modules separable.
PostgreSQL + PostGIS as the initial source of truth: supports farm operations, geographic data and structured agricultural records.
Independent device and physical-control boundaries: ensures that AI, cloud connectivity and user-interface failures cannot bypass equipment safety.
The next document should be the database design. It will define the actual data structures needed to support every TerraNexus application, not just the initial sensor-monitoring workflow.
Architecture deep dive: exact component boundaries, deployment diagram, service interactions and infrastructure.
Database design: complete ER diagram, table definitions, indexes, constraints and data relationships.
UI/UX design: actual screen-by-screen wireframes and high-fidelity designs for the 126-page inventory, including mobile layouts and interaction states.
API and device specifications: exact endpoint contracts, telemetry schemas, command lifecycle and synchronisation behaviour.. ,
Modular monolith first: avoids unnecessary infrastructure complexity while keeping the modules separable.
PostgreSQL + PostGIS as the initial source of truth: supports farm operations, geographic data and structured agricultural records.
Independent device and physical-control boundaries: ensures that AI, cloud connectivity and user-interface failures cannot bypass equipment safety.
The three architecture decisions are now the TerraNexus design baseline:
Modular monolith first, with explicit module boundaries and the option to extract services later.
PostgreSQL + PostGIS as the initial authoritative data store, with time-series partitioning as agricultural measurement volumes grow.
Independent device and physical-control boundaries, with local safety enforcement that cannot be overridden by AI or cloud failures.
I'll carry these decisions into all four engineering deliverables. The architecture, database, UI/UX and API/device specifications will use the same entities, terminology, permissions and workflows.
The next step is the database design. It needs to support the complete platform—not just farms and ESP32 sensor readings.
TerraNexus
Complete Database and Data Architecture Specification
