PRAXIS_SCHEMA = """
CREATE TABLE IF NOT EXISTS protocols_metadata (
    protocol_id SERIAL PRIMARY KEY,
    protocol_name TEXT UNIQUE NOT NULL,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    user_id UUID REFERENCES keycloak_users(id),
    status TEXT,
    data_directory TEXT,
    database_file TEXT,
    parameters JSONB,
    required_assets JSONB
);

CREATE TABLE IF NOT EXISTS substep_timings (
    timing_id SERIAL PRIMARY KEY,
    protocol_name TEXT REFERENCES protocols_metadata(protocol_name),
    func_hash TEXT,
    func_name TEXT,
    duration FLOAT,
    caller_name TEXT,
    task_id TEXT,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    metadata JSONB,
    plr_serialized JSONB,
    is_available BOOLEAN DEFAULT TRUE,
    locked_by_protocol TEXT REFERENCES protocols_metadata(protocol_name),
    locked_by_task TEXT,
    lock_acquired_at TIMESTAMPTZ,
    lock_expires_at TIMESTAMPTZ
);



CREATE INDEX IF NOT EXISTS idx_protocol_name ON protocols_metadata(protocol_name);
CREATE INDEX IF NOT EXISTS idx_asset_name ON assets(name);
CREATE INDEX IF NOT EXISTS idx_protocol_status ON protocols_metadata(status);
CREATE INDEX IF NOT EXISTS idx_protocol_assets ON protocols_metadata USING GIN (assets);
CREATE INDEX IF NOT EXISTS idx_asset_metadata ON assets USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_asset_plr_serialized ON assets USING GIN (plr_serialized);
"""

KEYCLOAK_VIEWS = """
CREATE OR REPLACE VIEW keycloak_users AS
SELECT
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    u.enabled,
    array_agg(ur.role_id) as roles,
    ua.value as phone_number
FROM user_entity u
LEFT JOIN user_role_mapping ur ON u.id = ur.user_id
LEFT JOIN user_attribute ua ON u.id = ua.user_id AND ua.name = 'phone_number'
WHERE u.realm_id = (SELECT id FROM realm WHERE name = 'praxis')
GROUP BY u.id, u.username, u.email, u.first_name, u.last_name, u.enabled, ua.value;
"""
