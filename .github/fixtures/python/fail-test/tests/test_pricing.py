from app.pricing import apply_discount


def test_should_apply_percentage_discount() -> None:
    assert apply_discount(200.0, 10) == 190.0  # Defect: wrong expectation
