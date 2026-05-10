# Fibonacci Trading Automation: Documentation Index

## 📚 Complete System Documentation

Welcome to the Fibonacci Trading Automation documentation. This directory contains comprehensive guides for understanding, deploying, and operating the system.

---

## 📖 Documentation Files

### 1. **ARCHITECTURE.md** — System Design & Philosophy
**Read this first to understand the big picture**

- **High-level system design**
  - Core philosophy: "Broker = Truth"
  - 4-layer clean architecture
  - Event-driven execution model
  
- **System layers breakdown**
  - Orchestration (main.py)
  - Execution (core/engine.py)
  - Strategy & events (core/, strategy/)
  - Broker integration (broker/)
  
- **Recovery system (institutional-grade)**
  - Startup recovery
  - Reconnect recovery
  - Real-time position sync
  
- **Performance optimizations**
  - O(1) level detection
  - WebSocket-only execution
  - Lock-free updates
  
- **Technology rationale**
  - Why Python, Fyers, WebSocket, etc.
  - Technology stack table

**Time to read:** ~15-20 minutes
**Best for:** Architects, system designers, management

---

### 2. **COMPONENTS.md** — Module-Level Details
**Read this to understand individual modules**

- **Engine (core/engine.py)**
  - Tick processing
  - Entry/exit logic
  - Order lifecycle
  - State machine transitions
  
- **State Management (core/state.py)**
  - TradeState class
  - State lifecycle
  - Methods and transitions
  
- **Event Detection (core/events.py)**
  - Pure signal functions
  - Level detection (O(1) algorithm)
  - Cross detection
  - SL/trailing SL calculation
  
- **Recovery System (core/recovery.py)**
  - Startup sync
  - Reconnect sync
  - Error handling
  
- **Broker Integration (broker/)**
  - Authentication (OAuth2)
  - Data WebSocket
  - Order WebSocket
  - Order operations
  - Historical data fetch
  
- **Configuration (config/)**
  - Settings
  - Trading parameters
  - Symbol generation
  
- **Utilities (utils/)**
  - Logging
  - State logging
  - Time utilities
  - Helpers

**Time to read:** ~25-30 minutes
**Best for:** Developers, engineers, code reviewers

---

### 3. **DATA_FLOW.md** — Event Flows & Execution Paths
**Read this to trace how data moves through the system**

- **System initialization flow**
  - Startup sequence
  - State machine
  - Bootstrap phases
  
- **Price tick flow**
  - WebSocket → on_tick()
  - Level detection
  - Entry signals
  - SL checks
  - Trailing SL updates
  
- **Order execution flow**
  - Entry → Pending → Fill → SL
  - Exit scenarios (SL hit, trailing, EOD)
  - Error handling
  
- **Recovery flows**
  - Startup sync
  - Reconnect sync
  - Position recovery
  - Order recovery
  
- **Error handling patterns**
  - Graceful degradation
  - Exception handling
  - Manual recovery
  
- **State consistency guarantees**
  - Atomic transitions
  - Broker validation
  - Audit trail
  
- **Performance characteristics**
  - Tick latency (<5ms)
  - Order latency (5-10ms)
  - Recovery latency (100-500ms)

**Time to read:** ~30-40 minutes
**Best for:** Traders, risk managers, ops teams, QA

---

### 4. **STRATEGY.md** — Trading Logic & Risk Management
**Read this to understand the trading strategy**

- **Fibonacci level generation**
  - Mathematical basis
  - Fibonacci ratios
  - Example calculation (NSE:ADANIPORTS)
  - Most predictive ratios
  
- **Entry rules**
  - First trade trigger
  - Subsequent trade entry
  - One active trade per side
  - Entry condition detection
  
- **Stop loss management**
  - Fixed SL calculation
  - Trailing SL rules
  - Trailing SL algorithm
  - Profit locking
  
- **Exit strategies**
  - SL hit
  - Trailing SL execution
  - EOD forced exit
  - Manual exit (future)
  
- **Risk management**
  - Maximum daily trades
  - Maximum daily loss
  - Position sizing
  - Risk/reward analysis
  
- **Expected performance**
  - Win rate analysis
  - Backtesting considerations
  - Configuration profiles (test vs live)
  
- **Strategy pseudocode**
  - Complete trading session flow
  - Decision tree

**Time to read:** ~35-45 minutes
**Best for:** Traders, strategists, analysts, investors

---

### 5. **INTEGRATION.md** — Deployment & Operations
**Read this to set up and run the system**

- **System setup & prerequisites**
  - Fyers account
  - Python environment
  - System requirements
  
- **Installation steps**
  - Virtual environment
  - Dependency installation
  - Verification
  
- **Configuration**
  - Environment variables (API credentials)
  - Configuration files
  - Mode switching (test vs live)
  
- **Running the system**
  - Direct execution
  - Background processes
  - Scheduled startup
  
- **Broker integration details**
  - OAuth2 flow
  - WebSocket subscriptions
  - Order types & execution
  
- **Monitoring & observability**
  - Log files
  - Monitoring checklist
  - Log patterns
  - Dashboard planning
  
- **Recovery scenarios**
  - WebSocket disconnect
  - Bot crash
  - Broker API timeout
  - Missing SL order
  
- **Configuration tuning**
  - SL point adjustment
  - Trailing aggressiveness
  - Daily loss limits
  
- **Production readiness checklist**
  - System setup
  - Testing procedures
  - Live trading prerequisites
  - Daily operations
  - Troubleshooting guide

**Time to read:** ~40-50 minutes
**Best for:** DevOps, system engineers, traders, operations

---

## 🎯 Reading Path by Role

### For Traders
1. **STRATEGY.md** (understand what you're trading)
2. **ARCHITECTURE.md** (how it works)
3. **DATA_FLOW.md** (what happens when)
4. **INTEGRATION.md** (how to run it)

**Estimated time:** 1.5-2 hours

---

### For Developers  
1. **ARCHITECTURE.md** (system design)
2. **COMPONENTS.md** (code modules)
3. **DATA_FLOW.md** (event flows)
4. **STRATEGY.md** (business logic)

**Estimated time:** 1.5-2 hours

---

### For DevOps/Operations
1. **INTEGRATION.md** (deployment & monitoring)
2. **ARCHITECTURE.md** (system overview)
3. **DATA_FLOW.md** (recovery scenarios)
4. **COMPONENTS.md** (modules reference)

**Estimated time:** 1-1.5 hours

---

### For Managers/Investors
1. **ARCHITECTURE.md** (system design)
2. **STRATEGY.md** (strategy overview)
3. **DATA_FLOW.md** (key concepts)
4. **INTEGRATION.md** (operations)

**Estimated time:** 45-60 minutes

---

## 🔗 Cross-References

### By Component

**Engine (core/engine.py)**
- COMPONENTS.md → Engine section
- DATA_FLOW.md → Tick processing & order execution
- ARCHITECTURE.md → Execution layer

**Fibonacci Strategy (strategy/fib_strategy.py)**
- STRATEGY.md → Fibonacci generation & entry rules
- COMPONENTS.md → Strategy module
- ARCHITECTURE.md → Strategy layer

**Recovery (core/recovery.py)**
- COMPONENTS.md → Recovery system section
- DATA_FLOW.md → Recovery flows
- ARCHITECTURE.md → Recovery system (institutional-grade)
- INTEGRATION.md → Recovery scenarios

**WebSocket (broker/data_ws.py, broker/order_ws.py)**
- COMPONENTS.md → WebSocket modules
- DATA_FLOW.md → Event flows
- INTEGRATION.md → Broker integration details

**State Management (core/state.py)**
- COMPONENTS.md → State management section
- DATA_FLOW.md → State consistency
- ARCHITECTURE.md → State machine

---

### By Concept

**Fibonacci Levels**
- STRATEGY.md → Fibonacci level generation
- DATA_FLOW.md → Level detection flow
- COMPONENTS.md → events.py level detection

**Entry Signals**
- STRATEGY.md → Entry rules (first trade & subsequent)
- DATA_FLOW.md → Entry order path
- COMPONENTS.md → engine.enter_trade()

**Stop Loss**
- STRATEGY.md → SL management
- DATA_FLOW.md → Exit order paths
- COMPONENTS.md → engine exit logic

**Trailing SL**
- STRATEGY.md → Trailing SL algorithm
- DATA_FLOW.md → Trailing SL update flow
- COMPONENTS.md → calculate_trailing_sl()

**Recovery**
- DATA_FLOW.md → Recovery flows
- COMPONENTS.md → recovery.py details
- INTEGRATION.md → Troubleshooting & recovery scenarios
- ARCHITECTURE.md → Recovery system design

**Errors & Debugging**
- INTEGRATION.md → Troubleshooting guide
- DATA_FLOW.md → Error handling flow
- COMPONENTS.md → Error scenarios

---

## 📊 Document Statistics

| Document | Pages | Time to Read | Primary Audience |
|----------|-------|--------------|------------------|
| ARCHITECTURE.md | 10 | 15-20 min | Architects |
| COMPONENTS.md | 15 | 25-30 min | Developers |
| DATA_FLOW.md | 18 | 30-40 min | Engineers |
| STRATEGY.md | 16 | 35-45 min | Traders |
| INTEGRATION.md | 20 | 40-50 min | DevOps/Ops |
| **Total** | **~79** | **2-3 hours** | Everyone |

---

## 🚀 Quick Start Paths

### Path 1: Understand Then Deploy (Recommended for New Users)
```
1. Read: STRATEGY.md (what we trade)
2. Read: ARCHITECTURE.md (how we trade it)
3. Skim: COMPONENTS.md (know what exists)
4. Follow: INTEGRATION.md (deploy it)
5. Reference: DATA_FLOW.md (when problems occur)
```
**Time:** ~2 hours

---

### Path 2: Deploy Then Learn (For Experienced Traders)
```
1. Follow: INTEGRATION.md (get running)
2. Monitor: logs/ (observe behavior)
3. Read: ARCHITECTURE.md (understand architecture)
4. Reference: DATA_FLOW.md (trace execution)
5. Deep Dive: STRATEGY.md (optimize)
```
**Time:** ~1.5 hours + operational experience

---

### Path 3: Implement Changes (For Developers)
```
1. Reference: COMPONENTS.md (find what to change)
2. Study: DATA_FLOW.md (understand flow)
3. Review: ARCHITECTURE.md (maintain design)
4. Implement: Make changes
5. Test: Verify with logs/DATA_FLOW patterns
```
**Time:** Varies by change

---

## 💡 Key Insights

### Philosophy
- **Broker = Truth:** Engine state is derived from broker, not authoritative
- **Event-Driven:** WebSocket callbacks trigger all logic, no polling
- **Recovery-Safe:** Reconnects and crashes handled deterministically

### Architecture
- **4 Layers:** Orchestration → Execution → Strategy → Broker
- **Pure Functions:** Strategy logic separated from state/execution
- **Fast:** O(1) level detection, <5ms tick processing

### Strategy
- **Fibonacci Levels:** Mathematically derived support/resistance
- **Fixed SL:** Risk is known and controlled
- **Trailing SL:** Profits locked in progressively
- **One Trade Per Side:** Prevents revenge trading

### Operations
- **No Database:** State from broker (simpler, more reliable)
- **Manual Auth:** OAuth2 flow (user responsible for security)
- **Graceful Degradation:** Errors don't crash system, recovery automatic
- **Audit Trail:** Comprehensive logging for debugging

---

## 📝 Documentation Standards

### Formatting
- **Bold** for emphasis (`**text**`)
- `Code blocks` for code samples
- Tables for comparisons
- ASCII diagrams for flows
- Numbered lists for sequences
- Bullet points for details

### Code References
- File paths: `core/engine.py` (relative to project root)
- Line numbers: `(Lines 46-300)` (actual code locations)
- Functions: `get_level_index()` (function names in code`)
- Classes: `TradeState` (class names in code)

### Time Estimates
- **Quick skim:** 5-10 minutes (overview only)
- **Read:** 15-30 minutes (full understanding)
- **Study:** 1+ hours (internalize details)

---

## 🔄 Maintenance & Updates

### When Documentation Needs Update
- Code changes (components modified)
- Parameter changes (trading_params.py)
- New features added
- Recovery patterns change
- Performance improvements

### How to Update
1. Identify affected documents (see cross-references)
2. Update code examples/references
3. Update diagrams/flows if needed
4. Update performance statistics
5. Note version/date at top of affected file

### Current Snapshot
- **Date:** May 10, 2026
- **Version:** 1.0 (Initial documentation)
- **Status:** Production-ready (pending testing)
- **Last Updated:** May 10, 2026

---

## ❓ Frequently Asked Questions About Docs

**Q: Where do I start?**
A: Read ARCHITECTURE.md first, then follow your role's reading path above.

**Q: How do I find information about X?**
A: Use cross-references section or search docs for keywords.

**Q: What if information is outdated?**
A: Check the date, and cross-reference with actual code in repository.

**Q: Can I modify strategies?**
A: Yes! See STRATEGY.md for all tunable parameters in config/trading_params.py

**Q: How do I troubleshoot?**
A: Use INTEGRATION.md troubleshooting guide + DATA_FLOW.md to trace execution.

**Q: Is this documentation complete?**
A: Yes, it covers all modules, flows, and operations comprehensively.

---

## 📞 Support

For issues or questions:
1. **Check documentation** (this folder)
2. **Search INTEGRATION.md troubleshooting**
3. **Review DATA_FLOW.md for your scenario**
4. **Check logs/** for error messages
5. **Reach out with documentation references**

---

## ✅ Completeness Checklist

Documentation includes:
- ✅ System architecture & philosophy
- ✅ All modules detailed (5+ modules)
- ✅ Data flows & event paths (10+ flows)
- ✅ Trading strategy & rules
- ✅ Deployment procedures
- ✅ Recovery scenarios (4+ scenarios)
- ✅ Configuration options
- ✅ Monitoring & observability
- ✅ Troubleshooting guide
- ✅ Performance analysis
- ✅ Cross-references
- ✅ Role-based reading paths

**Documentation Status:** COMPLETE (1.0)

---

## 🎓 Learning Outcomes

After reading this documentation, you should understand:

- **What:** A Fibonacci-level-based algorithmic trading system
- **Why:** Deterministic entry/exit, strict risk control, event-driven
- **How:** Event-driven architecture with broker-synced recovery
- **Where:** All modules, layers, and communication paths
- **When:** Trading hours (09:15 AM - 3:20 PM IST)
- **Who:** Individual traders, prop trading, education

---

## 📚 Related Files in Project

| File | Purpose | Location |
|------|---------|----------|
| `main.py` | Entry point & orchestrator | Root |
| `requirements.txt` | Dependencies | Root |
| `config/*.py` | Configuration | config/ |
| `core/*.py` | Core engine logic | core/ |
| `strategy/*.py` | Strategy rules | strategy/ |
| `broker/*.py` | Broker integration | broker/ |
| `utils/*.py` | Utilities | utils/ |
| `tests/*.py` | Unit tests | tests/ |
| `logs/*.log` | Runtime logs | logs/ |

---

## 🏁 Final Notes

- **No code modifications required to understand this documentation**
- **All components continue to work during documentation reading**
- **Use actual code and logs to verify understanding**
- **Documentation is reference material, not requirements**
- **Contribute updates as system evolves**

---

## Navigation

- **Next:** Choose your reading path from above
- **Questions:** See troubleshooting section in INTEGRATION.md
- **Changes:** Modify parameters in config/trading_params.py per STRATEGY.md

---

**Last Updated:** May 10, 2026  
**Version:** 1.0 (Initial Documentation)  
**Status:** ✅ Complete & Ready for Review


