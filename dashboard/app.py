from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"


@st.cache_data
def run_query(query: str) -> pd.DataFrame:
    connection = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


@st.cache_data
def load_base_data() -> pd.DataFrame:
    query = """
    WITH conversion_base AS (
        SELECT
            user_id,
            COUNT(DISTINCT conversion_id) AS conversion_count,
            ROUND(SUM(revenue), 2) AS total_revenue,
            MIN(plan_name) AS plan_name
        FROM stg_conversions
        GROUP BY user_id
    )
    SELECT
        u.user_id,
        u.first_seen_date,
        u.signup_date,
        u.activation_date,
        strftime('%Y-%m', u.first_seen_date) AS cohort_month,
        u.acquisition_channel,
        u.country,
        u.device_type,
        CASE WHEN u.signup_date IS NOT NULL THEN 1 ELSE 0 END AS did_signup,
        CASE WHEN u.activation_date IS NOT NULL THEN 1 ELSE 0 END AS did_activate,
        CASE WHEN cb.conversion_count > 0 THEN 1 ELSE 0 END AS did_convert,
        COALESCE(cb.conversion_count, 0) AS conversion_count,
        COALESCE(cb.total_revenue, 0) AS total_revenue,
        COALESCE(cb.plan_name, 'No Conversion') AS plan_name
    FROM dim_user u
    LEFT JOIN conversion_base cb
        ON u.user_id = cb.user_id
    ORDER BY cohort_month, u.user_id;
    """
    df = run_query(query)

    numeric_cols = [
        "did_signup",
        "did_activate",
        "did_convert",
        "conversion_count",
        "total_revenue",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    text_cols = [
        "user_id",
        "first_seen_date",
        "signup_date",
        "activation_date",
        "cohort_month",
        "acquisition_channel",
        "country",
        "device_type",
        "plan_name",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def format_currency(value: float) -> str:
    return f"£{value:,.2f}"


def build_monthly_funnel(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("cohort_month", as_index=False)
        .agg(
            total_visitors=("user_id", "nunique"),
            total_signups=("did_signup", "sum"),
            total_activations=("did_activate", "sum"),
            total_conversions=("did_convert", "sum"),
            total_revenue=("total_revenue", "sum"),
        )
        .sort_values("cohort_month")
    )

    monthly["signup_rate_pct"] = (
        monthly["total_signups"] * 100.0 / monthly["total_visitors"]
    ).round(2)

    monthly["activation_rate_pct"] = (
        monthly["total_activations"] * 100.0 / monthly["total_visitors"]
    ).round(2)

    monthly["visitor_to_conversion_rate_pct"] = (
        monthly["total_conversions"] * 100.0 / monthly["total_visitors"]
    ).round(2)

    monthly["signup_to_conversion_rate_pct"] = (
        monthly["total_conversions"] * 100.0
        / monthly["total_signups"].replace(0, pd.NA)
    ).round(2)

    monthly["activation_to_conversion_rate_pct"] = (
        monthly["total_conversions"] * 100.0
        / monthly["total_activations"].replace(0, pd.NA)
    ).round(2)

    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    return monthly


def build_channel_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("acquisition_channel", as_index=False)
        .agg(
            total_users=("user_id", "nunique"),
            total_signups=("did_signup", "sum"),
            total_activations=("did_activate", "sum"),
            total_converted_users=("did_convert", "sum"),
            total_revenue=("total_revenue", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    summary["signup_rate_pct"] = (
        summary["total_signups"] * 100.0 / summary["total_users"]
    ).round(2)

    summary["activation_rate_pct"] = (
        summary["total_activations"] * 100.0 / summary["total_users"]
    ).round(2)

    summary["conversion_rate_pct"] = (
        summary["total_converted_users"] * 100.0 / summary["total_users"]
    ).round(2)

    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def build_country_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("country", as_index=False)
        .agg(
            total_users=("user_id", "nunique"),
            total_signups=("did_signup", "sum"),
            total_activations=("did_activate", "sum"),
            total_converted_users=("did_convert", "sum"),
            total_revenue=("total_revenue", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    summary["conversion_rate_pct"] = (
        summary["total_converted_users"] * 100.0 / summary["total_users"]
    ).round(2)

    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def build_plan_summary(df: pd.DataFrame) -> pd.DataFrame:
    converted_df = df[df["did_convert"] == 1].copy()

    if converted_df.empty:
        return pd.DataFrame(
            columns=[
                "plan_name",
                "converted_users",
                "total_revenue",
                "avg_revenue_per_converted_user",
            ]
        )

    summary = (
        converted_df.groupby("plan_name", as_index=False)
        .agg(
            converted_users=("user_id", "nunique"),
            total_revenue=("total_revenue", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    summary["avg_revenue_per_converted_user"] = (
        summary["total_revenue"] / summary["converted_users"]
    ).round(2)

    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def build_display_table(
    df: pd.DataFrame,
    currency_cols: list[str] | None = None,
    pct_cols: list[str] | None = None,
) -> pd.DataFrame:
    display_df = df.copy()
    currency_cols = currency_cols or []
    pct_cols = pct_cols or []

    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(format_currency)

    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(
                lambda x: "" if pd.isna(x) else f"{x:.2f}%"
            )

    return display_df


st.set_page_config(
    page_title="Product Funnel & Conversion Analytics Warehouse",
    layout="wide",
)

st.title("Product Funnel & Conversion Analytics Warehouse")
st.write(
    "A SQL-based product analytics dashboard built with SQLite, SQL, Python, and Streamlit."
)

if not DB_PATH.exists():
    st.error("Database file not found. Build the database before running the dashboard.")
    st.stop()

base_df = load_base_data()

if base_df.empty:
    st.error("No data was found in the analytics tables.")
    st.stop()

st.sidebar.header("Filters")

channel_options = sorted(base_df["acquisition_channel"].dropna().unique().tolist())
country_options = sorted(base_df["country"].dropna().unique().tolist())
device_options = sorted(base_df["device_type"].dropna().unique().tolist())
month_options = sorted(base_df["cohort_month"].dropna().unique().tolist())

selected_channels = st.sidebar.multiselect(
    "Acquisition Channel",
    options=channel_options,
    default=channel_options,
)

selected_countries = st.sidebar.multiselect(
    "Country",
    options=country_options,
    default=country_options,
)

selected_devices = st.sidebar.multiselect(
    "Device Type",
    options=device_options,
    default=device_options,
)

selected_month_range = st.sidebar.select_slider(
    "Cohort Month Range",
    options=month_options,
    value=(month_options[0], month_options[-1]),
)

filtered_df = base_df[
    base_df["acquisition_channel"].isin(selected_channels)
    & base_df["country"].isin(selected_countries)
    & base_df["device_type"].isin(selected_devices)
    & (base_df["cohort_month"] >= selected_month_range[0])
    & (base_df["cohort_month"] <= selected_month_range[1])
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

monthly_df = build_monthly_funnel(filtered_df)
channel_summary_df = build_channel_summary(filtered_df)
country_summary_df = build_country_summary(filtered_df)
plan_summary_df = build_plan_summary(filtered_df)

total_visitors = filtered_df["user_id"].nunique()
total_signups = int(filtered_df["did_signup"].sum())
total_activations = int(filtered_df["did_activate"].sum())
total_converted_users = int(filtered_df["did_convert"].sum())
total_revenue = float(filtered_df["total_revenue"].sum())
visitor_to_conversion_rate = round(
    (total_converted_users * 100.0 / total_visitors), 2
) if total_visitors else 0.0

avg_revenue_per_converted_user = round(
    total_revenue / total_converted_users, 2
) if total_converted_users else 0.0

st.caption(
    f"Filtered view: {selected_month_range[0]} to {selected_month_range[1]} | "
    f"{len(selected_channels)} channel(s) | {len(selected_countries)} countr(y/ies) | "
    f"{len(selected_devices)} device type(s)"
)

metric_1, metric_2, metric_3, metric_4, metric_5, metric_6 = st.columns(6)
metric_1.metric("Total Visitors", f"{total_visitors:,}")
metric_2.metric("Total Signups", f"{total_signups:,}")
metric_3.metric("Total Activations", f"{total_activations:,}")
metric_4.metric("Total Converted Users", f"{total_converted_users:,}")
metric_5.metric("Visitor-to-Conversion Rate", f"{visitor_to_conversion_rate:.2f}%")
metric_6.metric("Total Revenue", format_currency(total_revenue))

st.subheader("Monthly Funnel Volume")
funnel_volume_chart = monthly_df[
    [
        "cohort_month",
        "total_visitors",
        "total_signups",
        "total_activations",
        "total_conversions",
    ]
].copy()
funnel_volume_chart = funnel_volume_chart.set_index("cohort_month")
st.line_chart(funnel_volume_chart, use_container_width=True)

st.subheader("Monthly Funnel Rates")
funnel_rate_chart = monthly_df[
    [
        "cohort_month",
        "signup_rate_pct",
        "activation_rate_pct",
        "visitor_to_conversion_rate_pct",
        "signup_to_conversion_rate_pct",
    ]
].copy()
funnel_rate_chart = funnel_rate_chart.set_index("cohort_month")
st.line_chart(funnel_rate_chart, use_container_width=True)

col_1, col_2 = st.columns(2)

with col_1:
    st.subheader("Revenue by Acquisition Channel")
    channel_chart = channel_summary_df[
        ["acquisition_channel", "total_revenue"]
    ].copy()
    channel_chart = channel_chart.set_index("acquisition_channel")
    st.bar_chart(channel_chart, use_container_width=True)

with col_2:
    st.subheader("Revenue by Plan")
    if not plan_summary_df.empty:
        plan_chart = plan_summary_df[["plan_name", "total_revenue"]].copy()
        plan_chart = plan_chart.set_index("plan_name")
        st.bar_chart(plan_chart, use_container_width=True)
    else:
        st.info("No conversions are available for the selected filters.")

col_3, col_4 = st.columns(2)

with col_3:
    st.subheader("Conversion Rate by Country")
    country_chart = country_summary_df[
        ["country", "conversion_rate_pct"]
    ].copy()
    country_chart = country_chart.set_index("country")
    st.bar_chart(country_chart, use_container_width=True)

with col_4:
    st.subheader("Average Revenue per Converted User")
    if not plan_summary_df.empty:
        arpu_chart = plan_summary_df[
            ["plan_name", "avg_revenue_per_converted_user"]
        ].copy()
        arpu_chart = arpu_chart.set_index("plan_name")
        st.bar_chart(arpu_chart, use_container_width=True)
    else:
        st.info("No conversion revenue is available for the selected filters.")

st.subheader("Insights")

data_driven_insights: list[str] = []
model_driven_insights: list[str] = []

if not channel_summary_df.empty:
    top_channel = channel_summary_df.iloc[0]
    data_driven_insights.append(
        f"{top_channel['acquisition_channel']} is the top revenue-generating channel, "
        f"contributing {format_currency(top_channel['total_revenue'])} from "
        f"{int(top_channel['total_converted_users'])} converted users."
    )

if not monthly_df.empty:
    best_month = monthly_df.sort_values(
        "visitor_to_conversion_rate_pct", ascending=False
    ).iloc[0]
    data_driven_insights.append(
        f"The strongest visitor-to-conversion month was {best_month['cohort_month']} "
        f"at {best_month['visitor_to_conversion_rate_pct']:.2f}%."
    )

if not plan_summary_df.empty:
    top_plan = plan_summary_df.iloc[0]
    data_driven_insights.append(
        f"{top_plan['plan_name']} generated the most revenue at "
        f"{format_currency(top_plan['total_revenue'])}."
    )

overall_dropoff_signup = total_visitors - total_signups
overall_dropoff_activation = total_signups - total_activations
overall_dropoff_conversion = total_activations - total_converted_users

largest_dropoff = max(
    [
        ("visitor_to_signup", overall_dropoff_signup),
        ("signup_to_activation", overall_dropoff_activation),
        ("activation_to_conversion", overall_dropoff_conversion),
    ],
    key=lambda x: x[1],
)

stage_map = {
    "visitor_to_signup": "visitor to signup",
    "signup_to_activation": "signup to activation",
    "activation_to_conversion": "activation to conversion",
}
data_driven_insights.append(
    f"The largest funnel drop-off occurs from {stage_map[largest_dropoff[0]]}, "
    f"with {largest_dropoff[1]:,} users not progressing to the next stage."
)

if not channel_summary_df.empty:
    best_channel = channel_summary_df.iloc[0]
    model_driven_insights.append(
        f"A conversion model would likely prioritize users from "
        f"{best_channel['acquisition_channel']}, because this channel currently "
        f"contributes the largest revenue base."
    )

if not country_summary_df.empty:
    highest_country = country_summary_df.sort_values(
        "conversion_rate_pct", ascending=False
    ).iloc[0]
    model_driven_insights.append(
        f"{highest_country['country']} appears to be the strongest candidate for "
        f"geo-targeted acquisition experiments because it currently shows the best "
        f"conversion efficiency within the filtered view."
    )

model_driven_insights.append(
    "A next predictive layer could estimate conversion probability using acquisition "
    "channel, country, device type, signup behaviour, and activation signals."
)

st.markdown("**Data-driven insights**")
for insight in data_driven_insights:
    st.write(f"- {insight}")

st.markdown("**Model-driven insights**")
for insight in model_driven_insights:
    st.write(f"- {insight}")

st.subheader("Detailed Tables")

tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs(
    [
        "Monthly Funnel",
        "Channel Performance",
        "Country Performance",
        "Plan Performance",
        "Filtered Users",
    ]
)

with tab_1:
    monthly_display_df = build_display_table(
        monthly_df,
        currency_cols=["total_revenue"],
        pct_cols=[
            "signup_rate_pct",
            "activation_rate_pct",
            "visitor_to_conversion_rate_pct",
            "signup_to_conversion_rate_pct",
            "activation_to_conversion_rate_pct",
        ],
    )
    st.dataframe(monthly_display_df, use_container_width=True)

with tab_2:
    channel_display_df = build_display_table(
        channel_summary_df,
        currency_cols=["total_revenue"],
        pct_cols=["signup_rate_pct", "activation_rate_pct", "conversion_rate_pct"],
    )
    st.dataframe(channel_display_df, use_container_width=True)

with tab_3:
    country_display_df = build_display_table(
        country_summary_df,
        currency_cols=["total_revenue"],
        pct_cols=["conversion_rate_pct"],
    )
    st.dataframe(country_display_df, use_container_width=True)

with tab_4:
    if not plan_summary_df.empty:
        plan_display_df = build_display_table(
            plan_summary_df,
            currency_cols=["total_revenue", "avg_revenue_per_converted_user"],
        )
        st.dataframe(plan_display_df, use_container_width=True)
    else:
        st.info("No plan-level conversion data is available for the selected filters.")

with tab_5:
    user_columns = [
        "cohort_month",
        "user_id",
        "acquisition_channel",
        "country",
        "device_type",
        "did_signup",
        "did_activate",
        "did_convert",
        "plan_name",
        "conversion_count",
        "total_revenue",
    ]
    user_display_df = build_display_table(
        filtered_df[user_columns].copy(),
        currency_cols=["total_revenue"],
    )
    st.dataframe(user_display_df, use_container_width=True)

st.subheader("Summary")
st.write(
    f"This filtered view contains {total_visitors:,} visitors, {total_signups:,} signups, "
    f"{total_activations:,} activations, and {total_converted_users:,} converted users. "
    f"The current average revenue per converted user is {format_currency(avg_revenue_per_converted_user)}."
)