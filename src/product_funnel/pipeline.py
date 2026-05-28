from __future__ import annotations

from pathlib import Path

from product_funnel.database import execute_sql_file, load_raw_csvs
from product_funnel.modeling import train_conversion_models
from product_funnel.paths import ROOT_DIR, database_path
from product_funnel.quality import run_quality_checks


def build_schema() -> None:
    execute_sql_file(ROOT_DIR / "sql" / "schema.sql")


def build_staging() -> None:
    execute_sql_file(ROOT_DIR / "sql" / "staging.sql")


def build_marts() -> None:
    execute_sql_file(ROOT_DIR / "sql" / "marts.sql")


def run_pipeline(generate_data: bool = True, train_model: bool = True) -> dict[str, object]:
    if generate_data:
        from scripts.generate_sample_data import main as generate_sample_data

        generate_sample_data()

    build_schema()
    load_raw_csvs()
    build_staging()
    build_marts()
    quality_results = run_quality_checks(write_report=True)

    failed_critical_checks = [
        result for result in quality_results if result.status == "fail" and result.severity == "critical"
    ]
    if failed_critical_checks:
        failed_names = ", ".join(result.name for result in failed_critical_checks)
        raise RuntimeError(f"Critical data quality checks failed: {failed_names}")

    model_results = train_conversion_models() if train_model else {}

    return {
        "database_path": str(database_path()),
        "quality_checks": [result.__dict__ for result in quality_results],
        "model": model_results,
    }


def run_sql_only_pipeline() -> Path:
    build_schema()
    load_raw_csvs()
    build_staging()
    build_marts()
    run_quality_checks(write_report=True)
    return database_path()
