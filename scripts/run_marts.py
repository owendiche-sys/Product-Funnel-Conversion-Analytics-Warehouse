import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"
SQL_PATH = BASE_DIR / "sql" / "marts.sql"


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        with open(SQL_PATH, "r", encoding="utf-8") as file:
            cursor.executescript(file.read())

        connection.commit()
        print("Mart tables created successfully.")
    except Exception as exc:
        connection.rollback()
        raise RuntimeError(f"Mart build failed: {exc}") from exc
    finally:
        connection.close()


if __name__ == "__main__":
    main()