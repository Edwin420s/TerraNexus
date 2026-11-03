-- 0005_operations_and_irrigation.sql
-- Farm Operations, Tasks, Equipment, Inventory, Harvest, and Irrigation Infrastructure
-- Aligned with TNX-DATA-001 Sections 7 & 13 and TNX-ARCH-001 Section 9

CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL, -- tractor, pump, harvester, sprayer, drone, solar_inverter, vehicle
    make VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    status VARCHAR(30) NOT NULL DEFAULT 'operational' CHECK (status IN ('operational', 'in_use', 'maintenance', 'decommissioned')),
    operating_hours NUMERIC(10,2) DEFAULT 0.0,
    properties JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    performed_by UUID REFERENCES users(id),
    maintenance_type VARCHAR(50) NOT NULL, -- routine, repair, overhaul, inspection
    cost_amount NUMERIC(10,2),
    cost_currency VARCHAR(3) DEFAULT 'USD',
    description TEXT NOT NULL,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    next_due_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- seed, fertilizer, pesticide, fuel, spare_part, packaging
    sku VARCHAR(100),
    quantity_on_hand NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    unit_of_measure VARCHAR(30) NOT NULL, -- kg, L, bags, units
    reorder_level NUMERIC(12,2),
    unit_cost NUMERIC(10,2),
    supplier VARCHAR(150),
    expiry_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_item_id UUID NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE,
    transaction_type VARCHAR(30) NOT NULL CHECK (transaction_type IN ('receipt', 'usage', 'adjustment', 'transfer', 'spoilage')),
    quantity NUMERIC(12,2) NOT NULL,
    reference_id UUID, -- e.g. task_id or harvest_id
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL, -- scouting, planting, spraying, fertilizing, weeding, irrigation, harvesting, maintenance
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(30) NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'completed', 'blocked', 'cancelled')),
    due_date DATE,
    completed_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tasks_farm ON tasks(farm_id);
CREATE INDEX IF NOT EXISTS idx_tasks_field ON tasks(field_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);

CREATE TABLE IF NOT EXISTS task_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'assignee',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (task_id, user_id)
);

CREATE TABLE IF NOT EXISTS task_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration_minutes INTEGER,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS harvest_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    field_crop_id UUID REFERENCES field_crops(id) ON DELETE SET NULL,
    harvest_date DATE NOT NULL,
    quantity_harvested_kg NUMERIC(14,2) NOT NULL,
    grade_quality VARCHAR(50),
    storage_location VARCHAR(100),
    batch_number VARCHAR(100),
    recorded_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Irrigation Infrastructure & Control (Physical Safety Protected)
CREATE TABLE IF NOT EXISTS water_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- borehole, river, dam, reservoir, rainwater_tank, municipal
    capacity_litres NUMERIC(14,2),
    current_level_litres NUMERIC(14,2),
    water_quality_ec NUMERIC(6,2),
    water_quality_ph NUMERIC(4,2),
    coordinates geometry(Point, 4326),
    status VARCHAR(30) NOT NULL DEFAULT 'operational' CHECK (status IN ('operational', 'low_water', 'depleted', 'maintenance')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pumps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    water_source_id UUID NOT NULL REFERENCES water_sources(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    pump_type VARCHAR(50) NOT NULL, -- submersible, centrifugal, solar_direct, booster
    max_flow_rate_lpm NUMERIC(10,2) NOT NULL, -- litres per minute
    power_source VARCHAR(50) NOT NULL, -- solar, grid, diesel, hybrid
    control_device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    control_relay_channel INTEGER DEFAULT 1,
    is_running BOOLEAN NOT NULL DEFAULT FALSE,
    max_continuous_runtime_sec INTEGER NOT NULL DEFAULT 3600, -- 1 hour physical limit
    minimum_cooloff_sec INTEGER NOT NULL DEFAULT 300, -- 5 min
    last_started_at TIMESTAMPTZ,
    last_stopped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS irrigation_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    water_source_id UUID NOT NULL REFERENCES water_sources(id),
    pump_id UUID REFERENCES pumps(id),
    name VARCHAR(150) NOT NULL,
    zone_code VARCHAR(50) NOT NULL,
    irrigation_method VARCHAR(50) NOT NULL, -- drip, sprinkler, pivot, micro_spray, furrow
    area_sqm NUMERIC(12,2),
    flow_rate_lpm NUMERIC(10,2),
    target_soil_moisture_pct NUMERIC(5,2) DEFAULT 60.0,
    solenoid_valve_device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    solenoid_relay_channel INTEGER DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (farm_id, zone_code)
);

CREATE TABLE IF NOT EXISTS irrigation_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    schedule_cron VARCHAR(100), -- cron or recurrence expression
    target_moisture_threshold NUMERIC(5,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS irrigation_plan_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    irrigation_plan_id UUID NOT NULL REFERENCES irrigation_plans(id) ON DELETE CASCADE,
    step_sequence INTEGER NOT NULL,
    irrigation_zone_id UUID NOT NULL REFERENCES irrigation_zones(id) ON DELETE CASCADE,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0 AND duration_minutes <= 180),
    target_water_volume_litres NUMERIC(10,2),
    fertigation_recipe JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS irrigation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    irrigation_zone_id UUID NOT NULL REFERENCES irrigation_zones(id) ON DELETE CASCADE,
    irrigation_plan_id UUID REFERENCES irrigation_plans(id) ON DELETE SET NULL,
    triggered_by VARCHAR(50) NOT NULL, -- manual_user, scheduled_plan, ai_recommendation, automated_rule
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    command_id UUID REFERENCES device_commands(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'aborted', 'safety_interlocked', 'failed')),
    scheduled_duration_minutes INTEGER NOT NULL,
    actual_duration_seconds INTEGER DEFAULT 0,
    water_applied_litres NUMERIC(12,2) DEFAULT 0.0,
    pre_soil_moisture_pct NUMERIC(5,2),
    post_soil_moisture_pct NUMERIC(5,2),
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    abort_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_irrigation_events_zone ON irrigation_events(irrigation_zone_id, started_at DESC);

CREATE TABLE IF NOT EXISTS safety_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    zone_id UUID REFERENCES irrigation_zones(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL, -- emergency_stop, watchdog_timeout, dry_run_detected, pipe_burst_pressure_drop, unauthorized_actuation
    severity VARCHAR(20) NOT NULL DEFAULT 'critical' CHECK (severity IN ('warning', 'error', 'critical')),
    interlock_tripped BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
