# ==========================================
# STATE TRANSITION LOGGER
# ==========================================

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path


# ------------------------------------------
# LOG FILE
# ------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs/state"

LOG_DIR.mkdir(exist_ok=True)
dt = datetime.now().strftime("%d-%m-%Y")
STATE_LOG_FILE = LOG_DIR / f"state_transitions{dt}_.log"


# ------------------------------------------
# PREVIOUS SNAPSHOTS
# ------------------------------------------
_previous_states = {}


# ------------------------------------------
# SAFE SERIALIZER
# ------------------------------------------
def _serialize(obj):

    try:
        return json.dumps(obj, default=str)

    except Exception:
        return str(obj)


# ------------------------------------------
# EXTRACT STATE DICT
# ------------------------------------------
def _state_to_dict(state):

    return {
        "symbol": state.symbol,

        "active_trade": state.active_trade,

        "entry_price": state.entry_price,
        "sl_price": state.sl_price,

        "entry_order_id": state.entry_order_id,
        "sl_order_id": state.sl_order_id,

        "qty": getattr(state, "qty", 0),

        "first_trade_done": state.first_trade_done,

        "trades_today": state.trades_today,

        "prev_price": state.prev_price,
        "curr_index": state.curr_index,
        "pending_qty": state.pending_qty,
        "entry_level_index": state.entry_level_index,
    }


# ------------------------------------------
# WRITE LOG
# ------------------------------------------
def _write_log(data):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    line = f"[{timestamp}] {data}\n"

    with open(STATE_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ------------------------------------------
# MAIN LOGGER
# ------------------------------------------
def log_state(state, event="STATE_UPDATE"):

    global _previous_states

    symbol = state.symbol

    current = _state_to_dict(state)

    previous = _previous_states.get(symbol)

    # --------------------------------------
    # FIRST SNAPSHOT
    # --------------------------------------
    if previous is None:

        _write_log(
            f"{symbol} | INITIAL_STATE | "
            f"{_serialize(current)}"
        )

        _previous_states[symbol] = deepcopy(current)

        return

    # --------------------------------------
    # DETECT CHANGES
    # --------------------------------------
    changes = {}

    for key in current:

        old = previous.get(key)
        new = current.get(key)

        if old != new:

            changes[key] = {
                "old": old,
                "new": new
            }

    # --------------------------------------
    # LOG ONLY IF CHANGED
    # --------------------------------------
    if changes:

        _write_log(
            f"{symbol} | {event} | "
            f"{_serialize(changes)}"
        )

        _previous_states[symbol] = deepcopy(current)

## Sample input


## After order placement
#     state.entry_order_id = order_id
#     log_state(state, "ENTRY_ORDER_PLACED")

## After trade activation
#     state.set_active_trade(...)
#     log_state(state, "TRADE_ACTIVATED")

## After SL update
#     state.update_sl(new_sl)
#     log_state(state, "TRAIL_SL_UPDATED")

## After recovery
#     log_state(state, "RECOVERY_SYNC")

# # After reset
#     state.reset_trade()
#     log_state(state, "TRADE_RESET")

## Sample output

# [2026-05-08 09:15:12]
# NSE:HDFCBANK-EQ | INITIAL_STATE |
# {
#   "active_trade": false,
#   "entry_price": null
# }
#
#
# [2026-05-08 09:16:40]
# NSE:HDFCBANK-EQ | ENTRY_ORDER_PLACED |
# {
#   "entry_order_id": {
#     "old": null,
#     "new": "26050800012345"
#   }
# }
#
# [2026-05-08 09:17:01]
# NSE:HDFCBANK-EQ | TRADE_ACTIVATED |
# {
#   "active_trade": {
#     "old": false,
#     "new": true
#   },
#   "entry_price": {
#     "old": null,
#     "new": 1780.5
#   }
# }