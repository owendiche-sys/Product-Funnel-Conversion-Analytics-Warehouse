import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            cursor.executescript(file.read())

        connection.commit()
        print(f"Database created successfully: {DB_PATH}")
    except Exception as exc:
        connection.rollback()
        raise RuntimeError(f"Database creation failed: {exc}") from exc
    finally:
        connection.close()


if __name__ == "__main__":
    main()