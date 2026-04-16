# DESTROYER QUANTUM V34 — Test Plan

## Overview

This test plan validates all 10 V34 fixes against the V27 baseline. Tests are structured in priority order: safety fixes first, then performance fixes, then architecture validation.

---

## Phase 1: Safety Tests (Circuit Breaker & Risk)

### Test 1.1: Circuit Breaker Blocks New Entries at 8% DD
**Priority:** CRITICAL
**Setup:**
1. Set InpDefensiveDD_Percent = 2.0 (artificially low for testing)
2. Set InpMaxOpenTrades = 2
3. Run backtest Jan 2020 – Jun 2020

**Expected:**
- When DD reaches 1.8% (90% of 2.0%), IsDrawdownSafe() returns false
- OnTick() returns immediately after management functions
- NO new trades are opened after circuit breaker triggers
- Existing trades still managed (trailing stops, basket closes)
- Comment shows "V34 CIRCUIT BREAKER ACTIVE"

**Fail Condition:** Any new OrderSend after circuit breaker trigger

### Test 1.2: Force-Enable Bug Eliminated
**Priority:** CRITICAL
**Setup:**
1. Set InpMeanReversion_Enabled = false
2. Set all other strategies to false
3. Run backtest

**Expected:**
- Zero Mean Reversion trades despite BoostMeanReversionPerformance() being called
- Log shows "Strategy DISABLED - returning"

**Fail Condition:** Any Mean Reversion trade when InpMeanReversion_Enabled = false

### Test 1.3: LEVIATHAN Override Eliminated
**Priority:** CRITICAL
**Setup:**
1. Set InpWarden_Enabled = false
2. Set InpTitan_Enabled = false
3. Run backtest

**Expected:**
- Zero Warden trades
- Zero Titan trades
- Other enabled strategies still trade normally

**Fail Condition:** Any Warden/Titan trade when disabled

### Test 1.4: Global Risk Check Enforced
**Priority:** HIGH
**Setup:**
1. Set InpMaxTotalRisk_Percent = 2.0 (very low)
2. Open several trades manually
3. Run backtest

**Expected:**
- Global_Risk_Check() blocks new trades when total risk exceeds 2%
- Lot sizes reduce automatically as risk approaches limit

**Fail Condition:** Total risk exceeds InpMaxTotalRisk_Percent

---

## Phase 2: Filter Architecture Tests

### Test 2.1: Warden No Longer Uses IsReaperConditionMet
**Priority:** HIGH
**Setup:**
1. Set only InpWarden_Enabled = true
2. Run backtest on EURUSD H4, Jan 2020 – Jan 2026
3. Check log for "Reaper market conditions not met" in Warden context

**Expected:**
- Zero "SKIPPED - Reaper market conditions" messages from Warden
- Warden uses only native squeeze + breakout + momentum + volume filters
- Trade count ≥ 15 in 6 years (vs 20 in V27)

**Fail Condition:** Any IsReaperConditionMet reference in Warden execution

### Test 2.2: Mean Reversion No Longer Double-Filters
**Priority:** HIGH
**Setup:**
1. Set InpMeanReversion_Enabled = true, all others false
2. Run backtest EURUSD H4, Jan 2020 – Jan 2026

**Expected:**
- MR uses only its native Hurst-based regime detection
- No "SKIPPED - Reaper market conditions" from MR
- Trade count ≥ 9 in 6 years (should be much higher, 30-60 target)

**Fail Condition:** IsReaperConditionMet still gates MR entries

### Test 2.3: Titan Trades More Than 5 in 6 Years
**Priority:** HIGH
**Setup:**
1. Set only InpTitan_Enabled = true
2. Run backtest EURUSD H4, Jan 2020 – Jan 2026

**Expected:**
- Trade count ≥ 15 in 6 years (vs 5 in V27)
- Filters are EMA trend + ATR vol + momentum (3 max)

**Fail Condition:** Fewer than 10 trades in 6 years

### Test 2.4: No Strategy Uses > 3 Sequential Filters
**Priority:** MEDIUM
**Setup:**
1. Code review of all strategy entry functions
2. Count sequential filter checks before OrderSend

**Expected:**
- Each strategy has ≤ 3 sequential `if(!condition) return;` before entry
- No filter overlaps (e.g., two separate BB checks)

**Fail Condition:** Any strategy with > 3 sequential filters

---

## Phase 3: Stop-Loss Tests

### Test 3.1: H4 Stop-Loss Uses Dynamic ATR
**Priority:** HIGH
**Setup:**
1. Run backtest EURUSD H4, Jan 2020 – Jan 2026
2. Log all stop-loss values

**Expected:**
- All stop-losses are ≥ 1.5 × ATR(14) on H4
- No hardcoded 15-pip or 100-pip stops
- Stop-loss adapts to volatility (wider in volatile periods)

**Fail Condition:** Any stop-loss < 1.0 × ATR(14)

### Test 3.2: H4 Loss Rate Improves
**Priority:** MEDIUM
**Setup:**
1. Compare V27 vs V34 backtest loss rates

**Expected:**
- V34 loss rate ≤ 65% (vs 78-81% in V27)
- Direction accuracy maintained or improved

**Fail Condition:** Loss rate > 75%

---

## Phase 4: Performance Tests

### Test 4.1: Total Trade Count ≥ 60/Year
**Priority:** HIGH
**Setup:**
1. Run backtest EURUSD H4, Jan 2020 – Jan 2026
2. Count total trades per year

**Expected:**
- Average ≥ 10 trades/year (conservative target, up from 27 in 6 years)
- Each strategy contributes trades

**Fail Condition:** Fewer than 5 trades/year average

### Test 4.2: Profit Factor ≥ 2.0
**Priority:** HIGH
**Setup:**
1. Run backtest EURUSD H4, Jan 2020 – Jan 2026

**Expected:**
- PF ≥ 2.0 (V27 was 3.61 with fewer trades)
- With more trades, PF may decrease slightly but net profit should increase

**Fail Condition:** PF < 1.5

### Test 4.3: Max Drawdown ≤ 10%
**Priority:** HIGH
**Setup:**
1. Run backtest with default parameters

**Expected:**
- Max DD ≤ 10% (V27 was 9.12%)
- Circuit breaker prevents DD spiraling

**Fail Condition:** DD > 12%

### Test 4.4: No Untracked/Pending Order Trades
**Priority:** CRITICAL
**Setup:**
1. Run backtest
2. Compare dashboard trade count vs tester trade count

**Expected:**
- Dashboard count = tester count (no invisible pending orders)
- All trades tracked in performance system

**Fail Condition:** > 10% discrepancy between dashboard and tester

---

## Phase 5: Multi-Pair Tests

### Test 5.1: GBPUSD H4
Run V34 Enhanced on GBPUSD H4, Jan 2020 – Jan 2026. Verify ≥ 0 trades, PF > 1.0.

### Test 5.2: USDJPY H4
Run V34 Enhanced on USDJPY H4, Jan 2020 – Jan 2026. Verify ≥ 0 trades, PF > 1.0.

### Test 5.3: XAUUSD H4
Run V34 Enhanced on XAUUSD H4, Jan 2020 – Jan 2026. Verify ≥ 0 trades, PF > 1.0.

---

## Test Execution Checklist

- [ ] Compile V34 Enhanced in MetaEditor (zero errors, zero warnings)
- [ ] Run Test 1.1 (Circuit breaker)
- [ ] Run Test 1.2 (Force-enable)
- [ ] Run Test 1.3 (LEVIATHAN)
- [ ] Run Test 2.1 (Warden filter)
- [ ] Run Test 2.2 (MR double-filter)
- [ ] Run Test 2.3 (Titan trade count)
- [ ] Run Test 3.1 (Stop-loss dynamic)
- [ ] Run Test 4.1 (Trade count)
- [ ] Run Test 4.2 (Profit factor)
- [ ] Run Test 4.3 (Max drawdown)
- [ ] Run Test 4.4 (No untracked trades)
- [ ] Run multi-pair tests (5.1-5.3)
- [ ] Compare V27 vs V34 summary table

---

## Pass/Fail Summary

| Test | Status | Notes |
|------|--------|-------|
| 1.1 Circuit Breaker | PENDING | |
| 1.2 Force-Enable | PENDING | |
| 1.3 LEVIATHAN | PENDING | |
| 1.4 Global Risk | PENDING | |
| 2.1 Warden Filter | PENDING | |
| 2.2 MR Double-Filter | PENDING | |
| 2.3 Titan Count | PENDING | |
| 2.4 Max 3 Filters | PENDING | |
| 3.1 Dynamic SL | PENDING | |
| 3.2 Loss Rate | PENDING | |
| 4.1 Trade Count | PENDING | |
| 4.2 Profit Factor | PENDING | |
| 4.3 Max DD | PENDING | |
| 4.4 No Untracked | PENDING | |
| 5.1 GBPUSD | PENDING | |
| 5.2 USDJPY | PENDING | |
| 5.3 XAUUSD | PENDING | |
