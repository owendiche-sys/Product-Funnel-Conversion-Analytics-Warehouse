from product_funnel.quality import CHECKS


def test_quality_checks_are_named() -> None:
    names = [check[0] for check in CHECKS]
    assert "users_unique" in names
    assert "revenue_non_negative" in names
    assert len(names) == len(set(names))
