import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"

TABLES = [
    "raw_users",
    "raw_sessions",
    "raw_events",
    "raw_signups",
    "raw_conversions",
    "stg_users",
    "stg_sessions",
    "stg_events",
    "stg_signups",
    "stg_conversions",
    "dim_user",
    "dim_channel",
    "fct_funnel_monthly",
    "fct_channel_performance",
    "fct_conversion_cohorts",
]


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        print("TABLE COUNTS")
        print("-" * 40)

        for table in TABLES:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count}")

        print("\nSample rows from fct_funnel_monthly:")
        cursor.execute("SELECT * FROM fct_funnel_monthly LIMIT 5")
        for row in cursor.fetchall():
            print(row)

        print("\nSample rows from fct_channel_performance:")
        cursor.execute("SELECT * FROM fct_channel_performance LIMIT 5")
        for row in cursor.fetchall():
            print(row)

    finally:
        connection.close()


if __name__ == "__main__":
    main()