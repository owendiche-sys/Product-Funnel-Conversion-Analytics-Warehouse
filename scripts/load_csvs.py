import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"
RAW_DIR = BASE_DIR / "data" / "raw"

FILES_AND_TABLES = {
    "users.csv": "raw_users",
    "sessions.csv": "raw_sessions",
    "events.csv": "raw_events",
    "signups.csv": "raw_signups",
    "conversions.csv": "raw_conversions",
}


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        for table_name in FILES_AND_TABLES.values():
            cursor.execute(f"DELETE FROM {table_name}")

        connection.commit()

        for file_name, table_name in FILES_AND_TABLES.items():
            csv_path = RAW_DIR / file_name
            dataframe = pd.read_csv(csv_path)
            dataframe.to_sql(table_name, connection, if_exists="append", index=False)
            print(f"Loaded {file_name} into {table_name}")

        connection.commit()
        print("All CSV files loaded successfully.")

    except Exception as exc:
        connection.rollback()
        raise RuntimeError(f"CSV load failed: {exc}") from exc

    finally:
        connection.close()


if __name__ == "__main__":
    main()