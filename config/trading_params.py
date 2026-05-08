# ==========================================
# STRATEGY PARAMETERS (FINAL CLEAN)
# ==========================================

# ==========================================
# MODE SWITCH (IMPORTANT)
# ==========================================
test_mode = True   #  True = equity testing | False = live options


# ==========================================
# FIBONACCI RATIOS
# ==========================================
FIB_RATIOS = [
    4.236, 3.618, 2.618, 1.618, 1,
    0.618, 0.5, 0.382, 0,
    -0.618, -1, -1.618, -2.618, -3.618, -4.236
]


# ==========================================
# ENTRY & STOP LOSS
# ==========================================
if test_mode:
    SL_POINTS = 10   # small SL for equity testing
else:
    SL_POINTS = 25  # real strategy value (options)


# ==========================================
# TRAILING SL RULES
# ==========================================
if test_mode:
    # ---- FAST TRAILING (EQUITY TESTING) ----
    TRAILING_RULES = {
        5: 2,
        6: 3,
        7: 4,
        9: 5,
        12: 6,
        15: 10,
        20: 16,
        25: 20
    }
else:
    # ---- REAL OPTIONS TRAILING ----
    TRAILING_RULES = {
        100: 30,
        200: 50,
        400: 200,
        600: 400,
        800: 700,
        1000: 900,
        1200: 1100
    }


# ==========================================
# TRADE RULES
# ==========================================
ALLOW_ONLY_ONE_ACTIVE_TRADE_PER_SIDE = True
ENABLE_FIRST_TRADE_TRIGGER_LOGIC = True


# ==========================================
# RISK CONTROL
# ==========================================
if test_mode:
    MAX_TRADES_PER_DAY = 50
    MAX_DAILY_LOSS = 1000
else:
    MAX_TRADES_PER_DAY = 10
    MAX_DAILY_LOSS = 6000


# ==========================================
# EXECUTION SETTINGS
# ==========================================
USE_MARKET_ORDER_FOR_EXIT = True
USE_STOP_ORDER_FOR_ENTRY = True