# ==========================================
# INSTRUMENT & SYMBOL UTILITIES (FINAL FIXED)
# ==========================================

import datetime
import json
from pathlib import Path


# ------------------------------------------
# MONTH MAP (CRITICAL FIX FOR FYERS)
# ------------------------------------------
MONTH_MAP = {
    1: "1", 2: "2", 3: "3", 4: "4",
    5: "5", 6: "6", 7: "7", 8: "8",
    9: "9", 10: "O", 11: "N", 12: "D"
}


# ------------------------------------------
# LOAD HOLIDAYS
# ------------------------------------------
def load_holidays():
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR / "data" / "holidays_2026.json"

    with open(file_path, "r") as f:
        return set(json.load(f))


HOLIDAYS = load_holidays()


# ------------------------------------------
# CHECK TRADING DAY
# ------------------------------------------
def is_trading_day(date):
    if date.weekday() >= 5:
        return False

    if date.strftime("%Y-%m-%d") in HOLIDAYS:
        return False

    return True


# ------------------------------------------
# ADJUST FOR HOLIDAY
# ------------------------------------------
def adjust_to_trading_day(date):
    while not is_trading_day(date):
        date -= datetime.timedelta(days=1)
    return date


# ------------------------------------------
# GET LAST THURSDAY
# ------------------------------------------
def get_last_thursday(year, month):

    if month == 12:
        next_month = datetime.date(year + 1, 1, 1)
    else:
        next_month = datetime.date(year, month + 1, 1)

    last_day = next_month - datetime.timedelta(days=1)

    while last_day.weekday() != 3:
        last_day -= datetime.timedelta(days=1)

    return last_day


# ------------------------------------------
# GET EXPIRY DATE + TYPE (ROBUST)
# ------------------------------------------
def get_expiry_date():

    today = datetime.date.today()

    # ----------------------------------
    # CASE 1: TODAY IS THURSDAY
    # ----------------------------------
    if today.weekday() == 3:
        expiry = today
    else:
        # find next Thursday
        days_ahead = 3 - today.weekday()
        if days_ahead < 0:
            days_ahead += 7

        expiry = today + datetime.timedelta(days=days_ahead)

    # ----------------------------------
    # CHECK MONTHLY
    # ----------------------------------
    last_thursday = get_last_thursday(expiry.year, expiry.month)

    # Adjust both for holiday BEFORE comparison
    expiry_adj = adjust_to_trading_day(expiry)
    last_thursday_adj = adjust_to_trading_day(last_thursday)

    if expiry_adj == last_thursday_adj:
        expiry_type = "MONTHLY"
    else:
        expiry_type = "WEEKLY"

    return expiry_adj, expiry_type


# ------------------------------------------
# FORMAT EXPIRY (CORRECT FYERS FORMAT)
# ------------------------------------------
def format_expiry(expiry_date, expiry_type):

    if expiry_type == "WEEKLY":
        year = expiry_date.strftime("%y")
        month = MONTH_MAP[expiry_date.month]   # 🔥 FIXED
        day = expiry_date.strftime("%d")

        return f"{year}{month}{day}"

    elif expiry_type == "MONTHLY":
        return expiry_date.strftime("%y%b").upper()

    else:
        raise ValueError("Invalid expiry type")


# ------------------------------------------
# ATM STRIKE
# ------------------------------------------
def get_atm_strike(price, step=100):
    return int(round(price / step) * step)


# ------------------------------------------
# BUILD SYMBOL
# ------------------------------------------
def build_option_symbol(strike, option_type):

    expiry_date, expiry_type = get_expiry_date()
    expiry = format_expiry(expiry_date, expiry_type)

    return f"BSE:SENSEX{expiry}{strike}{option_type}"


# ------------------------------------------
# GET SYMBOLS
# ------------------------------------------
def get_option_symbols(prev_close):

    atm = get_atm_strike(prev_close)

    expiry_date, expiry_type = get_expiry_date()
    expiry = format_expiry(expiry_date, expiry_type)

    call_symbol = f"BSE:SENSEX{expiry}{atm}CE"
    put_symbol = f"BSE:SENSEX{expiry}{atm}PE"

    result = {
        "atm": atm,
        "expiry": expiry_date,
        "expiry_type": expiry_type,
        "call": call_symbol,
        "put": put_symbol
    }

    return result