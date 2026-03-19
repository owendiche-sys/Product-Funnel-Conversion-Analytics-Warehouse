PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS raw_users (
    user_id TEXT PRIMARY KEY,
    first_seen_date TEXT,
    signup_date TEXT,
    activation_date TEXT,
    acquisition_channel TEXT,
    country TEXT,
    device_type TEXT
);

CREATE TABLE IF NOT EXISTS raw_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    session_start TEXT,
    session_end TEXT,
    traffic_source TEXT,
    landing_page TEXT,
    device_type TEXT,
    FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
);

CREATE TABLE IF NOT EXISTS raw_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT,
    user_id TEXT,
    event_time TEXT,
    event_name TEXT,
    page_name TEXT,
    FOREIGN KEY (session_id) REFERENCES raw_sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
);

CREATE TABLE IF NOT EXISTS raw_signups (
    signup_id TEXT PRIMARY KEY,
    user_id TEXT,
    signup_date TEXT,
    signup_method TEXT,
    signup_status TEXT,
    FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
);

CREATE TABLE IF NOT EXISTS raw_conversions (
    conversion_id TEXT PRIMARY KEY,
    user_id TEXT,
    conversion_date TEXT,
    conversion_type TEXT,
    revenue REAL,
    plan_name TEXT,
    FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
);