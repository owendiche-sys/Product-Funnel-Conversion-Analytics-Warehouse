from product_funnel.modeling import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES


def test_model_feature_contract_has_target_signals() -> None:
    assert "did_signup" in FEATURE_COLUMNS
    assert "did_activate" in FEATURE_COLUMNS
    assert "event_count" in FEATURE_COLUMNS
    assert set(CATEGORICAL_FEATURES).isdisjoint(NUMERIC_FEATURES)
