import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"

QUERIES = {
    "monthly_funnel": """
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
    """,
    "business_summary": """
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
    """,
    "channel_performance": """
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
    """,
    "revenue_by_plan": """
        SELECT
            plan_name,
            COUNT(DISTINCT user_id) AS converted_users,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue_per_conversion
        FROM stg_conversions
        GROUP BY plan_name
        ORDER BY total_revenue DESC;
    """,
    "cohort_performance": """
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
    """,
}


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        for name, query in QUERIES.items():
            print("\n" + "=" * 70)
            print(name.upper())
            print("=" * 70)
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows[:10]:
                print(row)

            if len(rows) > 10:
                print(f"... showing first 10 of {len(rows)} rows")

    finally:
        connection.close()


if __name__ == "__main__":
    main()