from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from product_funnel.paths import database_path, raw_data_dir


RAW_FILES_AND_TABLES = {
    "users.csv": "raw_users",
    "sessions.csv": "raw_sessions",
    "events.csv": "raw_events",
    "signups.csv": "raw_signups",
    "conversions.csv": "raw_conversions",
}


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def execute_sql_file(sql_path: Path) -> None:
    with connect() as connection:
        with open(sql_path, "r", encoding="utf-8") as file:
            connection.executescript(file.read())


def query_dataframe(query: str) -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(query, connection)


def load_raw_csvs() -> None:
    source_dir = raw_data_dir()
    with connect() as connection:
        cursor = connection.cursor()
        for table_name in reversed(RAW_FILES_AND_TABLES.values()):
            cursor.execute(f"DELETE FROM {table_name}")

        for file_name, table_name in RAW_FILES_AND_TABLES.items():
            csv_path = source_dir / file_name
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing raw source file: {csv_path}")
            dataframe = pd.read_csv(csv_path)
            dataframe.to_sql(table_name, connection, if_exists="append", index=False)
