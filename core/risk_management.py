# ==========================================
# RISK MANAGEMENT ENGINE
# ==========================================
from config.settings import CAPITAL
from utils.symbol_master import get_tick_size, get_lot_size, round_to_tick
from utils.logger import log, error_log


# ==========================================
# CONFIG
# ==========================================

# risk per trade
RISK_PERCENT = 1.0

# minimum SL %
MIN_SL_PERCENT = 0.3

# maximum SL %
MAX_SL_PERCENT = 2.0


# ==========================================
# CALCULATE RISK AMOUNT
# ==========================================
def calculate_risk_amount(capital=None):

    try:
        if capital is None:
            capital = CAPITAL

        risk_amount = (capital * RISK_PERCENT) / 100
        return round(risk_amount, 2)

    except Exception as e:
        error_log(f"RISK AMOUNT ERROR: {e}")
        return 0

# ==========================================
# CALCULATE SL POINTS
# ==========================================
def calculate_sl_points(symbol, price):

    try:
        # ----------------------------------
        # DYNAMIC SL MODEL
        # ----------------------------------
        # Example:
        # low-priced stocks -> tighter SL
        # high-priced stocks -> wider SL
        # ----------------------------------
        if price < 100:
            sl_percent = 1.0

        elif price < 500:
            sl_percent = 0.7

        elif price < 1000:
            sl_percent = 0.5

        else:
            sl_percent = 0.3

        # safety bounds
        sl_percent = max(MIN_SL_PERCENT, min(sl_percent, MAX_SL_PERCENT))
        sl_points = (price * sl_percent) / 100

        # ----------------------------------
        # ROUND TO TICK
        # ----------------------------------
        sl_points = round_to_tick(sl_points, symbol)

        return sl_points

    except Exception as e:
        error_log(f"SL POINTS ERROR | {symbol} | {e}")
        return None

# ==========================================
# CALCULATE QUANTITY
# ==========================================
def calculate_quantity(symbol, capital, risk_percent, sl_points, price):

    try:
        # ----------------------------------
        # VALIDATION
        # ----------------------------------
        if sl_points <= 0:
            return 0

        # ----------------------------------
        # RISK AMOUNT
        # ----------------------------------
        risk_amount = (capital * risk_percent) / 100

        # ----------------------------------
        # POSITION SIZE
        # ----------------------------------
        qty = int(risk_amount / sl_points)

        # ----------------------------------
        # CAPITAL CHECK
        # ----------------------------------
        max_affordable_qty = int(capital / price)
        qty = min(qty, max_affordable_qty)

        # ----------------------------------
        # LOT SIZE NORMALIZATION
        # ----------------------------------
        lot_size = get_lot_size(symbol)
        if lot_size and lot_size > 1:
            qty = (qty // lot_size) * lot_size

        # minimum qty
        qty = max(qty, 1)
        return qty

    except Exception as e:
        error_log(f"QUANTITY ERROR | {symbol} | {e}")

        return 0


# ==========================================
# FULL RISK PROFILE
# ==========================================
def get_trade_risk_profile(symbol, price, capital=None, risk_percent=None):

    try:
        if capital is None:
            capital = CAPITAL

        if risk_percent is None:
            risk_percent = RISK_PERCENT

        # ----------------------------------
        # SL
        # ----------------------------------
        sl_points = calculate_sl_points(symbol, price)

        if not sl_points:
            return None

        # ----------------------------------
        # QUANTITY
        # ----------------------------------
        qty = calculate_quantity(symbol=symbol, capital=capital, risk_percent=risk_percent, sl_points=sl_points, price=price)

        # ----------------------------------
        # RISK AMOUNT
        # ----------------------------------
        risk_amount = (qty * sl_points)

        profile = {

            "symbol": symbol,
            "price": price,
            "capital": capital,
            "risk_percent": risk_percent,
            "sl_points": sl_points,
            "quantity": qty,
            "risk_amount": round(risk_amount,2)
        }

        return profile

    except Exception as e:
        error_log(f"RISK PROFILE ERROR | {symbol} | {e}")
        return None