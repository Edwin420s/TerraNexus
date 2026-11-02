Document ID: TNX-DATA-001
Version: 1.0
Status: Proposed engineering baseline
Database: PostgreSQL + PostGIS
Architecture: Modular monolith
Primary data model: Relational, geospatial and time-series
Scope: Entire TerraNexus platform

1. Database design objectives
The TerraNexus database must support the entire agricultural ecosystem, including:
Users and organisations.
Farms, fields and geographical boundaries.
Crops, varieties and growing seasons.
Agricultural activities and farm operations.
Equipment and agricultural resources.
IoT devices, gateways and sensors.
Sensor observations and measurements.
External agricultural data.
Weather, soil and crop information.
Monitoring, alerts and notifications.
Irrigation and water management.
Analytics and machine learning.
Recommendations and decision records.
Research datasets.
Integrations and third-party applications.
Offline operations and synchronisation.
Reports and exports.
Security, permissions and audit records.
Billing and platform administration.
The database must also support future agricultural applications without requiring a redesign of the entire data model.
1.1 Database design principles
Principle
Implementation
Relational integrity
Foreign keys and constraints
Multi-tenancy
Organisation-scoped records
Geographic intelligence
PostGIS
Time-series support
Partitioned measurement tables
Data provenance
Source and processing metadata
Historical traceability
Versioning and audit records
Offline compatibility
Client-generated UUIDs and sync records
Security
Tenant isolation and restricted access
Extensibility
Controlled JSONB metadata
Interoperability
Standard units and external identifiers
Performance
Purpose-built indexes and partitioning
Reliability
Transactions and recoverable migrations

2. Database architecture
2.1 Logical database domains
TerraNexus will use one primary PostgreSQL database initially, organised into logical domains and PostgreSQL schemas where useful.
Schema
Responsibility
identity
Users, authentication references and sessions
organisation
Tenants, memberships and permissions
farm
Farms, fields and boundaries
agriculture
Crops, varieties and growing seasons
operations
Tasks, activities, equipment and inventory
devices
Gateways, devices, sensors and commands
observations
Measurements and agricultural observations
data_platform
Datasets, sources and imports
environment
Weather, soil and environmental records
monitoring
Rules, alerts and notifications
irrigation
Water sources, zones, plans and events
intelligence
Models, forecasts and recommendations
collaboration
Comments, assignments and shared work
integrations
External connectors, applications and webhooks
reporting
Reports and scheduled exports
sync
Offline operations and synchronisation
audit
Security and activity history
platform
Configuration, subscriptions and usage

These are logical ownership boundaries. They do not require separate databases.
2.2 Overall ER architecture
The following is the high-level entity relationship model. Detailed domain relationships and field definitions follow.
erDiagram
    USER ||--o{ MEMBERSHIP : joins
    ORGANISATION ||--o{ MEMBERSHIP : has
    ORGANISATION ||--o{ FARM : owns
    FARM ||--o{ FIELD : contains
    FARM ||--o{ FARM_MEMBER : grants_access
    USER ||--o{ FARM_MEMBER : participates

    FIELD ||--o{ FIELD_CROP : grows
    CROP ||--o{ FIELD_CROP : assigned
    CROP ||--o{ CROP_VARIETY : has
    GROWING_SEASON ||--o{ FIELD_CROP : schedules

    FARM ||--o{ DEVICE : registers
    DEVICE ||--o{ SENSOR : contains
    DEVICE ||--o{ DEVICE_EVENT : generates
    DEVICE ||--o{ DEVICE_COMMAND : receives
    SENSOR ||--o{ MEASUREMENT : produces
    FIELD ||--o{ MEASUREMENT : associated_with

    DATA_SOURCE ||--o{ DATASET : provides
    DATASET ||--o{ DATASET_VERSION : versions
    DATA_SOURCE ||--o{ EXTERNAL_OBSERVATION : supplies

    FARM ||--o{ TASK : has
    FIELD ||--o{ TASK : concerns
    TASK ||--o{ TASK_ASSIGNMENT : assigned
    USER ||--o{ TASK_ASSIGNMENT : receives
    TASK ||--o{ ACTIVITY : records

    FARM ||--o{ IRRIGATION_ZONE : contains
    IRRIGATION_ZONE ||--o{ IRRIGATION_PLAN : has
    IRRIGATION_PLAN ||--o{ IRRIGATION_EVENT : executes
    WATER_SOURCE ||--o{ IRRIGATION_EVENT : supplies

    FIELD ||--o{ ALERT : generates
    ALERT_RULE ||--o{ ALERT : triggers
    ALERT ||--o{ NOTIFICATION : produces

    MODEL ||--o{ MODEL_RUN : executes
    MODEL_RUN ||--o{ RECOMMENDATION : produces
    FIELD ||--o{ RECOMMENDATION : receives
    RECOMMENDATION ||--o{ RECOMMENDATION_EVIDENCE : supported_by

    ORGANISATION ||--o{ INTEGRATION : configures
    INTEGRATION ||--o{ WEBHOOK : exposes
    USER ||--o{ AUDIT_LOG : performs
3. Global database conventions
These conventions apply throughout the database unless a domain has a documented exception.
3.1 Primary identifiers
Use UUID primary keys for most platform entities.
Column
Type
Purpose
id
UUID
Primary identifier
organisation_id
UUID
Tenant association where applicable
created_at
TIMESTAMPTZ
Record creation
updated_at
TIMESTAMPTZ
Last modification
created_by
UUID
User or system actor
updated_by
UUID
Last modifying actor
version
BIGINT
Optimistic concurrency version

UUIDv7 is a suitable identifier strategy for new records because of its time-ordering characteristics. UUID generation must be consistent across backend and offline clients.
Not every record requires every standard field. High-volume measurement rows, immutable events and junction tables may use specialised conventions.
3.2 Timestamp conventions
All stored timestamps should use TIMESTAMPTZ.
Store timestamps in UTC and present them in the user's configured timezone.
Distinguish:
observed_at: when the event or measurement actually happened.
received_at: when TerraNexus received it.
processed_at: when processing completed.
created_at: when the database record was created.
updated_at: when the mutable record was last changed.
These values must not be treated as interchangeable.
3.3 Units
Measurements must use explicit units.
Examples:
Measurement
Unit
Temperature
°C
Relative humidity
%
Soil moisture
% or explicitly defined volumetric unit
Rainfall
mm
Wind speed
m/s
Soil pH
pH
Soil electrical conductivity
dS/m
Water volume
L or m³
Irrigation duration
seconds or minutes
Soil depth
mm or cm

Do not store a value of 30 without knowing what it represents and its unit.
A canonical unit system should be established for each measurement type, with conversion at ingestion or presentation boundaries.
3.4 JSONB policy
JSONB is appropriate for:
Device-specific capabilities.
External provider payloads.
Configurable rules.
Model parameters.
Integration settings.
Variable metadata.
JSONB must not replace relational columns for essential fields such as organisation ownership, farm IDs, timestamps, foreign keys or frequently filtered measurement values.
3.5 Deletion policy
Use different deletion approaches according to the nature of the record.
Record
Recommended policy
User account
Deactivation and controlled anonymisation
Organisation
Controlled archival and deletion workflow
Farm
Soft deletion or archival
Field
Soft deletion with history
Measurement
Retention policy; preserve provenance
Device
Revocation and archival
Command
Immutable execution history
Audit record
Append-only
Notification
Retention and user preference policy
Uploaded file
Controlled deletion with metadata retention where necessary

Avoid indiscriminate cascading deletion across agricultural history.
4. Identity and organisation database
4.1 identity.users
Stores TerraNexus user profiles.
Column
Type
Constraints / purpose
id
UUID
Primary key
email
CITEXT
Unique when provided
phone_number
VARCHAR(30)
Optional, normalised
password_hash
TEXT
Nullable if external identity provider
first_name
VARCHAR(100)
Required
last_name
VARCHAR(100)
Required
display_name
VARCHAR(150)
Optional
avatar_file_id
UUID
Optional
preferred_language
VARCHAR(10)
Default language
timezone
VARCHAR(64)
IANA timezone
account_status
VARCHAR(30)
Active, suspended, pending, deleted
email_verified_at
TIMESTAMPTZ
Nullable
phone_verified_at
TIMESTAMPTZ
Nullable
last_login_at
TIMESTAMPTZ
Nullable
created_at
TIMESTAMPTZ
Required
updated_at
TIMESTAMPTZ
Required

Indexes:
Unique index on normalised email.
Index on account status.
Index on creation date.
Authentication provider identifiers should be held separately if an external identity provider is used.
4.2 identity.external_identities
Column
Type
Purpose
id
UUID
Primary key
user_id
UUID
FK to users
provider
VARCHAR(50)
Identity provider
provider_subject
VARCHAR(255)
External unique subject
created_at
TIMESTAMPTZ
Creation

Unique constraint: (provider, provider_subject).
4.3 organisation.organisations
Represents a tenant, cooperative, company, research institution or other organisation.
Column
Type
Purpose
id
UUID
Primary key
name
VARCHAR(200)
Organisation name
slug
VARCHAR(150)
Unique URL identifier
organisation_type
VARCHAR(50)
Farm business, cooperative, research, etc.
registration_number
VARCHAR(100)
Optional
country_code
CHAR(2)
ISO country code
default_currency
CHAR(3)
ISO currency
timezone
VARCHAR(64)
Organisation timezone
contact_email
CITEXT
Optional
contact_phone
VARCHAR(30)
Optional
status
VARCHAR(30)
Active, suspended, archived
settings
JSONB
Controlled configuration
created_at
TIMESTAMPTZ
Creation
updated_at
TIMESTAMPTZ
Modification

Unique constraints:
slug.
(country_code, registration_number) when registration number is present and the business rules require uniqueness.
4.4 organisation.memberships
Connects users to organisations.
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
FK
user_id
UUID
FK
membership_status
VARCHAR(30)
Invited, active, suspended, removed
joined_at
TIMESTAMPTZ
Nullable
invited_by
UUID
Inviting user
created_at
TIMESTAMPTZ
Creation

Unique constraint: (organisation_id, user_id).
4.5 Roles and permissions
organisation.roles
id
organisation_id (nullable for platform-wide roles)
name
slug
description
is_system_role
created_at
organisation.permissions
id
permission_key
description
resource_type
action
organisation.role_permissions
role_id
permission_id
Composite primary key: (role_id, permission_id).
organisation.membership_roles
membership_id
role_id
Composite primary key: (membership_id, role_id).
organisation.resource_access
Controls access to individual resources.
id
membership_id
resource_type
resource_id
access_level
granted_by
expires_at
created_at
This allows a cooperative member to access one farm without automatically gaining access to every farm in the organisation.
5. Farm and geographic database
5.1 farm.farms
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
FK
name
VARCHAR(200)
Farm name
farm_code
VARCHAR(80)
Organisation-specific identifier
description
TEXT
Optional
country_code
CHAR(2)
Country
administrative_area
VARCHAR(150)
County or equivalent
sub_county
VARCHAR(150)
Optional
locality
VARCHAR(150)
Village or locality
address
TEXT
Optional
boundary
GEOMETRY(MULTIPOLYGON, 4326)
Farm boundary
centroid
GEOMETRY(POINT, 4326)
Derived location
area_value
NUMERIC(14,4)
Calculated area
area_unit
VARCHAR(20)
ha, acre, etc.
farm_status
VARCHAR(30)
Active, inactive, archived
metadata
JSONB
Additional information
created_at
TIMESTAMPTZ
Creation
updated_at
TIMESTAMPTZ
Modification

Constraints:
Farm code unique within an organisation.
Valid geographic geometry.
Non-negative area.
Organisation FK required.
Indexes:
(organisation_id, farm_status).
GiST index on boundary.
GiST index on centroid.
5.2 farm.fields
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
Tenant
farm_id
UUID
FK
name
VARCHAR(150)
Field name
field_code
VARCHAR(80)
Unique farm-level identifier
description
TEXT
Optional
boundary
GEOMETRY(MULTIPOLYGON, 4326)
Field boundary
centroid
GEOMETRY(POINT, 4326)
Derived
area_value
NUMERIC(14,4)
Calculated
area_unit
VARCHAR(20)
Area unit
slope_percentage
NUMERIC(8,3)
Optional
elevation_m
NUMERIC(10,3)
Optional
soil_profile_id
UUID
Optional FK
field_status
VARCHAR(30)
Active, inactive, archived
created_at
TIMESTAMPTZ
Creation
updated_at
TIMESTAMPTZ
Modification

Constraints:
(farm_id, field_code) unique.
Field boundary must be valid.
Field must belong to the same organisation as its farm.
Area must be non-negative.
Indexes:
(farm_id, field_status).
GiST on boundary.
GiST on centroid.
5.3 farm.farm_members
Controls user participation at farm level.
id
farm_id
user_id
membership_id
farm_role
status
assigned_at
expires_at
5.4 farm.field_zones
Represents subdivisions of a field.
id
organisation_id
field_id
name
zone_code
boundary
area_value
area_unit
zone_type
created_at
A zone can represent an irrigation area, crop block, sampling zone or management zone.
5.5 farm.field_observations
Captures human-entered field observations.
id
organisation_id
farm_id
field_id
observed_by
observation_type
description
observed_at
location
weather_context
verification_status
created_at
Examples:
Crop wilting.
Pest appearance.
Waterlogging.
Visible disease symptoms.
Soil condition.
Harvest observations.
Photographs should be linked through a file attachment relationship rather than stored as binary data in this table.
6. Agricultural catalogue and growing seasons
6.1 agriculture.crops
id
name
scientific_name
crop_category
description
growth_duration_min_days
growth_duration_max_days
water_requirement_profile
temperature_profile
metadata
created_at
Examples include maize, beans, coffee, tea, tomatoes and potatoes.
6.2 agriculture.crop_varieties
id
crop_id
name
variety_code
breeder
description
maturity_days
metadata
6.3 agriculture.growing_seasons
id
organisation_id
farm_id
name
start_date
end_date
season_status
created_at
6.4 agriculture.field_crops
Represents a crop assignment to a field during a growing season.
id
organisation_id
field_id
crop_id
crop_variety_id
growing_season_id
planting_date
expected_harvest_date
actual_harvest_date
cultivated_area
area_unit
planting_method
status
created_at
This relationship supports crop rotation and multiple growing seasons without overwriting historical crop assignments.
6.5 agriculture.crop_growth_stages
id
crop_id
stage_name
stage_code
sequence_number
typical_start_day
typical_end_day
description
The platform should not assume all crops have identical growth stages.
7. Farm operations database
7.1 operations.tasks
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
Tenant
farm_id
UUID
FK
field_id
UUID
Nullable FK
title
VARCHAR(200)
Task title
description
TEXT
Details
task_type
VARCHAR(50)
Irrigation, planting, inspection, etc.
priority
VARCHAR(20)
Low, normal, high, critical
status
VARCHAR(30)
Open, assigned, in progress, completed, cancelled
scheduled_start
TIMESTAMPTZ
Planned start
scheduled_end
TIMESTAMPTZ
Planned end
completed_at
TIMESTAMPTZ
Actual completion
created_by
UUID
Creator
created_at
TIMESTAMPTZ
Creation
updated_at
TIMESTAMPTZ
Modification
version
BIGINT
Optimistic concurrency

7.2 operations.task_assignments
id
task_id
user_id
assigned_by
assigned_at
assignment_status
A task may have multiple authorised participants.
7.3 operations.task_comments
id
task_id
user_id
comment
created_at
updated_at
7.4 operations.activities
Records completed or ongoing farm activities.
id
organisation_id
farm_id
field_id
field_crop_id
task_id
activity_type
description
started_at
completed_at
performed_by
status
created_at
7.5 operations.equipment
id
organisation_id
farm_id
name
equipment_type
manufacturer
model
serial_number
purchase_date
maintenance_status
equipment_status
metadata
7.6 operations.maintenance_records
id
equipment_id
maintenance_type
description
scheduled_at
performed_at
performed_by
cost_amount
currency
status
7.7 operations.inventory_items
id
organisation_id
farm_id
name
category
unit
description
minimum_stock_level
status
7.8 operations.inventory_transactions
id
inventory_item_id
transaction_type
quantity
unit
reference_type
reference_id
performed_by
recorded_at
Transactions should be used to derive stock balances. Do not maintain a stock number that can silently become inconsistent with its transaction history.
7.9 operations.harvest_records
id
organisation_id
farm_id
field_id
field_crop_id
harvest_date
quantity
unit
quality_grade
recorded_by
notes
8. Device and IoT database
8.1 devices.gateways
Represents a communication gateway connecting multiple field devices.
id
organisation_id
farm_id
gateway_identifier
name
manufacturer
model
protocol
firmware_version
status
last_seen_at
location
metadata
8.2 devices.devices
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
Tenant
farm_id
UUID
Associated farm
field_id
UUID
Optional field
gateway_id
UUID
Optional gateway
device_identifier
VARCHAR(150)
Unique device identity
name
VARCHAR(150)
Display name
manufacturer
VARCHAR(100)
Manufacturer
model
VARCHAR(100)
Hardware model
device_type
VARCHAR(50)
Sensor node, controller, station, etc.
firmware_version
VARCHAR(80)
Firmware
hardware_version
VARCHAR(80)
Hardware
connection_protocol
VARCHAR(30)
MQTT, HTTPS, LoRaWAN, etc.
provisioning_status
VARCHAR(30)
Pending, provisioned, revoked
operational_status
VARCHAR(30)
Online, offline, degraded, fault
last_seen_at
TIMESTAMPTZ
Last communication
location
GEOMETRY(POINT, 4326)
Optional location
capabilities
JSONB
Supported functions
configuration
JSONB
Device configuration
created_at
TIMESTAMPTZ
Creation
updated_at
TIMESTAMPTZ
Modification

Unique constraint: (organisation_id, device_identifier).
Do not store raw device secrets in this table. Store a reference to a secure credential-management system.
8.3 devices.sensors
A device may have multiple sensors.
id
organisation_id
device_id
sensor_identifier
sensor_type
measurement_type
manufacturer
model
unit
measurement_min
measurement_max
sampling_interval_seconds
calibration_status
status
installed_at
metadata
Unique constraint: (device_id, sensor_identifier).
8.4 devices.sensor_channels
Useful for multi-channel sensors and devices.
id
sensor_id
channel_identifier
measurement_type
unit
configuration
status
8.5 devices.calibration_records
id
sensor_id
calibration_date
calibrated_by
reference_value
measured_value
calibration_offset
calibration_factor
calibration_method
valid_until
calibration_status
notes
Calibration history must be retained. Do not overwrite the only calibration record when recalibrating a sensor.
8.6 devices.device_events
id
organisation_id
device_id
event_type
severity
event_payload
occurred_at
received_at
correlation_id
Examples:
Device connected.
Device disconnected.
Firmware updated.
Low battery.
Sensor failure.
Configuration changed.
Device rebooted.
8.7 devices.device_commands
Column
Type
Purpose
id
UUID
Command ID
organisation_id
UUID
Tenant
device_id
UUID
Target device
requested_by
UUID
Requesting user or system actor
command_type
VARCHAR(80)
Action type
payload
JSONB
Validated command parameters
status
VARCHAR(30)
Command state
priority
VARCHAR(20)
Command priority
idempotency_key
VARCHAR(150)
Duplicate protection
requested_at
TIMESTAMPTZ
Request time
expires_at
TIMESTAMPTZ
Expiry
published_at
TIMESTAMPTZ
MQTT publication
acknowledged_at
TIMESTAMPTZ
Device acknowledgement
completed_at
TIMESTAMPTZ
Completion
failure_reason
TEXT
Failure explanation
correlation_id
UUID
Traceability

Unique constraint: (device_id, idempotency_key).
8.8 devices.command_events
Append-only command lifecycle history.
id
command_id
event_type
previous_status
new_status
event_payload
occurred_at
This table preserves what happened even if the current command status changes.
8.9 devices.firmware_releases
id
manufacturer
model
firmware_version
file_id
checksum
release_notes
minimum_hardware_version
release_status
published_at
8.10 devices.firmware_deployments
id
device_id
firmware_release_id
deployment_status
started_at
completed_at
failure_reason
9. Agricultural observations and measurement database
This is one of the most important database domains in TerraNexus.
It must support different sensor manufacturers, different measurement types, external datasets and manual observations.
9.1 observations.measurement_types
Defines standard measurement categories.
Column
Type
Example
id
UUID
Identifier
code
VARCHAR(80)
soil_moisture
name
VARCHAR(120)
Soil Moisture
description
TEXT
Definition
canonical_unit
VARCHAR(30)
%
value_type
VARCHAR(20)
Numeric, categorical, boolean
minimum_valid_value
NUMERIC
Optional
maximum_valid_value
NUMERIC
Optional
metadata
JSONB
Measurement-specific metadata

The measurement type must identify what is being measured, while the sensor record identifies the hardware producing it.
9.2 observations.measurements
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
Tenant
farm_id
UUID
Associated farm
field_id
UUID
Associated field
device_id
UUID
Nullable
sensor_id
UUID
Nullable
channel_id
UUID
Nullable
measurement_type_id
UUID
Required FK
source_id
UUID
Data-source reference
source_record_id
VARCHAR(150)
External record identifier
value_numeric
NUMERIC(20,8)
Numeric value
value_text
TEXT
Categorical value
value_boolean
BOOLEAN
Boolean value
unit
VARCHAR(30)
Original or canonical unit
observed_at
TIMESTAMPTZ
Observation time
received_at
TIMESTAMPTZ
Receipt time
quality_status
VARCHAR(30)
Valid, suspect, invalid, etc.
location
GEOMETRY(POINT, 4326)
Optional
calibration_record_id
UUID
Nullable
raw_payload_file_id
UUID
Nullable
sequence_number
BIGINT
Device sequence
metadata
JSONB
Additional context

A check constraint should ensure that the value columns match the declared measurement type and that exactly the appropriate value representation is populated.
Recommended quality states:
valid
suspect
invalid
missing
stale
uncalibrated
estimated
corrected
manually_verified
The measurement should preserve the original observation. Corrections should be represented through a correction or processing record, not silent overwriting.
9.3 Measurement indexes
Initial index strategy:
(organisation_id, observed_at DESC).
(field_id, observed_at DESC).
(sensor_id, observed_at DESC).
(measurement_type_id, observed_at DESC).
(device_id, sequence_number) where applicable.
GiST index on location where spatial queries are required.
Unique deduplication key based on source/device identity and sequence or source record identifier.
The precise index set must be validated against actual query patterns and ingestion volume.
9.4 Partitioning
The measurements table should be partitioned by time, initially monthly if volumes justify it.
The exact partition interval must be established from ingestion benchmarks.
Partitioning introduces an important PostgreSQL consideration: unique constraints on partitioned tables generally need to include the partition key. Therefore, the global UUID strategy and deduplication strategy must be designed together rather than assuming a simple unique constraint on id is sufficient for every partitioned table.
A practical approach is:
UUIDv7 identifiers generated by the ingestion layer.
Time-partitioned measurement storage.
Explicit device/source deduplication keys.
Separate idempotency records where global uniqueness across partitions is required.
9.5 observations.measurement_quality_records
id
measurement_id
quality_status
quality_score
validation_rule
reason
evaluated_at
9.6 observations.measurement_corrections
id
measurement_id
original_value
corrected_value
correction_reason
corrected_by
corrected_at
9.7 observations.processing_records
id
measurement_id
processing_type
processing_version
input_metadata
output_metadata
processed_at
This supports traceability when data is normalised, corrected or transformed.
10. External agricultural data
10.1 data_platform.data_sources
Represents a source of agricultural information.
id
name
source_type
provider_name
description
base_url
licence
terms_url
attribution_requirements
update_frequency
status
metadata
Examples:
Weather provider.
Satellite provider.
Government agricultural dataset.
Research institution.
Manual upload.
IoT platform.
10.2 data_platform.datasets
id
organisation_id
data_source_id
name
description
dataset_type
geographic_coverage
temporal_coverage_start
temporal_coverage_end
spatial_reference_system
licence
visibility
status
metadata
10.3 data_platform.dataset_versions
id
dataset_id
version_number
file_id
schema_definition
record_count
checksum
created_at
created_by
10.4 data_platform.data_import_jobs
id
organisation_id
dataset_id
file_id
import_format
job_status
records_total
records_processed
records_rejected
started_at
completed_at
error_summary
10.5 data_platform.data_export_jobs
id
organisation_id
requested_by
export_format
filters
file_id
job_status
requested_at
completed_at
11. Environmental and soil database
11.1 Weather observations
environment.weather_observations
id
organisation_id
farm_id
field_id
data_source_id
location
observed_at
temperature_c
humidity_percentage
rainfall_mm
wind_speed_ms
wind_direction_degrees
solar_radiation
pressure_hpa
quality_status
source_record_id
Weather records should retain their source and spatial context.
11.2 Weather forecasts
environment.weather_forecasts
id
data_source_id
farm_id
field_id
location
issued_at
forecast_for
forecast_horizon_hours
temperature_min_c
temperature_max_c
rain_probability
expected_rainfall_mm
wind_speed_ms
forecast_payload
model_identifier
A forecast must be distinguishable from an actual weather observation.
11.3 Soil profiles
environment.soil_profiles
id
organisation_id
farm_id
field_id
profile_name
soil_classification
soil_texture
drainage_class
organic_matter_percentage
ph_value
electrical_conductivity
bulk_density
source_type
verified_at
metadata
11.4 Soil samples
environment.soil_samples
id
organisation_id
farm_id
field_id
soil_profile_id
sample_identifier
sampling_location
sampling_depth_cm
sampled_at
sampled_by
laboratory
results
verification_status
Laboratory results should have defined measurement types and units rather than relying solely on arbitrary JSON.
11.5 Soil sample results
environment.soil_sample_results
id
soil_sample_id
measurement_type_id
numeric_value
unit
detection_limit
quality_status
11.6 Remote sensing records
environment.remote_sensing_observations
id
organisation_id
farm_id
field_id
data_source_id
observation_date
satellite
sensor
spatial_resolution_m
cloud_coverage_percentage
vegetation_index_type
vegetation_index_value
file_id
metadata
This allows satellite-derived information to be linked to fields without treating it as a direct ground measurement.
12. Monitoring, alerts and notifications
12.1 monitoring.alert_rules
id
organisation_id
name
description
measurement_type_id
field_id
device_id
condition_operator
threshold_value
severity
evaluation_frequency
enabled
rule_configuration
created_at
The rule engine must support more than simple numerical thresholds. More complex conditions can be defined through validated rule configurations.
12.2 monitoring.alerts
id
organisation_id
farm_id
field_id
device_id
alert_rule_id
alert_type
severity
title
description
triggered_at
acknowledged_at
acknowledged_by
resolved_at
resolved_by
status
evidence
12.3 monitoring.alert_events
Append-only alert lifecycle events.
id
alert_id
event_type
performed_by
event_payload
occurred_at
12.4 monitoring.notifications
id
organisation_id
user_id
alert_id
notification_type
title
message
channel
delivery_status
sent_at
read_at
created_at
12.5 monitoring.notification_preferences
id
user_id
notification_type
channel
enabled
quiet_hours
updated_at
12.6 monitoring.notification_deliveries
id
notification_id
provider
provider_message_id
attempt_number
delivery_status
attempted_at
failure_reason
This supports retrying failed deliveries without duplicating the underlying notification.
13. Irrigation and water management
13.1 irrigation.water_sources
id
organisation_id
farm_id
name
source_type
location
estimated_capacity
capacity_unit
current_level
level_unit
status
metadata
Source types may include:
Borehole.
River.
Reservoir.
Water tank.
Rainwater harvesting.
Municipal supply.
13.2 irrigation.irrigation_zones
id
organisation_id
farm_id
field_id
field_zone_id
name
boundary
irrigation_method
design_flow_rate
flow_rate_unit
status
13.3 irrigation.pumps
id
organisation_id
farm_id
water_source_id
device_id
name
pump_type
rated_flow_rate
flow_rate_unit
maximum_runtime_seconds
safety_configuration
status
13.4 irrigation.irrigation_plans
id
organisation_id
farm_id
field_id
irrigation_zone_id
created_by
plan_name
plan_type
planned_start
planned_end
target_water_volume
water_volume_unit
decision_basis
approval_status
execution_status
created_at
13.5 irrigation.irrigation_plan_steps
id
irrigation_plan_id
sequence_number
pump_id
duration_seconds
target_volume
step_configuration
13.6 irrigation.irrigation_events
id
organisation_id
irrigation_plan_id
irrigation_zone_id
pump_id
device_command_id
started_at
completed_at
actual_water_volume
volume_unit
execution_status
failure_reason
recorded_at
13.7 irrigation.safety_events
id
organisation_id
device_id
pump_id
irrigation_event_id
safety_event_type
severity
triggered_at
details
Examples:
Emergency stop.
Maximum runtime exceeded.
Dry-run protection activated.
Water source unavailable.
Sensor validation failed.
Command expired.
Safety records must remain available for investigation.
14. Intelligence and machine learning database
14.1 intelligence.models
id
organisation_id
model_name
model_type
model_description
model_provider
model_version
artifact_file_id
input_schema
output_schema
evaluation_metrics
deployment_status
created_at
Models may be global platform models or organisation-specific models.
14.2 intelligence.model_runs
id
model_id
organisation_id
farm_id
field_id
model_version
input_reference
input_snapshot
output
execution_status
started_at
completed_at
execution_duration_ms
error_details
14.3 intelligence.forecasts
id
organisation_id
farm_id
field_id
model_run_id
forecast_type
target_variable
forecast_value
forecast_unit
forecast_for
confidence_value
generated_at
valid_until
14.4 intelligence.recommendations
Column
Type
Purpose
id
UUID
Primary key
organisation_id
UUID
Tenant
farm_id
UUID
Context
field_id
UUID
Context
model_run_id
UUID
Optional
recommendation_type
VARCHAR(80)
Irrigation, crop health, etc.
title
VARCHAR(200)
Display title
description
TEXT
Explanation
recommended_action
JSONB
Structured proposed action
priority
VARCHAR(20)
Priority
confidence_score
NUMERIC(6,5)
Optional
status
VARCHAR(30)
Pending, accepted, rejected, expired
generated_at
TIMESTAMPTZ
Creation
expires_at
TIMESTAMPTZ
Expiry
reviewed_by
UUID
Optional
reviewed_at
TIMESTAMPTZ
Optional

A recommendation is not an executed action.
14.5 intelligence.recommendation_evidence
id
recommendation_id
evidence_type
source_entity_type
source_entity_id
evidence_description
evidence_value
evidence_unit
observed_at
14.6 intelligence.recommendation_feedback
id
recommendation_id
user_id
decision
reason
recorded_at
14.7 intelligence.recommendation_outcomes
id
recommendation_id
outcome_type
outcome_value
outcome_unit
observed_at
recorded_by
notes
This creates the foundation for measuring whether recommendations actually improve agricultural outcomes.
14.8 intelligence.optimisation_runs
id
organisation_id
farm_id
optimisation_type
objective_definition
constraints
input_snapshot
result
solver_type
solver_version
execution_status
started_at
completed_at
Quantum optimisation experiments, if ever justified, can be recorded here alongside classical baselines. The platform must not assume quantum advantage.
15. Collaboration and file management
15.1 collaboration.comments
id
organisation_id
resource_type
resource_id
user_id
comment_text
parent_comment_id
created_at
updated_at
15.2 collaboration.assignments
id
organisation_id
resource_type
resource_id
assigned_to
assigned_by
assignment_status
assigned_at
due_at
15.3 data_platform.files
id
organisation_id
uploaded_by
storage_provider
storage_key
original_filename
mime_type
file_size_bytes
checksum
visibility
upload_status
created_at
15.4 data_platform.file_attachments
id
file_id
entity_type
entity_id
attachment_role
created_at
This allows photographs, documents and datasets to be attached to different platform entities.
16. Integration and developer database
16.1 integrations.integration_providers
id
provider_name
provider_category
description
documentation_url
authentication_type
status
metadata
16.2 integrations.integrations
id
organisation_id
provider_id
integration_name
configuration
credential_reference
integration_status
last_success_at
last_failure_at
created_at
Sensitive credentials must be stored in a secrets manager, not as plaintext JSONB.
16.3 integrations.integration_sync_runs
id
integration_id
started_at
completed_at
sync_status
records_received
records_processed
records_rejected
error_details
16.4 integrations.api_applications
id
organisation_id
application_name
description
client_identifier
status
created_by
created_at
16.5 integrations.api_credentials
id
application_id
credential_reference
credential_prefix
scopes
expires_at
revoked_at
created_at
Do not store reusable plaintext API secrets.
16.6 integrations.webhooks
id
organisation_id
application_id
target_url
subscribed_events
signing_secret_reference
status
created_at
16.7 integrations.webhook_deliveries
id
webhook_id
event_id
attempt_number
response_status
delivery_status
attempted_at
next_retry_at
17. Offline synchronisation database
Offline operation must be designed as a first-class platform capability.
17.1 sync.client_devices
id
user_id
organisation_id
client_identifier
client_type
client_version
last_sync_at
status
17.2 sync.sync_operations
Column
Type
Purpose
id
UUID
Client-generated operation ID
organisation_id
UUID
Tenant
client_device_id
UUID
Originating client
user_id
UUID
Originating user
entity_type
VARCHAR(80)
Entity
entity_id
UUID
Target entity
operation_type
VARCHAR(30)
Create, update, delete
base_version
BIGINT
Version client edited
payload
JSONB
Submitted change
operation_status
VARCHAR(30)
Pending, accepted, rejected, conflict
client_timestamp
TIMESTAMPTZ
Local event time
server_received_at
TIMESTAMPTZ
Server receipt
processed_at
TIMESTAMPTZ
Processing completion
failure_reason
TEXT
Optional

Unique constraint: (client_device_id, id).
17.3 sync.sync_conflicts
id
sync_operation_id
entity_type
entity_id
server_version
client_version
conflict_type
resolution_status
resolution_details
resolved_by
resolved_at
17.4 sync.sync_checkpoints
id
client_device_id
organisation_id
resource_type
last_synced_at
last_synced_cursor
updated_at
The server must support cursor-based synchronisation. Clients must not rely only on device clocks to determine which records have changed.
17.5 Synchronisation rules
Operation
Handling
New observation
Append and deduplicate
New photograph
Upload file and metadata
Task completion
Validate status and version
Farm metadata edit
Version conflict detection
Field boundary edit
Conflict detection and review
Irrigation command
Revalidate; never blindly replay
Deleted record
Controlled tombstone or deletion workflow
Permission change
Recheck authorisation at sync time

A client that loses access to an organisation while offline must not be allowed to upload previously prepared changes without reauthorisation.
18. Reporting and billing database
18.1 reporting.report_definitions
id
organisation_id
name
report_type
definition
created_by
created_at
18.2 reporting.report_runs
id
report_definition_id
requested_by
requested_at
completed_at
run_status
output_file_id
error_details
18.3 reporting.scheduled_reports
id
report_definition_id
schedule_expression
timezone
delivery_configuration
enabled
next_run_at
18.4 platform.plans
id
name
description
billing_interval
price
currency
limits
status
18.5 platform.subscriptions
id
organisation_id
plan_id
subscription_status
started_at
renewal_at
cancelled_at
provider_reference
18.6 platform.usage_records
id
organisation_id
usage_type
quantity
unit
recorded_at
metadata
Billing records should remain separate from farm operational records.
19. Audit and governance database
19.1 audit.audit_logs
id
organisation_id
actor_user_id
actor_type
action
resource_type
resource_id
request_id
correlation_id
ip_address
user_agent
previous_state
new_state
occurred_at
Audit records should be append-only to normal application users.
Sensitive values such as passwords, tokens and private credentials must never be copied into audit payloads.
19.2 audit.security_events
id
organisation_id
user_id
event_type
severity
source_ip
details
occurred_at
Examples:
Failed login.
Suspicious access.
Permission escalation.
Device credential revocation.
Unusual API activity.
20. Key database relationships
The following relationships are fundamental to the platform.
Parent
Child
Relationship
Organisation
Farm
One-to-many
Farm
Field
One-to-many
Field
Field crop
One-to-many
Crop
Field crop
One-to-many
Growing season
Field crop
One-to-many
Farm
Device
One-to-many
Device
Sensor
One-to-many
Sensor
Measurement
One-to-many
Field
Measurement
One-to-many
Farm
Task
One-to-many
Task
Assignment
One-to-many
Farm
Irrigation zone
One-to-many
Irrigation zone
Irrigation plan
One-to-many
Irrigation plan
Irrigation event
One-to-many
Model
Model run
One-to-many
Model run
Recommendation
One-to-many
Recommendation
Evidence
One-to-many
Organisation
Integration
One-to-many
Integration
Sync run
One-to-many
User
Organisation membership
One-to-many

The database must also support a user belonging to multiple organisations and a user having access to multiple farms.
21. Critical integrity constraints
The following rules must be enforced at the database or service boundary.
21.1 Tenant integrity
A field cannot belong to a farm in another organisation.
A device cannot be associated with a farm outside its organisation.
A recommendation cannot reference a field belonging to another tenant.
Use composite foreign keys or equivalent validated constraints where appropriate. Do not depend solely on the frontend to enforce tenant relationships.
21.2 Geographic integrity
All geographic columns must use an explicitly defined spatial reference system.
Geometry must be valid.
Field boundaries must be checked against their parent farm boundaries.
Area calculations must use suitable geodesic or projected-area methods.
The platform must document its handling of boundary overlap.
21.3 Measurement integrity
Measurement types must be registered.
Units must be recognised.
Observation timestamps must be present.
Source provenance must be preserved.
Invalid measurements must not silently become valid.
Duplicate ingestion must be controlled.
Device sequence numbers must be checked where supported.
21.4 Irrigation integrity
A plan must belong to an authorised farm and zone.
A pump must belong to the appropriate farm or authorised equipment scope.
A command must have an expiry.
An irrigation event must reference its execution command where applicable.
A failed or unacknowledged command must not be represented as successful irrigation.
Safety events must remain auditable.
21.5 Recommendation integrity
A recommendation must reference its evidence.
A recommendation must retain its generating model or ruleset where applicable.
An accepted recommendation must not be treated as completed action.
The actual outcome must be recorded separately.
22. Indexing strategy
Indexing must follow query patterns rather than simply indexing every column.
Table
Initial index
Users
Unique normalised email
Memberships
Organisation + user
Farms
Organisation + status
Fields
Farm + status; GiST boundary
Devices
Organisation + status
Sensors
Device + sensor identifier
Measurements
Field + observed_at
Measurements
Sensor + observed_at
Measurements
Organisation + observed_at
Tasks
Farm + status + scheduled start
Alerts
Organisation + status + triggered time
Irrigation plans
Zone + planned start
Recommendations
Field + generated time
Notifications
User + read status + created time
Audit logs
Organisation + occurred_at
Sync operations
Client device + status

For large tables, use:
Partition pruning.
Partial indexes.
Composite indexes.
BRIN indexes where appropriate for naturally ordered time data.
GiST indexes for spatial data.
Do not introduce GIN indexes on every JSONB column. Add them only when queries require them.
23. Data lifecycle and retention
TerraNexus must define a retention policy for every data domain.
Data category
Retention consideration
User profiles
Account lifecycle and legal requirements
Farm records
Long-term operational history
Sensor measurements
Configurable operational and research retention
Device events
Security and troubleshooting needs
Commands
Preserve execution and safety history
Audit logs
Security and compliance requirements
Uploaded datasets
Licence and ownership conditions
Weather forecasts
Retain historical forecast versions where useful
ML outputs
Model evaluation and reproducibility
Notifications
User preferences and operational needs
Temporary exports
Automatic expiry

For research, aggregated or anonymised data may be retained under an approved policy, but this must not bypass consent, privacy or licensing restrictions.
24. Database migration strategy
Use version-controlled database migrations.
Recommended approach:
Alembic for schema migrations.
One migration per logical change.
Reviewed migration scripts.
Automated migration tests.
Backup before risky production migrations.
Backward-compatible schema changes where possible.
Explicit data migration plans.
Rollback or forward-recovery procedures.
Avoid modifying production tables manually without a tracked migration.
For large measurement tables, use staged migrations and appropriate online migration techniques.
25. Database performance and capacity planning
Capacity must be estimated from actual device counts and sampling frequencies.
For example, an illustrative scenario:
100 devices.
5 measurement channels per device.
One observation every five minutes.
24 hours per day.
This produces:
20 observations per device per hour.
100,000 observations per day across the deployment.
Approximately 36.5 million observations per year.
This excludes indexes, metadata, raw payloads, replicas and backups.
The platform must benchmark:
Ingestion throughput.
Historical chart queries.
Farm-level summaries.
Spatial queries.
Concurrent dashboard access.
Data exports.
Background analytics.
Retention and archival jobs.
Do not select a specialised database solely because the product handles sensor data. PostgreSQL should remain the starting point until measured requirements justify a change.
26. Initial database deployment layout
TerraNexus PostgreSQL
│
├── identity
│   ├── users
│   └── external_identities
│
├── organisation
│   ├── organisations
│   ├── memberships
│   ├── roles
│   ├── permissions
│   └── resource_access
│
├── farm
│   ├── farms
│   ├── fields
│   ├── farm_members
│   ├── field_zones
│   └── field_observations
│
├── agriculture
│   ├── crops
│   ├── crop_varieties
│   ├── growing_seasons
│   ├── field_crops
│   └── crop_growth_stages
│
├── operations
│   ├── tasks
│   ├── task_assignments
│   ├── activities
│   ├── equipment
│   ├── maintenance_records
│   ├── inventory_items
│   └── harvest_records
│
├── devices
│   ├── gateways
│   ├── devices
│   ├── sensors
│   ├── sensor_channels
│   ├── calibration_records
│   ├── device_events
│   ├── device_commands
│   └── command_events
│
├── observations
│   ├── measurement_types
│   ├── measurements
│   ├── measurement_quality_records
│   └── measurement_corrections
│
├── data_platform
│   ├── data_sources
│   ├── datasets
│   ├── dataset_versions
│   ├── data_import_jobs
│   ├── data_export_jobs
│   ├── files
│   └── file_attachments
│
├── environment
│   ├── weather_observations
│   ├── weather_forecasts
│   ├── soil_profiles
│   ├── soil_samples
│   └── remote_sensing_observations
│
├── monitoring
│   ├── alert_rules
│   ├── alerts
│   ├── alert_events
│   ├── notifications
│   └── notification_preferences
│
├── irrigation
│   ├── water_sources
│   ├── irrigation_zones
│   ├── pumps
│   ├── irrigation_plans
│   ├── irrigation_plan_steps
│   ├── irrigation_events
│   └── safety_events
│
├── intelligence
│   ├── models
│   ├── model_runs
│   ├── forecasts
│   ├── recommendations
│   ├── recommendation_evidence
│   └── recommendation_outcomes
│
├── integrations
│   ├── integration_providers
│   ├── integrations
│   ├── integration_sync_runs
│   ├── api_applications
│   ├── api_credentials
│   ├── webhooks
│   └── webhook_deliveries
│
├── sync
│   ├── client_devices
│   ├── sync_operations
│   ├── sync_conflicts
│   └── sync_checkpoints
│
├── reporting
│   ├── report_definitions
│   ├── report_runs
│   └── scheduled_reports
│
├── audit
│   ├── audit_logs
│   └── security_events
│
└── platform
    ├── plans
    ├── subscriptions
    └── usage_records
27. Database acceptance criteria
The database specification is ready for implementation planning when:
Every platform domain has a defined data owner.
Every entity has a defined purpose.
Every important relationship is documented.
Every tenant-owned record has an isolation strategy.
Foreign keys and unique constraints are specified.
Geographic records have spatial rules.
Measurements have standard units and provenance.
Time-series partitioning is tested.
Device command history is auditable.
Offline operations are idempotent.
Recommendations retain evidence and outcomes.
Data retention is documented.
Migrations are version-controlled.
Backup and restore procedures are tested.
Performance is benchmarked against expected workloads.

28. Outstanding decisions before physical schema approval
The following are not safe to finalise without additional requirements or technical testing:
Final measurement partition interval.
Whether TimescaleDB is needed beyond native PostgreSQL partitioning.
Exact supported measurement catalogue.
Unit conversion library and canonical unit policy.
Geographic precision and coordinate validation rules.
Whether farm ownership is always organisational or can support independent personal farms.
Whether sensor readings require separate high-frequency raw and normalised tables.
Retention periods for measurements, device events and audit logs.
Exact device deduplication keys.
Whether file storage is managed cloud storage or self-hosted.
The final identity-provider integration.
Whether data sharing between organisations is required for the first release.
These decisions must be recorded rather than silently embedded into the implementation.

29. Handoff to the next engineering document
Next document: TNX-UI-001 — TerraNexus Complete UI/UX and Screen Design Specification.
It must use the entities and workflows defined here.
It will cover:
Global design system.
Brand colours, typography and spacing.
Navigation and information architecture.
Responsive desktop layouts.
Tablet layouts.
Mobile layouts.
All 126 previously identified pages.
Screen-level wireframes.
Component hierarchy.
Forms and validation.
Tables, filters and search.
Maps and spatial interactions.
Charts and agricultural visualisations.
Permissions and role-based visibility.
Loading, empty, populated, stale, offline and error states.
Accessibility.
Interaction specifications.
User journeys.
High-fidelity visual direction.
Page acceptance criteria.
Database status: Comprehensive logical schema baseline established. Physical SQL definitions, ERD refinement, migration scripts, benchmarks and implementation remain outstanding. No coding has been authorised by this specification.
What this establishes
The most important architectural distinction in the database is that TerraNexus stores different kinds of agricultural information separately:
Measurements are actual observations.
Weather forecasts are predictions about future conditions.
Recommendations are proposed actions supported by evidence.
Irrigation events are records of what physically happened.
Outcomes record what happened after an action.
Keeping these separate prevents the platform from confusing an AI prediction with an actual farm measurement or a recommended action with an executed operation.
Next: TNX-UI-001 — the 126-page UI/UX specification. We will use the database entities above to design the actual screens and their interactions, rather than designing attractive but disconnected dashboards.
TNX-UI-001 — the 126-page UI/UX specification. We will use the database entities above to design the actual screens and their interactions, rather than designing attractive but disconnected dashboards.
