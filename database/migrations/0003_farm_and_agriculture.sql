-- 0003_farm_and_agriculture.sql
-- Farm subdivisions, agricultural catalogues, crops, varieties, seasons, and field plantings
-- Aligned with TNX-DATA-001 Sections 5 & 6

CREATE TABLE IF NOT EXISTS farm_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_role VARCHAR(50) NOT NULL DEFAULT 'worker' CHECK (farm_role IN ('farm_manager', 'agronomist', 'operator', 'worker', 'inspector')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (farm_id, user_id)
);

CREATE TABLE IF NOT EXISTS field_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(50) NOT NULL DEFAULT 'management_zone',
    boundary geometry(MultiPolygon, 4326),
    soil_type VARCHAR(100),
    properties JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_field_zones_field ON field_zones(field_id);
CREATE INDEX IF NOT EXISTS idx_field_zones_boundary_gist ON field_zones USING GIST(boundary);

CREATE TABLE IF NOT EXISTS field_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    observed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    observation_type VARCHAR(50) NOT NULL, -- pest, disease, weed, deficiency, emergence, canopy
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    coordinates geometry(Point, 4326),
    photos JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_field_obs_field ON field_observations(field_id);
CREATE INDEX IF NOT EXISTS idx_field_obs_time ON field_observations(observed_at);

CREATE TABLE IF NOT EXISTS crops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID REFERENCES organisations(id) ON DELETE CASCADE, -- NULL means global system catalogue
    common_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    family VARCHAR(100),
    category VARCHAR(50) NOT NULL, -- cereal, vegetable, fruit, legume, root, forage, oilseed
    growing_days_min INTEGER CHECK (growing_days_min > 0),
    growing_days_max INTEGER CHECK (growing_days_max >= growing_days_min),
    water_requirement_mm NUMERIC(8,2),
    optimal_ph_min NUMERIC(4,2),
    optimal_ph_max NUMERIC(4,2),
    optimal_temp_min_c NUMERIC(5,2),
    optimal_temp_max_c NUMERIC(5,2),
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crop_varieties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    variety_name VARCHAR(100) NOT NULL,
    breeder_company VARCHAR(150),
    maturity_days INTEGER,
    drought_tolerance VARCHAR(20) CHECK (drought_tolerance IN ('low', 'medium', 'high', 'very_high')),
    disease_resistances JSONB DEFAULT '[]'::jsonb,
    yield_potential_kg_ha NUMERIC(10,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (crop_id, variety_name)
);

CREATE TABLE IF NOT EXISTS growing_seasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- e.g. "2026 Long Rains", "2026/2027 Summer"
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS field_crops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_id UUID NOT NULL REFERENCES crops(id),
    variety_id UUID REFERENCES crop_varieties(id),
    season_id UUID REFERENCES growing_seasons(id) ON DELETE SET NULL,
    planted_area_hectares NUMERIC(14,4),
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    plant_population_per_ha INTEGER,
    row_spacing_cm NUMERIC(6,2),
    planting_method VARCHAR(50),
    status VARCHAR(30) NOT NULL DEFAULT 'growing' CHECK (status IN ('planned', 'emerging', 'growing', 'flowering', 'ripening', 'harvested', 'failed', 'fallow')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_field_crops_field ON field_crops(field_id);
CREATE INDEX IF NOT EXISTS idx_field_crops_status ON field_crops(status);

CREATE TABLE IF NOT EXISTS crop_growth_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    stage_name VARCHAR(100) NOT NULL, -- Emergence, Vegetative, Floral, Fruit Set, Maturation
    bbch_code INTEGER,
    typical_duration_days INTEGER,
    kc_factor NUMERIC(4,2), -- Crop coefficient for evapotranspiration
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
