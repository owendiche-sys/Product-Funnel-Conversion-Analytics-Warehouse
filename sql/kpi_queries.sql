-- 1. Monthly funnel performance
SELECT
    funnel_month,
    total_visitors,
    total_signups,
    total_activations,
    total_conversions,
    total_revenue,
    signup_rate_pct,
    activation_rate_pct,
    visitor_to_conversion_rate_pct,
    signup_to_conversion_rate_pct
FROM fct_funnel_monthly
ORDER BY funnel_month;

-- 2. Overall business summary
SELECT
    COUNT(DISTINCT user_id) AS total_users,
    SUM(CASE WHEN signup_date IS NOT NULL THEN 1 ELSE 0 END) AS total_signups,
    SUM(CASE WHEN activation_date IS NOT NULL THEN 1 ELSE 0 END) AS total_activations,
    COUNT(DISTINCT c.user_id) AS total_converted_users,
    ROUND(COALESCE(SUM(c.revenue), 0), 2) AS total_revenue,
    ROUND(
        COUNT(DISTINCT c.user_id) * 100.0 / COUNT(DISTINCT u.user_id),
        2
    ) AS visitor_to_conversion_rate_pct
FROM dim_user u
LEFT JOIN stg_conversions c
    ON u.user_id = c.user_id;

-- 3. Channel performance
SELECT
    acquisition_channel,
    total_users,
    total_signups,
    total_activations,
    total_converted_users,
    total_revenue,
    signup_rate_pct,
    activation_rate_pct,
    conversion_rate_pct
FROM fct_channel_performance
ORDER BY total_revenue DESC;

-- 4. Revenue by plan
SELECT
    plan_name,
    COUNT(DISTINCT user_id) AS converted_users,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_revenue_per_conversion
FROM stg_conversions
GROUP BY plan_name
ORDER BY total_revenue DESC;

-- 5. Cohort performance
SELECT
    cohort_month,
    acquisition_channel,
    cohort_users,
    signed_up_users,
    activated_users,
    converted_users,
    total_revenue,
    signup_rate_pct,
    activation_rate_pct,
    conversion_rate_pct
FROM fct_conversion_cohorts
ORDER BY cohort_month, acquisition_channel;