# Product Funnel & Conversion Analytics Warehouse

An end-to-end product analytics project built with **SQLite, SQL, Python, pandas, and Streamlit** to model user funnel performance, conversion behaviour, channel effectiveness, and revenue outcomes through a warehouse-style analytics workflow.

## Overview

This project simulates a real-world product analytics and analytics engineering workflow for a digital product or SaaS business. It starts with raw user, session, event, signup, and conversion data, loads the data into a **SQLite analytics warehouse**, transforms it into clean **staging** and **mart** layers, calculates key funnel and conversion KPIs, and presents the final outputs through an interactive **Streamlit dashboard**.

The project was designed to show how event and user journey data can be structured into reporting-ready analytics for teams interested in acquisition, activation, conversion, monetisation, and funnel optimisation.

## Business Problem

Product and growth teams need to understand:

- how many users enter the funnel
- how many users sign up, activate, and convert
- where the biggest funnel drop-off happens
- which acquisition channels drive the most revenue
- which plans generate the strongest commercial outcomes
- how funnel performance changes by month, country, and device type

Without a structured analytics layer, it becomes difficult to monitor funnel performance consistently or identify which segments deserve optimisation.

## Project Objectives

This project was built to:

- design a lightweight product analytics warehouse using SQLite
- load and manage multi-table funnel and conversion data
- clean and standardise raw event and user data into staging tables
- create mart tables for funnel reporting and dashboarding
- calculate core funnel, conversion, and revenue KPIs
- build an interactive dashboard for business users
- demonstrate end-to-end analytics engineering workflow for a portfolio project

## Tech Stack

- **SQLite** for the analytics database
- **SQL** for schema creation, transformations, and KPI logic
- **Python** for pipeline automation and scripting
- **pandas** for CSV loading and query handling
- **Streamlit** for the dashboard interface

## Warehouse Architecture

The project follows a warehouse-style layered structure:

### Raw Layer
The raw layer stores source-level data loaded directly from CSV files.

Tables:
- `raw_users`
- `raw_sessions`
- `raw_events`
- `raw_signups`
- `raw_conversions`

### Staging Layer
The staging layer standardises and cleans the raw data for downstream analysis.

Tables:
- `stg_users`
- `stg_sessions`
- `stg_events`
- `stg_signups`
- `stg_conversions`

### Mart Layer
The mart layer contains analytics-ready dimension and fact tables.

Tables:
- `dim_user`
- `dim_channel`
- `fct_funnel_monthly`
- `fct_channel_performance`
- `fct_conversion_cohorts`

## Data Model Summary

### `dim_user`
Contains user-level descriptive attributes such as:
- user ID
- first seen date
- signup date
- activation date
- acquisition channel
- country
- device type

### `dim_channel`
Contains channel-level lookup values for acquisition analysis.

### `fct_funnel_monthly`
Monthly funnel summary table used for product funnel analysis, including:
- total visitors
- total signups
- total activations
- total conversions
- total revenue
- signup, activation, and conversion rates

### `fct_channel_performance`
Channel-level performance table used to compare acquisition efficiency and monetisation outcomes, including:
- total users
- total signups
- total activations
- total converted users
- total revenue
- signup, activation, and conversion rates

### `fct_conversion_cohorts`
Cohort-level performance table used for monthly and channel-based cohort analysis, including:
- cohort users
- signed up users
- activated users
- converted users
- cohort revenue
- funnel stage rates

## Key KPIs

The project calculates and surfaces the following metrics:

- Total Visitors
- Total Signups
- Total Activations
- Total Converted Users
- Visitor-to-Conversion Rate
- Total Revenue
- Monthly Signup Rate
- Monthly Activation Rate
- Monthly Visitor-to-Conversion Rate
- Monthly Signup-to-Conversion Rate
- Revenue by Acquisition Channel
- Revenue by Plan
- Conversion Rate by Country
- Average Revenue per Converted User

## Dashboard Features

The Streamlit dashboard includes:

- KPI summary cards
- monthly funnel volume chart
- monthly funnel rate chart
- revenue by acquisition channel chart
- revenue by plan chart
- conversion rate by country chart
- average revenue per converted user chart
- detailed performance tables
- business insight summaries

### Interactive Filters
The dashboard supports filtering by:

- acquisition channel
- country
- device type
- cohort month range

## Project Structure

```text
product-funnel-conversion-analytics-warehouse/
│
├── data/
│   └── raw/
│       ├── users.csv
│       ├── sessions.csv
│       ├── events.csv
│       ├── signups.csv
│       └── conversions.csv
│
├── database/
│   └── product_funnel_analytics.db
│
├── sql/
│   ├── schema.sql
│   ├── staging.sql
│   ├── marts.sql
│   └── kpi_queries.sql
│
├── scripts/
│   ├── build_database.py
│   ├── generate_sample_data.py
│   ├── load_csvs.py
│   ├── run_staging.py
│   ├── run_marts.py
│   ├── check_database.py
│   └── run_kpis.py
│
├── dashboard/
│   └── app.py
│
├── images/
│
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd product-funnel-conversion-analytics-warehouse
```

### 2. Create and activate a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## How to Run the Project

Run the pipeline in this order:

### 1. Build the database schema

```bash
python scripts/build_database.py
```

### 2. Generate the sample source data

```bash
python scripts/generate_sample_data.py
```

### 3. Load CSV data into the raw tables

```bash
python scripts/load_csvs.py
```

### 4. Create the staging layer

```bash
python scripts/run_staging.py
```

### 5. Create the mart layer

```bash
python scripts/run_marts.py
```

### 6. Validate table counts and sample outputs

```bash
python scripts/check_database.py
```

### 7. Run KPI outputs in the terminal

```bash
python scripts/run_kpis.py
```

### 8. Launch the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

## Example Business Findings

Using the generated sample data, the dashboard highlighted insights such as:

- Organic Search and Direct performed strongly as revenue-driving acquisition channels
- Pro generated the highest total revenue among converted plans
- funnel performance varied meaningfully across monthly cohorts
- the largest drop-off occurred between key funnel stages, showing where optimisation effort should focus
- revenue and conversion efficiency differed across geographies and devices

## Why This Project Is Valuable

This project demonstrates more than dashboard building. It shows how to:

- structure a product analytics warehouse
- work with multiple related user, session, event, and conversion tables
- write reusable SQL transformations
- move from raw data to reporting-ready marts
- build funnel and conversion metrics from behavioural data
- connect a relational warehouse to an interactive front end

It is especially useful as a portfolio project for roles related to:

- data analytics
- product analytics
- business intelligence
- analytics engineering
- growth analytics
- junior data engineering

## Future Improvements

Possible extensions for future versions include:

- multi-step event sequence analysis
- retention cohorts after conversion
- attribution modelling
- lead scoring or conversion prediction
- A/B test simulation and experiment analysis
- automated data quality checks
- dashboard styling upgrades
- deployment to Streamlit Community Cloud

## Author

**Owen Nda Diche**  
MSc Data Science  
University of Hertfordshire

## License

This project is for educational and portfolio use.
