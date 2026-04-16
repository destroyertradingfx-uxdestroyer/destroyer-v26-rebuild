# DESTROYER QUANTUM — Full Changelog (V26 → V34)

## V26.0 — Math-First Signal Engine (Base)
- Original math-first signal generation system
- Strategies: Mean Reversion, Titan, Warden, Reaper, Silicon-X, Chronos
- V23 Empirical Probability Engine integrated
- Geneva Protocol V4.1 performance tracking
- 12,282 lines, 517KB monolithic file

## V27 — Undertrading Diagnosis (2026-04-13)
**Backtest Results (EURUSD H4, Jan 2020 – Jan 2026):**
- Total Trades: 167 in 6 years = 27.8/year = SEVERE UNDERTRADING
- Net Profit: $5,284.78 (52.85% over 6 years)
- Profit Factor: 3.61
- Max Drawdown: 9.12%
- Win Rate: 87.43%

**Strategy Performance:**
- Warden: 20 trades, $4,242.53 profit, PF 3.60 (BEST — 80% of profits)
- Reaper: 84 trades, $792.27 profit, PF 2227 (churning)
- Silicon-X: 52 trades, $230.67 profit, PF 1.62 (WORST active)
- Titan: 5 trades, $19.09 profit, PF 2.43 (barely participating)
- Mean Reversion: 9 trades, $0.22 profit, PF 1.05 (dead weight)
- Quantum Oscillator: 0 trades (OFFLINE)
- Market Microstructure: 0 trades (OFFLINE)

**Root Causes Identified:**
1. OnTick_Institutional() hard-returned on ApproveTrade() rejection
2. VAR limit 10% of portfolio per trade
3. Apex Sentinel ATR filter 1.3x blocked ~40% of setups
4. ADX filter at 30 blocked moderate trends
5. Max 5 concurrent trades capped upside
6. Mean Reversion still enabled despite claim of being disabled

## V28 — Undertrading Fix + Filter Relaxation (2026-04-13)
**Changes:**
1. DISABLED Mean Reversion (PF 1.05 = breakeven)
2. REMOVED OnTick_Institutional hard-return (was blocking all strategies)
3. VAR limit: 10% → 25% of portfolio per trade
4. Apex Sentinel ATR: 1.3x → 1.8x average
5. Apex Sentinel spike: 1.5x → 2.0x average
6. ADX filter: 30 → 40
7. Trend acceleration: 1.1x → 1.2x
8. Conviction threshold: 0.6 → 0.5
9. Max open trades: 5 → 8
10. Base risk: 0.5% → 0.75%
11. Warden risk multiplier: 0.5x → 1.5x
12. Reaper/SX risk multiplier: 3.0x → 1.5x

## V29-V33 — Incremental Fixes
- Additional filter tuning
- Performance monitoring improvements
- Strategy health checks refined
- Aegis trail management updates

## V34 Enhanced — Circuit Breaker + Filter Architecture Rebuild (2026-04-16)

### Critical Bug Fixes
1. **Circuit Breaker at TOP of OnTick()** — IsDrawdownSafe() now blocks ALL new entries before any strategy runs
2. **Force-Enable Eliminated** — BoostMeanReversionPerformance() no longer overrides user settings
3. **LEVIATHAN Restored** — All 3 commented-out enabled checks uncommented
4. **Warden Filter Fix** — Removed contradictory IsReaperConditionMet (mean-rev filter on breakout strategy)
5. **MR Double-Filter Fix** — Removed redundant IsReaperConditionMet pre-filter
6. **Titan Simplified** — Filter chain reduced from 7 to 3 sequential filters
7. **H4 Stop-Loss Dynamic** — Changed from 15-pip hardcoded to 1.5 ATR minimum

### Architecture Improvements
8. IsDrawdownSafe() — Centralized portfolio-level circuit breaker function
9. 4-tier risk hierarchy — Portfolio → Bar → Strategy → Order
10. Maximum 3 filters per strategy architecture rule

### Parameter Changes
- InpMeanReversion_Enabled: false → true (re-enabled after filter fix)
- V34 changelog header added (300+ lines of documentation)

### Expected Impact
- Trade volume: 27/year → 60-120/year
- Warden: 3.3/yr → 15-30/yr (removed contradictory filter)
- Titan: 0.8/yr → 20-50/yr (7 filters → 3)
- Mean Reversion: 1.5/yr → 30-60/yr (removed redundant filter)
- H4 loss rate: 78-81% → 55-65% (dynamic stops)
- Max drawdown: uncontrolled → 8% circuit breaker cap
