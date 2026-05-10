# ==========================================
# SYMBOL MASTER UTILITIES
# ==========================================

import json
from pathlib import Path
from utils.logger import log, error_log


# ==========================================
# MASTER FILE PATH
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
MASTER_FILE = (BASE_DIR /"data" /"NSE_CM_sym_master.json")


# ==========================================
# GLOBAL CACHE
# ==========================================
_symbol_master = {}


# ==========================================
# LOAD MASTER FILE
# ==========================================
def load_symbol_master():
    global _symbol_master
    try:
        log("LOADING SYMBOL MASTER")
        with open(
            MASTER_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(
                "INVALID SYMBOL MASTER FORMAT"
            )

        _symbol_master = data
        log(
            f"SYMBOL MASTER LOADED | "
            f"count={len(_symbol_master)}"
        )
    except Exception as e:
        error_log(f"SYMBOL MASTER LOAD ERROR: {e}")
        _symbol_master = {}


# ==========================================
# GET RAW SYMBOL DATA
# ==========================================
def get_symbol_data(symbol):

    global _symbol_master
    if not _symbol_master:
        load_symbol_master()
    return _symbol_master.get(symbol)


# ==========================================
# GET TICK SIZE
# ==========================================
def get_tick_size(symbol):

    try:
        data = get_symbol_data(symbol)
        if not data:
            error_log(
                f"TICK SIZE NOT FOUND: {symbol}"
            )
            return None
        tick_size = float(
            data.get("tickSize", 0.1)
        )
        return tick_size
    except Exception as e:
        error_log(
            f"GET TICK SIZE ERROR | "
            f"{symbol} | {e}"
        )
        return 0.1


# ==========================================
# GET LOT SIZE
# ==========================================
def get_lot_size(symbol):

    try:
        data = get_symbol_data(symbol)
        if not data:
            error_log(
                f"LOT SIZE NOT FOUND: {symbol}"
            )
            return None
        lot_size = int(
            data.get("minLotSize", 1)
        )
        return lot_size
    except Exception as e:
        error_log(
            f"GET LOT SIZE ERROR | "
            f"{symbol} | {e}"
        )
        return None


# ==========================================
# ROUND TO TICK
# ==========================================
def round_to_tick(price, symbol):

    try:
        tick = get_tick_size(symbol)
        if not tick:
            return round(price, 2)
        rounded = round(
            round(price / tick) * tick,2
        )
        return rounded
    except Exception as e:
        error_log(
            f"ROUND TO TICK ERROR | "
            f"{symbol} | {e}"
        )
        return round(price, 2)