# ==========================================
# EVENT DETECTION (NO LOGIC, ONLY SIGNALS)
# ==========================================

import bisect




# ------------------------------------------
# FIND LEVEL BAND (FAST)
# ------------------------------------------
def get_level_index(price, levels, last_index=None):

    if last_index is not None:
        if 0 <= last_index < len(levels) - 1:
            if levels[last_index] <= price <= levels[last_index + 1]:
                return last_index

    idx = bisect.bisect_left(levels, price) - 1
    idx = max(0, min(idx, len(levels) - 2))

    return idx


# ------------------------------------------
# CROSS DETECTION
# ------------------------------------------
def detect_cross(prev_price, curr_price, level):

    if prev_price is None:
        return False

    # Cross from below
    if prev_price < level and curr_price >= level:
        return "CROSS_UP"

    # Cross from above
    if prev_price > level and curr_price <= level:
        return "CROSS_DOWN"

    return None


# ------------------------------------------
# TRIGGER HIT (FIRST TRADE)
# ------------------------------------------
# def trigger_hit(price, trigger_price, tick_size):
#     return trigger_price - tick_size < price < trigger_price + tick_size

def trigger_hit(price, trigger_price):
    return trigger_price-0.15 < price < trigger_price+0.15

# def trigger_hit(price, trigger_price):
#     return price >= trigger_price

# def trigger_short_hit(price, trigger_s_price):
#     return price >= trigger_s_price

# ------------------------------------------
# SL HIT
# ------------------------------------------
def sl_hit(price, sl_price):
    return price <= sl_price


# ------------------------------------------
# TRAILING SL CALCULATION
# ------------------------------------------
def calculate_trailing_sl(entry, current_price, rules):

    move = current_price - entry
    new_sl = None

    # Iterate rules in ascending order
    for move_level in sorted(rules.keys()):
        if move >= move_level:
            new_sl = entry + rules[move_level]

    return new_sl