-- NETRAVA Database Schema (PostgreSQL 16 + PostGIS)
-- Reference Implementation: Gujarat Police Innovation Challenge 2026

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enum Types
DO $$ BEGIN
    CREATE TYPE camera_status AS ENUM ('REGISTERED', 'CONNECTING', 'ONLINE', 'DEGRADED', 'OFFLINE', 'MAINTENANCE', 'DISABLED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE watchlist_category AS ENUM ('STOLEN_VEHICLE', 'WANTED_VEHICLE', 'MISSING_PERSON', 'PERSON_OF_INTEREST', 'TRAFFIC_VIOLATOR', 'CUSTOM_OPERATION');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE data_classification AS ENUM ('PUBLIC', 'INTERNAL', 'SENSITIVE', 'HIGHLY_SENSITIVE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'STATE_ADMIN', 'DISTRICT_ADMIN', 'CONTROL_ROOM_OPERATOR', 'INVESTIGATOR', 'ANALYST', 'AUDITOR');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 1. Camera Registry
CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(128) NOT NULL,          -- e.g., 'Gujarat Police', 'AMC', 'GSRTC'
    district VARCHAR(128) NOT NULL,            -- e.g., 'Ahmedabad', 'Surat', 'Vadodara'
    zone VARCHAR(128) NOT NULL,
    sub_district VARCHAR(128),
    police_station VARCHAR(128),
    location GEOMETRY(Point, 4326) NOT NULL,    -- PostGIS Point (longitude, latitude)
    elevation_m NUMERIC(6,2),
    camera_type VARCHAR(64) DEFAULT 'FIXED_IP',
    manufacturer VARCHAR(64) NOT NULL,
    model VARCHAR(128),
    firmware_version VARCHAR(64),
    protocol VARCHAR(32) DEFAULT 'RTSP',        -- RTSP, ONVIF, WEBRTC, VMS_REST, SYNTHETIC
    rtsp_url TEXT NOT NULL,
    stream_relay_url TEXT,                      -- Low-Latency HLS or WebRTC proxied URL
    status camera_status DEFAULT 'ONLINE',
    health_score NUMERIC(4,1) DEFAULT 98.5,
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    data_classification data_classification DEFAULT 'INTERNAL',
    retention_days INT DEFAULT 30,
    tags TEXT[] DEFAULT '{}',
    analytics_config JSONB DEFAULT '{"anpr_enabled": true, "sampling_fps": 5, "vehicle_detection": true}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cameras_location ON cameras USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_cameras_district ON cameras(district);
CREATE INDEX IF NOT EXISTS idx_cameras_status ON cameras(status);
CREATE INDEX IF NOT EXISTS idx_cameras_external_id ON cameras(external_id);

-- 2. Watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(128) NOT NULL,
    category watchlist_category NOT NULL,
    description TEXT,
    department VARCHAR(128) NOT NULL DEFAULT 'Gujarat Police',
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(64) NOT NULL DEFAULT 'SYSTEM',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Watchlist Entries (e.g. Stolen or Wanted Vehicles)
CREATE TABLE IF NOT EXISTS watchlist_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    entity_type VARCHAR(32) DEFAULT 'vehicle',
    identifier VARCHAR(64) NOT NULL,           -- Normalized Plate (e.g. 'GJ01AB1234')
    secondary_identifier VARCHAR(64),          -- Make/model or VIN
    threat_level alert_severity DEFAULT 'HIGH',
    case_reference VARCHAR(128),               -- FIR No. or CCTNS Reference
    notes TEXT,
    effective_from TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchlist_identifier ON watchlist_entries(identifier);

-- 4. Vehicle Sightings (Normalized AI Detections)
CREATE TABLE IF NOT EXISTS vehicle_sightings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(64) UNIQUE NOT NULL,
    camera_id UUID REFERENCES cameras(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    plate_number VARCHAR(32) NOT NULL,
    normalized_plate VARCHAR(32) NOT NULL,
    plate_confidence NUMERIC(5,4) NOT NULL,
    vehicle_class VARCHAR(32) DEFAULT 'car',    -- sedan, suv, truck, bus, motorcycle
    vehicle_color VARCHAR(32) DEFAULT 'white',
    track_id VARCHAR(64),
    appearance_embedding FLOAT8[] DEFAULT '{}',
    frame_uri TEXT,
    plate_crop_uri TEXT,
    evidence_hash VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sightings_plate ON vehicle_sightings(normalized_plate);
CREATE INDEX IF NOT EXISTS idx_sightings_time ON vehicle_sightings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sightings_location ON vehicle_sightings USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_sightings_camera_time ON vehicle_sightings(camera_id, timestamp DESC);

-- 5. Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(64) NOT NULL,
    camera_id UUID REFERENCES cameras(id),
    watchlist_entry_id UUID REFERENCES watchlist_entries(id),
    severity alert_severity NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    matched_entity VARCHAR(64) NOT NULL,       -- e.g. 'GJ01AB1234'
    match_confidence NUMERIC(5,4) NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    evidence_frame_uri TEXT,
    evidence_crop_uri TEXT,
    status VARCHAR(32) DEFAULT 'NEW',          -- NEW, ACKNOWLEDGED, ESCALATED, RESOLVED, FALSE_POSITIVE
    assigned_to VARCHAR(64),
    acknowledged_by VARCHAR(64),
    acknowledged_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_matched_entity ON alerts(matched_entity);

-- 6. Investigations & Evidence Dossiers
CREATE TABLE IF NOT EXISTS investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    lead_investigator VARCHAR(64) NOT NULL,
    department VARCHAR(128) NOT NULL DEFAULT 'Gujarat Police CID / Crime Branch',
    target_plate VARCHAR(32),
    status VARCHAR(32) DEFAULT 'OPEN',
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investigation_events (
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    sighting_id UUID REFERENCES vehicle_sightings(id) ON DELETE CASCADE,
    relevance_notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (investigation_id, sighting_id)
);

-- 7. Security Audit Logs (Immutable)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(64) NOT NULL,
    user_name VARCHAR(128) NOT NULL,
    user_role user_role NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    action VARCHAR(64) NOT NULL,               -- VIEW_FEED, SEARCH_VEHICLE, EXPORT_EVIDENCE, UPDATE_WATCHLIST
    entity_type VARCHAR(64) NOT NULL,          -- CAMERA, VEHICLE, EVIDENCE, WATCHLIST
    entity_id VARCHAR(128) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);
