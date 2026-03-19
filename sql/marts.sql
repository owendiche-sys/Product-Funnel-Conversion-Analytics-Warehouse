DROP TABLE IF EXISTS dim_user;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS fct_funnel_monthly;
DROP TABLE IF EXISTS fct_channel_performance;
DROP TABLE IF EXISTS fct_conversion_cohorts;

CREATE TABLE dim_user AS
SELECT DISTINCT
    user_id,
    first_seen_date,
    signup_date,
    activation_date,
    acquisition_channel,
    country,
    device_type
FROM stg_users;

CREATE TABLE dim_channel AS
SELECT DISTINCT
    acquisition_channel AS channel_name
FROM stg_users
ORDER BY acquisition_channel;

CREATE TABLE fct_funnel_monthly AS
WITH visitors AS (
    SELECT
        strftime('%Y-%m', first_seen_date) AS funnel_month,
        COUNT(DISTINCT user_id) AS total_visitors
    FROM stg_users
    GROUP BY strftime('%Y-%m', first_seen_date)
),
signups AS (
    SELECT
        strftime('%Y-%m', signup_date) AS funnel_month,
        COUNT(DISTINCT user_id) AS total_signups
    FROM stg_signups
    GROUP BY strftime('%Y-%m', signup_date)
),
activations AS (
    SELECT
        strftime('%Y-%m', activation_date) AS funnel_month,
        COUNT(DISTINCT user_id) AS total_activations
    FROM stg_users
    WHERE activation_date IS NOT NULL
    GROUP BY strftime('%Y-%m', activation_date)
),
conversions AS (
    SELECT
        strftime('%Y-%m', conversion_date) AS funnel_month,
        COUNT(DISTINCT user_id) AS total_conversions,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM stg_conversions
    GROUP BY strftime('%Y-%m', conversion_date)
)
SELECT
    v.funnel_month,
    v.total_visitors,
    COALESCE(s.total_signups, 0) AS total_signups,
    COALESCE(a.total_activations, 0) AS total_activations,
    COALESCE(c.total_conversions, 0) AS total_conversions,
    COALESCE(c.total_revenue, 0) AS total_revenue,
    ROUND(COALESCE(s.total_signups, 0) * 100.0 / NULLIF(v.total_visitors, 0), 2) AS signup_rate_pct,
    ROUND(COALESCE(a.total_activations, 0) * 100.0 / NULLIF(v.total_visitors, 0), 2) AS activation_rate_pct,
    ROUND(COALESCE(c.total_conversions, 0) * 100.0 / NULLIF(v.total_visitors, 0), 2) AS visitor_to_conversion_rate_pct,
    ROUND(COALESCE(c.total_conversions, 0) * 100.0 / NULLIF(s.total_signups, 0), 2) AS signup_to_conversion_rate_pct
FROM visitors v
LEFT JOIN signups s
    ON v.funnel_month = s.funnel_month
LEFT JOIN activations a
    ON v.funnel_month = a.funnel_month
LEFT JOIN conversions c
    ON v.funnel_month = c.funnel_month
ORDER BY v.funnel_month;

CREATE TABLE fct_channel_performance AS
WITH user_base AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        u.country,
        u.device_type,
        CASE WHEN u.signup_date IS NOT NULL THEN 1 ELSE 0 END AS did_signup,
        CASE WHEN u.activation_date IS NOT NULL THEN 1 ELSE 0 END AS did_activate
    FROM stg_users u
),
conversion_base AS (
    SELECT
        user_id,
        COUNT(DISTINCT conversion_id) AS conversions,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM stg_conversions
    GROUP BY user_id
)
SELECT
    ub.acquisition_channel,
    COUNT(DISTINCT ub.user_id) AS total_users,
    SUM(ub.did_signup) AS total_signups,
    SUM(ub.did_activate) AS total_activations,
    COUNT(DISTINCT CASE WHEN cb.conversions > 0 THEN ub.user_id END) AS total_converted_users,
    ROUND(COALESCE(SUM(cb.total_revenue), 0), 2) AS total_revenue,
    ROUND(SUM(ub.did_signup) * 100.0 / NULLIF(COUNT(DISTINCT ub.user_id), 0), 2) AS signup_rate_pct,
    ROUND(SUM(ub.did_activate) * 100.0 / NULLIF(COUNT(DISTINCT ub.user_id), 0), 2) AS activation_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN cb.conversions > 0 THEN ub.user_id END) * 100.0
        / NULLIF(COUNT(DISTINCT ub.user_id), 0),
        2
    ) AS conversion_rate_pct
FROM user_base ub
LEFT JOIN conversion_base cb
    ON ub.user_id = cb.user_id
GROUP BY ub.acquisition_channel
ORDER BY total_revenue DESC;

CREATE TABLE fct_conversion_cohorts AS
WITH user_cohorts AS (
    SELECT
        user_id,
        strftime('%Y-%m', first_seen_date) AS cohort_month,
        acquisition_channel
    FROM stg_users
),
signup_flags AS (
    SELECT DISTINCT user_id, 1 AS signed_up
    FROM stg_signups
),
activation_flags AS (
    SELECT DISTINCT user_id, 1 AS activated
    FROM stg_users
    WHERE activation_date IS NOT NULL
),
conversion_flags AS (
    SELECT
        user_id,
        1 AS converted,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM stg_conversions
    GROUP BY user_id
)
SELECT
    uc.cohort_month,
    uc.acquisition_channel,
    COUNT(DISTINCT uc.user_id) AS cohort_users,
    COUNT(DISTINCT CASE WHEN sf.signed_up = 1 THEN uc.user_id END) AS signed_up_users,
    COUNT(DISTINCT CASE WHEN af.activated = 1 THEN uc.user_id END) AS activated_users,
    COUNT(DISTINCT CASE WHEN cf.converted = 1 THEN uc.user_id END) AS converted_users,
    ROUND(COALESCE(SUM(cf.total_revenue), 0), 2) AS total_revenue,
    ROUND(
        COUNT(DISTINCT CASE WHEN sf.signed_up = 1 THEN uc.user_id END) * 100.0
        / NULLIF(COUNT(DISTINCT uc.user_id), 0),
        2
    ) AS signup_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN af.activated = 1 THEN uc.user_id END) * 100.0
        / NULLIF(COUNT(DISTINCT uc.user_id), 0),
        2
    ) AS activation_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN cf.converted = 1 THEN uc.user_id END) * 100.0
        / NULLIF(COUNT(DISTINCT uc.user_id), 0),
        2
    ) AS conversion_rate_pct
FROM user_cohorts uc
LEFT JOIN signup_flags sf
    ON uc.user_id = sf.user_id
LEFT JOIN activation_flags af
    ON uc.user_id = af.user_id
LEFT JOIN conversion_flags cf
    ON uc.user_id = cf.user_id
GROUP BY uc.cohort_month, uc.acquisition_channel
ORDER BY uc.cohort_month, uc.acquisition_channel;