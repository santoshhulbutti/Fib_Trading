# Components: Detailed Module Breakdown

## 📋 Overview

This document details each module's responsibilities, interfaces, and implementation patterns. Code references point to actual file locations (no duplication).

---

## Core Components

---

## 1. Engine: `core/engine.py` (500 lines)

### Purpose
The **Engine** is the trading brain. It processes price ticks, detects trading signals, manages order lifecycle, and maintains trade state.

### Key Responsibilities

#### 1.1 Initialization
```python
class Engine:
    def __init__(self, fyers, symbol, levels):
        self.fyers = fyers              # Broker connection
        self.symbol = symbol            # Trading symbol (e.g., "NSE:ADANIPORTS-EQ")
        self.levels = levels            # Sorted Fibonacci levels
        self.state = TradeState(symbol) # Trade state object
```

**Constructor Parameters:**
- `fyers` — FyersModel instance (authenticated)
- `symbol` — Symbol to trade
- `levels` — List of Fibonacci levels (sorted, ascending)

#### 1.2 Core Methods

**`on_tick(price)` — Main Price Processing (Lines 46-300)**

```
Input: Live price from WebSocket
Output: Order placements, state updates

Logic Flow:
  1. First tick: Initialize state
  2. Subsequent ticks:
     - Calculate current level index (O(1))
     - Detect level crossing (up/down)
     - Check SL hit
     - Check trailing SL trigger
     - Check first-trade trigger or cross
     - Execute entry/exit logic
```

**Decision Tree:**
```
on_tick(price):
  if first_tick:
    -> Initialize curr_index, prev_price
  else:
    -> Detect level change (curr_index)
    
    if SL_HIT and active_trade:
      -> exit_trade()
      -> reset_trade()
    
    elif NOT active_trade and entry_signal:
      -> enter_trade(level, price)
    
    elif active_trade and trailing_trigger:
      -> Calculate new_sl
      -> modify_sl_order()
    
    -> Update prev_price for next tick
```

**State Transitions:**
- Idle → Entry pending → Active → Idle (SL hit)
- Active → Active (trailing SL update)

**Code Location:** Lines 46-300

---

**`enter_trade(level, price)` — Entry Order Placement (Lines 301-380)**

```python
def enter_trade(self, level, price):
    """
    Prerequisites:
    - active_trade == False
    - entry_order_id == None
    
    Process:
    1. Validate entry conditions
    2. Calculate SL price
    3. Place stop-buy order at level
    4. Store entry_order_id
    5. Log entry attempt
    """
```

**Validation Checks:**
- Not already in active trade: `if self.state.active_trade: return`
- Not already pending entry: `if self.state.entry_order_id: return`
- Within trading hours
- First trade trigger OR cross signal

**Order Placement:**
```python
place_stop_buy(
    fyers, 
    symbol, 
    qty=1, 
    trigger_price=level,      # Stop trigger
    limit_price=level + 0.05   # Limit price (slightly above to ensure fill)
)
```

**Returns:**
- Response dict with `s` (status) and `order_id` if successful
- Sets `state.entry_order_id = order_id`

**Code Location:** Lines 301-380

---

**`handle_trade_update(msg)` — Trade Fill Handler (Lines 380-420)**

```python
def handle_trade_update(self, msg):
    """
    Triggered when: Order gets filled on broker side
    
    Process:
    1. Extract filled quantity & entry price
    2. Set active trade state
    3. Calculate SL
    4. Place SL order immediately
    
    Input msg fields:
    - symbol: Trading symbol
    - tradedQty: Filled quantity
    - tradePrice: Execution price
    - orderId: Original order ID
    """
```

**State Transition:**
```
IDLE → Entry pending (entry_order_id set)
     → ACTIVE (on fill, entry_price set, sl_order_id pending)
```

**SL Order Placement:**
```python
sl_price = calculate_sl(entry_price)  # entry_price - SL_POINTS

place_sl_order(
    fyers,
    symbol,
    qty=filled_qty,
    sl_price=sl_price
)
```

**Logging:**
- Trade execution: timestamp, entry price, SL, qty
- Next: Monitor for SL hit or trailing trigger

**Code Location:** Lines 380-420

---

**`exit_trade()` — Position Exit (Lines 420-480)**

```python
def exit_trade(self):
    """
    Closes entire position by:
    1. Checking if SL order exists
       - If pending: cancel it first
    2. If no SL protection, exit immediately
    3. Place market sell order
    
    Returns: Response dict from broker
    """
```

**Exit Scenarios:**
- **SL Hit:** `on_tick()` triggers exit when `price <= sl_price`
  - Cancels pending SL order (if any)
  - Places market sell at current price
  
- **EOD Exit:** Forced close before 3:20 PM
  - Always market order regardless of PnL
  
- **Manual Exit:** Could be triggered by external signal (future)

**Order Placement:**
```python
close_position(fyers, symbol, qty=state.qty)  # Market sell
```

**Post-Exit:**
- State reset: `state.reset_trade()`
- All order IDs cleared
- Ready for next trade

**Code Location:** Lines 420-480

---

**`handle_order_update(msg)` — Order Status Changes (Lines 480-500)**

```python
def handle_order_update(self, msg):
    """
    Handles order status changes:
    - Canceled: entry_order_id or sl_order_id update
    - Modified: SL modification confirmation
    - Rejected: Log & reset order tracking
    """
```

**Cases:**
1. **Entry order canceled:** Reset entry tracking
2. **SL order canceled:** Log and possibly re-place
3. **SL order modified:** Confirm new SL in state

**Code Location:** Lines 480-500

---

**`handle_position_update(msg)` — Position Changes (Lines 350-370)**

```python
def handle_position_update(self, msg):
    """
    Handles position quantity changes:
    - qty = 0 (closed): Reset trade state
    - qty < previous: Partial close (log warning)
    - qty > previous: Unplanned addition (error)
    """
```

**Normal Flow:**
- SL executes → qty becomes 0 → Reset state
- Manual close → qty becomes 0 → Reset state

**Error Cases:**
- Partial close detected → Log error, manual intervention needed
- Position increased → Log error, unexpected

**Code Location:** Lines 350-370

---

### Method Call Sequence Example

**Scenario: Entry signal → Fill → SL hit → Exit**

```
Time    Event                  Method Called          State Change
─────   ───────────────────    ─────────────────      ──────────────────────
09:15   Bot starts             initialize_system()    engines created
        First tick received    on_tick(2850.0)        curr_index = 5
        
09:30   Price at level 2 entry on_tick(2790)         Trigger detected
        Enters range            enter_trade(2800)      entry_order_id = 1001
        
09:32   Order fills             handle_trade_update()  active_trade = True
        SL order placed         (auto)                 sl_order_id = 1002
        
09:35   Price rises             on_tick(2825)         Profit = +25
        Trailing trigger        modify_sl_order()      sl_price = 2800
        
10:15   Price falls to SL       on_tick(2800.5)       SL hit detected
        Exit triggered          exit_trade()           Market sell sent
        
10:15   Position closed         handle_position_update() active_trade = False
        State reset             reset_trade()          Ready for next
```

---

### Design Patterns

**1. State Machine:**
- Clear states (IDLE, ENTRY_PENDING, ACTIVE)
- Deterministic transitions
- No undefined state paths

**2. Callback-Driven:**
- No polling, only WebSocket callbacks
- Fast response to market events
- Thread-safe (single execution thread)

**3. Guard Clauses:**
- Early returns for invalid states
- Prevents invalid transitions
- Clear error logging

**Code Example:**
```python
def on_tick(self, price):
    state = self.state
    
    # Guard: First tick
    if state.prev_price is None:
        state.prev_price = price
        state.curr_index = get_level_index(price, self.levels)
        return  # Early return, wait for next tick
    
    # Guard: Not active
    if not state.active_trade:
        if entry_signal:
            self.enter_trade(...)
        return
    
    # Guard: SL not hit yet
    if not sl_hit(price, state.sl_price):
        return
    
    # Main logic (only reaches here if all conditions met)
    self.exit_trade()
    state.reset_trade()
```

---

## 2. State Management: `core/state.py` (69 lines)

### Purpose
**Single representation of trade state.** All state data encapsulated in one object, avoiding scattered state across the codebase.

### TradeState Class

```python
class TradeState:
    symbol: str           # Trading symbol
    
    # Market state
    prev_price: float     # Previous tick (for crossing detection)
    curr_index: int       # Current level index (for O(1) lookup)
    
    # Active trade state
    active_trade: bool    # Is there an open position?
    entry_price: float    # Entry price of current trade
    sl_price: float       # Current SL price (fixed or trailing)
    qty: int              # Position quantity
    
    # Order tracking
    entry_order_id: str   # ID of pending entry order
    sl_order_id: str      # ID of pending/active SL order
    
    # Strategy flags
    first_trade_done: bool  # Has first trade been triggered?
    
    # Risk tracking
    trades_today: int     # Total trades executed today
```

### Methods

**`set_active_trade(entry_price, sl_price, qty=1)`**
- Transition from order-pending to active-trade state
- Called when entry order fills
- Increments `trades_today`
- Clears `entry_order_id`

**`reset_trade()`**
- Clear all trade-related fields
- Called after SL hit or manual exit
- Prepares state for next trade

**`update_sl(new_sl)`**
- Update SL price (for trailing)
- Only updates if `new_sl > current sl_price` (lock in profits)
- Called from engine on trailing trigger

### State Lifecycle

```
Initialized:
  active_trade = False
  entry_price = None
  entry_order_id = None
  sl_order_id = None
  
After enter_trade():
  entry_order_id = "1001"  (pending)
  
After handle_trade_update():
  active_trade = True
  entry_price = 2800.50
  sl_price = 2775.50
  sl_order_id = "1002"
  entry_order_id = None (cleared)
  
After SL hit:
  active_trade = False (reset)
  entry_price = None
  sl_price = None
  entry_order_id = None
  sl_order_id = None
```

---

## 3. Event Detection: `core/events.py` (77 lines)

### Purpose
**Pure signal detection with zero business logic.** Functions are deterministic, testable, and reusable.

### Functions

**`get_level_index(price, levels, last_index=None)` — O(1) Level Lookup**

```python
def get_level_index(price, levels, last_index=None):
    """
    Find which level band price is in.
    
    Input:
      price: Current market price
      levels: Sorted Fibonacci levels [low, ..., high]
      last_index: Previous index (cache optimization)
    
    Output:
      Index i such that levels[i] <= price < levels[i+1]
    
    Algorithm:
      1. Check if price still in last band (cache hit)
         → Return immediately (O(1))
      2. If not, use bisect to find correct band (O(log n))
      3. Clamp to valid range [0, len(levels)-2]
    
    Example:
      levels = [100, 110, 120, 130, 140]
      price = 123.5
      
      → Finds band: [120, 130]
      → Returns: index 2
    """
```

**Performance:**
- Cached: O(1) average (most ticks stay in same band)
- Worst case: O(log n) (only when crossing bands)
- Never O(n)

---

**`detect_cross(prev_price, curr_price, level)` — Crossing Detection**

```python
def detect_cross(prev_price, curr_price, level):
    """
    Detects if price crossed a level.
    
    Returns:
      "CROSS_UP" — Price was below, now >= level
      "CROSS_DOWN" — Price was above, now <= level
      None — No crossing
    
    Example 1 (Up cross):
      prev = 109.9, level = 110, curr = 110.5
      → "CROSS_UP"
    
    Example 2 (Down cross):
      prev = 110.5, level = 110, curr = 109.9
      → "CROSS_DOWN"
    
    Example 3 (Within band):
      prev = 110.2, level = 110, curr = 110.3
      → None
    """
```

**Used for:**
- Detecting subsequent trade entry triggers
- Not used directly for first trade (uses trigger_hit instead)

---

**`trigger_hit(price, trigger_price)` — First Trade Trigger**

```python
def trigger_hit(price, trigger_price):
    """
    Detects if price approaches trigger level.
    
    Trigger = level - SL_POINTS
    
    Logic:
      Returns true if:
      trigger_price - 0.1 < price < trigger_price + 0.1
      
      (10 paise tolerance band, prevents multiple fires)
    
    Example:
      trigger = 2750, price = 2749.94
      → True (within 0.1 band)
    """
```

**Note:** The tolerance band prevents rapid re-triggering on slight price oscillations.

---

**`sl_hit(price, sl_price)` — Stop Loss Detection**

```python
def sl_hit(price, sl_price):
    """
    Detects if SL level is breached.
    
    Logic:
      Returns true if price <= sl_price
    
    Executed as soon as SL is hit (no tolerance band).
    
    Example:
      sl_price = 2775.50, price = 2775.50
      → True (exact hit, execute)
    """
```

**Critical:** No tolerance band here (must execute immediately on SL breach).

---

**`calculate_trailing_sl(entry, current_price, rules)` — Trailing SL Calculation**

```python
def calculate_trailing_sl(entry, current_price, rules):
    """
    Calculate new SL based on profit move.
    
    Input:
      entry: Entry price
      current_price: Current market price
      rules: Dict mapping move_levels to SL offsets
      
      Example rules:
        {100: 30, 200: 50, 400: 200}
        
        If profit >= 100, SL can be entry + 30
        If profit >= 200, SL can be entry + 50
        If profit >= 400, SL can be entry + 200
    
    Logic:
      move = current - entry
      for each threshold in ascending order:
        if move >= threshold:
          new_sl = entry + offset
      return new_sl
    
    Example:
      entry = 100, current = 250, rules = {100: 30, 200: 50}
      
      move = 150
      → 150 >= 100 → new_sl = 100 + 30 = 130
      → new_sl = 130
    """
```

**Returns:**
- `new_sl` value to pass to `modify_order()`
- `None` if no rule matches (keep current SL)

---

### Design Principles

1. **Pure Functions:**
   - No side effects
   - No state modification
   - Deterministic (same input → same output)

2. **Testability:**
   - Each function can be tested independently
   - No mocking of broker/logging needed
   - Test coverage: 100% possible

3. **Reusability:**
   - Can be used in backtesting
   - Can be used in analysis scripts
   - Not tied to Fyers API

4. **Performance:**
   - Lightweight calculations
   - No loops (except sorted iteration in trailing SL)
   - Fast enough for real-time use

---

## 4. Recovery System: `core/recovery.py` (218 lines)

### Purpose
Synchronize in-memory engine state with broker state. Called on startup and reconnection.

### Main Function: `sync_engine(engine)`

**Process:** 3-step sync

#### Step 1: Fetch Broker State

```python
positions = get_positions(fyers)           # All open positions
orders = get_orderbook(fyers)              # All pending orders
trades = fyers.tradebook().get("tradeBook", [])  # Trade history
```

#### Step 2: Reconstruct Active Trade

```python
for pos in positions:
    if pos["symbol"] == symbol and pos["qty"] != 0:
        # Position is open
        
        # Get latest BUY trade from history
        entry_price, qty = get_latest_buy_trade(fyers, symbol)
        
        # Reconstruct SL
        sl_price = calculate_sl(entry_price)
        
        # Set state
        state.set_active_trade(entry_price, sl_price, qty)
```

**Result:**
- If position open: `active_trade = True`, entry/SL set
- If position closed: `active_trade = False`, state reset

#### Step 3: Reconstruct Pending Orders

```python
entry_orders = []
sl_orders = []

for order in orders:
    if order["symbol"] == symbol and order["status"] in [6, 4]:  # Pending/confirmed
        if order["side"] == 1:  # BUY
            entry_orders.append(order)
        elif order["side"] == -1:  # SELL
            sl_orders.append(order)

# Match order IDs to state
if entry_orders:
    state.entry_order_id = entry_orders[0]["id"]
if sl_orders:
    state.sl_order_id = sl_orders[0]["id"]
```

**Result:**
- Pending entry order restored
- Pending SL order restored
- No duplicate orders created

---

### Helper Functions

**`get_latest_buy_trade(fyers, symbol)` — Trade History Lookup**

```python
def get_latest_buy_trade(fyers, symbol):
    """
    From all trades on broker, find most recent BUY for this symbol.
    
    Process:
    1. Fetch all trades from tradebook
    2. Filter by symbol
    3. Sort by timestamp (newest first)
    4. Find first BUY trade (side == 1)
    5. Return (trade_price, traded_qty)
    
    Returns:
      (entry_price, qty) if found
      (None, None) if not found
    """
```

**Used in:** Position recovery to get exact entry price

---

### Recovery Scenarios

**Scenario 1: Bot Starts, No Previous Position**

```
Broker State: No positions open, no orders pending

Sync Result:
  active_trade = False
  All IDs cleared
  Ready for new trades
```

**Scenario 2: Bot Starts, Position Open (e.g., from previous run)**

```
Broker State:
  Position: qty=1, symbol=NSE:ADANIPORTS-EQ
  Orders: No pending entry, SL order pending

Sync Result:
  active_trade = True
  entry_price = 2800.50 (from trade history)
  sl_price = 2775.50
  sl_order_id = 1052 (restored)
  entry_order_id = None
```

**Scenario 3: WebSocket Reconnects During Active Trade**

```
Previous State: active_trade=True, entry_order_id=None, sl_order_id=1050
Broker State: Position still open, SL order still pending

Sync Result:
  active_trade = True (unchanged)
  entry_price = 2800.50 (unchanged)
  sl_price = 2775.50 (unchanged)
  sl_order_id = 1050 (confirmed)
  
  → Engine resumes monitoring price for trailing SL
```

---

### Error Handling

**Case 1: Position found but no corresponding trade**

```python
# Entry price cannot be determined
→ Log error
→ Use average price: entry_price = avg_price
→ Continue with reconstructed SL
```

**Case 2: Multiple SL orders found**

```python
# Keep most recent
sl_order = sorted_orders[0]
state.sl_order_id = sl_order["id"]
```

**Case 3: Broker API timeout**

```python
# Catch exception
→ Log error with timestamp
→ Retry up to 3 times
→ If all retries fail, raise exception
→ Manual intervention needed
```

---

## 5. Broker Integration: `broker/` (5 modules)

### 5.1 Authentication: `broker/auth.py`

**Function:** `get_access_token()`

**Process:**

```
1. Create SessionModel with credentials
2. Generate OAuth2 authorization URL
3. Print URL to console
4. Prompt user to visit URL, pass auth code
5. Exchange auth code for access token
6. Validate token in response
7. Return token
```

**Manual Flow:**
- Not automated (user intervention required)
- Suitable for low-frequency token refresh
- Future: Add token persistence and refresh logic

**Error Handling:**
- Catches auth failure
- Raises exception with error message
- System halts (cannot continue without token)

---

### 5.2 Price WebSocket: `broker/data_ws.py`

**Function:** `start_ws(access_token, symbols, on_message)`

**Purpose:** Subscribe to live price feed

**Initialization:**

```python
fyers = data_ws.FyersDataSocket(
    access_token=access_token,
    litemode=False,                # Full data (not lite)
    write_to_file=False,           # No disk write
    reconnect=True,                # Auto-reconnect
    on_connect=on_connect,         # Callback when connected
    on_close=on_close,             # Callback when closed
    on_error=on_error,             # Callback on error
    on_message=onmessage,          # Callback on tick
    reconnect_retry=20             # Max retry attempts
)
```

**Callbacks:**

```python
def on_connect():
    # Subscribe to symbols and start streaming
    fyers.subscribe(symbols=symbols, data_type="SymbolUpdate")
    fyers.keep_running()

def on_message(msg):
    # Route to main.on_message(msg)
    # msg contains: symbol, ltp (last traded price), bid, ask, etc.

def on_close(message):
    # Log closure, will auto-reconnect due to reconnect=True

def on_error(message):
    # Log error, system continues
```

**Tick Data Model:**

```python
msg = {
    "symbol": "NSE:ADANIPORTS-EQ",
    "ltp": 2850.50,           # Last traded price
    "bid": 2850.45,
    "ask": 2850.55,
    "volume": 1000000,
    "oi": 5000000,
    ...
}
```

**Execution:** Runs in daemon thread (non-blocking)

---

### 5.3 Order WebSocket: `broker/order_ws.py`

**Function:** `start_order_ws(order_token, engine_router, resync_all)`

**Purpose:** Subscribe to order, trade, and position updates

**Initialization:**

```python
fyers = order_ws.FyersOrderSocket(
    order_token=order_token,  # Client-specific token
    log_path="",
    callback_order=on_order,
    callback_trade=on_trade,
    callback_position=on_position,
    callback_connect=resync_all,  # Called on reconnect
    ...
)
```

**Callbacks:**

```python
def on_order(msg):
    engine_router("ORDER", msg)
    # msg: orderId, status, symbol, qty, etc.

def on_trade(msg):
    engine_router("TRADE", msg)
    # msg: symbol, tradedQty, tradePrice, etc.

def on_position(msg):
    engine_router("POSITION", msg)
    # msg: symbol, qty, avgPrice, etc.

def on_connect():
    resync_all()  # Trigger full state sync on reconnect
```

**Execution:** Runs in daemon thread (non-blocking)

---

### 5.4 Order Operations: `broker/orders.py`

**Low-level order management wrapper**

**Functions:**

```python
def place_stop_buy(fyers, symbol, qty, trigger_price, limit_price)
    # Stop-buy order for entry
    # Returns: {s: "ok", id: "1001"} or {s: "error", ...}

def place_sl_order(fyers, symbol, qty, sl_price)
    # Protective SL order (stop-loss)
    # Returns: {s: "ok", id: "1002"} or {s: "error", ...}

def cancel_order(fyers, order_id)
    # Cancel pending order

def modify_order(fyers, order_id, new_price)
    # Modify order price (for trailing SL)

def close_position(fyers, symbol, qty)
    # Market sell to close entire position

def get_positions(fyers)
    # Fetch all open positions
    # Returns: [{symbol, qty, avgPrice, ...}]

def get_orderbook(fyers)
    # Fetch all pending orders
    # Returns: [{orderId, status, symbol, ...}]
```

**Error Handling:**
- API errors logged
- Exceptions raised
- Caller (engine) handles errors

---

### 5.5 Historical Data: `broker/data_fetch.py`

**Function:** `get_prev_day_ohlc_for_symbol(fyers, symbol)`

**Purpose:** Fetch previous day's OHLC for Fibonacci calculation

**Process:**
1. Call Fyers historical API with:
   - symbol
   - resolution = "day"
   - range_from = yesterday
   - range_to = yesterday
2. Extract: high, low, open, close
3. Return dict: `{high, low, open, close}`

**Called Once At Startup:**
- Calculates Fibonacci levels
- Levels then fixed for entire session

---

## 6. Configuration: `config/` (3 modules)

### 6.1 Settings: `config/settings.py`

**API Credentials:**
```python
CLIENT_ID = get_env("FYERS_CLIENT_ID")
SECRET_KEY = get_env("FYERS_SECRET_KEY")
REDIRECT_URI = "https://www.google.com"
```

**Trading Config:**
```python
CAPITAL = 100000         # Account size
DEFAULT_QTY = 1          # Lot size
```

**Market Config:**
```python
UNDERLYING = "BSE:SENSEX-INDEX"  # For option generation
LOG_PATH = "./logs"              # Log directory
ENABLE_LOGGING = True            # Toggle logging
```

**Helper:**
```python
def get_env(key, required=True, default=None)
    # Safe environment variable access
    # Raises error if missing and required
```

---

### 6.2 Trading Parameters: `config/trading_params.py`

**Mode Switch:**
```python
test_mode = True   # True = Equity testing, False = Live options
```

**Fibonacci Configuration:**
```python
FIB_RATIOS = [4.236, 3.618, 2.618, 1.618, 1, 0.618, 0.5, 0.382, 0, -0.618, -1, -1.618, -2.618, -3.618, -4.236]
```

**Entry & SL:**
```python
if test_mode:
    SL_POINTS = 10    # Test mode: 10 points
else:
    SL_POINTS = 25    # Live mode: 25 points
```

**Trailing SL Rules:**
```python
if test_mode:
    TRAILING_RULES = {
        5: 2,      # If profit >= 5, SL = entry + 2
        6: 3,      # If profit >= 6, SL = entry + 3
        7: 4,
        9: 5,
        12: 6,
        15: 10,
        20: 16,
        25: 20
    }
else:
    TRAILING_RULES = {
        100: 30,
        200: 50,
        400: 200,
        600: 400,
        800: 700,
        1000: 900,
        1200: 1100
    }
```

**Trade Rules:**
```python
ALLOW_ONLY_ONE_ACTIVE_TRADE_PER_SIDE = True
ENABLE_FIRST_TRADE_TRIGGER_LOGIC = True
```

**Risk Control:**
```python
if test_mode:
    MAX_TRADES_PER_DAY = 50
    MAX_DAILY_LOSS = 1000
else:
    MAX_TRADES_PER_DAY = 10
    MAX_DAILY_LOSS = 6000
```

**Execution:**
```python
USE_MARKET_ORDER_FOR_EXIT = True
USE_STOP_ORDER_FOR_ENTRY = True
```

---

### 6.3 Symbol Generation: `config/symbols.py`

**Function:** `get_option_symbols(prev_close)`

**Purpose:** Generate ATM call/put symbols from previous close

**Process:**
1. Get next expiry date (weekly or monthly)
2. Find ATM strike: nearest strike to prev_close
3. Generate call symbol: NSE:SENSEX{expiry}{strike}CE
4. Generate put symbol: NSE:SENSEX{expiry}{strike}PE
5. Return: {call, put}

**Example:**
```python
prev_close = 79500
expiry = "06-MAY-26" (next week closing)
atm_strike = 79500 (rounds to nearest 100)

→ {
    'call': 'NSE:SENSEX06MAY2679500CE',
    'put': 'NSE:SENSEX06MAY2679500PE'
}
```

---

## 7. Utilities: `utils/` (4 modules)

### 7.1 Logging: `utils/logger.py`

**Functions:**

```python
def log(message)
    # INFO level. Writes to system.log and console

def trade_log(message)
    # TRADE level. Writes to trades.log and console

def error_log(message)
    # ERROR level. Writes to errors.log and console
```

**Log Format:**
```
[INFO] 2026-05-10 09:30:45:123456 | Market starting up
[TRADE] 2026-05-10 09:35:12:456789 | Entry: NSE:ADANIPORTS-EQ @ 2800.50
[ERROR] 2026-05-10 10:45:30:789012 | Connection lost, retrying...
```

**Output:**
- Console: Real-time monitoring
- Files: Persistent audit trail
- Timestamp: Microsecond precision

---

### 7.2 State Logging: `utils/state_logger.py`

**Function:** `log_state(state, checkpoint_name)`

**Purpose:** Audit trail of state changes

**Output Example:**
```
[STATE] ENGINE - FIRST STATE
  symbol: NSE:ADANIPORTS-EQ
  active_trade: False
  entry_price: None
  sl_price: None
  entry_order_id: None
  trades_today: 0

[STATE] ENGINE - LEVEL DETECT STATE
  symbol: NSE:ADANIPORTS-EQ
  prev_price: 2850.00
  curr_index: 5
  
[STATE] TRADE EXECUTION LOG
  symbol: NSE:ADANIPORTS-EQ
  active_trade: True
  entry_price: 2800.50
  sl_price: 2775.50
  entry_order_id: None
  sl_order_id: 1052
  trades_today: 1
```

**Called at Checkpoints:**
- ENGINE - FIRST STATE
- ENGINE - LEVEL DETECT STATE
- ENGINE - SL HIT - RESET
- RECOVERY - OPEN POSITION STATE
- TRADE EXECUTION LOG

---

### 7.3 Time Utilities: `utils/time_utils.py`

**Functions:**

```python
def is_eod_exit_time()
    # Check if current time >= 3:20 PM
    # Used to trigger EOD exit

def is_market_open()
    # Check if current time is within trading hours

def get_next_expiry_date()
    # Get next weekly/monthly option expiry

def is_trading_holiday()
    # Check holidays_2026.json
```

---

### 7.4 Helpers: `utils/helpers.py`

**Utility Functions:**

```python
def round_to_tick(price, tick_size=0.05)
    # Round price to valid tick size

def get_tick_size(symbol)
    # Get tick size for symbol from NSE symbol master
```

---

## Summary: Component Interaction Map

```
┌─────────────────────────────────────────┐
│ MAIN (main.py)                          │
│ - Initializer                           │
│ - Callback dispatcher                   │
└──────────────────┬──────────────────────┘
                   │
                   ├─→ ENGINE (core/engine.py)
                   │   - Tick processor
                   │   - Decision maker
                   │   - Order manager
                   │
                   ├─→ STATE (core/state.py)
                   │   - State holder
                   │   - Lifecycle tracker
                   │
                   ├─→ EVENTS (core/events.py)
                   │   - Signal detector (pure)
                   │
                   ├─→ STRATEGY (strategy/fib_strategy.py)
                   │   - Trading rules (pure)
                   │
                   ├─→ RECOVERY (core/recovery.py)
                   │   - Broker sync
                   │   - State reconstruction
                   │
                   └─→ BROKER (broker/)
                       - auth.py (token)
                       - data_ws.py (prices)
                       - order_ws.py (orders)
                       - orders.py (CRUD)
                       - data_fetch.py (history)
```

---

## Module Dependencies

```
main.py
  ├── imports: broker/auth, broker/data_ws, broker/order_ws, 
  │            core/engine, core/recovery, config/symbols
  ├── calls: engine.on_tick(), engine.handle_*_update(), 
  │          engine.force_exit()
  ├── creates: Engine instances
  
core/engine.py
  ├── imports: core/state, core/events, strategy/fib_strategy,
  │            broker/orders, config/trading_params
  ├── contains: Main decision logic, order execution
  
core/recovery.py
  ├── imports: broker/orders, strategy/fib_strategy
  ├── calls: get_positions(), get_orderbook()
  ├── purpose: State reconstruction from broker
  
broker/data_ws.py
  ├── imports: fyers_apiv3 WebSocket
  ├── calls: on_message() callback
  
broker/order_ws.py
  ├── imports: fyers_apiv3 WebSocket
  ├── calls: engine_router() callback
  
strategy/fib_strategy.py
  ├── imports: config/trading_params
  ├── purpose: Pure trading rules
  
config/trading_params.py
  ├── contains: Static parameters
  ├── imported by: engine, strategy
```

---

## Next Steps

- See `DATA_FLOW.md` for execution paths
- See `STRATEGY.md` for trading logic details
- See `INTEGRATION.md` for deployment procedures


