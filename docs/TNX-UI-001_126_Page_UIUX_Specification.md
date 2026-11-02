TerraNexus — TNX-UI-001
COMPLETE UI/UX AND SCREEN DESIGN SPECIFICATION · VERSION 1.0
Design baseline established
Visual implementation pending
This specification defines the interface for the entire TerraNexus platform. It uses the approved architectural direction:
Modular monolith.
PostgreSQL + PostGIS.
Independent device and physical-control boundaries.
Multi-tenant organisations.
Offline-first mobile workflows.
Evidence-based agricultural intelligence.
The purpose is to make every screen part of a coherent agricultural workflow. A farmer should be able to move from a field condition to an informed decision and, where authorised, an operational action without navigating disconnected features.
TERRANEXUS
Complete UI/UX and Screen Design Specification
Document ID: TNX-UI-001
Version: 1.0
Status: Proposed design baseline
Product: Open Agricultural Intelligence & Operations Platform
Platform surfaces: Web, tablet and mobile
Page inventory: 126 pages
Design approach: Workflow-first, responsive, accessible, data-aware and offline-conscious

PART I — PRODUCT EXPERIENCE AND DESIGN FOUNDATION
1. Product experience objectives
TerraNexus should help users answer five questions:
What is happening on my farm?
Where is it happening?
Why is it happening?
What should happen next?
Did the action produce the expected result?
Every major feature should contribute to at least one of these questions.
1.1 Core UX principles
Agricultural context first
Show farm, field, crop, season, location and measurement context wherever they are relevant.
Evidence before recommendations
An insight must show the underlying observations, their dates, quality and source.
Actionable information
Do not present an alert without providing a meaningful next step where one exists.
Progressive complexity
Farmers should not have to understand model registries, API credentials or data pipelines to operate their farms.
User control
Users must know when a device is being controlled, what action is requested and whether it actually succeeded.
Offline awareness
Users must be able to identify locally saved records, pending uploads, conflicts and unavailable information.
Role-based experiences
A farmer, researcher and platform administrator should not receive the same navigation or dashboard.

2. Brand and visual direction
2.1 Brand personality
TerraNexus should feel:
Professional.
Agricultural.
Scientific.
Trustworthy.
Practical.
Calm.
Modern.
International, with room for African agricultural contexts.
Avoid:
Purple AI gradients.
Excessive glassmorphism.
Decorative dashboards full of meaningless cards.
Unnecessary animations.
Overuse of bright green.
Tiny, crowded agricultural data tables.
Fake-looking AI assistant interfaces.
Excessively technical language in farmer-facing screens.
2.2 Colour system
Proposed design tokens:
Token
Proposed value
Purpose
Primary
#245B45
Main brand and navigation
Primary dark
#173D30
Emphasis and strong contrast
Primary light
#E7F0E9
Selected backgrounds
Soil
#9A7653
Agricultural and terrain accents
Earth light
#F2EAE0
Supporting surfaces
Amber
#D49A36
Attention and caution
Background
#F7F8F5
Main application background
Surface
#FFFFFF
Cards and panels
Text primary
#202923
Main text
Text secondary
#66736A
Supporting text
Border
#DFE5DF
Separators
Success
#24764B
Confirmed successful states
Warning
#A66A12
Warnings
Danger
#B33A35
Errors and critical events
Information
#376A91
Informational states

These are initial tokens, not final accessibility-certified values. Contrast must be tested in actual components.
2.3 Typography
Primary font: Inter.
Use a consistent hierarchy:
Element
Desktop size
Weight
Main page title
28–32 px
600
Section title
20–24 px
600
Card title
15–17 px
600
Body
14–16 px
400
Supporting text
12–14 px
400
Table text
13–14 px
400
Large metric
28–36 px
600

Do not use oversized headings throughout operational dashboards.
2.4 Spacing and shape
Base spacing unit: 4 px.
Main page padding: 24 px desktop.
Card padding: 16–20 px.
Form spacing: 16 px.
Section spacing: 24–32 px.
Standard border radius: 8 px.
Larger panels: 12 px.
Inputs: 40–44 px minimum height.
Touch targets: preferably at least 44 × 44 px.
2.5 Iconography
Use a consistent outline icon set such as Lucide.
Examples:
Farm: sprout
Field: map
Crop: wheat
Device: cpu
Data: database
Weather: cloud-sun
Irrigation: droplets
Analytics: chart-no-axes-combined
Tasks: clipboard-list
Alerts: bell
Settings: settings
Use labels alongside important icons. Do not make essential functions icon-only.

3. Global application layout
3.1 Desktop shell
Target desktop breakpoint: 1280 px and above.
┌──────────────────────────────────────────────────────────────────────┐
│ TERRANEXUS   Workspace ▼       Search...      Help  Alerts  Profile │
├───────────────┬──────────────────────────────────────────────────────┤
│               │                                                      │
│ Overview      │ Page title                         Context actions   │
│               │ Breadcrumbs                                           │
│ Farm          │                                                      │
│  Farms        │ ┌──────────────────────────────────────────────────┐ │
│  Fields       │ │ Context / status / key information               │ │
│  Crops        │ └──────────────────────────────────────────────────┘ │
│               │                                                      │
│ Operations    │ Main content                                         │
│               │                                                      │
│ Devices       │ Tables / maps / charts / forms / workflows           │
│               │                                                      │
│ Data          │                                                      │
│               │                                                      │
│ Intelligence  │                                                      │
│               │                                                      │
│ Reports       │                                                      │
│               │                                                      │
│ Settings      │                                                      │
├───────────────┴──────────────────────────────────────────────────────┤
│ Connection status · Last sync · Version                              │
└──────────────────────────────────────────────────────────────────────┘
Global shell components
Brand and workspace selector.
Global search.
Help and documentation.
Notification centre.
User profile menu.
Primary navigation.
Breadcrumbs.
Page title and actions.
Context selector where relevant.
Offline and synchronisation indicator.
3.2 Tablet layout
Target: 768–1279 px.
Collapsible navigation drawer.
Two-column content where space allows.
Tables may become horizontally scrollable or switch to structured row cards.
Maps and charts remain usable.
Side panels become drawers.
Primary actions remain visible.
3.3 Mobile layout
Target: below 768 px.
┌──────────────────────────────┐
│ ☰  TerraNexus       🔔  👤   │
├──────────────────────────────┤
│ Farm / Field context         │
│                              │
│ Page title                   │
│ Supporting information       │
│                              │
│ ┌──────────────────────────┐ │
│ │ Primary information      │ │
│ └──────────────────────────┘ │
│                              │
│ ┌──────────────────────────┐ │
│ │ Secondary information    │ │
│ └──────────────────────────┘ │
│                              │
│ Main content                 │
│                              │
├──────────────────────────────┤
│ Home  Farm  Tasks  Data  More│
└──────────────────────────────┘
Mobile navigation priorities:
Home.
Farm.
Tasks.
Monitoring.
More.
The navigation must be role-aware. A researcher may receive Data instead of Tasks in the primary navigation.
3.4 Global context selectors
Context selectors should be consistent across pages.
Available contexts:
Organisation.
Farm.
Field.
Growing season.
Date range.
Changing the active farm must update all dependent views and queries.
The system must make it clear when a user is viewing:
One farm.
All authorised farms.
A specific field.
Organisation-wide information.
3.5 Global interaction patterns
Create actions: Open a dedicated form page or a suitable drawer.
Edit actions: Use an explicit edit page or panel. Preserve unsaved changes warnings.
Delete actions: Confirm irreversible operations and explain consequences.
Tables: Support filtering, sorting, pagination, empty states and export where appropriate.
Charts: Show units, time ranges, missing intervals, source and quality context.
Maps: Support layers, legend, selection, zoom, boundary visibility and location details.
Forms: Validate on input and on submission. Preserve entered values when recoverable errors occur.
Destructive controls: Require explicit confirmation.

PART II — DESIGN SYSTEM AND REUSABLE COMPONENTS
4. Component library
4.1 Navigation components
Main sidebar.
Collapsible sidebar.
Mobile navigation drawer.
Bottom navigation.
Breadcrumbs.
Tabs.
Context selector.
Workspace switcher.
Page action menu.
4.2 Data display components
Metric card.
Status badge.
Data-quality badge.
Measurement table.
Comparison table.
Timeline.
Activity feed.
Geographic map.
Field boundary panel.
Chart panel.
Forecast panel.
Evidence panel.
File attachment panel.
Data-source attribution.
4.3 Forms
Text input.
Numeric input with unit.
Date and time selector.
Location picker.
Map boundary editor.
Farm selector.
Field selector.
Crop selector.
Device selector.
Sensor selector.
File uploader.
Multi-step form.
Permission selector.
Dynamic configuration editor.
4.4 Operational components
Task status selector.
Task assignment panel.
Irrigation control panel.
Command confirmation modal.
Command lifecycle timeline.
Device health panel.
Alert acknowledgement control.
Offline sync queue.
Conflict resolution panel.
Approval workflow.
4.5 Intelligence components
Recommendation card.
Evidence list.
Confidence indicator.
Forecast chart.
Model metadata panel.
Model execution status.
Recommendation decision controls.
Outcome capture form.
4.6 Component state contract
Every reusable component must define:
Default.
Hover.
Focus.
Selected.
Disabled.
Loading.
Empty.
Error.
Success.
Offline or stale where relevant.

PART III — INFORMATION ARCHITECTURE
5. Global navigation
TerraNexus
│
├── Overview
│   ├── Dashboard
│   ├── Search
│   ├── Notifications
│   └── Activity
│
├── Farm
│   ├── Farms
│   ├── Fields
│   ├── Crops
│   └── Growing Seasons
│
├── Connect
│   ├── Devices
│   ├── Gateways
│   ├── Sensors
│   └── Firmware
│
├── Data
│   ├── Measurements
│   ├── Datasets
│   ├── Data Sources
│   ├── Imports
│   └── Data Quality
│
├── Monitor
│   ├── Live Monitoring
│   ├── Charts
│   ├── Alerts
│   └── Alert Rules
│
├── Operations
│   ├── Tasks
│   ├── Calendar
│   ├── Activities
│   ├── Equipment
│   ├── Inventory
│   └── Harvest
│
├── Water
│   ├── Irrigation
│   ├── Zones
│   ├── Plans
│   ├── Control
│   └── Water Sources
│
├── Intelligence
│   ├── Recommendations
│   ├── Weather
│   ├── Soil
│   ├── Crop Health
│   ├── Predictive Analytics
│   └── Models
│
├── Collaboration
│   ├── Members
│   ├── Agronomy
│   ├── Extension
│   └── Research
│
├── Reports
│
├── Developer
│   ├── Integrations
│   ├── API Keys
│   ├── Webhooks
│   └── API Documentation
│
└── Settings
    ├── Personal
    ├── Organisation
    ├── Security
    └── Administration
Navigation visibility is determined by role, permissions and enabled modules.

PART IV — SCREEN-BY-SCREEN SPECIFICATION
Each page below defines its purpose, major screen structure, actions and mobile behaviour. The global component and state rules above apply to every page.
GROUP A — PUBLIC PAGES
001. Home
Route: /
Purpose: Introduce TerraNexus and communicate its value.
Desktop wireframe:
┌──────────────────────────────────────────────────────────────┐
│ Logo     Platform  Solutions  Integrations  Docs   Sign in  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Agricultural intelligence connected to real-world action    │
│                                                              │
│ Connect farms, data, devices and people.                     │
│                                                              │
│ [Explore platform] [Create account]                          │
│                                                              │
│             Agricultural platform visual                     │
├──────────────────────────────────────────────────────────────┤
│ Farm operations | Connected data | Intelligence | Action    │
├──────────────────────────────────────────────────────────────┤
│ Platform capabilities                                        │
├──────────────────────────────────────────────────────────────┤
│ Applications and use cases                                   │
├──────────────────────────────────────────────────────────────┤
│ Integrations and ecosystem                                   │
├──────────────────────────────────────────────────────────────┤
│ Footer: Company / Documentation / Legal / Contact            │
└──────────────────────────────────────────────────────────────┘
Interactions:
Explore platform.
Create account.
Sign in.
Open documentation.
Navigate to solutions.
Mobile:
Compact header.
Stacked hero.
Single-column capability sections.
Persistent primary call to action where appropriate.
002. About
Route: /about
Sections:
TerraNexus mission.
Vision.
Platform philosophy.
Agricultural data ecosystem.
Principles of interoperability.
Contact and organisation information.
Actions:
Contact team.
Explore platform.
003. Platform Overview
Route: /platform
Sections:
Connect.
Understand.
Decide.
Act.
Learn.
Show how the modules work together through a workflow diagram.
004. Solutions
Route: /solutions
Role and problem-oriented solution catalogue:
Smallholder farming.
Commercial farms.
Cooperatives.
Agronomists.
Research institutions.
Agricultural service providers.
Do not claim that any solution is proven until validated.
005. Integrations
Route: /integrations
Components:
Integration categories.
Available providers.
Protocols.
Connector documentation.
Integration request form.
Show verified integration status, not merely planned integrations.
006. Documentation
Route: /docs
Features:
Search.
Documentation categories.
Quick start.
User guides.
Device guides.
API reference.
Release notes.
007. Contact
Route: /contact
Fields:
Name.
Email.
Organisation.
Enquiry category.
Message.
Consent.
Show submission confirmation and validation errors.
008. Legal
Route: /legal
Sections:
Terms of service.
Privacy policy.
Cookie policy.
Data processing information.
Data-sharing policy.
Acceptable use.
Licence information.
Use versioned legal documents.

GROUP B — AUTHENTICATION AND ONBOARDING
009. Registration
Route: /register
Fields:
First name.
Last name.
Email.
Phone, optional.
Password.
Terms acceptance.
Interactions:
Password visibility.
Strength guidance.
Duplicate-account handling.
Email verification initiation.
Mobile:
Single-column form.
Large input targets.
Clear progress and error messages.
010. Login
Route: /login
Components:
Email or identity provider login.
Password.
Remember-session option where supported.
Forgot password.
MFA challenge when enabled.
011. Email Verification
Route: /verify-email
Components:
Verification status.
Resend link.
Change email.
Expiry message.
Continue after success.
012. Password Recovery
Route: /forgot-password
Fields:
Email.
Show neutral success messaging that does not reveal whether an account exists.
013. MFA Setup
Route: /security/mfa
Components:
Authenticator setup.
QR code.
Verification code.
Recovery codes.
Confirmation.
Recovery codes must be displayed securely and not logged.
014. User Onboarding
Route: /onboarding
Steps:
Personal details.
User role or intended use.
Organisation choice.
Language and timezone.
Notification preferences.
Completion.
Allow skipping optional steps.
015. Organisation Setup
Route: /onboarding/organisation
Fields:
Organisation name.
Type.
Country.
Currency.
Timezone.
Contact details.
Registration information, optional.
016. Workspace Setup
Route: /onboarding/workspace
Actions:
Create a farm workspace.
Join an existing organisation.
Accept invitation.
Explore a demonstration workspace where available.

GROUP C — MAIN APPLICATION SHELL
017. Dashboard
Route: /dashboard
Purpose: Give the user a contextual overview.
Desktop:
┌──────────────────────────────────────────────────────────────┐
│ Dashboard               Farm ▼  Season ▼   Date range        │
├──────────────────────────────────────────────────────────────┤
│ Conditions      Active alerts     Open tasks     Devices     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Farm map / spatial overview       Field conditions          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ Recent measurements             Weather outlook              │
├──────────────────────────────────────────────────────────────┤
│ Pending tasks                   Recommendations              │
├──────────────────────────────────────────────────────────────┤
│ Recent activity                 Data/device health            │
└──────────────────────────────────────────────────────────────┘
Content is role-dependent.
Farmer:
Field conditions.
Tasks.
Weather.
Alerts.
Irrigation status.
Manager:
Multi-field status.
Workload.
Equipment.
Resources.
Performance.
Researcher:
Datasets.
Data quality.
Processing jobs.
Model runs.
Interactions:
Change farm.
Open field details.
Acknowledge alert.
Open task.
View measurement.
Review recommendation.
018. Global Search
Route: /search
Search categories:
Farms.
Fields.
Crops.
Devices.
Measurements.
Tasks.
Datasets.
Alerts.
Reports.
Features:
Search suggestions.
Recent searches.
Permission-aware results.
Filters.
No-results guidance.
019. Notifications
Route: /notifications
Tabs:
All.
Unread.
Alerts.
Tasks.
System.
Actions:
Mark read.
Mark all read.
Open source record.
Manage preferences.
020. Activity Feed
Route: /activity
Timeline:
User activity.
Farm changes.
Device events.
Task changes.
Irrigation operations.
Recommendations.
Integration activity.
Filters by date, actor, farm and activity type.
021. Help and Support
Route: /help
Sections:
Search documentation.
Frequently asked questions.
Report a problem.
Device troubleshooting.
Contact support.
Support ticket history.

GROUP D — FARMS AND FIELDS
022. Farms List
Route: /farms
Layout:
Farm summary.
Farm table or cards.
Search.
Status filter.
Location filter.
Create farm.
Each farm card:
Name.
Location.
Area.
Field count.
Device count.
Status.
023. Create Farm
Route: /farms/new
Form:
Farm name.
Organisation.
Country and locality.
Farm boundary.
Area.
Contact details.
Additional information.
Map boundary editor:
Draw polygon.
Edit vertices.
Import GeoJSON.
Validate geometry.
Calculate area.
024. Farm Overview
Route: /farms/:farmId
Sections:
Farm identity.
Map.
Fields.
Crop assignments.
Device status.
Current conditions.
Tasks.
Alerts.
Recent activities.
025. Edit Farm
Route: /farms/:farmId/edit
Editable:
Name.
Location.
Boundary.
Metadata.
Farm status.
Show change history and unsaved-change warnings.
026. Farm Map
Route: /farms/:farmId/map
Layers:
Farm boundary.
Field boundaries.
Devices.
Irrigation zones.
Soil samples.
Alerts.
Observations.
Interactions:
Toggle layers.
Select field.
Measure distance.
Measure area.
Zoom to device.
Open location details.
027. Fields List
Route: /fields
Views:
Table.
Cards.
Map.
Columns:
Field.
Farm.
Area.
Crop.
Season.
Status.
Last observation.
028. Create Field
Route: /fields/new
Fields:
Farm.
Field name.
Field code.
Boundary.
Area.
Description.
Soil profile.
Validate farm membership and boundary.
029. Field Overview
Route: /fields/:fieldId
Sections:
Field summary.
Geographic boundary.
Current crop.
Current conditions.
Sensors.
Recent measurements.
Alerts.
Tasks.
Recommendations.
Activity history.
030. Field History
Route: /fields/:fieldId/history
Timeline:
Crop assignments.
Planting.
Irrigation.
Fertilisation.
Field inspections.
Harvest.
Boundary changes.
Sensor history.
031. Field Observations
Route: /fields/:fieldId/observations
Features:
Observation list.
Date filters.
Observation categories.
Photograph attachments.
Map locations.
Verification state.
Create observation.
Mobile:
Camera capture.
Location capture.
Offline draft support.

GROUP E — CROPS AND GROWING SEASONS
032. Crop Catalogue
Route: /crops
Features:
Crop search.
Crop categories.
Scientific names.
Growing characteristics.
Variety filters.
033. Crop Details
Route: /crops/:cropId
Sections:
Crop description.
Varieties.
Typical growth duration.
Growth stages.
Environmental requirements.
Water requirements.
Reference information.
034. Assign Crop
Route: /fields/:fieldId/crops/new
Fields:
Field.
Crop.
Variety.
Season.
Planting date.
Expected harvest.
Cultivated area.
035. Growing Seasons
Route: /seasons
Views:
Season list.
Calendar.
Active season.
Completed seasons.
036. Crop Calendar
Route: /crops/calendar
Views:
Calendar.
Growth-stage timeline.
Planting.
Expected activities.
Harvest periods.
037. Crop Health
Route: /crop-health
Sections:
Field selection.
Crop status.
Observations.
Images.
Vegetation indicators where available.
Health trends.
Supporting evidence.
Do not display an AI diagnosis as a confirmed disease diagnosis without validation.

GROUP F — DEVICES AND IoT
038. Devices Overview
Route: /devices
Summary:
Registered devices.
Online.
Offline.
Degraded.
Unprovisioned.
Faulted.
Table:
Device.
Farm.
Field.
Type.
Status.
Firmware.
Last seen.
039. Register Device
Route: /devices/new
Fields:
Device identity.
Manufacturer.
Model.
Farm.
Field.
Gateway.
Protocol.
Capabilities.
040. Device Details
Route: /devices/:deviceId
Sections:
Device status.
Identity.
Hardware and firmware.
Sensors.
Recent telemetry.
Connectivity.
Events.
Commands.
Configuration.
Security state.
041. Device Provisioning
Route: /devices/:deviceId/provision
Workflow:
Verify identity.
Issue provisioning credentials.
Configure broker or endpoint.
Test connection.
Verify first telemetry.
Activate device.
Show security warnings and provisioning expiry.
042. Sensor Registry
Route: /sensors
Columns:
Sensor.
Device.
Type.
Measurement.
Unit.
Calibration.
Status.
043. Sensor Details
Route: /sensors/:sensorId
Sections:
Sensor identity.
Measurement type.
Unit.
Recent readings.
Historical chart.
Calibration history.
Quality status.
Configuration.
044. Device Configuration
Route: /devices/:deviceId/configuration
Features:
Configuration version.
Editable parameters.
Allowed ranges.
Validation.
Change preview.
Publish configuration.
Acknowledgement.
Configuration changes must be versioned.
045. Device Commands
Route: /devices/:deviceId/commands
Features:
Command history.
Command state.
Requested by.
Expiry.
Acknowledgement.
Execution result.
Failure reason.
046. Device Events
Route: /devices/:deviceId/events
Timeline:
Connected.
Disconnected.
Rebooted.
Sensor error.
Low battery.
Firmware update.
Configuration change.
047. Firmware Management
Route: /devices/firmware
Sections:
Firmware catalogue.
Hardware compatibility.
Release notes.
Deployment groups.
Deployment progress.
Failure handling.
Rollback eligibility.

GROUP G — AGRICULTURAL DATA
048. Data Overview
Route: /data
Summary:
Total datasets.
Data sources.
Latest ingestion.
Quality issues.
Processing jobs.
Storage usage.
049. Measurements Explorer
Route: /data/measurements
Filters:
Farm.
Field.
Device.
Sensor.
Measurement type.
Date range.
Quality status.
Visualisations:
Time-series charts.
Measurement tables.
Map view.
Export.
050. Measurement Details
Route: /data/measurements/:measurementId
Display:
Value and unit.
Measurement type.
Source.
Device and sensor.
Field.
Observed time.
Received time.
Quality.
Calibration.
Processing history.
051. Data Sources
Route: /data/sources
Source catalogue:
Provider.
Category.
Licence.
Last update.
Connection status.
Data availability.
052. Dataset Catalogue
Route: /datasets
Views:
Organisation datasets.
Shared datasets.
Public datasets.
Research datasets.
Filters:
Category.
Source.
Date coverage.
Geography.
Licence.
053. Dataset Details
Route: /datasets/:datasetId
Sections:
Description.
Owner.
Source.
Licence.
Version history.
Schema.
Geographic coverage.
Temporal coverage.
Access policy.
054. Data Import
Route: /data/import
Workflow:
Upload.
Identify format.
Map columns.
Map measurement types.
Validate units.
Preview.
Import.
Review results.
Support CSV, JSON and GeoJSON initially. Spreadsheet support can be added with explicit format validation.
055. Data Export
Route: /data/export
Fields:
Dataset.
Date range.
Farm/field.
Measurement type.
Output format.
Privacy scope.
Formats:
CSV.
JSON.
GeoJSON where spatial.
Supported spreadsheet formats.
056. Data Quality
Route: /data/quality
Indicators:
Missing records.
Invalid values.
Outliers.
Stale sensors.
Uncalibrated sensors.
Duplicate observations.
Source inconsistencies.
Actions:
Review.
Correct.
Exclude from selected analysis.
Reprocess.
Export issue report.
057. Data Processing Jobs
Route: /data/jobs
Columns:
Job.
Type.
Source.
Submitted.
Progress.
Status.
Errors.
Details include logs, retry eligibility and processed-record counts.

GROUP H — MONITORING AND ALERTS
058. Live Monitoring
Route: /monitoring/live
Main layout:
Farm/field selector.
Live device status.
Latest measurements.
Current conditions.
Data freshness.
Alert panel.
Each value must show its last observation time.
059. Monitoring Charts
Route: /monitoring/charts
Features:
Measurement selection.
Time-range selector.
Multiple series.
Compare fields.
Threshold overlays.
Missing-data markers.
Export.
060. Alerts Overview
Route: /alerts
Filters:
Active.
Acknowledged.
Resolved.
Critical.
Farm.
Field.
Alert type.
061. Alert Details
Route: /alerts/:alertId
Sections:
Alert description.
Triggered time.
Severity.
Related measurement.
Rule.
Evidence.
Related device.
Acknowledgement history.
Resolution history.
Actions:
Acknowledge.
Assign.
Resolve.
Create task.
062. Alert Rules
Route: /alerts/rules
Features:
Rule list.
Enable/disable.
Condition summary.
Scope.
Severity.
Evaluation frequency.
063. Notification Preferences
Route: /settings/notifications
Channels:
In-app.
Email.
Push.
SMS, where supported.
Controls:
Event categories.
Severity.
Quiet hours.
Delivery preferences.

GROUP I — FARM OPERATIONS
064. Operations Overview
Route: /operations
Summary:
Tasks due.
Overdue tasks.
Active activities.
Equipment status.
Inventory warnings.
Harvest records.
065. Task List
Route: /tasks
Views:
List.
Board.
Calendar.
Filters:
Status.
Assigned user.
Farm.
Field.
Priority.
Date.
066. Create Task
Route: /tasks/new
Fields:
Title.
Description.
Farm.
Field.
Type.
Priority.
Assignees.
Due date.
Attachments.
067. Task Details
Route: /tasks/:taskId
Sections:
Task information.
Status.
Assignees.
Due date.
Comments.
Attachments.
Related field.
Activity log.
Actions:
Update status.
Reassign.
Complete.
Cancel.
068. Calendar
Route: /calendar
Views:
Day.
Week.
Month.
Agenda.
Events:
Tasks.
Planting.
Irrigation.
Inspections.
Harvest.
Maintenance.
069. Activity Records
Route: /activities
Features:
Record activity.
Filter by field.
Filter by crop.
View history.
Attach photographs.
Link to tasks.
070. Equipment Management
Route: /equipment
Columns:
Equipment.
Farm.
Type.
Status.
Maintenance.
Last service.
071. Inventory and Inputs
Route: /inventory
Sections:
Items.
Stock.
Transactions.
Reorder warnings.
Usage history.
Inventory changes must be recorded as transactions.
072. Field Inspections
Route: /inspections
Workflow:
Select farm and field.
Select inspection type.
Record observations.
Capture photographs.
Record location.
Submit.
Review.
073. Harvest Records
Route: /harvest
Fields:
Field.
Crop.
Season.
Harvest date.
Quantity.
Unit.
Quality grade.
Notes.

GROUP J — IRRIGATION AND WATER MANAGEMENT
074. Irrigation Overview
Route: /irrigation
Display:
Irrigation status.
Active plans.
Recent events.
Water availability.
Zones.
Pump status.
Safety alerts.
075. Irrigation Zones
Route: /irrigation/zones
Views:
Map.
List.
Field grouping.
Each zone displays:
Boundary.
Area.
Irrigation method.
Pump association.
Status.
076. Create Irrigation Plan
Route: /irrigation/plans/new
Steps:
Select farm.
Select field or zone.
Select water source.
Select pump.
Set intended schedule.
Define duration or target volume.
Review supporting evidence.
Submit for approval.
077. Irrigation Plan Details
Route: /irrigation/plans/:planId
Display:
Plan.
Target.
Evidence.
Approval state.
Execution state.
Steps.
Command references.
History.
078. Irrigation Schedule
Route: /irrigation/schedule
Views:
Calendar.
Timeline.
Zone schedule.
Conflicts.
Show water-resource and pump constraints.
079. Irrigation Control
Route: /irrigation/control
This is a high-risk operational screen.
Display:
Device and pump identity.
Zone.
Connectivity.
Water availability.
Current state.
Safety status.
Active command.
Emergency stop state.
Actions:
Start.
Stop.
Emergency stop.
Review command history.
Before execution:
Confirm user permission.
Validate device.
Validate command expiry.
Check safety conditions.
Show explicit confirmation.
The interface must never claim that a pump has started until the device acknowledgement and execution evidence support that state.
080. Irrigation History
Route: /irrigation/history
Columns:
Zone.
Pump.
Start.
End.
Actual volume.
Status.
Initiated by.
Command result.
081. Water Management
Route: /water-management
Sections:
Water sources.
Capacity.
Availability.
Usage.
Irrigation demand.
Historical records.
Resource warnings.

GROUP K — AGRICULTURAL INTELLIGENCE
082. Intelligence Overview
Route: /intelligence
Display:
Available insights.
Forecasts.
Recommendations.
Data availability.
Model health.
Recent model runs.
083. Recommendations
Route: /recommendations
Filters:
Farm.
Field.
Type.
Priority.
Status.
Date.
Each recommendation shows:
Suggested action.
Reason.
Evidence count.
Confidence where meaningful.
Expiry.
Review status.
084. Recommendation Details
Route: /recommendations/:recommendationId
Sections:
Proposed action.
Explanation.
Evidence.
Data freshness.
Model or ruleset.
Confidence and limitations.
Alternatives.
Review history.
Actions:
Accept.
Reject.
Defer.
Record reason.
Create task.
Request further review.
Accepting a recommendation must not automatically execute a physical operation unless a separate approved workflow authorises it.
085. Weather Intelligence
Route: /intelligence/weather
Display:
Current observations.
Forecast.
Rain probability.
Expected rainfall.
Temperature.
Wind.
Data source.
Forecast issue time.
Forecast validity.
086. Soil Intelligence
Route: /intelligence/soil
Sections:
Soil profiles.
Soil samples.
pH.
Electrical conductivity.
Moisture.
Organic matter.
Soil maps.
Historical trends.
087. Crop Intelligence
Route: /intelligence/crops
Sections:
Crop health.
Growth-stage context.
Field observations.
Vegetation indicators.
Weather context.
Supporting evidence.
088. Predictive Analytics
Route: /intelligence/predictions
Features:
Forecast selection.
Time horizon.
Field selection.
Model selection where authorised.
Prediction chart.
Confidence intervals.
Historical evaluation.
089. Model Registry
Route: /intelligence/models
Columns:
Model.
Type.
Version.
Owner.
Status.
Evaluation.
Deployment.
090. Model Execution History
Route: /intelligence/model-runs
Columns:
Model.
Version.
Farm/field.
Start.
Duration.
Status.
Output.
091. AI Assistant Workspace
Route: /intelligence/assistant
Optional interface.
Capabilities:
Ask questions about authorised farm data.
Summarise field history.
Explain recommendations.
Summarise reports.
Help users navigate the platform.
Rules:
Clearly identify generated content.
Cite the platform records used.
Distinguish measured facts from inferred statements.
Never invent missing farm records.
Never execute dangerous equipment operations directly.
Provide useful non-AI workflows when the service is unavailable.
092. Local Intelligence Settings
Route: /intelligence/local
Settings:
Local inference availability.
Model selection.
Hardware compatibility.
Storage use.
Privacy settings.
Offline capability.
Resource usage.
QVAC or other local inference integrations are optional and must not be prerequisites for core functionality.

GROUP L — COLLABORATION AND ORGANISATION
093. Organisation Dashboard
Route: /organisation
Display:
Organisation summary.
Farms.
Members.
Device status.
Operations.
Data usage.
Reports.
094. Members
Route: /organisation/members
Features:
Member list.
Invitations.
Roles.
Membership status.
Farm-level access.
Suspension.
095. Organisation Analytics
Route: /organisation/analytics
Metrics:
Farm coverage.
Activity completion.
Measurement availability.
Device health.
Irrigation activity.
Data quality.
Metrics must be clearly defined and comparable.
096. Agronomist Workspace
Route: /workspace/agronomy
Features:
Assigned farms.
Field assessments.
Recommendations.
Crop observations.
Soil reports.
Follow-up tasks.
097. Extension Workspace
Route: /workspace/extension
Features:
Assigned communities or farms.
Farmer support.
Visit records.
Field observations.
Training activities.
Follow-up.
098. Research Workspace
Route: /workspace/research
Features:
Dataset catalogue.
Data access requests.
Analysis workspace.
Model runs.
Research notes.
Export permissions.
099. Collaboration and Comments
Route: /collaboration
Features:
Shared comments.
Discussions.
Resource references.
Mentions.
Attachments.
Activity history.
100. Service Provider Workspace
Route: /workspace/providers
Features:
Assigned clients.
Service records.
Equipment maintenance.
Field services.
Service reports.
Work completion.

GROUP M — INTEGRATIONS AND DEVELOPER TOOLS
101. Integration Catalogue
Route: /developer/integrations
Categories:
Weather.
Satellite.
Soil.
Devices.
Research.
Farm management.
External APIs.
102. Integration Details
Route: /developer/integrations/:providerId
Display:
Provider description.
Capabilities.
Protocol.
Authentication.
Data coverage.
Documentation.
Licence.
Connection status.
103. Configure Integration
Route: /developer/integrations/configure/:providerId
Workflow:
Select organisation.
Enter configuration.
Add credentials securely.
Test connection.
Select data scopes.
Configure synchronisation.
Activate.
104. API Keys
Route: /developer/api-keys
Features:
Create application.
Generate credential.
Assign scopes.
Expiry.
Rotation.
Revocation.
Last-used information.
Show secrets only when initially issued.
105. Webhooks
Route: /developer/webhooks
Features:
Endpoint registration.
Event subscriptions.
Signing secret setup.
Enable/disable.
Test delivery.
106. API Documentation
Route: /developer/docs
Features:
OpenAPI reference.
Authentication.
Endpoint groups.
Schemas.
Error responses.
Examples.
Versioning.
107. Developer Applications
Route: /developer/applications
Display:
Application.
Organisation.
Scopes.
Credentials.
Usage.
Status.
108. Integration Logs
Route: /developer/logs
Filters:
Provider.
Integration.
Event.
Status.
Date.
Display:
Requests.
Responses where safe.
Processing errors.
Retry history.
Synchronisation results.
Never expose credentials in logs.

GROUP N — REPORTING
109. Reports Overview
Route: /reports
Categories:
Farm.
Field.
Crop.
Irrigation.
Device.
Organisation.
Research.
110. Farm Report
Route: /reports/farm
Sections:
Farm summary.
Fields.
Crops.
Operations.
Measurements.
Alerts.
Resources.
111. Field Report
Route: /reports/field
Sections:
Field information.
Crop history.
Measurements.
Soil.
Weather.
Activities.
Observations.
112. Irrigation Report
Route: /reports/irrigation
Sections:
Plans.
Events.
Water volume.
Pump operation.
Failed commands.
Safety events.
113. Device Report
Route: /reports/devices
Sections:
Device availability.
Firmware.
Sensor health.
Measurement quality.
Connectivity.
Events.
114. Organisation Report
Route: /reports/organisation
Sections:
Farm summary.
Members.
Operations.
Data.
Device coverage.
Alerts.
Usage.
115. Custom Report Builder
Route: /reports/builder
Workflow:
Select report domain.
Select authorised data.
Define filters.
Select columns and metrics.
Select grouping.
Preview.
Save or export.
116. Scheduled Reports
Route: /reports/scheduled
Features:
Schedule.
Timezone.
Recipients.
Format.
Next run.
Delivery status.
Disable or delete.

GROUP O — ADMINISTRATION AND SETTINGS
117. Platform Administration Dashboard
Route: /admin
Display:
Platform health.
Tenant count.
User count.
Device connections.
Ingestion health.
Queue health.
Error rates.
Security alerts.
118. Tenant Management
Route: /admin/tenants
Features:
Organisation list.
Status.
Usage.
Subscription.
Suspension.
Tenant configuration.
119. User Administration
Route: /admin/users
Features:
Search users.
Status.
Account verification.
Access review.
Suspension.
Account lifecycle.
120. Permission Administration
Route: /admin/permissions
Features:
Role catalogue.
Permission definitions.
Role assignments.
Resource access.
Policy testing.
121. Audit Logs
Route: /admin/audit
Filters:
Actor.
Organisation.
Resource.
Action.
Date.
Severity.
Audit logs must be read-only to normal administrators.
122. System Configuration
Route: /admin/configuration
Features:
Global settings.
Feature flags.
Data policies.
Integration policies.
Notification configuration.
Operational limits.
123. Security Centre
Route: /admin/security
Display:
Security events.
Suspicious access.
Credential status.
Device security.
MFA adoption.
API abuse indicators.
Incident records.
124. System Monitoring
Route: /admin/monitoring
Display:
API health.
Database health.
Redis.
MQTT.
Worker queues.
Object storage.
Background jobs.
External provider health.
125. Billing and Subscription
Route: /settings/billing
Features:
Current plan.
Usage.
Subscription status.
Invoices.
Payment history.
Plan changes.
Cancellation.
Financial data must be accessible only to authorised roles.
126. Personal Settings
Route: /settings/profile
Sections:
Profile.
Email.
Phone.
Password.
MFA.
Language.
Timezone.
Notifications.
Sessions.
Privacy preferences.
Data export and account requests.

PART V — CROSS-PAGE INTERACTION SPECIFICATIONS
6. Primary user journeys
Journey A: Farmer creates and manages a farm
Register.
Verify account.
Create or join organisation.
Create farm.
Draw farm boundary.
Create fields.
Assign crops.
Add team members.
Open dashboard.
Begin recording observations and activities.
Completion condition: the farmer can access the farm and its authorised records.
Journey B: Connect an IoT device
Open Devices.
Register device.
Associate farm and field.
Provision device.
Configure sensors.
Verify telemetry.
View measurement history.
Monitor connectivity.
Completion condition: valid observations are associated with the correct farm, field and device.
Journey C: Respond to a low-moisture alert
Receive alert.
Open alert details.
Review soil-moisture reading.
Check reading freshness and sensor quality.
Review field and weather context.
Inspect recommendation.
Accept, reject or defer.
Create irrigation plan if appropriate.
Approve operation.
Verify device execution.
Record outcome.
Journey D: Work offline
Open mobile application.
Load previously synchronised farm data.
Record field observation.
Capture photograph.
Create or update a permitted task.
Save locally.
Display pending-sync state.
Reconnect.
Synchronise.
Resolve conflicts if necessary.
Journey E: Research agricultural data
Open Research Workspace.
Find dataset.
Review licence.
Request access if required.
Inspect schema.
Filter data.
Run analysis.
Evaluate output.
Export authorised results.
Journey F: Manage an organisation
Open organisation dashboard.
Review farms.
Invite member.
Assign role.
Grant farm-level access.
Review activity.
Generate report.

PART VI — INTERACTION STATES AND ERROR HANDLING
7. Mandatory page states
Every page must define the states that apply to it.
7.1 Loading
Skeletons for major content.
No unnecessary blocking of unrelated page areas.
Loading indicators for long-running actions.
Preserve previously loaded information when safe.
7.2 Empty
Examples:
No farms created.
No measurements received.
No alerts.
No datasets.
No tasks assigned.
Every empty state should explain what the user can do next.
7.3 Partial data
Examples:
Device exists but has no telemetry.
Field exists but has no crop assignment.
Forecast exists but historical observations are missing.
Show what is available and what is missing.
7.4 Stale data
Every time-sensitive measurement must communicate its observation time and freshness.
A stale sensor reading must not be presented as current.
7.5 Offline
Show:
Offline indicator.
Last successful sync.
Locally available records.
Pending operations.
Blocked operations.
Retry status.
7.6 Permission denied
Explain that access is unavailable without revealing restricted data.
Provide a route to request access where appropriate.
7.7 Validation errors
Identify the invalid field.
Explain the required correction.
Preserve valid entered values.
Do not silently discard the form.
7.8 Server errors
Provide a useful error reference.
Preserve recoverable work.
Offer retry where safe.
Avoid displaying internal stack traces.
7.9 Conflict
Display:
Client version.
Server version.
Conflict reason.
Available resolution.
Audit information.
Never resolve high-impact irrigation or physical-control conflicts through silent last-write-wins behaviour.
7.10 Deleted or unavailable records
Show a clear unavailable state and a safe return path.

PART VII — ROLE-BASED EXPERIENCE
8. Role-based navigation
Farmer
Primary:
Dashboard.
Farms.
Fields.
Monitoring.
Tasks.
Irrigation.
Recommendations.
Farm manager
Primary:
Dashboard.
Farms.
Operations.
Equipment.
Inventory.
Monitoring.
Reports.
Agronomist
Primary:
Assigned farms.
Field observations.
Crop health.
Soil intelligence.
Recommendations.
Reports.
Extension officer
Primary:
Assigned farmers.
Field visits.
Observations.
Tasks.
Community reports.
Researcher
Primary:
Datasets.
Data sources.
Data quality.
Analysis.
Models.
Research reports.
Cooperative manager
Primary:
Organisation dashboard.
Farms.
Members.
Operations.
Analytics.
Reports.
Service provider
Primary:
Clients.
Assigned work.
Equipment.
Maintenance.
Service records.
Platform administrator
Primary:
Tenants.
Users.
Permissions.
Audit.
Security.
System monitoring.
Configuration.
Permissions must still be checked on the backend. Hiding a menu item is not an authorisation mechanism.

PART VIII — ACCESSIBILITY AND RESPONSIVE QUALITY
9. Accessibility requirements
Target WCAG 2.2 AA where applicable.
Requirements:
Keyboard navigation.
Visible focus.
Accessible labels.
Screen-reader-friendly forms.
Colour contrast.
Text resizing.
Accessible error messages.
Alternatives to colour-only statuses.
Accessible chart summaries.
Captions and descriptions for relevant media.
Large touch targets.
Maps and charts must provide an alternative structured representation for users who cannot interpret the visualisation.
10. Responsive testing matrix
Test:
Small mobile: 320–374 px.
Standard mobile: 375–430 px.
Large mobile: 431–767 px.
Tablet: 768–1023 px.
Small desktop: 1024–1279 px.
Standard desktop: 1280–1535 px.
Large desktop: 1536 px and above.
Important pages requiring additional testing:
Farm map.
Measurements explorer.
Device details.
Irrigation control.
Report builder.
Research workspace.
Administration monitoring.

PART IX — DESIGN AND IMPLEMENTATION HANDOFF
11. Proposed frontend architecture
web/
├── src/
│   ├── app/
│   │   ├── routes/
│   │   ├── providers/
│   │   ├── layouts/
│   │   └── navigation/
│   │
│   ├── design-system/
│   │   ├── tokens/
│   │   ├── typography/
│   │   ├── components/
│   │   └── patterns/
│   │
│   ├── modules/
│   │   ├── dashboard/
│   │   ├── farms/
│   │   ├── fields/
│   │   ├── crops/
│   │   ├── devices/
│   │   ├── data/
│   │   ├── monitoring/
│   │   ├── operations/
│   │   ├── irrigation/
│   │   ├── intelligence/
│   │   ├── collaboration/
│   │   ├── integrations/
│   │   ├── reports/
│   │   └── administration/
│   │
│   ├── services/
│   ├── hooks/
│   ├── stores/
│   ├── utilities/
│   └── assets/
│
└── tests/
12. Proposed frontend implementation tools
React.
Vite.
React Router.
Tailwind CSS.
Accessible component primitives.
TanStack Query for server-state management.
Zustand or another lightweight state-management solution where justified.
React Hook Form.
Zod.
MapLibre GL JS.
Recharts or another appropriate charting library.
Playwright.
Vitest and React Testing Library.
The final library choices must be reviewed against the required map, chart, accessibility and offline workflows.
13. Design file and component organisation
Recommended design-system organisation:
TerraNexus Design System
│
├── Foundations
│   ├── Colour
│   ├── Typography
│   ├── Spacing
│   ├── Grid
│   └── Elevation
│
├── Components
│   ├── Buttons
│   ├── Inputs
│   ├── Selects
│   ├── Tables
│   ├── Cards
│   ├── Dialogs
│   ├── Navigation
│   ├── Badges
│   └── Charts
│
├── Patterns
│   ├── Data tables
│   ├── Farm maps
│   ├── Device panels
│   ├── Irrigation control
│   ├── Recommendations
│   ├── Offline sync
│   └── Forms
│
└── Templates
    ├── Dashboard
    ├── List
    ├── Detail
    ├── Create
    ├── Edit
    ├── Analytics
    └── Administration

PART X — PAGE ACCEPTANCE CRITERIA
14. Every page must have
A defined purpose.
A defined route.
A defined user role.
A defined permission requirement.
A defined data source.
A defined page layout.
A defined primary action.
A defined secondary action.
Defined navigation behaviour.
Responsive behaviour.
Validation behaviour.
Loading state.
Empty state.
Error state.
Offline behaviour where applicable.
Accessibility requirements.
Test cases.
15. Cross-platform acceptance
The web and mobile interfaces must share:
Terminology.
Domain concepts.
Permission semantics.
Status definitions.
Data-quality definitions.
Workflow rules.
API contracts.
They do not need identical layouts.
Mobile should prioritise field work, observation capture, task completion and offline operation. Web should support richer management, data exploration, maps, reporting and administration.
16. Definition of done for a page
A page is complete only when:
The screen design is approved.
All data dependencies are identified.
All permissions are mapped.
All interactions are defined.
All states are designed.
Mobile behaviour is specified.
Accessibility is reviewed.
API dependencies are documented.
Test cases exist.
Acceptance criteria pass.

PART XI — DESIGN APPROVAL AND REMAINING WORK
17. Design decisions established
TerraNexus is the product identity.
The interface uses a calm agricultural technology aesthetic.
The design supports multiple user roles.
Desktop and mobile are separate experiences over shared workflows.
Maps, data quality and provenance are first-class UI elements.
Irrigation control receives stronger safety treatment.
AI recommendations are evidence-based and reviewable.
Offline states are visible.
The 126-page inventory remains the master page catalogue.
18. Work not yet completed
This document is a complete page-level functional and structural design baseline, not a claim that all 126 pages have been visually rendered.
The following remain separate design-production tasks:
High-fidelity desktop visual screens.
High-fidelity mobile visual screens.
Interactive prototypes.
Final responsive component measurements.
Detailed map and chart visual specifications.
Design-system component library implementation.
Accessibility testing.
Usability testing with representative users.
Final visual sign-off.
The next design-production stage should use representative screen families before creating every visual variant.
Suggested first visual prototypes:
Farmer dashboard.
Farm overview and map.
Field overview.
Live monitoring.
Device details.
Measurements explorer.
Irrigation control.
Recommendation details.
Mobile field observation.
Research workspace.
These ten screens establish the most important visual patterns for the rest of the product.
19. Handoff to the next engineering document
Next document: TNX-API-001 — Complete API and Device Specification.
It must align with all three established design documents and define:
API architecture and versioning.
Authentication and authorisation contracts.
Complete endpoint catalogue.
Request and response schemas.
Error model.
Pagination and filtering.
Tenant enforcement.
Farm and field contracts.
Device provisioning.
MQTT topic specification.
Telemetry schemas.
Measurement ingestion.
Command lifecycle.
Irrigation safety interfaces.
Offline synchronisation.
File upload and export.
Integration and webhook contracts.
Rate limits and idempotency.
API security.
Testing and acceptance criteria.
TNX-UI-001 status: The 126-page information architecture, functional page specifications, shared design system, interaction patterns, user journeys and responsive behaviour are established as the proposed design baseline. High-fidelity visual production and user validation remain outstanding.
The most important design decision
TerraNexus should not have one universal dashboard with dozens of widgets. It should have a shared design system with different workspaces, built around the same underlying farm and data records.
For example, the same soil-moisture measurement should be presented differently:
A farmer sees whether the field needs attention.
An agronomist sees the reading, crop context and supporting evidence.
A researcher sees the time series, quality status and source metadata.
An administrator sees ingestion and device-health information.
That is how the platform can serve different users without duplicating its underlying data.
Next document: TNX-API-001 — Complete API and Device Specification, including exact endpoint contracts, telemetry schemas, MQTT topics, command execution, safety rules and offline synchronisation.
Next document: TNX-API-001 — Complete API and Device Specification, including exact endpoint contracts, telemetry schemas, MQTT topics, command execution, safety rules and offline synchronisation. and everything else left out
