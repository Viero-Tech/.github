def apply_discount(amount: float, percent: float) -> float:
    return round(amount * (1 - percent / 100), 2)


# Defect: an unused import at the bottom of the module. mypy accepts it; ruff rejects it.
import os  # noqa: E402
