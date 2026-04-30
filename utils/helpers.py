# ==========================================
# HELPER FUNCTIONS
# ==========================================

def round_to_step(price, step):
    """
    Round price to nearest step (e.g., 100 for Sensex)
    """
    return int(round(price / step) * step)


def safe_get(data, key, default=None):
    """
    Safe dictionary access
    """
    return data[key] if key in data else default


def is_valid_price(price):
    """
    Basic price validation
    """
    return price is not None and price > 0


def percentage_change(old, new):
    """
    Calculate % change
    """
    if old == 0:
        return 0
    return ((new - old) / old) * 100


def clamp(value, min_val, max_val):
    """
    Restrict value within bounds
    """
    return max(min_val, min(value, max_val))


def format_price(price):
    """
    Standardize price format
    """
    return round(price, 2)