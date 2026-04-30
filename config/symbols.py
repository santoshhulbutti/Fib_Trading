# ==========================================
# INSTRUMENT & SYMBOL UTILITIES
# ==========================================

import datetime


# ------------------------------------------
# ATM STRIKE CALCULATION
# ------------------------------------------
def get_atm_strike(price, step=100):
    """
    Round to nearest strike
    Sensex uses 100 step
    """
    return int(round(price / step) * step)


# ------------------------------------------
# EXPIRY CALCULATION (WEEKLY)
# ------------------------------------------
def get_expiry():
    """
    Returns next weekly expiry (Friday)
    Format: 24APR
    """

    today = datetime.date.today()

    # Friday = 4
    days_ahead = 4 - today.weekday()

    if days_ahead <= 0:
        days_ahead += 7

    expiry = today + datetime.timedelta(days=days_ahead)

    return expiry.strftime("%y%b").upper()


# ------------------------------------------
# OPTION SYMBOL BUILDER
# ------------------------------------------
def build_option_symbol(strike, option_type):
    """
    option_type = "CE" or "PE"

    Example:
    BSE:SENSEX24APR80000CE
    """

    expiry = get_expiry()

    return f"BSE:SENSEX{expiry}{strike}{option_type}"


# ------------------------------------------
# FULL SYMBOL SETUP (ONE FUNCTION)
# ------------------------------------------
def get_option_symbols(prev_close):

    atm = get_atm_strike(prev_close)

    call_symbol = build_option_symbol(atm, "CE")
    put_symbol = build_option_symbol(atm, "PE")

    return {
        "atm": atm,
        "call": call_symbol,
        "put": put_symbol
    }