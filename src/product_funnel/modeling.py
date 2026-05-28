from __future__ import annotations

import json
import pickle
from dataclasses import asdict, dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from product_funnel.database import connect, query_dataframe
from product_funnel.paths import load_config, model_dir, report_dir


@dataclass
class ModelMetrics:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float


FEATURE_COLUMNS = [
    "acquisition_channel",
    "country",
    "device_type",
    "signup_method",
    "session_count",
    "total_session_minutes",
    "avg_session_minutes",
    "event_count",
    "pricing_views",
    "signup_started_events",
    "signup_completed_events",
    "activation_events",
    "unique_landing_pages",
    "days_to_signup",
    "days_to_activation",
    "did_signup",
    "did_activate",
]

CATEGORICAL_FEATURES = [
    "acquisition_channel",
    "country",
    "device_type",
    "signup_method",
]

NUMERIC_FEATURES = [column for column in FEATURE_COLUMNS if column not in CATEGORICAL_FEATURES]


def load_feature_frame() -> pd.DataFrame:
    return query_dataframe("SELECT * FROM mart_user_features")


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def evaluate_model(model_name: str, pipeline: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> ModelMetrics:
    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    return ModelMetrics(
        model_name=model_name,
        accuracy=round(float(accuracy_score(y_test, predictions)), 4),
        precision=round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        recall=round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        f1=round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        roc_auc=round(float(roc_auc_score(y_test, probabilities)), 4),
    )


def train_conversion_models() -> dict[str, object]:
    config = load_config()
    dataframe = load_feature_frame()
    target = config["target"]

    if dataframe[target].nunique() < 2:
        raise ValueError("Model training requires at least two target classes.")

    x = dataframe[FEATURE_COLUMNS]
    y = dataframe[target].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=float(config["test_size"]),
        random_state=int(config["random_state"]),
        stratify=y,
    )

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            min_samples_leaf=5,
            random_state=int(config["random_state"]),
            class_weight="balanced",
        ),
    }

    metrics: list[ModelMetrics] = []
    fitted_models: dict[str, Pipeline] = {}

    for name, estimator in candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)
        fitted_models[name] = pipeline
        metrics.append(evaluate_model(name, pipeline, x_test, y_test))

    best_metrics = max(metrics, key=lambda item: item.roc_auc)
    best_model = fitted_models[best_metrics.model_name]

    model_path = model_dir() / "conversion_propensity_model.pkl"
    metrics_path = report_dir() / "model_metrics.json"
    scores_path = report_dir() / "conversion_propensity_scores.csv"

    with open(model_path, "wb") as file:
        pickle.dump(best_model, file)

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "best_model": best_metrics.model_name,
                "metrics": [asdict(item) for item in metrics],
                "feature_columns": FEATURE_COLUMNS,
            },
            file,
            indent=2,
        )

    scored = dataframe[
        [
            "user_id",
            "acquisition_channel",
            "country",
            "device_type",
            "did_convert",
            "total_revenue",
        ]
    ].copy()
    scored["conversion_probability"] = best_model.predict_proba(x)[:, 1].round(4)
    scored["risk_segment"] = pd.cut(
        scored["conversion_probability"],
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["low", "medium", "high"],
    ).astype(str)
    scored.sort_values("conversion_probability", ascending=False).to_csv(scores_path, index=False)

    with connect() as connection:
        scored.to_sql("mart_conversion_scores", connection, if_exists="replace", index=False)

    return {
        "best_model": best_metrics.model_name,
        "metrics": [asdict(item) for item in metrics],
        "model_path": str(model_path),
        "scores_path": str(scores_path),
    }
