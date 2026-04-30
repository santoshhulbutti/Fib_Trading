# ==========================================
# STRATEGY PARAMETERS
# ==========================================

# -------- FIBONACCI RATIOS --------
FIB_RATIOS = [
    4.236, 3.618, 2.618, 1.618, 1,
    0.618, 0.5, 0.382, 0,
    -0.618, -1, -1.618, -2.618, -3.618, -4.236
]

# -------- ENTRY --------
SL_POINTS = 2   # fixed stop loss

# -------- TRAILING SL RULES --------
# format: move_from_entry : new_SL_from_entry

TRAILING_RULES = {
    # 100: 50,
    # 200: 100,
    # 400: 200,
    # 600: 400,
    # 800: 700,
    # 1000: 900,
    # 1200: 1100
    5: 2,
    6: 3,
    7: 4,
    9: 5,
    12: 6,
    15: 10,
    20: 16,
    25: 20
}

# -------- TRADE RULES --------
ALLOW_ONLY_ONE_ACTIVE_TRADE_PER_SIDE = True
ENABLE_FIRST_TRADE_TRIGGER_LOGIC = True

# -------- RISK CONTROL --------
MAX_TRADES_PER_DAY = 10 #earlier was 50
MAX_DAILY_LOSS = 100 #earlier was 6000 # optional (you can enforce later)

# -------- EXECUTION --------
USE_MARKET_ORDER_FOR_EXIT = True
USE_STOP_ORDER_FOR_ENTRY = True