# ==========================================
# TEST FIB STRATEGY
# ==========================================

import pytest
from strategy.fib_strategy import (
    generate_fib_levels,
    should_place_first_trade,
    should_place_subsequent_trade,
    calculate_sl,
    calculate_trailing_sl
)


# ------------------------------------------
# TEST FIB LEVEL GENERATION
# ------------------------------------------
def test_generate_fib_levels():
    high = 80000
    low = 79000

    levels = generate_fib_levels(high, low)

    assert isinstance(levels, list)
    assert len(levels) > 0
    assert levels == sorted(levels)


# ------------------------------------------
# TEST FIRST TRADE TRIGGER
# ------------------------------------------
def test_first_trade_trigger():
    level = 80000
    price = 79970  # below trigger (25 points)

    assert should_place_first_trade(price, level) is True


def test_first_trade_not_triggered():
    level = 80000
    price = 79990  # above trigger

    assert should_place_first_trade(price, level) is False


# ------------------------------------------
# TEST SUBSEQUENT TRADE CROSS
# ------------------------------------------
def test_subsequent_trade_cross_up():
    prev_price = 79950
    curr_price = 80010
    level = 80000

    assert should_place_subsequent_trade(prev_price, curr_price, level) is True


def test_subsequent_trade_no_cross():
    prev_price = 80010
    curr_price = 80020
    level = 80000

    assert should_place_subsequent_trade(prev_price, curr_price, level) is False


# ------------------------------------------
# TEST STOP LOSS
# ------------------------------------------
def test_stop_loss_calculation():
    entry = 80000
    sl = calculate_sl(entry)

    assert sl == 80000 - 25


# ------------------------------------------
# TEST TRAILING SL
# ------------------------------------------
def test_trailing_sl_basic():
    entry = 80000
    price = 80200  # +200 move

    sl = calculate_trailing_sl(entry, price)

    assert sl is not None
    assert sl > entry


def test_trailing_sl_no_move():
    entry = 80000
    price = 80050

    sl = calculate_trailing_sl(entry, price)

    assert sl is None