# ==========================================
# TEST ENGINE LOGIC (WITH MOCKS)
# ==========================================

import pytest
from core.engine import Engine


# ------------------------------------------
# MOCK FYERS
# ------------------------------------------
class MockFyers:
    def place_order(self, data):
        return {"id": "test_order"}

    def cancel_order(self, data):
        return {"status": "cancelled"}

    def modify_order(self, data):
        return {"status": "modified"}


# ------------------------------------------
# MOCK ORDER FUNCTIONS
# ------------------------------------------
def mock_place_stop_buy(fyers, symbol, qty, price):
    return {"id": "order_1"}


def mock_place_sl_order(fyers, symbol, qty, price):
    return {"id": "sl_1"}


def mock_cancel_order(fyers, order_id):
    return {"status": "cancelled"}


def mock_modify_order(fyers, order_id, price, trigger):
    return {"status": "modified"}


# ------------------------------------------
# PATCH ENGINE DEPENDENCIES
# ------------------------------------------
@pytest.fixture
def engine():
    fyers = MockFyers()
    levels = [79000, 79500, 80000, 80500]

    eng = Engine(fyers, "TEST_SYMBOL", levels)

    # Inject mocks
    eng.place_stop_buy = mock_place_stop_buy
    eng.place_sl_order = mock_place_sl_order
    eng.cancel_order = mock_cancel_order
    eng.modify_order = mock_modify_order

    return eng


# ------------------------------------------
# TEST INITIAL STATE
# ------------------------------------------
def test_engine_initial_state(engine):
    assert engine.state.active_trade is False
    assert engine.state.prev_price is None


# ------------------------------------------
# TEST FIRST TICK INIT
# ------------------------------------------
def test_first_tick_initialization(engine):
    engine.on_tick(80000)

    assert engine.state.prev_price == 80000
    assert engine.state.curr_index is not None


# ------------------------------------------
# TEST FIRST TRADE ORDER PLACEMENT
# ------------------------------------------
def test_first_trade_order(engine):
    engine.on_tick(80000)  # init

    # Move below trigger
    engine.on_tick(79960)

    assert engine.state.pending_order_id is not None


# ------------------------------------------
# TEST TRADE EXECUTION
# ------------------------------------------
def test_trade_execution(engine):
    engine.on_tick(80000)
    engine.on_tick(79960)  # trigger

    # Price crosses level
    engine.on_tick(80010)

    assert engine.state.active_trade is True
    assert engine.state.entry_price is not None
    assert engine.state.sl_price is not None


# ------------------------------------------
# TEST SL HIT
# ------------------------------------------
def test_sl_hit(engine):
    engine.on_tick(80000)
    engine.on_tick(79960)
    engine.on_tick(80010)  # execute trade

    sl = engine.state.sl_price

    # Price falls below SL
    engine.on_tick(sl - 10)

    assert engine.state.active_trade is False


# ------------------------------------------
# TEST NO DUPLICATE TRADE
# ------------------------------------------
def test_no_duplicate_trade(engine):
    engine.on_tick(80000)
    engine.on_tick(79960)
    engine.on_tick(80010)  # trade active

    prev_state = engine.state.active_trade

    # Try triggering again
    engine.on_tick(79960)

    assert engine.state.active_trade == prev_state