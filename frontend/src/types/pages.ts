export interface PageDef {
  id: string;
  number: string;
  name: string;
  route: string;
  group: string;
  category: string;
  description: string;
  primaryActions: string[];
}

export const ALL_126_PAGES: PageDef[] = [
  // Group A - Public Pages
  { id: "p001", number: "001", name: "Home", route: "/", group: "A", category: "Public", description: "Public landing page, value proposition, and platform entry point.", primaryActions: ["Explore Platform", "Create Account", "Sign In"] },
  { id: "p002", number: "002", name: "About", route: "/about", group: "A", category: "Public", description: "Mission, vision, agricultural data philosophy, and interoperability.", primaryActions: ["Contact Team", "Explore Platform"] },
  { id: "p003", number: "003", name: "Platform Overview", route: "/platform", group: "A", category: "Public", description: "System architecture: Connect, Understand, Decide, Act, Learn.", primaryActions: ["View Architecture", "Try Demo"] },
  { id: "p004", number: "004", name: "Solutions", route: "/solutions", group: "A", category: "Public", description: "Solutions for smallholders, commercial farms, agronomists, and researchers.", primaryActions: ["Filter by Persona", "Request Assessment"] },
  { id: "p005", number: "005", name: "Integrations", route: "/integrations", group: "A", category: "Public", description: "Provider catalogue: Open-Meteo, Copernicus, LoRaWAN, John Deere.", primaryActions: ["Request Connector", "View Protocol Docs"] },
  { id: "p006", number: "006", name: "Documentation", route: "/docs", group: "A", category: "Public", description: "Developer and user guides, API references, and hardware tutorials.", primaryActions: ["Search Docs", "Download SDK"] },
  { id: "p007", number: "007", name: "Contact", route: "/contact", group: "A", category: "Public", description: "Contact, pilot inquiry, and agricultural collaboration forms.", primaryActions: ["Send Message"] },
  { id: "p008", number: "008", name: "Legal & Privacy", route: "/legal", group: "A", category: "Public", description: "Data ownership policies, open source licenses, and terms.", primaryActions: ["Review Terms", "Download Data Agreement"] },

  // Group B - Auth & Onboarding
  { id: "p009", number: "009", name: "Registration", route: "/register", group: "B", category: "Auth", description: "Account creation with email, phone, and organisation profile.", primaryActions: ["Submit Registration"] },
  { id: "p010", number: "010", name: "Login", route: "/login", group: "B", category: "Auth", description: "Secure authentication with JWT, MFA, and SSO options.", primaryActions: ["Log In", "Use Single Sign-On"] },
  { id: "p011", number: "011", name: "Email Verification", route: "/verify-email", group: "B", category: "Auth", description: "Verify account email address and security token.", primaryActions: ["Resend Code", "Verify"] },
  { id: "p012", number: "012", name: "Password Recovery", route: "/forgot-password", group: "B", category: "Auth", description: "Self-service credential recovery and reset link dispatch.", primaryActions: ["Send Recovery Link"] },
  { id: "p013", number: "013", name: "MFA Setup", route: "/security/mfa", group: "B", category: "Auth", description: "Time-based one-time password (TOTP) authenticator setup.", primaryActions: ["Scan QR Code", "Confirm Token"] },
  { id: "p014", number: "014", name: "User Onboarding", route: "/onboarding", group: "B", category: "Auth", description: "Initial role selection, language preference, and metric defaults.", primaryActions: ["Complete Profile"] },
  { id: "p015", number: "015", name: "Organisation Setup", route: "/onboarding/organisation", group: "B", category: "Auth", description: "Tenant creation, legal identity, and member invitations.", primaryActions: ["Save Organisation"] },
  { id: "p016", number: "016", name: "Workspace Setup", route: "/onboarding/workspace", group: "B", category: "Auth", description: "Initial farm configuration and module toggles.", primaryActions: ["Launch Workspace"] },

  // Group C - Core Farm & Agronomy
  { id: "p017", number: "017", name: "Main Dashboard", route: "/dashboard", group: "C", category: "Farm Operations", description: "Primary command centre: farm status, weather, alerts, and quick actions.", primaryActions: ["Trigger Irrigation", "View Active Alerts", "Add Field"] },
  { id: "p018", number: "018", name: "Global Search", route: "/search", group: "C", category: "Platform", description: "Fast full-text cross-entity search across farms, sensors, tasks, and crops.", primaryActions: ["Filter by Entity", "Export Results"] },
  { id: "p019", number: "019", name: "Notifications Centre", route: "/notifications", group: "C", category: "Platform", description: "In-app notification inbox, alert escalations, and system updates.", primaryActions: ["Mark All Read", "Configure Channels"] },
  { id: "p020", number: "020", name: "Activity Feed", route: "/activity", group: "C", category: "Platform", description: "Chronological operational activity stream across all farm workers.", primaryActions: ["Filter by User", "Date Range"] },
  { id: "p021", number: "021", name: "Help & Support", route: "/help", group: "C", category: "Support", description: "Agronomic support knowledgebase, device troubleshooting, and tickets.", primaryActions: ["Open Ticket", "Browse FAQs"] },
  { id: "p022", number: "022", name: "Farms List", route: "/farms", group: "C", category: "Farms", description: "List of all farms in the organisation with area, location, and health.", primaryActions: ["Add Farm", "Export Farm List"] },
  { id: "p023", number: "023", name: "Create Farm", route: "/farms/new", group: "C", category: "Farms", description: "Boundary polygon upload (GeoJSON/KML), timezone, and metadata.", primaryActions: ["Draw Boundary", "Save Farm"] },
  { id: "p024", number: "024", name: "Farm Overview", route: "/farms/:farmId", group: "C", category: "Farms", description: "Deep dive into a specific farm: fields, weather, soil, active crop blocks.", primaryActions: ["Edit Farm", "View Map", "Add Field"] },
  { id: "p025", number: "025", name: "Edit Farm", route: "/farms/:farmId/edit", group: "C", category: "Farms", description: "Update farm details, boundaries, coordinates, and operational settings.", primaryActions: ["Save Changes", "Archive Farm"] },
  { id: "p026", number: "026", name: "Farm Map", route: "/farms/:farmId/map", group: "C", category: "Farms", description: "Interactive GIS map with PostGIS boundary overlays and sensor pins.", primaryActions: ["Toggle Layers", "Filter Sensors"] },
  { id: "p027", number: "027", name: "Fields List", route: "/fields", group: "C", category: "Fields", description: "Catalogue of management fields with crop planting status and soil types.", primaryActions: ["Add Field", "Filter by Crop"] },
  { id: "p028", number: "028", name: "Create Field", route: "/fields/new", group: "C", category: "Fields", description: "Create a new field plot with boundary polygons and soil profiles.", primaryActions: ["Save Field"] },
  { id: "p029", number: "029", name: "Field Overview", route: "/fields/:fieldId", group: "C", category: "Fields", description: "Field health score, crop stage, current soil moisture, and active tasks.", primaryActions: ["Log Observation", "Assign Crop"] },
  { id: "p030", number: "030", name: "Field History", route: "/fields/:fieldId/history", group: "C", category: "Fields", description: "Historical crop rotations, past yields, fertilizer inputs, and soil trends.", primaryActions: ["Export History"] },
  { id: "p031", number: "031", name: "Field Observations", route: "/fields/:fieldId/observations", group: "C", category: "Fields", description: "In-field scouting observations with photo evidence and severity tags.", primaryActions: ["Log New Observation"] },
  { id: "p032", number: "032", name: "Crop Catalogue", route: "/crops", group: "C", category: "Agronomy", description: "Database of agricultural crops, optimal pH, temperatures, and water needs.", primaryActions: ["Add Custom Crop", "Browse Varieties"] },
  { id: "p033", number: "033", name: "Crop Details", route: "/crops/:cropId", group: "C", category: "Agronomy", description: "Crop growth stages, FAO-56 Kc factors, and pest vulnerability matrix.", primaryActions: ["Edit Crop", "View Varieties"] },
  { id: "p034", number: "034", name: "Assign Crop", route: "/fields/:fieldId/crops/new", group: "C", category: "Agronomy", description: "Planting registration: variety, planting date, expected harvest date.", primaryActions: ["Record Planting"] },
  { id: "p035", number: "035", name: "Growing Seasons", route: "/seasons", group: "C", category: "Agronomy", description: "Season calendar management: planned, active, and completed seasons.", primaryActions: ["Create Season"] },
  { id: "p036", number: "036", name: "Crop Calendar", route: "/crops/calendar", group: "C", category: "Agronomy", description: "Visual timeline of planting, vegetative, flowering, and harvest windows.", primaryActions: ["Filter by Field"] },
  { id: "p037", number: "037", name: "Crop Health", route: "/crop-health", group: "C", category: "Agronomy", description: "Canopy health, NDVI satellite index, stress indices, and disease risk.", primaryActions: ["Run Health Scan"] },

  // Group D - Devices & Sensors
  { id: "p038", number: "038", name: "Devices Overview", route: "/devices", group: "D", category: "Devices", description: "Registry of all edge devices, ESP32 nodes, gateways, and connection states.", primaryActions: ["Register Device", "Provision Device"] },
  { id: "p039", number: "039", name: "Register Device", route: "/devices/new", group: "D", category: "Devices", description: "Pair new hardware via MAC address / UID and assign to field.", primaryActions: ["Save Device"] },
  { id: "p040", number: "040", name: "Device Details", route: "/devices/:deviceId", group: "D", category: "Devices", description: "Battery level, signal RSSI, attached sensors, and live telemetry log.", primaryActions: ["Send Command", "Edit Config"] },
  { id: "p041", number: "041", name: "Device Provisioning", route: "/devices/:deviceId/provision", group: "D", category: "Devices", description: "Provisioning tokens, MQTT topics, and WiFi credential generator.", primaryActions: ["Generate Token", "Download Config"] },
  { id: "p042", number: "042", name: "Sensor Registry", route: "/sensors", group: "D", category: "Devices", description: "Individual sensor channels: soil moisture, temperature, humidity, flow.", primaryActions: ["Calibrate Sensor"] },
  { id: "p043", number: "043", name: "Sensor Details", route: "/sensors/:sensorId", group: "D", category: "Devices", description: "Sensor calibration curves, depth placement (10cm/30cm), and quality stats.", primaryActions: ["Update Calibration"] },
  { id: "p044", number: "044", name: "Device Configuration", route: "/devices/:deviceId/configuration", group: "D", category: "Devices", description: "Sampling frequency, sleep intervals, and reporting thresholds.", primaryActions: ["Push Configuration"] },
  { id: "p045", number: "045", name: "Device Commands", route: "/devices/:deviceId/commands", group: "D", category: "Devices", description: "Durable command dispatch state machine, acknowledgements, and audit.", primaryActions: ["Issue Turn On/Off", "Ping Device"] },
  { id: "p046", number: "046", name: "Device Events", route: "/devices/:deviceId/events", group: "D", category: "Devices", description: "Hardware event log: boot events, brownouts, watchdog trips, reconnects.", primaryActions: ["Filter Events"] },
  { id: "p047", number: "047", name: "Firmware Management", route: "/devices/firmware", group: "D", category: "Devices", description: "Firmware release catalogue, SHA-256 binary validation, and OTA deployment.", primaryActions: ["Upload Firmware", "Trigger OTA"] },

  // Group E - Telemetry & Data Explorer
  { id: "p048", number: "048", name: "Data Overview", route: "/data", group: "E", category: "Data Platform", description: "Data ingestion throughput, storage volume, and freshness metrics.", primaryActions: ["Open Explorer", "Export Data"] },
  { id: "p049", number: "049", name: "Measurements Explorer", route: "/data/measurements", group: "E", category: "Data Platform", description: "Interactive time-series charting of soil, climate, and water measurements.", primaryActions: ["Filter by Metric", "Compare Depths", "Export CSV"] },
  { id: "p050", number: "050", name: "Measurement Details", route: "/data/measurements/:measurementId", group: "E", category: "Data Platform", description: "Raw measurement envelope, quality score, device provenance, and flags.", primaryActions: ["Flag Anomaly"] },
  { id: "p051", number: "051", name: "Data Sources", route: "/data/sources", group: "E", category: "Data Platform", description: "Registered data sources: on-farm sensors, satellites, weather stations.", primaryActions: ["Add Source"] },
  { id: "p052", number: "052", name: "Dataset Catalogue", route: "/datasets", group: "E", category: "Data Platform", description: "Standard agricultural datasets for agronomic modeling and benchmark research.", primaryActions: ["Download Dataset"] },
  { id: "p053", number: "053", name: "Dataset Details", route: "/datasets/:datasetId", group: "E", category: "Data Platform", description: "Dataset versions, spatial coverage, license, and schema definition.", primaryActions: ["Download Version"] },
  { id: "p054", number: "054", name: "Data Import", route: "/data/import", group: "E", category: "Data Platform", description: "Import CSV, GeoJSON, or lab soil analysis sheets into the platform.", primaryActions: ["Upload File", "Validate Schema"] },
  { id: "p055", number: "055", name: "Data Export", route: "/data/export", group: "E", category: "Data Platform", description: "Export historical measurements, task records, and yield summaries.", primaryActions: ["Generate Export"] },
  { id: "p056", number: "056", name: "Data Quality", route: "/data/quality", group: "E", category: "Data Platform", description: "Data quality assessment rules: range checks, frozen sensor detection.", primaryActions: ["Run Audit"] },
  { id: "p057", number: "057", name: "Data Processing Jobs", route: "/data/jobs", group: "E", category: "Data Platform", description: "Batch aggregation jobs, daily ET0 summaries, and statistical rollups.", primaryActions: ["Trigger Aggregation"] },

  // Group F - Live Monitoring & Alerts
  { id: "p058", number: "058", name: "Live Monitoring", route: "/monitoring/live", group: "F", category: "Monitoring", description: "Real-time telemetry stream from online sensors with live indicator dials.", primaryActions: ["Select Field", "Pause Stream"] },
  { id: "p059", number: "059", name: "Monitoring Charts", route: "/monitoring/charts", group: "F", category: "Monitoring", description: "Multi-parameter comparative plots: temperature vs soil moisture dynamics.", primaryActions: ["Add Curve", "Zoom Timeframe"] },
  { id: "p060", number: "060", name: "Alerts Overview", route: "/alerts", group: "F", category: "Monitoring", description: "Active agricultural alerts: moisture deficiency, frost warning, sensor offline.", primaryActions: ["Acknowledge Alert", "Resolve Alert"] },
  { id: "p061", number: "061", name: "Alert Details", route: "/alerts/:alertId", group: "F", category: "Monitoring", description: "Root cause analysis, sensor reading at trigger time, and action checklist.", primaryActions: ["Mark Resolved", "Assign Action"] },
  { id: "p062", number: "062", name: "Alert Rules", route: "/alerts/rules", group: "F", category: "Monitoring", description: "Customizable alert thresholds, cooldown periods, and notification channels.", primaryActions: ["Create Alert Rule"] },
  { id: "p063", number: "063", name: "Notification Preferences", route: "/settings/notifications", group: "F", category: "Monitoring", description: "Configure in-app, SMS, email, and push dispatch for each alert severity.", primaryActions: ["Save Preferences"] },

  // Group G - Farm Operations
  { id: "p064", number: "064", name: "Operations Overview", route: "/operations", group: "G", category: "Operations", description: "Daily farm work overview: active tasks, machine deployment, input usage.", primaryActions: ["Create Task", "Log Activity"] },
  { id: "p065", number: "065", name: "Task List", route: "/tasks", group: "G", category: "Operations", description: "Kanban and list view of farm tasks categorized by status and priority.", primaryActions: ["Add Task", "Filter by Worker"] },
  { id: "p066", number: "066", name: "Create Task", route: "/tasks/new", group: "G", category: "Operations", description: "Create work order with field assignment, due date, and worker assignment.", primaryActions: ["Save Task"] },
  { id: "p067", number: "067", name: "Task Details", route: "/tasks/:taskId", group: "G", category: "Operations", description: "Task description, attachments, progress comments, and completion stamp.", primaryActions: ["Mark In Progress", "Complete Task"] },
  { id: "p068", number: "068", name: "Operations Calendar", route: "/calendar", group: "G", category: "Operations", description: "Scheduled tasks, irrigation cycles, spray days, and expected harvests.", primaryActions: ["Add Event", "Toggle Schedule"] },
  { id: "p069", number: "069", name: "Activity Records", route: "/activities", group: "G", category: "Operations", description: "Historical log of completed farm activities for traceability certification.", primaryActions: ["Export Log"] },
  { id: "p070", number: "070", name: "Equipment Management", route: "/equipment", group: "G", category: "Operations", description: "Tractors, pumps, sprayers, operating hours, and maintenance schedules.", primaryActions: ["Register Equipment", "Log Service"] },
  { id: "p071", number: "071", name: "Inventory & Inputs", route: "/inventory", group: "G", category: "Operations", description: "Stock levels of seeds, fertilizers, pesticides, fuels, and reorder alerts.", primaryActions: ["Add Inventory Item", "Log Usage"] },
  { id: "p072", number: "072", name: "Field Inspections", route: "/inspections", group: "G", category: "Operations", description: "Formal agronomist scouting and quality audit inspection reports.", primaryActions: ["Schedule Inspection"] },
  { id: "p073", number: "073", name: "Harvest Records", route: "/harvest", group: "G", category: "Operations", description: "Recorded crop yields, grade quality, batch numbers, and storage bins.", primaryActions: ["Log Harvest"] },

  // Group H - Irrigation & Water Management
  { id: "p074", number: "074", name: "Irrigation Overview", route: "/irrigation", group: "H", category: "Irrigation", description: "Irrigation system command centre: water reserve, active pumps, schedules.", primaryActions: ["Open Control Rig", "Create Plan"] },
  { id: "p075", number: "075", name: "Irrigation Zones", route: "/irrigation/zones", group: "H", category: "Irrigation", description: "Management zones with driplines, solenoid channels, and target moisture.", primaryActions: ["Add Zone", "Configure Valves"] },
  { id: "p076", number: "076", name: "Create Irrigation Plan", route: "/irrigation/plans/new", group: "H", category: "Irrigation", description: "Multi-step automated watering sequence with volume and duration caps.", primaryActions: ["Save Plan"] },
  { id: "p077", number: "077", name: "Irrigation Plan Details", route: "/irrigation/plans/:planId", group: "H", category: "Irrigation", description: "Plan steps, fertigation recipes, approval status, and trigger rules.", primaryActions: ["Activate Plan", "Execute Sequence"] },
  { id: "p078", number: "078", name: "Irrigation Schedule", route: "/irrigation/schedule", group: "H", category: "Irrigation", description: "Timeline of automated irrigation cycles and weather-based delays.", primaryActions: ["Pause Automation"] },
  { id: "p079", number: "079", name: "Irrigation Control Rig", route: "/irrigation/control", group: "H", category: "Irrigation", description: "Physical control rig with safety preflight checks, pump interlocks, and E-Stop.", primaryActions: ["Start Irrigation", "EMERGENCY STOP", "Cutoff Valve"] },
  { id: "p080", number: "080", name: "Irrigation History", route: "/irrigation/history", group: "H", category: "Irrigation", description: "Historical execution logs, actual duration, water volume, and soil response.", primaryActions: ["Audit Events"] },
  { id: "p081", number: "081", name: "Water Management", route: "/water-management", group: "H", category: "Irrigation", description: "Reservoirs, boreholes, rainfall catchment levels, and water budget.", primaryActions: ["Update Tank Level"] },

  // Group I - Agricultural Intelligence & AI
  { id: "p082", number: "082", name: "Intelligence Overview", route: "/intelligence", group: "I", category: "Intelligence", description: "AI engine summary: active recommendations, model accuracy, weather outlook.", primaryActions: ["Review Recommendations", "Ask Assistant"] },
  { id: "p083", number: "083", name: "Recommendations", route: "/recommendations", group: "I", category: "Intelligence", description: "Evidence-backed agronomic recommendations: irrigation, nutrition, spraying.", primaryActions: ["Accept Action", "Reject with Feedback"] },
  { id: "p084", number: "084", name: "Recommendation Details", route: "/recommendations/:recommendationId", group: "I", category: "Intelligence", description: "Deep evidence breakdown: sensor readings, weather, crop stage, and rationale.", primaryActions: ["Execute Proposed Action"] },
  { id: "p085", number: "085", name: "Weather Intelligence", route: "/intelligence/weather", group: "I", category: "Intelligence", description: "Microclimate forecasts, Penman-Monteith ET0, precipitation probability.", primaryActions: ["Refresh Forecast"] },
  { id: "p086", number: "086", name: "Soil Intelligence", route: "/intelligence/soil", group: "I", category: "Intelligence", description: "Soil moisture depletion analysis, field capacity, permanent wilting point.", primaryActions: ["Analyze Deficit"] },
  { id: "p087", number: "087", name: "Crop Intelligence", route: "/intelligence/crops", group: "I", category: "Intelligence", description: "Growth stage tracking, thermal unit accumulation (GDD), and harvest window.", primaryActions: ["Update Growth Stage"] },
  { id: "p088", number: "088", name: "Predictive Analytics", route: "/intelligence/predictions", group: "I", category: "Intelligence", description: "Yield forecast models, drought risk projections, and water consumption trends.", primaryActions: ["Run Simulation"] },
  { id: "p089", number: "089", name: "Model Registry", route: "/intelligence/models", group: "I", category: "Intelligence", description: "Governed agronomic models: FAO-56 Evapotranspiration, Scikit-learn, QVAC.", primaryActions: ["Register Model", "Inspect Metrics"] },
  { id: "p090", number: "090", name: "Model Execution History", route: "/intelligence/model-runs", group: "I", category: "Intelligence", description: "Audit trail of every AI model inference run, input features, and outcomes.", primaryActions: ["View Input Features"] },
  { id: "p091", number: "091", name: "AI Assistant Workspace", route: "/intelligence/assistant", group: "I", category: "Intelligence", description: "Interactive conversational agronomist with farm context memory.", primaryActions: ["Ask Farm Question", "Draft Plan"] },
  { id: "p092", number: "092", name: "Local Intelligence (QVAC)", route: "/intelligence/local", group: "I", category: "Intelligence", description: "Local edge AI inference settings, QVAC quantized model host, and offline mode.", primaryActions: ["Test Local Model", "Update Weights"] },

  // Group J - Workspaces & Collaboration
  { id: "p093", number: "093", name: "Organisation Dashboard", route: "/organisation", group: "J", category: "Organisation", description: "High-level tenant view: aggregate hectares, total output, team allocation.", primaryActions: ["Manage Members"] },
  { id: "p094", number: "094", name: "Team Members", route: "/organisation/members", group: "J", category: "Organisation", description: "Invite workers, assign roles (Owner, Agronomist, Operator), and permissions.", primaryActions: ["Invite Member"] },
  { id: "p095", number: "095", name: "Organisation Analytics", route: "/organisation/analytics", group: "J", category: "Organisation", description: "Productivity metrics, water conservation benchmarks, and resource cost.", primaryActions: ["Export Analytics"] },
  { id: "p096", number: "096", name: "Agronomist Workspace", route: "/workspace/agronomy", group: "J", category: "Workspaces", description: "Specialized view for agronomists: crop scouting, soil chemistry, recipes.", primaryActions: ["Issue Prescription"] },
  { id: "p097", number: "097", name: "Extension Workspace", route: "/workspace/extension", group: "J", category: "Workspaces", description: "Farmer advisory tools, regional guidance leaflets, and survey collection.", primaryActions: ["Broadcast Advisory"] },
  { id: "p098", number: "098", name: "Research Workspace", route: "/workspace/research", group: "J", category: "Workspaces", description: "Scientific field trials, randomized control plots, and dataset export.", primaryActions: ["Create Trial Plot"] },
  { id: "p099", number: "099", name: "Collaboration & Comments", route: "/collaboration", group: "J", category: "Workspaces", description: "Threaded discussions on field observations, tasks, and recommendations.", primaryActions: ["Post Comment"] },
  { id: "p100", number: "100", name: "Service Provider Workspace", route: "/workspace/providers", group: "J", category: "Workspaces", description: "Tractor hire, drone spraying, and contract harvesting provider interface.", primaryActions: ["Accept Job"] },

  // Group K - Developer & Integrations
  { id: "p101", number: "101", name: "Integration Catalogue", route: "/developer/integrations", group: "K", category: "Developer", description: "Catalogue of certified connectors: weather, satellite, LoRaWAN, agentic finance.", primaryActions: ["Configure Connector"] },
  { id: "p102", number: "102", name: "Integration Details", route: "/developer/integrations/:providerId", group: "K", category: "Developer", description: "Provider specs, authentication protocol, rate limits, and supported topics.", primaryActions: ["Test Connection"] },
  { id: "p103", number: "103", name: "Configure Integration", route: "/developer/integrations/configure/:providerId", group: "K", category: "Developer", description: "Manage API keys, OAuth tokens, and sync schedule for external providers.", primaryActions: ["Save Credentials"] },
  { id: "p104", number: "104", name: "API Keys", route: "/developer/api-keys", group: "K", category: "Developer", description: "Generate scoped API keys (X-TNX-API-KEY) for custom scripts and agents.", primaryActions: ["Create API Key"] },
  { id: "p105", number: "105", name: "Webhooks", route: "/developer/webhooks", group: "K", category: "Developer", description: "Configure HTTP POST webhooks for real-time telemetry and alert forwarding.", primaryActions: ["Add Webhook", "Test Payload"] },
  { id: "p106", number: "106", name: "Developer API Docs", route: "/developer/docs", group: "K", category: "Developer", description: "Interactive Swagger/OpenAPI documentation for all /api/v1 endpoints.", primaryActions: ["Explore OpenAPI"] },
  { id: "p107", number: "107", name: "Developer Applications", route: "/developer/applications", group: "K", category: "Developer", description: "Registered third-party apps, Tether WDK finance agents, and bot clients.", primaryActions: ["Register Application"] },
  { id: "p108", number: "108", name: "Integration Logs", route: "/developer/logs", group: "K", category: "Developer", description: "HTTP traffic logs, webhook delivery receipts, and sync error diagnostics.", primaryActions: ["Filter Errors"] },

  // Group L - Reporting & Platform Administration
  { id: "p109", number: "109", name: "Reports Overview", route: "/reports", group: "L", category: "Reports", description: "Executive summary reports for farm performance, water usage, and yield.", primaryActions: ["Generate Report"] },
  { id: "p110", number: "110", name: "Farm Report", route: "/reports/farm", group: "L", category: "Reports", description: "Comprehensive agricultural summary of fields, crops, and operations.", primaryActions: ["Download PDF"] },
  { id: "p111", number: "111", name: "Field Report", route: "/reports/field", group: "L", category: "Reports", description: "Plot-specific report with soil dynamics, harvest quality, and fertilizer ROI.", primaryActions: ["Export Sheet"] },
  { id: "p112", number: "112", name: "Irrigation Report", route: "/reports/irrigation", group: "L", category: "Reports", description: "Water resource audit, pumping energy consumption, and efficiency score.", primaryActions: ["Audit Water Balance"] },
  { id: "p113", number: "113", name: "Device Report", route: "/reports/devices", group: "L", category: "Reports", description: "Hardware uptime, battery degradation trends, and packet loss analysis.", primaryActions: ["Check Uptime"] },
  { id: "p114", number: "114", name: "Organisation Report", route: "/reports/organisation", group: "L", category: "Reports", description: "Multi-farm portfolio summary for agricultural cooperatives and enterprises.", primaryActions: ["Generate Portfolio Report"] },
  { id: "p115", number: "115", name: "Custom Report Builder", route: "/reports/builder", group: "L", category: "Reports", description: "Drag-and-drop report builder with custom parameters, metrics, and charts.", primaryActions: ["Save Template"] },
  { id: "p116", number: "116", name: "Scheduled Reports", route: "/reports/scheduled", group: "L", category: "Reports", description: "Automated weekly/monthly email dispatches of operational reports.", primaryActions: ["Schedule Dispatch"] },
  { id: "p117", number: "117", name: "Admin Dashboard", route: "/admin", group: "L", category: "Admin", description: "Platform engineering health: DB connections, MQTT broker, Redis, queues.", primaryActions: ["System Diagnostics"] },
  { id: "p118", number: "118", name: "Tenant Management", route: "/admin/tenants", group: "L", category: "Admin", description: "Super-admin tenant administration, quota enforcement, and isolation checks.", primaryActions: ["Provision Tenant"] },
  { id: "p119", number: "119", name: "User Administration", route: "/admin/users", group: "L", category: "Admin", description: "Super-admin view of all registered accounts, deactivation, and verification.", primaryActions: ["Manage User Status"] },
  { id: "p120", number: "120", name: "Permission Administration", route: "/admin/permissions", group: "L", category: "Admin", description: "Role-based access control (RBAC) matrices and fine-grained permissions.", primaryActions: ["Edit Role Policy"] },
  { id: "p121", number: "121", name: "Audit Logs", route: "/admin/audit", group: "L", category: "Admin", description: "Immutable security audit trail of all sensitive operations and control actions.", primaryActions: ["Filter Security Events"] },
  { id: "p122", number: "122", name: "System Configuration", route: "/admin/configuration", group: "L", category: "Admin", description: "Environment variables, broker settings, and system parameter flags.", primaryActions: ["Reload Configuration"] },
  { id: "p123", number: "123", name: "Security Centre", route: "/admin/security", group: "L", category: "Admin", description: "Threat monitoring, brute force detection, and certificate renewal status.", primaryActions: ["Run Security Audit"] },
  { id: "p124", number: "124", name: "System Monitoring", route: "/admin/monitoring", group: "L", category: "Admin", description: "CPU, memory, database latency, MQTT throughput, and API response SLOs.", primaryActions: ["Inspect Metrics"] },
  { id: "p125", number: "125", name: "Billing & Subscriptions", route: "/settings/billing", group: "L", category: "Admin", description: "Subscription plans, usage meters, storage tiers, and payment receipts.", primaryActions: ["Upgrade Plan"] },
  { id: "p126", number: "126", name: "Personal Settings", route: "/settings/profile", group: "L", category: "Admin", description: "User profile, preferred language, timezone, password change, and session list.", primaryActions: ["Save Profile", "Logout All Devices"] }
];
