-- QuaNet Vision SQLite Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'Researcher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS water_bodies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    basin_type TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    water_body_id INTEGER REFERENCES water_bodies(id),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    ph REAL NOT NULL,
    temperature REAL NOT NULL,
    turbidity REAL NOT NULL,
    dissolved_oxygen REAL NOT NULL,
    tds REAL NOT NULL,
    conductivity REAL NOT NULL,
    water_quality TEXT NOT NULL, -- 'GOOD', 'MODERATE', 'POOR'
    is_demo BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Simulated Station IoT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    water_body_id INTEGER REFERENCES water_bodies(id),
    ph REAL,
    temperature REAL,
    turbidity REAL,
    dissolved_oxygen REAL,
    tds REAL,
    conductivity REAL,
    image_path TEXT,
    prediction TEXT NOT NULL, -- 'GOOD', 'MODERATE', 'POOR'
    confidence REAL NOT NULL,
    model_name TEXT NOT NULL,
    risk_level TEXT,
    recommendation TEXT,
    features_json TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    water_body_id INTEGER REFERENCES water_bodies(id),
    severity TEXT NOT NULL, -- 'CRITICAL', 'WARNING', 'INFO'
    parameter TEXT NOT NULL,
    value REAL,
    threshold_exceeded TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE' -- 'ACTIVE', 'RESOLVED', 'DISMISSED'
);

CREATE TABLE IF NOT EXISTS satellite_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    water_body_id INTEGER REFERENCES water_bodies(id),
    image_filename TEXT NOT NULL,
    title TEXT,
    turbidity_index REAL,
    algae_risk_index REAL,
    water_surface_area_pct REAL,
    detected_condition TEXT,
    confidence REAL,
    notes TEXT
);

-- Indices for rapid querying
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_water_body ON sensor_data(water_body_id);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
