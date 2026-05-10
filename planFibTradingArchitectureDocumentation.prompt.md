# Plan: Create Comprehensive Architecture & Implementation Documentation

## Executive Summary

Create a `docs` folder with structured markdown files documenting the Fibonacci Trading Automation system's event-driven architecture, component interactions, data flow, strategy logic, and deployment procedures. All documentation will be reference-based without modifying any existing codebase.

---

## Objectives

1. **Provide System Overview** — Document high-level architecture philosophy and design patterns
2. **Detail Component Responsibilities** — Break down each module's purpose, interfaces, and dependencies
3. **Illustrate Data Flows** — Show tick processing, order execution, WebSocket event routing, and recovery patterns
4. **Explain Strategy Implementation** — Detail Fibonacci level generation, entry/exit rules, SL mechanics, and risk parameters
5. **Enable Operational Deployment** — Document broker integration, authentication, environment setup, and production readiness checks

---

## Architecture Overview

### Core Philosophy (Broker = Truth)

```
Broker = Source of Truth (single point of reality)
Engine State = Real-time Mirror (derived from broker)
WebSocket = Event Triggers (price and order notifications)
Recovery System = Sync Mechanism (validates and corrects state)
```

**Key Principles:**
- Event-driven execution (no polling)
- Stateless logic (state derived from broker)
- Deterministic recovery (broker-synced)
- O(1) level detection (performance optimized)
- No database dependency (in-memory state only)

---

## System Layers (Clean Architecture)

```
┌─────────────────────────────────────────────────────────┐
│ MAIN ORCHESTRATOR (main.py)                             │
│ - System initialization                                 │
│ - WebSocket startups                                    │
│ - Callback routing                                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ ENGINE LAYER (core/engine.py)                           │
│ - Tick processing                                       │
│ - Level detection & crossings                           │
│ - Entry/exit decision logic                             │
│ - State management (active trade tracking)              │
│ - Order lifecycle management                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STRATEGY & EVENT LAYERS                                 │
│ - core/events.py: Fast event detection (no logic)       │
│ - strategy/fib_strategy.py: Pure trading rules          │
│ - core/state.py: Trade state representation             │
│ - core/recovery.py: Broker state sync                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ BROKER INTEGRATION (broker/)                            │
│ - broker/auth.py: OAuth2 authentication                 │
│ - broker/data_ws.py: Price feed WebSocket               │
│ - broker/order_ws.py: Orders/positions WebSocket        │
│ - broker/orders.py: Broker order actions                │
│ - broker/data_fetch.py: Historical OHLC data            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ UTILITIES & CONFIG (config/, utils/)                    │
│ - config/settings.py: API & system credentials          │
│ - config/trading_params.py: Strategy parameters         │
│ - config/symbols.py: Option symbol generation           │
│ - utils/logger.py: Unified logging                      │
│ - utils/state_logger.py: State audit trail              │
│ - utils/time_utils.py: Market session checks            │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.11+ | Core implementation |
| Broker API | Fyers API v3 | Market data & order execution |
| Market Data | WebSocket (SymbolUpdate) | Real-time price ticks |
| Execution | WebSocket (orders/trades/positions) | Order confirmations & fills |
| Architecture | Event-driven | Reactive programming model |
| Storage | In-memory + Broker sync | No database required |
| Logging | File-based + Console | System & trade audit trail |

---

## Documentation Structure (Files to Create)

### 1. `docs/ARCHITECTURE.md` — High-Level System Design

**Contents:**
- System philosophy & design patterns
- Layered architecture breakdown
- Enterprise-grade concepts (recovery, state consistency, audit trail)
- Technology stack rationale
- Performance design (O(1) level detection, WebSocket-only)
- Data consistency model (broker as source of truth)

### 2. `docs/COMPONENTS.md` — Module-Level Details

**Contents:**
- **Engine (core/engine.py)**
  - Responsibilities: Tick processing, level detection, trade decisions
  - Key methods: `on_tick()`, `enter_trade()`, `exit_trade()`, handle_*_update()
  - State lifecycle: Initialization → Monitoring → Entry → Active → Exit → Reset
  
- **State Management (core/state.py)**
  - TradeState class: market state, active trade tracking, order IDs, risk flags
  - Methods: set_active_trade(), reset_trade(), update_sl()
  
- **Event Detection (core/events.py)**
  - Fast, logic-free event signals
  - Functions: get_level_index(), detect_cross(), trigger_hit(), sl_hit(), calculate_trailing_sl()
  
- **Recovery System (core/recovery.py)**
  - Startup recovery: fetch broker positions & orders, rebuild state
  - Reconnect recovery: triggered on WebSocket reconnection
  - Real-time position sync: handle_position_update()
  
- **Broker Integration (broker/)**
  - auth.py: OAuth2 token generation
  - data_ws.py: Price feed subscription & tick routing
  - order_ws.py: Order/trade/position event handling
  - orders.py: Low-level CRUD operations (place, cancel, modify, get)
  - data_fetch.py: Historical OHLC fetching
  
- **Configuration (config/)**
  - settings.py: API credentials, market config
  - trading_params.py: Strategy parameters (SL, trailing rules, limits)
  - symbols.py: Option symbol generation logic

### 3. `docs/DATA_FLOW.md` — Event Processing & Execution Paths

**Contents:**
- **Initialization Flow**
  ```
  Start → Load Config → Fetch Prev OHLC → Generate Fib Levels 
  → Create Engines → Initial Recovery → Start WebSockets → Trading Loop
  ```
  
- **Price Tick Flow**
  ```
  WebSocket tick → on_message() → Route to Engine.on_tick()
  → Level detection → Entry/SL/Trailing decisions → Broker orders
  ```
  
- **Order/Trade Execution Flow**
  ```
  Entry signal → place_stop_buy() → Trade WebSocket confirms
  → handle_trade_update() → place_sl_order() → Active trade state
  ```
  
- **Position Sync Flow**
  ```
  Broker position change → Position WebSocket 
  → handle_position_update() → SL order placement/modification
  ```
  
- **Recovery Flow**
  ```
  Startup/Reconnect → Fetch positions & orders from broker
  → Rebuild active_trade, entry_order_id, sl_order_id → Validate state
  ```
  
- **Error Handling Path**
  ```
  Exception → error_log() → State audit via log_state()
  → Graceful degradation or manual intervention
  ```

### 4. `docs/STRATEGY.md` — Trading Logic & Risk Management

**Contents:**
- **Fibonacci Level Generation**
  - Input: Previous day HIGH, LOW
  - Logic: diff = HIGH - LOW; levels = [HIGH - diff * ratio for ratio in FIB_RATIOS]
  - Ratios: [4.236, 3.618, ..., 0.618, 0.5, ..., -4.236]
  - Output: Sorted, deduplicated, tick-rounded levels
  
- **Entry Rules**
  - **First Trade:**
    - Trigger = level - SL_POINTS
    - Condition: price <= trigger → place stop-buy at level
    - Only once per session
  
  - **Subsequent Trades:**
    - Condition: detect_cross(prev_price < level, curr_price >= level)
    - Only after previous trade exits
    - Max 1 active trade per side (ALLOW_ONLY_ONE_ACTIVE_TRADE_PER_SIDE = True)
  
- **Stop Loss Management**
  - **Fixed SL:** entry_price - SL_POINTS
  - **Trailing SL:** Applied when price moves in profit
    - Rules table (config/trading_params.py):
      - Test mode: {5: 2, 6: 3, 7: 4, ..., 25: 20}
      - Live mode: {100: 30, 200: 50, 400: 200, ..., 1200: 1100}
    - Logic: For each move_level in rules, if (current - entry) >= move_level, set new_sl = entry + rules[move_level]
  
- **End-of-Day (EOD) Exit**
  - Time trigger: 3:20 PM
  - Action: Force close all positions using market orders
  
- **Risk Parameters**
  - SL_POINTS: 10 (test), 25 (live)
  - TRAILING_RULES: Dynamic SL based on profit
  - MAX_TRADES_PER_DAY: 50 (test), 10 (live)
  - MAX_DAILY_LOSS: 1000 (test), 6000 (live)

### 5. `docs/INTEGRATION.md` — Deployment & Operations

**Contents:**
- **Broker Integration**
  - Fyers API v3 (REST + WebSocket)
  - Authentication: OAuth2 with manual auth code entry
  - Credentials: FYERS_CLIENT_ID, FYERS_SECRET_KEY (environment variables)
  
- **Environment Setup**
  ```
  set FYERS_CLIENT_ID=your_client_id
  set FYERS_SECRET_KEY=your_secret_key
  pip install -r requirements.txt
  python main.py
  ```
  
- **Mode Switching**
  - Test Mode (main.py line 54): test_mode = True
    - Trades NSE:ADANIPORTS-EQ (equity)
    - Small SL (10 points) for fast iteration
  
  - Live Mode (main.py line 54): test_mode = False
    - Trades BSE Sensex Call & Put options
    - Full strategy with 25-point SL
  
- **WebSocket Subscriptions**
  - Data WS: SymbolUpdate for price ticks on [symbol]
  - Order WS: Orders, Trades, Positions for execution feedback
  
- **Recovery Scenarios**
  - **Startup Recovery**: Syncs with broker on initialization
  - **Reconnect Recovery**: Triggered by order_ws.on_connect(), resync_all()
  - **Graceful Degradation**: State corrections logged, system continues
  
- **Operational Checks**
  - [ ] Verify symbol generation (weekly/monthly expiry logic)
  - [ ] Test reconnect scenarios (WS drop/resume)
  - [ ] Run with 1 lot initially (scale after validation)
  - [ ] Monitor log files (system.log, trades.log, errors.log)
  - [ ] Validate auth token refresh (if needed)
  
- **Monitoring & Debugging**
  - Logs: `/logs/system.log`, `/logs/trades.log`, `/logs/errors.log`
  - State audit: `log_state()` function captures full state at key checkpoints
  - WebSocket logs: `fyersApi.log`, `fyersDataSocket.log`, `fyersOrderSocket.log`
  
- **Production Readiness Checklist**
  - [ ] Recovery system tested with reconnects
  - [ ] Trailing SL rules validated against historical data
  - [ ] EOD exit tested (position closed before 3:20 PM)
  - [ ] Max daily loss enforcement configured
  - [ ] Error handling & alerts in place

---

## Key Design Patterns

### 1. Event-Driven Architecture
- WebSocket callbacks drive all logic (no polling)
- Price ticks → Engine.on_tick()
- Order updates → engine_router(event_type, msg)
- Position updates → handle_position_update()

### 2. Separation of Concerns
- **events.py**: Pure signal detection (no business logic)
- **fib_strategy.py**: Pure strategy rules (no execution)
- **engine.py**: Orchestrates decisions → broker orders
- **recovery.py**: State validation & correction

### 3. Broker as Source of Truth
- State is derived from broker (not authoritative)
- Recovery syncs engine state with broker state
- Position changes trigger immediate state reconstruction

### 4. O(1) Performance
- Fibonacci levels stored in sorted array
- Bisect algorithm for fast level index lookup
- No loops in hot paths (on_tick)

---

## Known Limitations & Trade-offs

1. **No Database**
   - trades_today resets on restart
   - first_trade_done resets on restart
   - Solution: Add persistent trade journal (CSV/DB) for future

2. **State Resilience**
   - Recovery depends on broker's trade history API
   - If broker API is down, state may not recover
   - Mitigation: Implement local state cache with fallback logic

3. **Multi-symbol Scaling**
   - Currently single symbol per engine
   - Multiple engines work, but no load balancing
   - Future: Implement engine pool manager

4. **Latency Sensitivity**
   - SL detection relies on tick granularity
   - Fast markets may miss levels
   - Optimization: Implement tick aggregation buffer (future)

---

## Future Enhancements

### High Priority
- Max daily loss enforcement
- Trade journal (CSV export)
- PnL tracking per trade
- Reconnection watchdog

### Medium Priority
- Multi-strategy engine support
- Position scaling (pyramiding)
- Auto-restart capability
- Latency monitoring & alerts

### Advanced
- Dashboard (Streamlit/React)
- Backtesting engine
- Multi-broker support
- ML-based level prediction

---

## File Structure After Documentation

```
Fib_Trading/
├── docs/
│   ├── ARCHITECTURE.md           # System design & philosophy
│   ├── COMPONENTS.md             # Module-level details
│   ├── DATA_FLOW.md              # Event flows & execution paths
│   ├── STRATEGY.md               # Trading logic & risk management
│   ├── INTEGRATION.md            # Deployment & operations
│   └── README.md                 # Index & quick reference
├── main.py
├── core/
├── broker/
├── strategy/
├── config/
├── utils/
├── data/
├── logs/
└── requirements.txt
```

---

## Documentation Best Practices

1. **Reference-Based**: All docs reference actual code files (no duplication)
2. **Executed Examples**: Code snippets from actual implementation
3. **Audit Trail**: State logging patterns documented for debugging
4. **Operational Guidance**: Deployment checklists & monitoring procedures
5. **Expandable**: Structure supports future additions (e.g., backtesting docs)

---

## Success Criteria

- ✅ All modules documented with clear responsibilities
- ✅ Data flows illustrated with ASCII diagrams
- ✅ Strategy logic explained with parameter examples
- ✅ Recovery scenarios mapped to actual code paths
- ✅ Deployment procedures clear & actionable
- ✅ Production readiness checklist complete
- ✅ No code changes made to existing codebase

---

## Implementation Order

1. Create `docs/` folder
2. Write `ARCHITECTURE.md` (high-level overview)
3. Write `COMPONENTS.md` (module details)
4. Write `DATA_FLOW.md` (execution paths)
5. Write `STRATEGY.md` (trading logic)
6. Write `INTEGRATION.md` (deployment)
7. Create `docs/README.md` (index & navigation)
8. Validate all cross-references & code citations

---

## Estimated Scope

- **ARCHITECTURE.md**: 400-500 lines
- **COMPONENTS.md**: 600-700 lines
- **DATA_FLOW.md**: 500-600 lines
- **STRATEGY.md**: 400-500 lines
- **INTEGRATION.md**: 350-450 lines
- **Total**: ~2,500-2,750 lines of comprehensive documentation
- **Time**: 4-6 hours with code review
- **Risk**: Low (reference-based, no code changes)

---

## Quality Assurance

- [ ] All file paths verified
- [ ] Code citations match actual implementation
- [ ] ASCII diagrams tested for readability
- [ ] Cross-references validated
- [ ] No typos or inconsistencies
- [ ] Deployment steps executable
- [ ] Checklist items actionable

---

## Notes

- Documentation assumes Python 3.11+, Fyers API v3
- Current date: May 10, 2026 (trading system context)
- System is production-ready pending testing verification
- Recovery system is institutional-grade (broker-synced)
- No database required (in-memory state only)


