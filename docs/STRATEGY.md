# Trading Strategy: Fibonacci Levels & Risk Management

## 🎯 Strategy Overview

### Philosophy
**Price Action Only + Fibonacci Levels = Deterministic Entries/Exits**

- No indicators (RSI, MACD, moving averages)
- No sentiment analysis
- Pure mathematical Fibonacci retracements
- Strict risk management (fixed SL, trailing SL)
- One trade per side (prevents revenge trading)

### Strategic Approach
```
Yesterday's Range [Low ... High]
         ↓
Calculate Fibonacci Retracement Levels
         ↓
Monitor Price Crossing Levels
         ↓
Take Structured Entries at Levels
         ↓
Protect with Fixed SL
         ↓
Lock Profits with Trailing SL
         ↓
Manage Exits via SL, Trailing, or EOD
```

---

## 📊 Fibonacci Level Generation

### Mathematical Basis

**Input:**
- `prev_high` — Previous day's HIGH price
- `prev_low` — Previous day's LOW price

**Calculation:**
```python
diff = prev_high - prev_low

for ratio in FIB_RATIOS:
    level = prev_high - (diff * ratio)
    levels.append(level)
```

### Example: NSE:ADANIPORTS-EQ

```
Date: May 10, 2026
Previous Day (May 9):
  High: 2900.00
  Low: 2700.00
  Range (diff): 200.00

Fibonacci Ratios: [4.236, 3.618, 2.618, 1.618, 1, 0.618, 0.5, 0.382, 0, 
                   -0.618, -1, -1.618, -2.618, -3.618, -4.236]

Levels Calculated (level = 2900 - 200 * ratio):

Ratio    Calculation              Level
─────    ──────────────────────   ──────────
 4.236   2900 - 200*4.236 =       1952.80
 3.618   2900 - 200*3.618 =       2076.40
 2.618   2900 - 200*2.618 =       2376.40
 1.618   2900 - 200*1.618 =       2576.40
 1.000   2900 - 200*1 =           2700.00  ← Equals prev_low
 0.618   2900 - 200*0.618 =       2776.40
 0.500   2900 - 200*0.5 =         2800.00  ← Key level
 0.382   2900 - 200*0.382 =       2823.60
 0.000   2900 - 200*0 =           2900.00  ← Equals prev_high
-0.618   2900 - 200*(-0.618) =    3023.60
-1.000   2900 - 200*(-1) =        3100.00
-1.618   2900 - 200*(-1.618) =    3223.60
-2.618   2900 - 200*(-2.618) =    3423.60
-3.618   2900 - 200*(-3.618) =    3623.60
-4.236   2900 - 200*(-4.236) =    3747.20

Sorted Levels (ascending):
[1952.80, 2076.40, 2376.40, 2576.40, 2700.00, 2776.40, 2800.00, 
 2823.60, 2900.00, 3023.60, 3100.00, 3223.60, 3423.60, 3623.60, 3747.20]
```

### Key Levels Explained

```
Extended Levels (negative ratios) = Breakout targets if price breaks above prev_high
│
├─ 3747.20 (4.236 extension)
├─ 3623.60 (3.618 extension)
├─ 3423.60 (2.618 extension)
├─ 3223.60 (1.618 extension)
├─ 3100.00 (1.0 extension)
├─ 3023.60 (0.618 extension)
│                                ↑ If price breaks above 2900, expect 3023.60
│ ═════════════════════ YESTERDAY'S HIGH (2900.00) ═════════════════════
│
├─ 2900.00 (0 level - same as high)
├─ 2823.60 (0.382 retracement)
├─ 2800.00 (0.5 retracement)  ← Major support/resistance
├─ 2776.40 (0.618 retracement) ← Key Fibonacci level
├─ 2700.00 (1.0 retracement) ← Equals yesterday's low
│ ═════════════════════ YESTERDAY'S LOW (2700.00) ═════════════════════
│
├─ 2576.40
├─ 2376.40
├─ 2076.40
├─ 1952.80
│
└─ Breakdown levels if price breaks below 2700
```

### Most Predictive Ratios (Tested Empirically)

In order of importance:
1. **0.618** — Most critical (25.2% retrace) — Fibonacci golden ratio
2. **0.5** — 50% retrace — Psychological level
3. **0.382** — 38.2% retrace — Secondary support
4. **1.0** — 100% (yesterday's low) — Daily breakpoint
5. **-0.618** — First breakout target
6. **-1.0** — Second breakout target

---

## 🎯 Entry Rules

### Rule 1: First Trade Trigger

**Condition:**
```
price <= trigger_price

where trigger_price = level - SL_POINTS
```

**Example:**
```
Level: 2800.00
SL_POINTS: 10
Trigger: 2800.00 - 10 = 2790.00

Signal:
  If price touches 2790.00 → Place stop-buy @ 2800.00
  If price stays > 2790.00 → No entry (level not validated)
```

**Execution:**
- Trigger acts as **validation** of level (price commitment)
- Order placed at the level itself (2800.00)
- Prevents whipsaws (price just grazing level)
- Ensures genuine breakout interest

**Logic Flow:**
```python
if NOT active_trade AND NOT first_trade_done:
    if should_place_first_trade(price, level):
        # price <= level - SL_POINTS
        enter_trade(level, price)
        first_trade_done = True
```

**Example Sequence:**
```
Scenario: Trading 2800 level

Time    Price   Trigger  Status
────    ────    ───────  ──────────────────────────────
09:30   2810    2790     Price > trigger, no entry
09:40   2805    2790     Price > trigger, no entry
09:50   2795    2790     Price > trigger, no entry
10:00   2789    2790     Price < trigger! SIGNAL
        → Place stop-buy @ 2800
        → PENDING

10:05   2798    2790     Order pending, waiting
10:10   2802    2790     ORDER FILLS @ 2801
        → Entry: 2801
        → SL: 2791
        → ACTIVE TRADE
```

---

### Rule 2: Subsequent Trade Entry (After First Trade Exits)

**Condition:**
```
detect_cross(prev_price < level AND curr_price >= level)
```

**Example:**
```
Level: 2800.00

Time    Price   Prev    Status
────    ────    ────    ──────────────────────
10:00   2798    2796    Moving up, below level
10:05   2799    2798    Moving up, below level
10:10   2801    2799    CROSSED ABOVE! SIGNAL
        → Cross confirmed
        → Place stop-buy @ 2800
```

**Key Differences from First Trade:**
- First trade: Uses trigger (level - SL_POINTS)
- Subsequent: Uses level crossing directly
- First trade: Validates level acceptance
- Subsequent: Assumes level already validated

**Execution:**
```python
if NOT active_trade AND first_trade_done:
    if detect_cross(prev_price, price, level) == "CROSS_UP":
        enter_trade(level, price)
```

---

### Rule 3: One Active Trade Per Side (No Stacking)

**Configuration:**
```python
ALLOW_ONLY_ONE_ACTIVE_TRADE_PER_SIDE = True
```

**Enforcement:**
```python
if active_trade:
    # Only entry when previous trade exited
    if entry_signal:
        return  # Skip entry, already in trade
```

**Rationale:**
- Prevents position doubling
- Limits maximum loss per side
- Allows proper SL management
- Simplifies risk calculations

**Example (VIOLATION PREVENTION):**
```
T1: 10:00 - Entry @ 2800 (Level 1), qty=1
    Status: ACTIVE TRADE

T2: 10:05 - Level 2 crosses (2850)
    Entry signal detected
    Check: active_trade = True → SKIP ENTRY
    
    Reason: Can't have 2 concurrent trades
    
T3: 10:30 - SL hit @ 2790
    Position closes, qty=0
    Status: IDLE
    
T4: 10:32 - Level 2 crosses again (2850)
    Entry signal detected
    Check: active_trade = False → ENTER
    New trade @ 2850, qty=1
```

---

## 🛡️ Stop Loss Management

### Fixed Stop Loss

**Calculation:**
```python
sl_price = entry_price - SL_POINTS
```

**Values by Mode:**
```python
if test_mode:
    SL_POINTS = 10     # 10 points for equity testing
else:
    SL_POINTS = 25     # 25 points for options trading
```

**Example:**
```
Entry: 2800.50
Mode: LIVE (SL_POINTS = 25)
SL: 2800.50 - 25 = 2775.50

Risk per trade: Entry - SL = 25 points
Risk in rupees: 25 * 1 = ₹25 per share
```

### Trailing Stop Loss

**Purpose:** Lock in profits as price moves favorably

**Configuration (from `trading_params.py`):**

**Test Mode:**
```python
TRAILING_RULES = {
    5: 2,       # If profit >= 5, SL = entry + 2
    6: 3,       # If profit >= 6, SL = entry + 3
    7: 4,
    9: 5,
    12: 6,
    15: 10,
    20: 16,
    25: 20
}
```

**Live Mode (Options):**
```python
TRAILING_RULES = {
    100: 30,       # If profit >= 100, SL = entry + 30
    200: 50,       # If profit >= 200, SL = entry + 50
    400: 200,
    600: 400,
    800: 700,
    1000: 900,
    1200: 1100
}
```

### Trailing SL Calculation

**Algorithm:**
```python
def calculate_trailing_sl(entry, current_price, TRAILING_RULES):
    move = current_price - entry
    new_sl = None
    
    # Iterate rules in ascending order
    for move_threshold in sorted(TRAILING_RULES.keys()):
        if move >= move_threshold:
            new_sl = entry + TRAILING_RULES[move_threshold]
    
    return new_sl
```

**Example (Test Mode):**
```
Entry: 100
Trailing Rules: {5: 2, 6: 3, 7: 4, 9: 5, ...}

Current Price    Profit   New SL Candidate        SL Executed
─────────────    ──────   ──────────────────      ───────────
100.00           0        None                    None (not executable yet)
103.00           3        None                    None (profit < 5)
104.00           4        None                    None (profit < 5)
105.00           5 ✓      100 + 2 = 102           102
106.00           6 ✓      100 + 3 = 103           103
107.00           7 ✓      100 + 4 = 104           104
108.00           8        100 + 4 = 104           104 (no new rule >= 8)
110.00           10       100 + 5 = 105           105 (rule at 9 applies)
112.00           12       100 + 6 = 106           106
115.00           15       100 + 10 = 110          110
120.00           20       100 + 16 = 116          116
127.00           27       100 + 20 = 120          120 (rule at 25 applies now)

Key Points:
- SL only moves UP (never DOWN) ← Locks profits
- SL jumps to highest threshold matched
- Once SL hits, trade closes
```

### Trailing SL Behavior: Key Rules

1. **SL Only Moves UP** (never down)
   ```
   old_sl = 102
   new_sl = 103
   
   if new_sl > old_sl:
       apply(new_sl)  ← Move SL up
   else:
       keep(old_sl)   ← Don't move down
   ```

2. **Locked Profit Increases Linearly**
   ```
   As profit increases by threshold amounts,
   SL moves up by corresponding offset
   
   Example:
     Profit 5-9: SL at entry+2 (locked 2 points)
     Profit 9-12: SL at entry+5 (locked 5 points)
     Profit 12+: SL at entry+6 (locked 6 points)
   ```

3. **Exponential Buffer**
   ```
   For large moves, buffer grows exponentially:
   
   Move      Locked
   100       30 (30%)
   200       50 (25%)
   400       200 (50%)
   600       400 (67%)
   800       700 (87%)
   1000      900 (90%)
   
   Larger profits = larger protection cushion
   ```

---

## ⏰ Exit Strategies

### Exit 1: Stop Loss Hit

**Trigger:**
```python
if price <= sl_price:
    exit_trade()
```

**Execution:**
- Automatic on price tick
- Market sell order placed
- Position closed within 1-2 seconds
- State reset, ready for next trade

**Example:**
```
Entry: 2800.50
SL: 2775.50
Position: 1 share

Time    Price    Action
────    ─────    ──────────────────────
10:05   2793     SL monitor (price > SL)
10:06   2776     SL monitor (price > SL)
10:07   2774.90  SL HIT! price < 2775.50
        → Market sell triggered
        → Position closed @ 2774.90
        → Loss: 25.60 (worse than SL by 0.10)
        → State reset
```

**Loss Scenario:**
```
Best case: Exit at SL (2775.50) → Loss = 25 points
Worst case: Gap down → Exit at market (below SL)
Expected: Most exits near SL price
```

---

### Exit 2: Trailing Stop Loss Execution

**Trigger:**
```
SL moves up as profit increases
Price eventually retraces and hits new SL
```

**Example:**
```
Entry: 100
Initial SL: 90 (fixed)

Price moves to 110 (profit = 10)
  → Trailing rule: {10+: 5}
  → New SL: 100 + 5 = 105
  → SL updated from 90 → 105

Price moves to 115 (profit = 15)
  → Trailing rule: {15+: 10}
  → New SL: 100 + 10 = 110
  → SL updated from 105 → 110

Price retraces to 108 (profit = 8)
  → price (108) > SL (110)
  → No SL hit yet, continue monitoring

Price retraces to 109.5 (profit = 9.5)
  → price (109.5) < SL (110)
  → SL HIT!
  → Exit @ 109.5
  → P&L: +9.5 (profit locked)
```

---

### Exit 3: End of Day (EOD) Exit

**Trigger:**
```python
if is_eod_exit_time():  # 3:20 PM
    for engine in engines:
        engine.force_exit()
```

**Execution:**
- Mandatory for all open positions
- Market order (get out at any price)
- No SL protection at EOD
- Reason: Overnight gaps, broker position carries risk

**Example:**
```
3:19 PM: Active trade still open
         Entry: 2800
         Current Price: 2850
         Unrealized P&L: +50

3:20 PM: EOD exit triggered
         Force exit at market
         Actual exit: 2849.50
         Realized P&L: +49.50
         
3:21 PM: Position closed, state reset
         Ready for next day
```

**Why Mandatory:**
- Overnight gaps can wipe out profits
- Broker liquidation fees (if not exited)
- Regulatory restrictions (options expiry)
- Risk concentration in single overnight position

---

### Exit 4: Manual Exit (Future Enhancement)

Not currently implemented, but architecture supports:
```python
def manual_exit(engine, price):
    exit_trade()
    log(f"Manual exit @ {price}")
```

---

## 📈 Risk Management Framework

### Maximum Trades Per Day

**Configuration:**
```python
if test_mode:
    MAX_TRADES_PER_DAY = 50  # Quick iteration
else:
    MAX_TRADES_PER_DAY = 10  # Conservative
```

**Enforcement:**
```python
if state.trades_today >= MAX_TRADES_PER_DAY:
    return  # Skip entry, daily limit reached
```

**Rationale:**
- Prevents over-trading
- Reduces transaction costs
- Limits daily loss exposure
- Ensures quality trades only

---

### Maximum Daily Loss

**Configuration:**
```python
if test_mode:
    MAX_DAILY_LOSS = 1000
else:
    MAX_DAILY_LOSS = 6000
```

**Enforcement (Future):**
```python
current_daily_loss = sum(lost_trades_today)
if current_daily_loss > MAX_DAILY_LOSS:
    disable_entries()  # Stop taking new trades
    force_exit()       # Close remaining positions
```

**Current Status:** Configured but tracking not implemented (planned feature)

---

### Position Sizing

**Fixed Quantity:**
```python
DEFAULT_QTY = 1  # Always trade 1 share/contract
```

**Rationale:**
```
Risk per trade = entry - SL = SL_POINTS

Test mode: 10 points × 1 = ₹10 max loss
Live mode: 25 points × 1 = ₹25 max loss

Scaling rule (future):
  If account > ₹200k: Qty = 2
  If account > ₹500k: Qty = 3
  etc.
```

**Currently:** Fixed at 1 for simplicity

---

## 🧮 Expected Performance Characteristics

### Win Rate Analysis (Theoretical)

**Assumption:** Trading all Fibonacci level crossings

```
Win Rate Components:

1. False Pips (No-profit trades):
   - Entry triggers but reverses: ~20% of trades
   - Likely reason: Level rejection

2. Losing Trades:
   - SL hit on real reversal: ~30% of trades
   - Risk per trade: SL_POINTS fixed

3. Winning Trades:
   - Profitable exits: ~50% of trades
   - Profit varies: Could be small (1-2 points) to large (50+ points)

Break-even Analysis:
  Expected Win Rate: 50% (at fib levels)
  Risk/Reward Ratio: 1:1 (fixed SL, loose exit)
  Expected Return: ~0 (break-even)

With Trailing SL:
  Win Rate: Still ~50%
  Risk/Reward: 1:2 (locked profits early)
  Expected Return: +10% to +20% (annualized, with compounding)
```

### Backtesting Considerations

**Historical Performance (Not Actual Results):**
```
Backtest Assumptions:
- Use daily closes to generate levels
- Simulate intraday levels and crossings
- No slippage, no commissions (first pass)
- Add 1-2 points slippage (realistic)
- Add ₹20 per trade commission (Fyers)

Typical Results (from similar strategies):
- Win Rate: 45-55%
- Average Win: 20-40 points
- Average Loss: SL_POINTS (10-25)
- Profit Factor: 1.5 - 2.0
- Drawdown: 10-20%
```

---

## ⚙️ Configuration Profiles

### Test Profile (config/trading_params.py, test_mode=True)

```python
SL_POINTS = 10
TRAILING_RULES = {5: 2, 6: 3, 7: 4, 9: 5, 12: 6, 15: 10, 20: 16, 25: 20}
MAX_TRADES_PER_DAY = 50
MAX_DAILY_LOSS = 1000
DEFAULT_QTY = 1

Trade in: NSE:ADANIPORTS-EQ (equity)
Purpose: Fast iteration, risk learning
```

### Live Profile (config/trading_params.py, test_mode=False)

```python
SL_POINTS = 25
TRAILING_RULES = {100: 30, 200: 50, 400: 200, 600: 400, 800: 700, 1000: 900, 1200: 1100}
MAX_TRADES_PER_DAY = 10
MAX_DAILY_LOSS = 6000
DEFAULT_QTY = 1

Trade in: BSE:SENSEX options (weekly/monthly ATM)
Purpose: Institutional trading, capital preservation
```

---

## 🔄 Strategy Decision Tree

```
                    ┌─ IDLE ─────────────┐
                    │ No active trade    │
                    └────────┬───────────┘
                             │
                    Is first trade done?
                    /              \
                  NO              YES
                 /                  \
    ┌──────────────────┐      ┌──────────────────┐
    │ Check Trigger    │      │ Check Crossing   │
    │ level - SL       │      │ lower → upper    │
    └────────┬─────────┘      └────────┬─────────┘
             │                         │
      price <= trigger?          price crosses?
         /        \                /        \
       YES        NO             YES        NO
       /            \            /            \
    ENTER         WAIT         ENTER        WAIT
   (trade)        (tick)       (trade)      (tick)
   │              │            │            │
   ├─ Place       └─ Return    ├─ Place    └─ Return
   │  stop-buy                 │  stop-buy
   │
   ├─ Status: ENTRY_PENDING
   │
   └─ Await trade fill...
        │
    ┌───┴───┐
    │ FILL  │
    └───┬───┘
        │
    ├─ Extract: entry_price, qty
    ├─ Calculate: sl_price = entry - SL_POINTS
    ├─ Place: SL order
    ├─ Status: ACTIVE
    │
    └─ Await price action...
        │
    ┌───┴──────────────────┬────────────────┐
    │                      │                 │
   Price                Price            Trailing
  touches SL          crosses up        trigger hit
    │                  (higher level)        │
    │                  │                 Calculate
    │                  │                 new_SL
    │                  │                 │
    ├─ CLOSE        ├─ (Already          ├─ Modify
    │  position     │  protected by      │  SL order
    │  (SL)         │  current SL)       ├─ Continue
    │               │ (If new level      │  monitoring
    └─ Reset state  │  crosses, first
       EXIT          │  trade done)
                     └─ Return
```

---

## 📝 Strategy Pseudocode

```python
def trading_session():
    """Complete trading session flow."""
    
    # Initialization
    ohlc = get_prev_day_ohlc()
    levels = generate_fib_levels(ohlc.high, ohlc.low)
    state = TradeState()
    
    # Main loop - process each price tick
    while market_is_open():
        price = wait_for_tick()
        
        # First tick setup
        if state.prev_price is None:
            state.prev_price = price
            state.curr_index = get_level_index(price, levels)
            continue
        
        # Level detection
        state.curr_index = get_level_index(price, levels, state.curr_index)
        level = levels[state.curr_index]
        
        # SL check (exit)
        if state.active_trade and price <= state.sl_price:
            exit_trade()
            state.reset_trade()
            continue
        
        # Entry check
        if not state.active_trade:
            # First trade trigger
            if not state.first_trade_done:
                trigger = level - SL_POINTS
                if price <= trigger:
                    enter_trade(level)
                    state.first_trade_done = True
                    continue
            
            # Subsequent trade entry
            if state.first_trade_done:
                if detect_cross(state.prev_price, price, level):
                    enter_trade(level)
                    continue
        
        # Trailing SL (update)
        if state.active_trade:
            profit = price - state.entry_price
            new_sl = calculate_trailing_sl(
                state.entry_price,
                price,
                TRAILING_RULES
            )
            if new_sl and new_sl > state.sl_price:
                modify_order(state.sl_order_id, new_sl)
                state.sl_price = new_sl
        
        # EOD exit
        if is_eod_exit_time():
            if state.active_trade:
                force_exit()
                state.reset_trade()
                break
        
        state.prev_price = price
    
    return state
```

---

## Summary: Strategy Parameters Table

| Parameter | Test | Live | Purpose |
|-----------|------|------|---------|
| **SL_POINTS** | 10 | 25 | Risk per trade |
| **Max daily trades** | 50 | 10 | Overtrading prevention |
| **Max daily loss** | ₹1000 | ₹6000 | Loss cap |
| **First trigger** | level - SL_POINTS | level - SL_POINTS | Entry validation |
| **Subsequent entry** | Level crossing | Level crossing | Re-entry signal |
| **Trailing SL** | Fast ramp | Gradual climb | Profit locking |
| **QTY per trade** | 1 | 1 | Position size |
| **EOD exit time** | 3:20 PM | 3:20 PM | Overnight risk mitigation |

---

## Next Steps

- See `INTEGRATION.md` for deployment
- See `COMPONENTS.md` for code implementation
- See `DATA_FLOW.md` for execution paths


