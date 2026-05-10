# System Architecture: Fibonacci Trading Automation

## 🏗️ High-Level Design Philosophy

### Core Principle: "Broker = Truth"

```
Broker = Source of Truth (single point of reality)
         ↓
Engine State = Real-time Mirror (derived from broker state)
         ↓
WebSocket = Event Triggers (price ticks & order confirmations)
         ↓
Recovery System = Sync Mechanism (validates & corrects state)
```

This design ensures:
- **No blind assumptions** — Trade state is always validated against broker
- **No polling-based execution** — Fully event-driven via WebSocket
- **Deterministic recovery** — Broker is always the source of truth
- **State consistency** — Engine state is reconstructed from broker on reconnect
- **Audit trail** — All state changes logged for debugging

---

## 🔄 System Layers (Clean Architecture)

The system is structured in **4 distinct layers**, each with clear responsibilities:

### Layer 1: Orchestration (`main.py`)
**Responsibility:** System initialization and callback routing

- Authenticates with broker
- Fetches previous day OHLC and calculates Fibonacci levels
- Creates Engine instances (one per symbol/strategy)
- Initializes recovery system
- Starts WebSocket threads for price feed and order updates
- Routes price ticks and order events to appropriate engines
- Manages EOD exit workflow

**Key Functions:**
- `initialize_system()` — Startup sequence
- `on_message(msg)` — Price callback from data WebSocket
- `engine_router(event_type, msg)` — Order/trade event dispatcher
- `resync_all()` — Reconnect recovery trigger

---

### Layer 2: Execution Engine (`core/engine.py`)
**Responsibility:** Real-time trading decision and order lifecycle management

The **Engine** is the brain of the system. It operates as a state machine:

```
IDLE (no trade) → MONITORING (waiting for signal)
     ↓
ENTRY TRIGGERED (order placed)
     ↓
ACTIVE (position open, SL placed)
     ↓
EXIT (position closed via SL or manual)
     ↓
IDLE (ready for next trade)
```

**Key Responsibilities:**
1. **Tick Processing** — `on_tick(price)`
   - Detects current level band (O(1) bisect lookup)
   - Identifies level crossings
   - Triggers entry/exit/trailing SL logic

2. **Entry Logic** — `enter_trade(level, price)`
   - Validates first-trade trigger or cross condition
   - Places stop-buy order at Fibonacci level
   - Tracks entry_order_id

3. **Trade Management** — `handle_trade_update(msg)`
   - Processes fill confirmation from broker
   - Calculates fixed SL = entry - SL_POINTS
   - Places SL order immediately
   - Activates trading state

4. **Risk Management** — `on_tick()` (trailing logic)
   - Monitors profit (price - entry)
   - Applies trailing SL rules from trading_params.py
   - Modifies SL order to lock in profits

5. **Exit Handling** — `handle_position_update(msg)` and `force_exit()`
   - Processes SL execution or manual exit
   - Resets trade state
   - Prepares for next trade

---

### Layer 3: Strategy & Event Detection (`core/`, `strategy/`)

This layer contains **pure logic** with **no side effects**:

#### `core/events.py` — Fast Event Signals
Detects trading signals without any business logic:

```python
def get_level_index(price, levels)           # Find current level band (O(1))
def detect_cross(prev_price, curr_price, level)  # Upside/downside crossing
def trigger_hit(price, trigger)              # First trade trigger
def sl_hit(price, sl_price)                  # Stop loss breach
def calculate_trailing_sl(entry, price, rules)  # New trailing SL
```

**Design Pattern:** Functions are pure (no state), deterministic, and tested independently.

#### `strategy/fib_strategy.py` — Strategy Rules
Encodes all trading rules:

```python
def generate_fib_levels(prev_high, prev_low)      # Fibonacci calculation
def get_trigger_price(level)                      # Trigger = level - SL_POINTS
def should_place_first_trade(price, level)        # First entry condition
def should_place_subsequent_trade(prev_price, curr_price, level)  # Re-entry
def calculate_sl(entry_price)                     # Fixed SL calculation
```

**Design Pattern:** Strategy functions are parameterized (from `trading_params.py`), pure, and reusable.

#### `core/state.py` — Trade State Representation
Single source of truth for engine state:

```python
class TradeState:
    symbol              # Trading symbol (e.g., "NSE:ADANIPORTS-EQ")
    prev_price          # Last received price (for crossing detection)
    curr_index          # Current level index (for fast band detection)
    
    active_trade        # Boolean: is there an open position?
    entry_price         # Entry price of current trade
    sl_price            # Current SL price (fixed or trailing)
    qty                 # Position quantity
    
    entry_order_id      # ID of pending entry order
    sl_order_id         # ID of pending/active SL order
    
    first_trade_done    # Boolean: has first trade been triggered this session?
    trades_today        # Counter: total trades executed today
```

**Methods:**
- `set_active_trade()` — Transition from order to active trade
- `reset_trade()` — Reset state after exit
- `update_sl()` — Update SL price (trailing)

---

### Layer 4: Broker Integration (`broker/`)

All communication with Fyers broker happens here:

#### `broker/auth.py` — OAuth2 Authentication
```python
def get_access_token()
```
- Generates OAuth2 authorization URL
- Prompts for manual auth code entry
- Exchanges auth code for access token
- Returns token for API calls

**Pattern:** Manual entry (suitable for trading systems with low frequency token refresh)

#### `broker/data_ws.py` — Price Feed WebSocket
```python
def start_ws(access_token, symbols, on_message)
```
- Subscribes to real-time SymbolUpdate feed
- Calls `on_message(tick)` for every price update
- Handles reconnection with exponential backoff
- Runs in daemon thread (non-blocking)

**Data Model:**
```python
msg = {
    "symbol": "NSE:ADANIPORTS-EQ",
    "ltp": 2850.50,  # Last traded price
    ...other fields...
}
```

#### `broker/order_ws.py` — Order/Trade/Position WebSocket
```python
def start_order_ws(order_token, engine_router, resync_all)
```
- Subscribes to order, trade, and position update streams
- Routes events to `engine_router(event_type, msg)`:
  - `event_type = "TRADE"` → trade execution event
  - `event_type = "ORDER"` → order status change
  - `event_type = "POSITION"` → position balance change
- Triggers `resync_all()` on reconnection
- Runs in daemon thread (non-blocking)

#### `broker/orders.py` — Broker Order Operations
Low-level CRUD operations wrapping Fyers API:

```python
def place_stop_buy(fyers, symbol, qty, trigger_price, limit_price)
def place_sl_order(fyers, symbol, qty, sl_price)
def cancel_order(fyers, order_id)
def modify_order(fyers, order_id, new_price)
def close_position(fyers, symbol, qty)
def get_positions(fyers)
def get_orderbook(fyers)
```

**Pattern:** Minimal wrapper around Fyers API (no business logic, just formatting)

#### `broker/data_fetch.py` — Historical Data
```python
def get_prev_day_ohlc_for_symbol(fyers, symbol)
```
- Fetches 1-day OHLC for previous trading day
- Used for initial Fibonacci level calculation
- Data retrieved once at system startup

---

## 🔐 Recovery System (Institutional-Grade)

The recovery system ensures state consistency across three scenarios:

### 1. Startup Recovery (`sync_engine()` at line 127-131 in main.py)

**Scenario:** Bot starts after being offline (crash, restart, etc.)

**Process:**
1. Fetch open positions from broker
2. Fetch pending orders from broker
3. Match positions to symbols:
   - If position found → Extract entry_price from trade history
   - Reconstruct sl_price = entry_price - SL_POINTS
   - Set active_trade = True
4. Match orders to symbols:
   - Entry orders (buy, status=pending) → Restore entry_order_id
   - SL orders (sell, status=pending) → Restore sl_order_id

**State After Recovery:**
- If position open: `active_trade=True`, `entry_order_id=None`, `sl_order_id={pending_id}`
- If position closed: `active_trade=False`, all IDs cleared
- If entry order pending: `active_trade=False`, `entry_order_id={pending_id}`

**Code Location:** `core/recovery.py` lines 35-160

---

### 2. Reconnect Recovery (Triggered on WebSocket reconnect)

**Scenario:** WebSocket connection drops and recovers

**Process:**
1. `order_ws.on_connect()` callback triggered
2. Calls global `resync_all()` function (main.py line 138-164)
3. Skips resync on first connect (avoids duplicate sync)
4. For subsequent reconnects: Calls `sync_engine()` for all engines

**Effect:** State corrected without missing price ticks

**Code Location:** main.py lines 138-164, broker/order_ws.py

---

### 3. Real-Time Position Sync (Position updates)

**Scenario:** Broker position changes (SL hit, manual close, etc.)

**Process:**
1. Broker executes SL or position change
2. Position WebSocket fires → `on_position()` event
3. Main router calls `engine.handle_position_update(msg)`
4. Engine validates position quantity:
   - If qty = 0 → Reset trade state
   - If qty < previous → Partial close (log warning)
   - Should not happen under normal operation

**Code Location:** main.py lines 223-224, core/engine.py lines 300+

---

## ⚡ Performance Optimizations

### O(1) Level Detection
```python
# Regular approach (naive - slow)
for i, level in enumerate(levels):
    if level <= price < levels[i+1]:
        return i  # O(n)

# Optimized approach (used in production)
idx = bisect.bisect_left(levels, price) - 1
idx = max(0, min(idx, len(levels) - 2))
return idx  # O(log n), and cached with get_level_index()
```

**Caching Strategy:** `curr_index` cached in state, only recalculated if price moves to adjacent band

### No Polling
- All execution driven by WebSocket callbacks
- No background threads checking conditions
- Minimal CPU usage when market is quiet

### Lock-Free Updates
- Engine state updated only in main thread (WebSocket callbacks)
- No multi-threaded state access issues
- Simple and correct by design

---

## 🔄 Event-Driven State Machine

```
                    ┌─────────────────────────────────────┐
                    │ IDLE (No Active Trade)              │
                    │ - Waiting for entry signal          │
                    │ - Monitoring price at levels        │
                    └──────────────┬──────────────────────┘
                                   │
                                   │ Entry condition met:
                                   │ - First trigger: price <= (level - SL_POINTS)
                                   │ - Subsequent: price crosses level upward
                                   ↓
              ┌────────────────────────────────────────────────┐
              │ ENTRY_PENDING (Entry Order Placed)             │
              │ - entry_order_id set                           │
              │ - Waiting for fill from broker                 │
              └──────────────┬─────────────────────────────────┘
                             │
                             │ Trade WebSocket: Order filled
                             ↓
              ┌────────────────────────────────────────────────┐
              │ ACTIVE (Position Open, SL Pending)             │
              │ - active_trade = True                          │
              │ - entry_price set                              │
              │ - sl_order_id pending                          │
              └──────────────┬─────────────────────────────────┘
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
   (1) Price moves        (2) SL triggered       (3) EOD exit
      in profit              (price <= SL)       (3:20 PM)
      │                      │                      │
      ↓                      ↓                      ↓
   Update SL          Close position       Force exit
   (trailing)         (SL order executed)  (market order)
      │                      │                      │
      └──────────────────────┼──────────────────────┘
                             │
                             ↓
                    ┌─────────────────────────────────────┐
                    │ IDLE (Trade Complete)               │
                    │ - State reset                       │
                    │ - Ready for next trade              │
                    └─────────────────────────────────────┘
```

---

## 📊 Technology Stack Rationale

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.11+ | Fast development, finance libraries, readable code for trading logic |
| Broker | Fyers API v3 | Cost-effective NSE/BSE options trading, WebSocket support |
| Data Feed | WebSocket | Real-time, low-latency, no HTTP overhead |
| Execution | WebSocket | Order confirmations instant, recovery easier than long-polling |
| Architecture | Event-driven | Reactive programming matches trading needs (respond to ticks) |
| Storage | None (in-memory) | Simplifies deployment, state derived from broker, recovery always available |
| Logging | File-based | Audit trail for debugging, no external service dependency |

---

## 🛡️ Resilience Mechanisms

### 1. Graceful Degradation
If a non-critical operation fails:
- Exception caught and logged
- System continues operation
- State remains valid (derived from broker)

### 2. Automatic Reconnection
- Data WebSocket: `reconnect=True`, `reconnect_retry=20`
- Order WebSocket: Auto-reconnect with exponential backoff
- Resync triggered on successful reconnect

### 3. Fallback Recovery
- On startup: Full state reconstruction from broker
- On reconnect: Incremental sync with broker
- On error: Manual intervention possible (state is always available)

### 4. Audit Trail
- Every state change logged to `system.log`
- Trade events logged to `trades.log`
- Errors logged to `errors.log`
- Full state snapshots via `log_state()` at key checkpoints

---

## ⚙️ Configuration Management

**Static Configuration** (`config/settings.py`):
```python
CLIENT_ID = os.getenv("FYERS_CLIENT_ID")     # API credentials
SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
UNDERLYING = "BSE:SENSEX-INDEX"              # For option symbol generation
LOG_PATH = "./logs"                          # Log directory
```

**Strategy Parameters** (`config/trading_params.py`):
```python
test_mode = True/False                        # Mode switch
FIB_RATIOS = [4.236, 3.618, ...]            # Fibonacci sequence
SL_POINTS = 10 (test) or 25 (live)          # Stop loss distance
TRAILING_RULES = {...}                       # Trailing SL thresholds
MAX_TRADES_PER_DAY = 50 (test) or 10 (live) # Risk limit
MAX_DAILY_LOSS = 1000 (test) or 6000 (live) # Loss limit
```

**Symbol Configuration** (`config/symbols.py`):
```python
def get_option_symbols(prev_close)            # Generates ATM call/put from prev close
```

---

## 🔍 Debugging & Observability

### Logging Levels
1. **INFO** (system.log) — General flow, startup, shutdown
2. **TRADE** (trades.log) — Entry, exit, SL modification
3. **ERROR** (errors.log) — Exceptions, failures, retries

### State Logging
```python
log_state(state, checkpoint_name)
# Output: Full TradeState object at key execution points
```

**Checkpoints:**
- ENGINE - FIRST STATE (initial tick)
- ENGINE - LEVEL DETECT STATE (every level change)
- ENGINE - SL HIT - RESET (after SL execution)
- RECOVERY - OPEN POSITION STATE (position found during sync)
- TRADE EXECUTION LOG (complete trade lifecycle)

### Monitoring Dashboard (Future)
- Current price vs levels
- Active trade P&L
- Order book status
- Recovery health

---

## 🚀 Deployment Model

### Single Bot Instance
- 1 Fyers account
- Multiple symbols via multiple Engine instances
- Shared recovery system
- Shared WebSocket connections

### Scaling Strategy (Future)
- Load balancer distributes symbols across multiple bot instances
- Shared broker sync queue
- Centralized recovery service

---

## Summary Table: Layers & Responsibilities

| Layer | Files | Responsibility | Pattern |
|-------|-------|-----------------|---------|
| **Orchestration** | main.py | System init, callback routing | Event dispatcher |
| **Execution** | core/engine.py | State machine, trade decisions | State observer |
| **Strategy** | strategy/fib_strategy.py, core/events.py | Trading rules, signals | Pure functions |
| **State** | core/state.py | State representation | Data class |
| **Recovery** | core/recovery.py | Broker-state sync | Recovery pattern |
| **Broker** | broker/* | API communication | Adapter pattern |
| **Config** | config/* | Parameters | Singleton |
| **Utils** | utils/* | Logging, time, helpers | Utilities |

---

## Next Steps

- See `COMPONENTS.md` for detailed module breakdown
- See `DATA_FLOW.md` for execution path visualization
- See `STRATEGY.md` for trading logic deep-dive
- See `INTEGRATION.md` for deployment procedures


