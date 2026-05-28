# Product Funnel Conversion Analytics Warehouse

An end-to-end data science and analytics engineering project for product funnel analysis, conversion behavior, revenue reporting, and conversion propensity modeling.

The project simulates a SaaS/product analytics workflow: raw event and user data is loaded into SQLite, transformed into staging and mart layers, validated with automated data quality checks, converted into model-ready user features, scored with machine learning, and surfaced through a Streamlit dashboard.

## Business Problem

Product and growth teams need to understand where users enter, where they drop off, which segments create revenue, and which users are most likely to convert. This project answers both descriptive and predictive questions:

- What is the funnel conversion rate by month, channel, country, and device?
- Which acquisition channels and plans generate the most revenue?
- Where is the biggest funnel drop-off?
- Which user behaviors are associated with conversion?
- Can we estimate conversion propensity for each user?

## What This Project Demonstrates

- Warehouse-style SQL modeling with raw, staging, dimension, fact, and feature mart layers.
- Reproducible Python pipeline orchestration.
- Automated data quality validation.
- Behavioral feature engineering from sessions and events.
- Conversion propensity modeling with scikit-learn.
- Model metrics and user-level scoring outputs.
- Streamlit dashboard for BI reporting and model interpretation.
- Tests for core project contracts.

## Tech Stack

- SQLite for the local analytics warehouse.
- SQL for schema, staging, marts, KPIs, and feature engineering.
- Python and pandas for orchestration and data handling.
- scikit-learn for conversion propensity modeling.
- Streamlit for the interactive dashboard.
- pytest for test coverage.

## Project Structure

```text
Product-Funnel-Conversion-Analytics-Warehouse/
|-- config/
|   `-- project_config.json
|-- dashboard/
|   `-- app.py
|-- data/
|   `-- raw/
|-- database/
|   `-- product_funnel_analytics.db
|-- docs/
|   |-- data_dictionary.md
|   `-- model_card.md
|-- models/
|   `-- conversion_propensity_model.pkl
|-- notebooks/
|   |-- 01_data_quality_eda.ipynb
|   `-- 02_conversion_modeling.ipynb
|-- reports/
|   |-- conversion_propensity_scores.csv
|   |-- data_quality_report.json
|   `-- model_metrics.json
|-- scripts/
|   |-- run_pipeline.py
|   |-- run_quality_checks.py
|   |-- train_model.py
|   `-- ...
|-- sql/
|   |-- schema.sql
|   |-- staging.sql
|   |-- marts.sql
|   `-- kpi_queries.sql
|-- src/
|   `-- product_funnel/
|-- tests/
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Warehouse Layers

Raw tables:

- `raw_users`
- `raw_sessions`
- `raw_events`
- `raw_signups`
- `raw_conversions`

Staging tables:

- `stg_users`
- `stg_sessions`
- `stg_events`
- `stg_signups`
- `stg_conversions`

Analytics marts:

- `dim_user`
- `dim_channel`
- `fct_funnel_monthly`
- `fct_channel_performance`
- `fct_conversion_cohorts`
- `mart_user_features`
- `mart_conversion_scores`

## Modeling Objective

The predictive task is binary classification:

- Target: `did_convert`
- Unit of analysis: user
- Output: user-level conversion probability
- Primary metrics: ROC AUC, precision, recall, F1, and accuracy

The model uses acquisition attributes, geography, device type, signup/activation behavior, session activity, event counts, pricing views, and timing features.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If using editable package mode:

```bash
pip install -e ".[dev]"
```

## Run the Full Pipeline

```bash
python scripts/run_pipeline.py
```

This command:

1. Generates deterministic sample data.
2. Builds the SQLite schema.
3. Loads raw CSV files.
4. Builds staging tables.
5. Builds analytics and feature marts.
6. Runs data quality checks.
7. Trains conversion models.
8. Writes model metrics and conversion scores.

## Run Individual Steps

```bash
python scripts/build_database.py
python scripts/generate_sample_data.py
python scripts/load_csvs.py
python scripts/run_staging.py
python scripts/run_marts.py
python scripts/run_quality_checks.py
python scripts/train_model.py
python scripts/check_database.py
python scripts/run_kpis.py
```

## Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard includes:

- KPI summary metrics.
- Monthly funnel volume and rate trends.
- Revenue and conversion analysis by segment.
- Feature-enriched user table.
- Conversion model metrics.
- Propensity segment summaries.
- Top scored users.

## Run Tests

```bash
pytest
```

## Key Outputs

- `database/product_funnel_analytics.db`: local analytics warehouse.
- `reports/data_quality_report.json`: validation results.
- `reports/model_metrics.json`: model comparison metrics.
- `reports/conversion_propensity_scores.csv`: user-level model scores.
- `models/conversion_propensity_model.pkl`: trained model artifact.

## Portfolio Notes

This project is suitable for demonstrating analytics engineering, product analytics, business intelligence, and junior data science skills. The strongest talking points are the end-to-end workflow, warehouse modeling, automated validation, feature engineering, and the bridge from descriptive funnel analytics to predictive conversion scoring.

## Author

Owen Nda Diche  
MSc Data Science  
University of Hertfordshire
