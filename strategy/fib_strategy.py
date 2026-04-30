# ==========================================
# FIBONACCI STRATEGY (PURE LOGIC LAYER)
# ==========================================

from config.trading_params import FIB_RATIOS, SL_POINTS, TRAILING_RULES


# ------------------------------------------
# GENERATE FIBONACCI LEVELS
# ------------------------------------------
def generate_fib_levels(prev_high, prev_low):
    """
    Generate Fibonacci levels based on previous day range
    Returns sorted levels (ascending)
    """

    diff = prev_high - prev_low

    levels = [round(prev_high - diff * r, 2) for r in FIB_RATIOS]

    levels = sorted(set(levels))  # remove duplicates if any

    return levels


# ------------------------------------------
# GET TRIGGER PRICE (FIRST TRADE)
# ------------------------------------------
def get_trigger_price(level):
    """
    Trigger = level - SL_POINTS
    Used only for first trade
    """
    return level - SL_POINTS


# ------------------------------------------
# FIRST TRADE CONDITION
# ------------------------------------------
def should_place_first_trade(price, level):
    """
    Condition:
    price must go below trigger price
    """

    trigger = get_trigger_price(level)

    return price <= trigger


# ------------------------------------------
# SUBSEQUENT TRADE CONDITION
# ------------------------------------------
def should_place_subsequent_trade(prev_price, curr_price, level):
    """
    Condition:
    price crosses level from below
    """

    if prev_price is None:
        return False

    return prev_price < level and curr_price >= level


# ------------------------------------------
# STOP LOSS CALCULATION
# ------------------------------------------
def calculate_sl(entry_price):
    """
    Fixed SL
    """
    return entry_price - SL_POINTS


# ------------------------------------------
# TRAILING SL LOGIC
# ------------------------------------------
def calculate_trailing_sl(entry_price, current_price):
    """
    Apply trailing SL rules based on move from entry
    """

    move = current_price - entry_price
    new_sl = None

    # Iterate in ascending order
    for move_level in sorted(TRAILING_RULES.keys()):
        if move >= move_level:
            new_sl = entry_price + TRAILING_RULES[move_level]

    return new_sl


# ------------------------------------------
# VALIDATE LEVEL CROSS (GENERIC)
# ------------------------------------------
def crossed_above(prev_price, curr_price, level):
    return prev_price < level and curr_price >= level


def crossed_below(prev_price, curr_price, level):
    return prev_price > level and curr_price <= level


# ------------------------------------------
# LEVEL BAND HELPER (OPTIONAL)
# ------------------------------------------
def get_level_band(price, levels):
    """
    Simple helper (not optimized)
    Engine should use fast method (bisect)
    """

    for i in range(1, len(levels)):
        if levels[i-1] <= price <= levels[i]:
            return levels[i-1], levels[i]

    return None, None


# ------------------------------------------
# STRATEGY DECISION WRAPPER (OPTIONAL)
# ------------------------------------------
def evaluate_entry(
    prev_price,
    curr_price,
    level,
    first_trade_done
):
    """
    Returns:
    "FIRST_ENTRY", "SUBSEQUENT_ENTRY", or None
    """

    # First trade
    if not first_trade_done:
        if should_place_first_trade(curr_price, level):
            return "FIRST_ENTRY"

    # Subsequent trades
    else:
        if should_place_subsequent_trade(prev_price, curr_price, level):
            return "SUBSEQUENT_ENTRY"

    return None