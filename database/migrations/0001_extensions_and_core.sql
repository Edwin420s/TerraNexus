-- Foundation migration only. Expand against TNX-DATA-001 before production.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS organisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 200),
    organisation_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id),
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 200),
    farm_code TEXT,
    boundary geometry(MultiPolygon, 4326),
    area_hectares NUMERIC(14,4) CHECK (area_hectares IS NULL OR area_hectares >= 0),
    country_code CHAR(2),
    timezone TEXT NOT NULL DEFAULT 'Africa/Nairobi',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organisation_id, farm_code)
);
CREATE INDEX IF NOT EXISTS idx_farms_org ON farms(organisation_id);
CREATE INDEX IF NOT EXISTS idx_farms_boundary_gist ON farms USING GIST(boundary);

CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id),
    farm_id UUID NOT NULL REFERENCES farms(id),
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 200),
    field_code TEXT,
    boundary geometry(MultiPolygon, 4326),
    area_hectares NUMERIC(14,4) CHECK (area_hectares IS NULL OR area_hectares >= 0),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (farm_id, field_code)
);
CREATE INDEX IF NOT EXISTS idx_fields_org ON fields(organisation_id);
CREATE INDEX IF NOT EXISTS idx_fields_farm ON fields(farm_id);
CREATE INDEX IF NOT EXISTS idx_fields_boundary_gist ON fields USING GIST(boundary);
