import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric, Float,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# ----------------- Identity & Organisations -----------------
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(30), nullable=True)
    password_hash = Column(Text, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(150), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    timezone = Column(String(64), default="UTC", nullable=False)
    account_status = Column(String(30), default="active", nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(Text, nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")

class Organisation(Base):
    __tablename__ = "organisations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    organisation_type = Column(String(50), nullable=False, default="commercial_farm")
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    memberships = relationship("Membership", back_populates="organisation", cascade="all, delete-orphan")
    farms = relationship("Farm", back_populates="organisation", cascade="all, delete-orphan")

class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="viewer", nullable=False) # owner, admin, manager, agronomist, operator, viewer
    status = Column(String(30), default="active", nullable=False)
    joined_at = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="memberships")
    organisation = relationship("Organisation", back_populates="memberships")

# ----------------- Farms & Fields -----------------
class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    farm_code = Column(String(50), nullable=True)
    boundary_geojson = Column(JSON, nullable=True)
    area_hectares = Column(Numeric(14, 4), nullable=True)
    country_code = Column(String(2), nullable=True)
    timezone = Column(String(64), default="Africa/Nairobi", nullable=False)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organisation = relationship("Organisation", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="farm", cascade="all, delete-orphan")
    water_sources = relationship("WaterSource", back_populates="farm", cascade="all, delete-orphan")
    irrigation_zones = relationship("IrrigationZone", back_populates="farm", cascade="all, delete-orphan")

class Field(Base):
    __tablename__ = "fields"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    field_code = Column(String(50), nullable=True)
    boundary_geojson = Column(JSON, nullable=True)
    area_hectares = Column(Numeric(14, 4), nullable=True)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    farm = relationship("Farm", back_populates="fields")
    field_crops = relationship("FieldCrop", back_populates="field", cascade="all, delete-orphan")
    observations = relationship("FieldObservation", back_populates="field", cascade="all, delete-orphan")

class FieldObservation(Base):
    __tablename__ = "field_observations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    observed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    observation_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=True)
    description = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    photos = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    field = relationship("Field", back_populates="observations")

# ----------------- Crops & Agriculture -----------------
class Crop(Base):
    __tablename__ = "crops"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=True)
    common_name = Column(String(100), nullable=False)
    scientific_name = Column(String(150), nullable=True)
    family = Column(String(100), nullable=True)
    category = Column(String(50), nullable=False)
    growing_days_min = Column(Integer, nullable=True)
    growing_days_max = Column(Integer, nullable=True)
    water_requirement_mm = Column(Numeric(8, 2), nullable=True)
    optimal_ph_min = Column(Numeric(4, 2), nullable=True)
    optimal_ph_max = Column(Numeric(4, 2), nullable=True)
    optimal_temp_min_c = Column(Numeric(5, 2), nullable=True)
    optimal_temp_max_c = Column(Numeric(5, 2), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    varieties = relationship("CropVariety", back_populates="crop", cascade="all, delete-orphan")

class CropVariety(Base):
    __tablename__ = "crop_varieties"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    variety_name = Column(String(100), nullable=False)
    breeder_company = Column(String(150), nullable=True)
    maturity_days = Column(Integer, nullable=True)
    drought_tolerance = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    crop = relationship("Crop", back_populates="varieties")

class GrowingSeason(Base):
    __tablename__ = "growing_seasons"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class FieldCrop(Base):
    __tablename__ = "field_crops"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    variety_id = Column(String(36), ForeignKey("crop_varieties.id"), nullable=True)
    season_id = Column(String(36), ForeignKey("growing_seasons.id"), nullable=True)
    planted_area_hectares = Column(Numeric(14, 4), nullable=True)
    planting_date = Column(DateTime(timezone=True), nullable=False)
    expected_harvest_date = Column(DateTime(timezone=True), nullable=True)
    actual_harvest_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="growing", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    field = relationship("Field", back_populates="field_crops")
    crop = relationship("Crop")

# ----------------- Devices & Sensors -----------------
class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    device_uid = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    device_type = Column(String(50), nullable=False) # weather_station, soil_probe, irrigation_controller, relay_actuator
    hardware_version = Column(String(50), default="v1.0")
    firmware_version = Column(String(50), default="1.0.0")
    provisioning_status = Column(String(30), default="provisioned", nullable=False)
    connection_status = Column(String(30), default="offline", nullable=False)
    battery_level_pct = Column(Numeric(5, 2), nullable=True)
    signal_strength_rssi = Column(Integer, nullable=True)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    config = Column(JSON, default=dict)
    last_telemetry_at = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    last_command_sequence = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    farm = relationship("Farm", back_populates="devices")
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    commands = relationship("DeviceCommand", back_populates="device", cascade="all, delete-orphan")

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    sensor_index = Column(Integer, default=0, nullable=False)
    sensor_code = Column(String(100), nullable=False)
    measurement_type_code = Column(String(50), nullable=False)
    depth_cm = Column(Numeric(6, 2), nullable=True)
    unit = Column(String(30), nullable=False)
    status = Column(String(30), default="active", nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    device = relationship("Device", back_populates="sensors")

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    sensor_id = Column(String(36), ForeignKey("sensors.id"), nullable=True)
    measurement_type = Column(String(50), nullable=False, index=True)
    value = Column(Numeric(14, 4), nullable=False)
    unit = Column(String(30), nullable=False)
    depth_cm = Column(Numeric(6, 2), nullable=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    quality_score = Column(Numeric(3, 2), default=1.0)
    is_valid = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class DeviceCommand(Base):
    __tablename__ = "device_commands"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    command_type = Column(String(50), nullable=False) # turn_on, turn_off, set_config, reboot
    payload = Column(JSON, default=dict, nullable=False)
    sequence = Column(Integer, default=1, nullable=True)
    status = Column(String(30), default="queued", nullable=False) # queued, dispatched, acknowledged, executing, completed, failed, cancelled, expired
    priority = Column(Integer, default=5, nullable=False)
    preflight_checks = Column(JSON, default=dict)
    max_execution_duration_sec = Column(Integer, default=1800)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    initiated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    device = relationship("Device", back_populates="commands")

# ----------------- Irrigation & Physical Control -----------------
class WaterSource(Base):
    __tablename__ = "water_sources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    source_type = Column(String(50), nullable=False) # borehole, river, dam, reservoir
    capacity_litres = Column(Numeric(14, 2), nullable=True)
    current_level_litres = Column(Numeric(14, 2), nullable=True)
    status = Column(String(30), default="operational", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    farm = relationship("Farm", back_populates="water_sources")
    pumps = relationship("Pump", back_populates="water_source", cascade="all, delete-orphan")

class Pump(Base):
    __tablename__ = "pumps"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    water_source_id = Column(String(36), ForeignKey("water_sources.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    pump_type = Column(String(50), default="solar_direct", nullable=False)
    max_flow_rate_lpm = Column(Numeric(10, 2), nullable=False)
    power_source = Column(String(50), default="solar", nullable=False)
    control_device_id = Column(String(36), ForeignKey("devices.id"), nullable=True)
    is_running = Column(Boolean, default=False, nullable=False)
    max_continuous_runtime_sec = Column(Integer, default=3600, nullable=False)
    minimum_cooloff_sec = Column(Integer, default=300, nullable=False)
    last_started_at = Column(DateTime(timezone=True), nullable=True)
    last_stopped_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    water_source = relationship("WaterSource", back_populates="pumps")

class IrrigationZone(Base):
    __tablename__ = "irrigation_zones"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    water_source_id = Column(String(36), ForeignKey("water_sources.id"), nullable=False)
    pump_id = Column(String(36), ForeignKey("pumps.id"), nullable=True)
    name = Column(String(150), nullable=False)
    zone_code = Column(String(50), nullable=False)
    irrigation_method = Column(String(50), default="drip", nullable=False)
    area_sqm = Column(Numeric(12, 2), nullable=True)
    flow_rate_lpm = Column(Numeric(10, 2), nullable=True)
    target_soil_moisture_pct = Column(Numeric(5, 2), default=60.0)
    solenoid_valve_device_id = Column(String(36), ForeignKey("devices.id"), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    pump = relationship("Pump")
    farm = relationship("Farm", back_populates="irrigation_zones")
    events = relationship("IrrigationEvent", back_populates="zone", cascade="all, delete-orphan")

class IrrigationPlan(Base):
    __tablename__ = "irrigation_plans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    schedule_cron = Column(String(100), nullable=True)
    target_moisture_threshold = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    steps = relationship("IrrigationPlanStep", back_populates="plan", cascade="all, delete-orphan")

class IrrigationPlanStep(Base):
    __tablename__ = "irrigation_plan_steps"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    irrigation_plan_id = Column(String(36), ForeignKey("irrigation_plans.id", ondelete="CASCADE"), nullable=False)
    step_sequence = Column(Integer, nullable=False)
    irrigation_zone_id = Column(String(36), ForeignKey("irrigation_zones.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    target_water_volume_litres = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    plan = relationship("IrrigationPlan", back_populates="steps")

class IrrigationEvent(Base):
    __tablename__ = "irrigation_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    irrigation_zone_id = Column(String(36), ForeignKey("irrigation_zones.id", ondelete="CASCADE"), nullable=False)
    irrigation_plan_id = Column(String(36), ForeignKey("irrigation_plans.id"), nullable=True)
    triggered_by = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="running", nullable=False) # pending, running, completed, aborted, safety_interlocked
    scheduled_duration_minutes = Column(Integer, nullable=False)
    actual_duration_seconds = Column(Integer, default=0)
    water_applied_litres = Column(Numeric(12, 2), default=0.0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    abort_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    zone = relationship("IrrigationZone", back_populates="events")

class SafetyEvent(Base):
    __tablename__ = "safety_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=True)
    zone_id = Column(String(36), ForeignKey("irrigation_zones.id"), nullable=True)
    event_type = Column(String(50), nullable=False) # emergency_stop, watchdog_timeout, dry_run
    severity = Column(String(20), default="critical", nullable=False)
    interlock_tripped = Column(Boolean, default=True, nullable=False)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Operations & Tasks -----------------
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), nullable=False) # scouting, planting, spraying, fertilizing, weeding, irrigation, harvesting
    priority = Column(String(20), default="medium", nullable=False) # low, medium, high, urgent
    status = Column(String(30), default="todo", nullable=False) # todo, in_progress, completed, blocked, cancelled
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    status = Column(String(30), default="operational", nullable=False)
    operating_hours = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False) # seed, fertilizer, pesticide, fuel, spare_part
    sku = Column(String(100), nullable=True)
    quantity_on_hand = Column(Numeric(12, 2), default=0.0, nullable=False)
    unit_of_measure = Column(String(30), nullable=False)
    reorder_level = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class HarvestRecord(Base):
    __tablename__ = "harvest_records"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    field_crop_id = Column(String(36), ForeignKey("field_crops.id"), nullable=True)
    harvest_date = Column(DateTime(timezone=True), nullable=False)
    quantity_harvested_kg = Column(Numeric(14, 2), nullable=False)
    grade_quality = Column(String(50), nullable=True)
    batch_number = Column(String(100), nullable=True)
    recorded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Monitoring & Alerts -----------------
class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    name = Column(String(150), nullable=False)
    rule_type = Column(String(50), nullable=False)
    measurement_type = Column(String(50), nullable=True)
    conditions = Column(JSON, nullable=False)
    severity = Column(String(20), default="warning", nullable=False)
    channels = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=True)
    alert_rule_id = Column(String(36), ForeignKey("alert_rules.id"), nullable=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(30), default="active", nullable=False) # active, acknowledged, resolved
    triggered_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    context_data = Column(JSON, default=dict)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    alert_id = Column(String(36), ForeignKey("alerts.id"), nullable=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(50), default="alert", nullable=False)
    link_url = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Intelligence & AI -----------------
class IntelligenceModel(Base):
    __tablename__ = "intelligence_models"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    model_type = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    framework = Column(String(50), default="rule_based", nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    confidence_score = Column(Numeric(3, 2), default=0.9)
    urgency = Column(String(20), default="medium", nullable=False)
    proposed_actions = Column(JSON, default=list, nullable=False)
    status = Column(String(30), default="proposed", nullable=False) # proposed, accepted, modified, rejected, executed
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    evidence = relationship("RecommendationEvidence", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationEvidence(Base):
    __tablename__ = "recommendation_evidence"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    observed_value = Column(String(100), nullable=False)
    threshold_value = Column(String(100), nullable=True)
    source_reference = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    recommendation = relationship("Recommendation", back_populates="evidence")

# ----------------- Offline Sync Engine -----------------
class ClientDevice(Base):
    __tablename__ = "client_devices"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client_uuid = Column(String(100), unique=True, nullable=False)
    device_model = Column(String(100), nullable=True)
    os_name = Column(String(50), nullable=True)
    app_version = Column(String(50), default="1.0.0", nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_cursor = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class SyncOperation(Base):
    __tablename__ = "sync_operations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_device_id = Column(String(36), ForeignKey("client_devices.id", ondelete="CASCADE"), nullable=False)
    operation_type = Column(String(30), nullable=False) # create, update, delete
    entity_name = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    client_timestamp = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(30), default="applied", nullable=False) # applied, conflict, rejected
    conflict_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class SyncConflict(Base):
    __tablename__ = "sync_conflicts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sync_operation_id = Column(String(36), ForeignKey("sync_operations.id", ondelete="CASCADE"), nullable=False)
    entity_name = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    client_payload = Column(JSON, nullable=False)
    server_payload = Column(JSON, nullable=False)
    resolution_strategy = Column(String(50), default="server_wins")
    resolved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Integrations & Webhooks -----------------
class ApiApplication(Base):
    __tablename__ = "api_applications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    api_key_hash = Column(Text, nullable=True)
    api_key_prefix = Column(String(16), nullable=True)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    target_url = Column(Text, nullable=False)
    secret_token = Column(String(100), nullable=False)
    event_subscriptions = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Security Audit -----------------
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    changes = Column(JSON, default=dict)
    status = Column(String(20), default="success", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Private Documents (Local RAG) -----------------
class FarmDocument(Base):
    __tablename__ = "farm_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False) # fao56_manual, agronomy_guide, soil_report, field_inspection
    doc_format = Column(String(20), default="markdown", nullable=False)
    content_text = Column(Text, nullable=False)
    chunks_count = Column(Integer, default=1, nullable=False)
    embeddings_metadata = Column(JSON, default=dict)
    is_indexed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

# ----------------- Tether WDK Agentic Finance -----------------
class AgentPayment(Base):
    __tablename__ = "agent_payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=True)
    wallet_address = Column(String(64), nullable=False)
    recipient_address = Column(String(64), nullable=False)
    amount_usdt = Column(Float, nullable=False)
    currency = Column(String(10), default="USD₮", nullable=False)
    chain = Column(String(30), default="Polygon", nullable=False)
    purpose = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    agent_reasoning = Column(Text, nullable=True)
    status = Column(String(30), default="pending_approval", nullable=False) # pending_approval, approved, rejected, broadcasted
    requires_human_approval = Column(Boolean, default=True, nullable=False)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    transaction_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
