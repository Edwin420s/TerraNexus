-- 0008_seed_data.sql
-- Seed baseline data for TerraNexus development, testing, and production bootstrapping

-- 1. Standard Measurement Types
INSERT INTO measurement_types (code, name, category, canonical_unit, min_physical_value, max_physical_value, description)
VALUES
    ('soil_moisture', 'Soil Volumetric Water Content', 'soil', '%', 0.0, 100.0, 'Volumetric soil moisture percentage'),
    ('ambient_temp', 'Ambient Air Temperature', 'atmospheric', '°C', -40.0, 85.0, 'Air temperature at 1.5m-2m height'),
    ('relative_humidity', 'Relative Humidity', 'atmospheric', '%', 0.0, 100.0, 'Relative atmospheric humidity'),
    ('solar_radiation', 'Solar Radiation', 'atmospheric', 'W/m²', 0.0, 1500.0, 'Global solar irradiance'),
    ('wind_speed', 'Wind Speed', 'atmospheric', 'm/s', 0.0, 65.0, 'Sustained horizontal wind speed'),
    ('rainfall', 'Rainfall Precipitation', 'atmospheric', 'mm', 0.0, 500.0, 'Cumulative precipitation depth'),
    ('water_flow', 'Water Flow Rate', 'water', 'L/min', 0.0, 5000.0, 'Pipe or dripline water flow rate'),
    ('battery_voltage', 'Battery Voltage', 'system', 'V', 0.0, 15.0, 'Device operating or battery voltage'),
    ('soil_ph', 'Soil Acidity / pH', 'soil', 'pH', 0.0, 14.0, 'Soil pH acidity level'),
    ('soil_ec', 'Soil Electrical Conductivity', 'soil', 'dS/m', 0.0, 20.0, 'Soil salinity / conductivity')
ON CONFLICT (code) DO NOTHING;

-- 2. Standard Integration Providers
INSERT INTO integration_providers (name, slug, category, auth_mechanism, documentation_url)
VALUES
    ('Open-Meteo Weather API', 'open_meteo', 'weather', 'none', 'https://open-meteo.com/en/docs'),
    ('Copernicus Sentinel Satellite', 'copernicus', 'satellite', 'api_key', 'https://dataspace.copernicus.eu/'),
    ('QVAC Local AI Engine', 'qvac_local', 'ai', 'none', 'http://localhost:8080/v1/qvac'),
    ('ChirpStack LoRaWAN Server', 'chirpstack', 'lora_server', 'api_key', 'https://www.chirpstack.io/')
ON CONFLICT (slug) DO NOTHING;

-- 3. Standard Crops & Varieties
INSERT INTO crops (id, common_name, scientific_name, category, growing_days_min, growing_days_max, water_requirement_mm, optimal_ph_min, optimal_ph_max, optimal_temp_min_c, optimal_temp_max_c)
VALUES
    ('11111111-0000-0000-0000-000000000001', 'Maize', 'Zea mays', 'cereal', 110, 140, 600.0, 5.8, 7.0, 18.0, 32.0),
    ('11111111-0000-0000-0000-000000000002', 'Tomato', 'Solanum lycopersicum', 'vegetable', 75, 110, 500.0, 6.0, 6.8, 18.0, 28.0),
    ('11111111-0000-0000-0000-000000000003', 'Avocado', 'Persea americana', 'fruit', 365, 730, 850.0, 6.0, 6.5, 16.0, 30.0),
    ('11111111-0000-0000-0000-000000000004', 'Wheat', 'Triticum aestivum', 'cereal', 100, 130, 450.0, 6.0, 7.5, 12.0, 25.0)
ON CONFLICT (id) DO NOTHING;

-- 4. Standard Growth Stages (FAO-56 Kc factors)
INSERT INTO crop_growth_stages (crop_id, stage_number, stage_name, typical_duration_days, kc_factor, description)
VALUES
    ('11111111-0000-0000-0000-000000000001', 1, 'Initial / Emergence', 20, 0.30, 'Plant emergence to 10% ground cover'),
    ('11111111-0000-0000-0000-000000000001', 2, 'Crop Development / Vegetative', 35, 0.70, 'Vegetative growth to rapid canopy expansion'),
    ('11111111-0000-0000-0000-000000000001', 3, 'Mid-Season / Tasseling & Silking', 40, 1.20, 'Flowering and grain filling (critical water period)'),
    ('11111111-0000-0000-0000-000000000001', 4, 'Late Season / Ripening', 30, 0.60, 'Maturity and grain dry-down'),
    ('11111111-0000-0000-0000-000000000002', 1, 'Initial Stage', 25, 0.45, 'Transplanting to early vegetative growth'),
    ('11111111-0000-0000-0000-000000000002', 2, 'Crop Development', 35, 0.75, 'Rapid vegetative growth and first flowers'),
    ('11111111-0000-0000-0000-000000000002', 3, 'Mid-Season (Fruiting)', 40, 1.15, 'Fruit development and swelling'),
    ('11111111-0000-0000-0000-000000000002', 4, 'Late Season (Ripening)', 25, 0.80, 'Harvest and ripening phase')
ON CONFLICT DO NOTHING;

-- 5. Standard Intelligence Models
INSERT INTO intelligence_models (id, name, model_type, version, framework, description, parameters)
VALUES
    ('22222222-0000-0000-0000-000000000001', 'FAO-56 Evapotranspiration & Soil Water Balance', 'irrigation_scheduler', '1.0.0', 'rule_based', 'Calculates daily crop water depletion using Penman-Monteith and soil physical characteristics', '{"wilting_point": 15.0, "field_capacity": 35.0, "mad_fraction": 0.5}'),
    ('22222222-0000-0000-0000-000000000002', 'QVAC Local Agronomic Reasoning Engine', 'qvac_local_agronomist', '1.0.0', 'qvac', 'Local quantized LLM model for contextual farm advisory and agronomic triage', '{"context_window": 4096, "temperature": 0.2}')
ON CONFLICT (name, version) DO NOTHING;

-- 6. Demo Organisation, User, Farm, and Fields
INSERT INTO organisations (id, name, organisation_type, status)
VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Nexus Agri Enterprise', 'commercial_farm', 'active')
ON CONFLICT (id) DO NOTHING;

-- Demo User: admin@terranexus.org (password: TerraNexus2026! - hashed with sha256/pbkdf2)
INSERT INTO users (id, email, password_hash, first_name, last_name, display_name, preferred_language, timezone, account_status, email_verified)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'admin@terranexus.org', 'pbkdf2_sha256$260000$terranexus$9ad11e9f2910bb4265b704c7b8aa249f33f671c66708451b72e505847db5d9c2', 'Admin', 'Nexus', 'TerraNexus Admin', 'en', 'Africa/Nairobi', 'active', TRUE),
    ('b0000000-0000-0000-0000-000000000002', 'agronomist@terranexus.org', 'pbkdf2_sha256$260000$terranexus$9ad11e9f2910bb4265b704c7b8aa249f33f671c66708451b72e505847db5d9c2', 'Sarah', 'Kiprono', 'Sarah Kiprono (Agronomist)', 'en', 'Africa/Nairobi', 'active', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO memberships (organisation_id, user_id, role, status)
VALUES
    ('a0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'owner', 'active'),
    ('a0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', 'agronomist', 'active')
ON CONFLICT (organisation_id, user_id) DO NOTHING;

INSERT INTO farms (id, organisation_id, name, farm_code, area_hectares, country_code, timezone, status)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'GreenValley Demonstration Farm', 'GV-01', 45.5, 'KE', 'Africa/Nairobi', 'active')
ON CONFLICT (organisation_id, farm_code) DO NOTHING;

INSERT INTO fields (id, organisation_id, farm_id, name, field_code, area_hectares, status)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'North Plot - Maize Block', 'NP-01', 12.5, 'active'),
    ('d0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'South Greenhouse - Drip Tomatoes', 'SG-02', 2.0, 'active')
ON CONFLICT (farm_id, field_code) DO NOTHING;

-- 7. Demo Water Sources, Pump, and Irrigation Zone
INSERT INTO water_sources (id, organisation_id, farm_id, name, source_type, capacity_litres, current_level_litres, status)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'Main Reservoir Dam', 'dam', 500000.0, 420000.0, 'operational')
ON CONFLICT (id) DO NOTHING;

INSERT INTO pumps (id, water_source_id, name, pump_type, max_flow_rate_lpm, power_source, is_running, max_continuous_runtime_sec)
VALUES
    ('e1000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'Primary Solar Pump A', 'solar_direct', 150.0, 'solar', FALSE, 3600)
ON CONFLICT (id) DO NOTHING;

INSERT INTO irrigation_zones (id, organisation_id, farm_id, field_id, water_source_id, pump_id, name, zone_code, irrigation_method, area_sqm, flow_rate_lpm, target_soil_moisture_pct, is_active)
VALUES
    ('e2000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', 'Greenhouse Tomato Drip Zone', 'Z-GH1', 'drip', 2000.0, 45.0, 65.0, FALSE)
ON CONFLICT (farm_id, zone_code) DO NOTHING;

-- 8. Demo ESP32 Device & Attached Sensors
INSERT INTO devices (id, organisation_id, farm_id, field_id, device_uid, name, device_type, hardware_version, firmware_version, provisioning_status, connection_status, battery_level_pct, signal_strength_rssi)
VALUES
    ('f0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'esp32-node-001', 'ESP32 Soil & Climate Monitor', 'soil_probe', 'esp32-devkit-v1', '1.0.0', 'active', 'online', 94.0, -68)
ON CONFLICT (organisation_id, device_uid) DO NOTHING;

INSERT INTO sensors (id, device_id, sensor_index, sensor_code, measurement_type_code, depth_cm, unit, status)
VALUES
    ('f1000000-0000-0000-0000-000000000001', 'f0000000-0000-0000-0000-000000000001', 0, 'soil_moist_10cm', 'soil_moisture', 10.0, '%', 'active'),
    ('f1000000-0000-0000-0000-000000000002', 'f0000000-0000-0000-0000-000000000001', 1, 'soil_moist_30cm', 'soil_moisture', 30.0, '%', 'active'),
    ('f1000000-0000-0000-0000-000000000003', 'f0000000-0000-0000-0000-000000000001', 2, 'dht22_temp', 'ambient_temp', NULL, '°C', 'active'),
    ('f1000000-0000-0000-0000-000000000004', 'f0000000-0000-0000-0000-000000000001', 3, 'dht22_humidity', 'relative_humidity', NULL, '%', 'active')
ON CONFLICT (device_id, sensor_code) DO NOTHING;
