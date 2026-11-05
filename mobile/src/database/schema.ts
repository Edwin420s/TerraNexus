// SQLite Schema for Offline-First Mobile Operation (TNX-SYNC-001)
export const SQL_INIT_LOCAL_DB = `
CREATE TABLE IF NOT EXISTS local_farms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    farm_code TEXT,
    area_hectares REAL,
    sync_status TEXT DEFAULT 'synced'
);

CREATE TABLE IF NOT EXISTS local_fields (
    id TEXT PRIMARY KEY,
    farm_id TEXT NOT NULL,
    name TEXT NOT NULL,
    field_code TEXT,
    area_hectares REAL,
    sync_status TEXT DEFAULT 'synced'
);

CREATE TABLE IF NOT EXISTS local_tasks (
    id TEXT PRIMARY KEY,
    farm_id TEXT NOT NULL,
    field_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date TEXT,
    updated_at TEXT NOT NULL,
    sync_status TEXT DEFAULT 'synced' -- synced, pending_push, conflict
);

CREATE TABLE IF NOT EXISTS local_field_observations (
    id TEXT PRIMARY KEY,
    field_id TEXT NOT NULL,
    observation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT,
    latitude REAL,
    longitude REAL,
    observed_at TEXT NOT NULL,
    sync_status TEXT DEFAULT 'pending_push'
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    operation_type TEXT NOT NULL, -- create, update, delete
    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attempt_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sync_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
`;
