# ==========================================
# TIME UTILITIES (MARKET CONTROL)
# ==========================================

from datetime import datetime
from config.settings import MARKET_START, MARKET_END, EOD_EXIT_TIME


# ------------------------------------------
# PARSE TIME STRING
# ------------------------------------------
def _parse_time(time_str):
    """
    Converts 'HH:MM' → (hour, minute)
    """
    h, m = map(int, time_str.split(":"))
    return h, m


# ------------------------------------------
# CURRENT TIME
# ------------------------------------------
def now():
    return datetime.now()


# ------------------------------------------
# CHECK MARKET OPEN
# ------------------------------------------
def is_market_open():
    current = now()

    start_h, start_m = _parse_time(MARKET_START)
    end_h, end_m = _parse_time(MARKET_END)

    start = current.replace(hour=start_h, minute=start_m, second=0)
    end = current.replace(hour=end_h, minute=end_m, second=0)

    return start <= current <= end


# ------------------------------------------
# CHECK MARKET CLOSED
# ------------------------------------------
def is_market_closed():
    return not is_market_open()


# ------------------------------------------
# CHECK EOD EXIT TIME
# ------------------------------------------
def is_eod_exit_time():
    current = now()

    eod_h, eod_m = _parse_time(EOD_EXIT_TIME)
    eod = current.replace(hour=eod_h, minute=eod_m, second=0)

    return current >= eod


# ------------------------------------------
# WAIT UNTIL MARKET START
# ------------------------------------------
def wait_for_market_open():
    import time

    while not is_market_open():
        print("Waiting for market open...")
        time.sleep(30)


# ------------------------------------------
# TIME LEFT TO MARKET CLOSE
# ------------------------------------------
def time_to_market_close():
    current = now()

    end_h, end_m = _parse_time(MARKET_END)
    end = current.replace(hour=end_h, minute=end_m, second=0)

    return (end - current).total_seconds()