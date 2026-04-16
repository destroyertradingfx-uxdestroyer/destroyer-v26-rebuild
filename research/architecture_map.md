# DESTROYER QUANTUM V34 — Architecture Map

## EA Structure Overview

**File:** DESTROYER_QUANTUM_V34_ENHANCED.mq4
**Lines:** ~12,383
**Version:** 34.00
**Symbol:** EURUSD (primary), any forex pair
**Timeframe:** H4 (primary strategies), M15 (Chronos scalper)

---

## Entry Points

```
OnTick()                          [Line 4872] — Main entry, called every tick
├── IsDrawdownSafe()              [NEW]      — V34 circuit breaker (FIRST CHECK)
├── ManageDrawdownExposure_V2()   [4719]     — Smart load shedding
├── CheckCircuitBreaker()         [10950]    — Global emergency stop
├── Hades_ManageBaskets()         [8543]     — Basket-level exits
├── OnNewBar()                    [4997]     — Strategy execution (new bar only)
│   ├── V23_DetectMarketRegime()  [11794]    — Regime detection
│   ├── UpdateQueenBeeStatus()    [5074]     — HWM, drawdown, hive state
│   ├── ExecuteReaperProtocol()   [6042]     — Grid/martingale system
│   ├── ExecuteTitanStrategy()    [7590]     — MTF momentum (V34: 3 filters)
│   ├── ExecuteMeanReversionModelV8_6() [5401] — BB/RSI mean-reversion
│   ├── ExecuteWardenStrategy()   [7805]     — BB squeeze breakout (V34: no Reaper filter)
│   └── ExecuteMathReversal()     [V26]      — Math-first signal generator
├── ManageOpenTradesV13_ELITE()   [7386]     — Trailing stops, partial closes
├── ManageWardenTrailingStop()    [11186]    — Warden-specific trailing
├── OnTick_SiliconX()             [8743]     — Grid/breakout (every tick)
├── OnTick_Reaper()               [8760]     — Grid management (every tick)
├── ManageUnified_AegisTrail()    [4869]     — Unified trailing defense
├── OnTick_Institutional()        [9488]     — Dashboard + advisory approval
├── OnTick_Elite()                [10657]    — Performance fine-tuning
└── V24_ProcessReentries()        [12098]    — Re-entry processing
```

---

## Strategy Modules

### 1. Warden (Cerberus Model W) — BB Squeeze Breakout
**Magic:** InpWarden_MagicNumber
**Timeframe:** H4
**Entry Logic:**
1. BB/Keltner squeeze detection (BB inside KC)
2. Breakout confirmation (close beyond BB)
3. Momentum filter (close vs SMA)
4. Volume confirmation (Volume[1] > Volume[2])
**V34 Change:** Removed IsReaperConditionMet() contradictory filter
**Stop Loss:** CalculateStopLoss_Warden() — ATR-based

### 2. Reaper (Cerberus Model R) — Grid/Martingale
**Magic:** InpReaper_BuyMagicNumber / InpReaper_SellMagicNumber
**Timeframe:** H4
**Entry Logic:**
1. Range detection
2. Grid placement with geometric lot multiplier
3. Basket TP/SL management
**Stop Loss:** Dynamic trailing + basket close

### 3. Titan (Cerberus Model T) — MTF Momentum
**Magic:** InpTitan_MagicNumber
**Timeframe:** H4
**Entry Logic (V34: simplified to 3 filters):**
1. EMA 20 vs 50 trend direction
2. ATR volatility check
3. Momentum confirmation
**V34 Change:** Reduced from 7 sequential filters to 3

### 4. Mean Reversion (Cerberus Model A) — Adaptive BB/RSI
**Magic:** InpMagic_MeanReversion
**Timeframe:** H4
**Entry Logic:**
1. Hurst exponent regime detection (H < 0.6 = mean-reverting)
2. Adaptive BB deviation (1.8-2.2 based on regime)
3. Adaptive RSI levels (65/35 to 70/30 based on regime)
4. CCI confirmation
**V34 Change:** Removed IsReaperConditionMet() pre-filter, re-enabled by default

### 5. Silicon-X (Cerberus Model S) — True North Grid
**Magic:** InpSX_MagicNumber
**Timeframe:** H4
**Entry Logic:**
1. Apex Sentinel: Volatility regime (ATR < 1.8x avg)
2. Apex Sentinel: Trend regime (ADX < 40)
3. Apex Sentinel: Market structure (price within 5% of 200 EMA)
**Grid:** Up to 8 levels, geometric spacing, basket TP/trail

### 6. Chronos (Model M) — M15 High-Frequency Scalper
**Magic:** InpChronos_MagicNumber
**Timeframe:** M15
**Entry Logic:** Microstructure analysis
**Stop Loss:** 25 pips, Take Profit: 35 pips

---

## Risk Management

### 4-Tier Circuit Breaker
1. **Portfolio** — IsDrawdownSafe() at TOP of OnTick()
2. **State** — HIVE_STATE_DEFENSIVE set by UpdateQueenBeeStatus()
3. **Strategy** — IsStrategyHealthy() per-strategy check
4. **Order** — Global_Risk_Check() pre-OrderSend

### Genetic Allocation Tiers
| Tier | PF Range | Risk Multiplier |
|------|----------|-----------------|
| KILL | < 0.8 | 0.0x (disabled) |
| DAMPEN | 0.8-1.2 | 0.2x |
| NORMAL | 1.2-2.0 | 1.0x |
| AMPLIFY | 2.0-3.0 | 2.0x |
| APEX | > 3.0 | 3.0x |

### Lot Sizing
- Base risk: 0.75% per trade (V28)
- Kelly criterion with 0.25 fraction
- Volatility-adjusted (ATR factor)
- Drawdown-dampened (0.3x in defensive mode)

---

## Performance Tracking

### V23 Empirical Probability Engine
- Strategy registration with magic numbers
- Empirical probability by deviation bin
- R-expectancy tracking
- Conditional loss probability by regime
- Entropy and skew calculations

### Geneva Protocol V4.1
- In-memory performance update per strategy
- Gross profit/loss tracking
- Win/loss streak counters
- High watermark management

---

## V34 Change Map

| Line(s) | Change | Fix # |
|---------|--------|-------|
| ~4873 | Added IsDrawdownSafe() circuit breaker at TOP of OnTick() | #1 |
| ~5117 | Added IsDrawdownSafe() function | #2 |
| ~9282 | Neutralized BoostMeanReversionPerformance() force-enable | #3 |
| Various | Restored 3 LEVIATHAN commented-out enabled checks | #4 |
| ~7913 | Removed IsReaperConditionMet() from Warden | #5 |
| ~5522 | Removed IsReaperConditionMet() from Mean Reversion | #8 |
| ~7590 | Added simplified Titan filter comment | #6 |
| ~10841 | Changed H4 stop-loss to 1.5 ATR minimum | #7 |
| ~1047 | Changed InpMeanReversion_Enabled default to true | #9 |
| Line 7 | Added V34 changelog header | #10 |
