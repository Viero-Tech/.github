def apply_discount(amount: float, percent: float) -> float:
    return round(amount * (1 - percent / 100), 2)
