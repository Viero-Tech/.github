def apply_discount(amount: float, percent: float) -> float:
    return round(amount * (1 - percent / 100), 2)


# Defect: a type error. ruff accepts it; mypy rejects it.
DEFAULT_PERCENT: int = "ten"
