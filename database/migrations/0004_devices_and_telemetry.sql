-- 0004_devices_and_telemetry.sql
-- IoT Gateways, Devices, Sensors, Actuator Commands, Firmware, and Time-Series Measurements
-- Aligned with TNX-DATA-001 Sections 8 & 9 and TNX-API-001 Sections 20-32

CREATE TABLE IF NOT EXISTS gateways (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    gateway_eui VARCHAR(64) UNIQUE,
    model VARCHAR(100),
    ip_address VARCHAR(45),
    connection_type VARCHAR(50) NOT NULL DEFAULT 'ethernet', -- ethernet, cellular, wifi, satellite
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'offline', 'maintenance', 'decommissioned')),
    last_seen_at TIMESTAMPTZ,
    configuration JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    gateway_id UUID REFERENCES gateways(id) ON DELETE SET NULL,
    device_uid VARCHAR(100) NOT NULL, -- e.g. "esp32-node-001" or MAC/EUI
    name VARCHAR(150) NOT NULL,
    device_type VARCHAR(50) NOT NULL, -- weather_station, soil_probe, irrigation_controller, relay_actuator, pump_monitor
    hardware_version VARCHAR(50) DEFAULT 'v1.0',
    firmware_version VARCHAR(50) DEFAULT '1.0.0',
    provisioning_status VARCHAR(30) NOT NULL DEFAULT 'unprovisioned' CHECK (provisioning_status IN ('unprovisioned', 'provisioned', 'active', 'quarantined', 'revoked')),
    connection_status VARCHAR(30) NOT NULL DEFAULT 'offline' CHECK (connection_status IN ('online', 'offline', 'intermittent', 'error')),
    auth_token_hash TEXT,
    mqtt_client_id VARCHAR(100),
    battery_level_pct NUMERIC(5,2),
    signal_strength_rssi INTEGER,
    coordinates geometry(Point, 4326),
    location_description TEXT,
    config JSONB DEFAULT '{}'::jsonb,
    last_telemetry_at TIMESTAMPTZ,
    last_heartbeat_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organisation_id, device_uid)
);

CREATE INDEX IF NOT EXISTS idx_devices_org_uid ON devices(organisation_id, device_uid);
CREATE INDEX IF NOT EXISTS idx_devices_farm ON devices(farm_id);
CREATE INDEX IF NOT EXISTS idx_devices_field ON devices(field_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(connection_status);

CREATE TABLE IF NOT EXISTS measurement_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL, -- soil_moisture, ambient_temp, relative_humidity, solar_radiation, wind_speed, rainfall, water_flow, battery_voltage
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- soil, atmospheric, crop, water, system
    canonical_unit VARCHAR(30) NOT NULL,
    min_physical_value NUMERIC(12,4),
    max_physical_value NUMERIC(12,4),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    sensor_index INTEGER NOT NULL DEFAULT 0, -- channel / index on device
    sensor_code VARCHAR(100) NOT NULL,
    measurement_type_code VARCHAR(50) NOT NULL REFERENCES measurement_types(code),
    depth_cm NUMERIC(6,2), -- for soil sensors, e.g. 10cm, 30cm, 60cm
    unit VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'calibrating', 'faulty', 'disabled')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (device_id, sensor_code)
);

CREATE INDEX IF NOT EXISTS idx_sensors_device ON sensors(device_id);

CREATE TABLE IF NOT EXISTS sensor_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    channel_name VARCHAR(50) NOT NULL,
    channel_index INTEGER NOT NULL,
    scale_factor NUMERIC(10,5) DEFAULT 1.0,
    offset_value NUMERIC(10,5) DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS calibration_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    calibrated_by UUID REFERENCES users(id),
    calibration_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    reference_value NUMERIC(14,4) NOT NULL,
    raw_reading NUMERIC(14,4) NOT NULL,
    calibration_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    certificate_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Core Measurements Table (time-partitioned or time-indexed for performance)
CREATE TABLE IF NOT EXISTS measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    sensor_id UUID REFERENCES sensors(id) ON DELETE SET NULL,
    measurement_type VARCHAR(50) NOT NULL REFERENCES measurement_types(code),
    value NUMERIC(14,4) NOT NULL,
    unit VARCHAR(30) NOT NULL,
    depth_cm NUMERIC(6,2),
    observed_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    quality_score NUMERIC(3,2) DEFAULT 1.00 CHECK (quality_score BETWEEN 0.00 AND 1.00),
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    validation_flags JSONB DEFAULT '[]'::jsonb,
    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_measurements_type_time ON measurements(measurement_type, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_measurements_field_time ON measurements(field_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_measurements_device_time ON measurements(device_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_measurements_org_time ON measurements(organisation_id, observed_at DESC);

CREATE TABLE IF NOT EXISTS measurement_quality_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    measurement_id UUID NOT NULL REFERENCES measurements(id) ON DELETE CASCADE,
    rule_name VARCHAR(100) NOT NULL,
    check_status VARCHAR(20) NOT NULL CHECK (check_status IN ('passed', 'suspect', 'rejected')),
    details TEXT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS measurement_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    measurement_id UUID NOT NULL REFERENCES measurements(id) ON DELETE CASCADE,
    original_value NUMERIC(14,4) NOT NULL,
    corrected_value NUMERIC(14,4) NOT NULL,
    reason TEXT NOT NULL,
    corrected_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS device_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- boot, disconnect, battery_low, sensor_fault, tamper, ota_start, ota_finish
    severity VARCHAR(20) NOT NULL DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    payload JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_device_events_device ON device_events(device_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS device_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    command_type VARCHAR(50) NOT NULL, -- turn_on, turn_off, set_config, calibrate, reboot, ota_update
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'dispatched', 'acknowledged', 'executing', 'completed', 'failed', 'cancelled', 'expired')),
    priority INTEGER NOT NULL DEFAULT 5, -- 1 highest, 10 lowest
    preflight_checks JSONB DEFAULT '{}'::jsonb,
    max_execution_duration_sec INTEGER DEFAULT 1800, -- safe cutoff default (30 min)
    idempotency_key VARCHAR(100),
    dispatched_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    error_message TEXT,
    initiated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_device_commands_device ON device_commands(device_id, status);
CREATE INDEX IF NOT EXISTS idx_device_commands_status ON device_commands(status);

CREATE TABLE IF NOT EXISTS command_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_id UUID NOT NULL REFERENCES device_commands(id) ON DELETE CASCADE,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    event_message TEXT,
    telemetry_snapshot JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS firmware_releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    binary_url TEXT NOT NULL,
    binary_sha256 VARCHAR(64) NOT NULL,
    release_notes TEXT,
    is_stable BOOLEAN NOT NULL DEFAULT FALSE,
    min_hardware_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (device_type, version)
);

CREATE TABLE IF NOT EXISTS firmware_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firmware_release_id UUID NOT NULL REFERENCES firmware_releases(id),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'success', 'failed', 'rolled_back')),
    attempt_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
