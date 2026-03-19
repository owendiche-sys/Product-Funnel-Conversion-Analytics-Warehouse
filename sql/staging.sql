DROP TABLE IF EXISTS stg_users;
DROP TABLE IF EXISTS stg_sessions;
DROP TABLE IF EXISTS stg_events;
DROP TABLE IF EXISTS stg_signups;
DROP TABLE IF EXISTS stg_conversions;

CREATE TABLE stg_users AS
SELECT
    TRIM(user_id) AS user_id,
    DATE(first_seen_date) AS first_seen_date,
    CASE
        WHEN TRIM(signup_date) = '' THEN NULL
        ELSE DATE(signup_date)
    END AS signup_date,
    CASE
        WHEN TRIM(activation_date) = '' THEN NULL
        ELSE DATE(activation_date)
    END AS activation_date,
    TRIM(acquisition_channel) AS acquisition_channel,
    TRIM(country) AS country,
    LOWER(TRIM(device_type)) AS device_type
FROM raw_users;

CREATE TABLE stg_sessions AS
SELECT
    TRIM(session_id) AS session_id,
    TRIM(user_id) AS user_id,
    DATETIME(session_start) AS session_start,
    DATETIME(session_end) AS session_end,
    TRIM(traffic_source) AS traffic_source,
    TRIM(landing_page) AS landing_page,
    LOWER(TRIM(device_type)) AS device_type
FROM raw_sessions;

CREATE TABLE stg_events AS
SELECT
    TRIM(event_id) AS event_id,
    TRIM(session_id) AS session_id,
    TRIM(user_id) AS user_id,
    DATETIME(event_time) AS event_time,
    LOWER(TRIM(event_name)) AS event_name,
    TRIM(page_name) AS page_name
FROM raw_events;

CREATE TABLE stg_signups AS
SELECT
    TRIM(signup_id) AS signup_id,
    TRIM(user_id) AS user_id,
    DATE(signup_date) AS signup_date,
    LOWER(TRIM(signup_method)) AS signup_method,
    LOWER(TRIM(signup_status)) AS signup_status
FROM raw_signups;

CREATE TABLE stg_conversions AS
SELECT
    TRIM(conversion_id) AS conversion_id,
    TRIM(user_id) AS user_id,
    DATE(conversion_date) AS conversion_date,
    LOWER(TRIM(conversion_type)) AS conversion_type,
    ROUND(revenue, 2) AS revenue,
    TRIM(plan_name) AS plan_name
FROM raw_conversions;