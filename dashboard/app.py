from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "product_funnel_analytics.db"
MODEL_METRICS_PATH = BASE_DIR / "reports" / "model_metrics.json"


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
    SELECT
        user_id,
        cohort_month,
        acquisition_channel,
        country,
        device_type,
        did_signup,
        did_activate,
        did_convert,
        conversion_count,
        total_revenue,
        signup_method,
        session_count,
        event_count,
        pricing_views,
        days_to_signup,
        days_to_activation
    FROM mart_user_features
    ORDER BY cohort_month, user_id;
    """
    df = run_query(query)

    numeric_cols = [
        "did_signup",
        "did_activate",
        "did_convert",
        "conversion_count",
        "total_revenue",
        "session_count",
        "event_count",
        "pricing_views",
        "days_to_signup",
        "days_to_activation",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    text_cols = [
        "user_id",
        "cohort_month",
        "acquisition_channel",
        "country",
        "device_type",
        "signup_method",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


@st.cache_data
def load_model_scores() -> pd.DataFrame:
    try:
        scores = run_query("SELECT * FROM mart_conversion_scores")
    except Exception:
        return pd.DataFrame()

    if scores.empty:
        return scores

    scores["conversion_probability"] = pd.to_numeric(
        scores["conversion_probability"], errors="coerce"
    ).fillna(0)
    scores["did_convert"] = pd.to_numeric(scores["did_convert"], errors="coerce").fillna(0)
    scores["total_revenue"] = pd.to_numeric(scores["total_revenue"], errors="coerce").fillna(0)
    return scores


def load_model_metrics() -> dict:
    if not MODEL_METRICS_PATH.exists():
        return {}

    with open(MODEL_METRICS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def format_currency(value: float) -> str:
    return f"GBP {value:,.2f}"


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


def build_segment_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, as_index=False)
        .agg(
            total_users=("user_id", "nunique"),
            total_signups=("did_signup", "sum"),
            total_activations=("did_activate", "sum"),
            total_converted_users=("did_convert", "sum"),
            total_revenue=("total_revenue", "sum"),
            avg_sessions=("session_count", "mean"),
            avg_events=("event_count", "mean"),
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
    summary["avg_sessions"] = summary["avg_sessions"].round(2)
    summary["avg_events"] = summary["avg_events"].round(2)
    summary["total_revenue"] = summary["total_revenue"].round(2)
    return summary


def build_plan_summary(df: pd.DataFrame) -> pd.DataFrame:
    conversions = run_query(
        """
        SELECT c.user_id, c.plan_name, c.revenue
        FROM stg_conversions c
        """
    )
    conversions = conversions[conversions["user_id"].isin(df["user_id"])]
    if conversions.empty:
        return pd.DataFrame(
            columns=["plan_name", "converted_users", "total_revenue", "avg_revenue_per_conversion"]
        )

    summary = (
        conversions.groupby("plan_name", as_index=False)
        .agg(
            converted_users=("user_id", "nunique"),
            total_revenue=("revenue", "sum"),
            avg_revenue_per_conversion=("revenue", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["avg_revenue_per_conversion"] = summary["avg_revenue_per_conversion"].round(2)
    return summary


def build_display_table(
    df: pd.DataFrame,
    currency_cols: list[str] | None = None,
    pct_cols: list[str] | None = None,
) -> pd.DataFrame:
    display_df = df.copy()
    for col in currency_cols or []:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(format_currency)
    for col in pct_cols or []:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda value: "" if pd.isna(value) else f"{value:.2f}%")
    return display_df


st.set_page_config(
    page_title="Product Funnel Analytics and Conversion Modeling",
    layout="wide",
)

st.title("Product Funnel Analytics and Conversion Modeling")
st.write(
    "A warehouse-backed product analytics project with funnel reporting, data quality checks, "
    "feature engineering, and conversion propensity scoring."
)

if not DB_PATH.exists():
    st.error("Database file not found. Run `python scripts/run_pipeline.py` first.")
    st.stop()

try:
    base_df = load_base_data()
except Exception as exc:
    st.error(f"Analytics tables are not ready yet: {exc}")
    st.stop()

if base_df.empty:
    st.error("No data was found in the analytics tables.")
    st.stop()

model_scores_df = load_model_scores()
model_metrics = load_model_metrics()

st.sidebar.header("Filters")
channel_options = sorted(base_df["acquisition_channel"].dropna().unique().tolist())
country_options = sorted(base_df["country"].dropna().unique().tolist())
device_options = sorted(base_df["device_type"].dropna().unique().tolist())
month_options = sorted(base_df["cohort_month"].dropna().unique().tolist())

selected_channels = st.sidebar.multiselect("Acquisition Channel", channel_options, default=channel_options)
selected_countries = st.sidebar.multiselect("Country", country_options, default=country_options)
selected_devices = st.sidebar.multiselect("Device Type", device_options, default=device_options)
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

filtered_scores_df = pd.DataFrame()
if not model_scores_df.empty:
    filtered_scores_df = model_scores_df[model_scores_df["user_id"].isin(filtered_df["user_id"])].copy()

monthly_df = build_monthly_funnel(filtered_df)
channel_summary_df = build_segment_summary(filtered_df, "acquisition_channel")
country_summary_df = build_segment_summary(filtered_df, "country")
device_summary_df = build_segment_summary(filtered_df, "device_type")
plan_summary_df = build_plan_summary(filtered_df)

total_visitors = filtered_df["user_id"].nunique()
total_signups = int(filtered_df["did_signup"].sum())
total_activations = int(filtered_df["did_activate"].sum())
total_converted_users = int(filtered_df["did_convert"].sum())
total_revenue = float(filtered_df["total_revenue"].sum())
visitor_to_conversion_rate = round(total_converted_users * 100.0 / total_visitors, 2)
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
metric_4.metric("Converted Users", f"{total_converted_users:,}")
metric_5.metric("Conversion Rate", f"{visitor_to_conversion_rate:.2f}%")
metric_6.metric("Total Revenue", format_currency(total_revenue))

st.subheader("Monthly Funnel")
volume_chart = monthly_df.set_index("cohort_month")[
    ["total_visitors", "total_signups", "total_activations", "total_conversions"]
]
st.line_chart(volume_chart, use_container_width=True)

rate_chart = monthly_df.set_index("cohort_month")[
    ["signup_rate_pct", "activation_rate_pct", "visitor_to_conversion_rate_pct"]
]
st.line_chart(rate_chart, use_container_width=True)

col_1, col_2 = st.columns(2)
with col_1:
    st.subheader("Revenue by Channel")
    st.bar_chart(channel_summary_df.set_index("acquisition_channel")[["total_revenue"]], use_container_width=True)

with col_2:
    st.subheader("Conversion Rate by Country")
    st.bar_chart(country_summary_df.set_index("country")[["conversion_rate_pct"]], use_container_width=True)

st.subheader("Insights")
data_driven_insights: list[str] = []
model_driven_insights: list[str] = []

top_channel = channel_summary_df.iloc[0]
data_driven_insights.append(
    f"{top_channel['acquisition_channel']} is the top revenue-generating channel, "
    f"contributing {format_currency(top_channel['total_revenue'])}."
)

best_month = monthly_df.sort_values("visitor_to_conversion_rate_pct", ascending=False).iloc[0]
data_driven_insights.append(
    f"The strongest visitor-to-conversion month was {best_month['cohort_month']} "
    f"at {best_month['visitor_to_conversion_rate_pct']:.2f}%."
)

dropoffs = {
    "visitor to signup": total_visitors - total_signups,
    "signup to activation": total_signups - total_activations,
    "activation to conversion": total_activations - total_converted_users,
}
largest_dropoff_stage = max(dropoffs, key=dropoffs.get)
data_driven_insights.append(
    f"The largest funnel drop-off is {largest_dropoff_stage}, with "
    f"{dropoffs[largest_dropoff_stage]:,} users not progressing."
)

if not filtered_scores_df.empty:
    high_propensity_count = int((filtered_scores_df["risk_segment"] == "high").sum())
    avg_probability = float(filtered_scores_df["conversion_probability"].mean() * 100)
    model_driven_insights.append(
        f"The trained model flags {high_propensity_count:,} high-propensity user(s), "
        f"with an average predicted conversion probability of {avg_probability:.2f}%."
    )

if model_metrics:
    model_driven_insights.append(
        f"The current best model is {model_metrics.get('best_model', '').replace('_', ' ').title()}."
    )

model_driven_insights.append(
    "The strongest next experiment candidates are high-propensity users who have viewed pricing "
    "or started signup but have not converted."
)

st.markdown("**Data-driven insights**")
for insight in data_driven_insights:
    st.write(f"- {insight}")

st.markdown("**Model-driven insights**")
for insight in model_driven_insights:
    st.write(f"- {insight}")

st.subheader("Detailed Tables")
tab_1, tab_2, tab_3, tab_4, tab_5, tab_6 = st.tabs(
    [
        "Monthly Funnel",
        "Channel Performance",
        "Country Performance",
        "Device Performance",
        "Conversion Model",
        "User Features",
    ]
)

with tab_1:
    st.dataframe(
        build_display_table(
            monthly_df,
            currency_cols=["total_revenue"],
            pct_cols=[
                "signup_rate_pct",
                "activation_rate_pct",
                "visitor_to_conversion_rate_pct",
                "signup_to_conversion_rate_pct",
                "activation_to_conversion_rate_pct",
            ],
        ),
        use_container_width=True,
    )

with tab_2:
    st.dataframe(
        build_display_table(
            channel_summary_df,
            currency_cols=["total_revenue"],
            pct_cols=["signup_rate_pct", "activation_rate_pct", "conversion_rate_pct"],
        ),
        use_container_width=True,
    )

with tab_3:
    st.dataframe(
        build_display_table(
            country_summary_df,
            currency_cols=["total_revenue"],
            pct_cols=["signup_rate_pct", "activation_rate_pct", "conversion_rate_pct"],
        ),
        use_container_width=True,
    )

with tab_4:
    st.dataframe(
        build_display_table(
            device_summary_df,
            currency_cols=["total_revenue"],
            pct_cols=["signup_rate_pct", "activation_rate_pct", "conversion_rate_pct"],
        ),
        use_container_width=True,
    )
    if not plan_summary_df.empty:
        st.markdown("**Plan Performance**")
        st.dataframe(
            build_display_table(
                plan_summary_df,
                currency_cols=["total_revenue", "avg_revenue_per_conversion"],
            ),
            use_container_width=True,
        )

with tab_5:
    if filtered_scores_df.empty:
        st.info("Model scores are not available yet. Run `python scripts/run_pipeline.py`.")
    else:
        score_1, score_2, score_3 = st.columns(3)
        score_1.metric(
            "Average Probability",
            f"{filtered_scores_df['conversion_probability'].mean() * 100:.2f}%",
        )
        score_2.metric("High Propensity Users", f"{int((filtered_scores_df['risk_segment'] == 'high').sum()):,}")
        score_3.metric("Best Model", model_metrics.get("best_model", "Not available").replace("_", " ").title())

        if model_metrics:
            st.dataframe(pd.DataFrame(model_metrics.get("metrics", [])), use_container_width=True)

        segment_summary = (
            filtered_scores_df.groupby("risk_segment", as_index=False)
            .agg(
                users=("user_id", "nunique"),
                actual_conversions=("did_convert", "sum"),
                avg_probability=("conversion_probability", "mean"),
                total_revenue=("total_revenue", "sum"),
            )
            .sort_values("avg_probability", ascending=False)
        )
        segment_summary["avg_probability"] = (segment_summary["avg_probability"] * 100).round(2)
        segment_summary["total_revenue"] = segment_summary["total_revenue"].round(2)

        st.markdown("**Propensity Segments**")
        st.dataframe(
            build_display_table(
                segment_summary,
                currency_cols=["total_revenue"],
                pct_cols=["avg_probability"],
            ),
            use_container_width=True,
        )

        top_scores = filtered_scores_df.sort_values("conversion_probability", ascending=False).head(25)
        top_scores = top_scores.copy()
        top_scores["conversion_probability"] = (top_scores["conversion_probability"] * 100).round(2)
        st.markdown("**Top Scored Users**")
        st.dataframe(
            build_display_table(
                top_scores,
                currency_cols=["total_revenue"],
                pct_cols=["conversion_probability"],
            ),
            use_container_width=True,
        )

with tab_6:
    user_columns = [
        "cohort_month",
        "user_id",
        "acquisition_channel",
        "country",
        "device_type",
        "signup_method",
        "did_signup",
        "did_activate",
        "did_convert",
        "session_count",
        "event_count",
        "pricing_views",
        "conversion_count",
        "total_revenue",
    ]
    st.dataframe(
        build_display_table(filtered_df[user_columns].copy(), currency_cols=["total_revenue"]),
        use_container_width=True,
    )

st.subheader("Summary")
st.write(
    f"This filtered view contains {total_visitors:,} visitors, {total_signups:,} signups, "
    f"{total_activations:,} activations, and {total_converted_users:,} converted users. "
    f"The average revenue per converted user is {format_currency(avg_revenue_per_converted_user)}."
)
