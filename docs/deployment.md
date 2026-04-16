# DESTROYER QUANTUM V34 Enhanced — Deployment Guide

## Prerequisites
- MetaTrader 4 (build 1380+)
- MetaEditor (included with MT4)
- EURUSD H4 chart (primary pair)
- XM or compatible broker account

## Step 1: Install the EA

1. Open MetaTrader 4
2. Go to **File → Open Data Folder**
3. Navigate to `MQL4/Experts/`
4. Copy `DESTROYER_QUANTUM_V34_ENHANCED.mq4` into this folder
5. In MetaTrader, open **Navigator** (Ctrl+N)
6. Right-click **Expert Advisors → Refresh**
7. The EA should appear as `DESTROYER_QUANTUM_V34_ENHANCED`

## Step 2: Compile

1. Open MetaEditor (F4 from MetaTrader)
2. Open `DESTROYER_QUANTUM_V34_ENHANCED.mq4`
3. Click **Compile** (F7)
4. Verify: **0 errors, 0 warnings**
5. If errors occur, check the specific line numbers in the error log

**Expected compile time:** 2-5 seconds (file is ~12K lines)
**Expected .ex4 size:** ~2-3 MB

## Step 3: Backtest Configuration

1. In MetaTrader, go to **View → Strategy Tester** (Ctrl+R)
2. Settings:
   - **Expert Advisor:** DESTROYER_QUANTUM_V34_ENHANCED
   - **Symbol:** EURUSD
   - **Period:** H4
   - **Model:** Control Points (NOT "Every tick" — too slow for 6 years)
   - **Use date:** ✓
   - **From:** 2020.01.01
   - **To:** 2026.01.01
   - **Deposit:** 10000
   - **Leverage:** 1:100
3. Click **Start**

**Expected test duration:** 5-15 minutes

## Step 4: Verify V34 Fixes

After backtest, check the **Journal** tab for these confirmations:

1. **V34 Changelog** — Look for "V34.0 ENHANCED" header in logs
2. **Circuit Breaker** — If DD ever exceeded threshold, look for "V34 CIRCUIT BREAKER ACTIVE"
3. **No Force-Enable** — No "MEAN REVERSION PERFORMANCE BOOST ACTIVATED" messages
4. **Filter Removals** — No "Reaper market conditions not met" from Warden

## Step 5: Compare Against V27 Baseline

| Metric | V27 Baseline | V34 Target | Your Result |
|--------|-------------|-----------|-------------|
| Total Trades | 167 (6yr) | 360-720 (6yr) | _____ |
| Trades/Year | 27.8 | 60-120 | _____ |
| Net Profit | $5,284 | $5,000+ | _____ |
| Profit Factor | 3.61 | 2.0+ | _____ |
| Max Drawdown | 9.12% | ≤10% | _____ |
| Win Rate | 87.4% | 75-85% | _____ |

## Step 6: Deploy to Demo

1. Open a demo account with your broker (same conditions as live)
2. Attach EA to EURUSD H4 chart
3. Set parameters to match your risk tolerance
4. Run for 2 weeks minimum before going live

## Step 7: Deploy to Live (XM MT4)

1. Open XM MT4 live account
2. Set risk to $5 max per trade (InpBase_Risk_Percent = 0.5)
3. Attach EA to EURUSD H4 chart
4. Monitor first 10 trades closely
5. Review weekly performance against targets

## Parameter Tuning Guide

### Conservative Settings (Lower Risk)
```
InpBase_Risk_Percent = 0.5
InpMaxOpenTrades = 5
InpDefensiveDD_Percent = 5.0
```

### Aggressive Settings (Higher Risk)
```
InpBase_Risk_Percent = 1.0
InpMaxOpenTrades = 10
InpDefensiveDD_Percent = 10.0
```

### Strategy-Specific Enable/Disable
```
InpMeanReversion_Enabled = true   // Mean reversion strategy
InpTitan_Enabled = true           // MTF momentum strategy
InpWarden_Enabled = true          // BB squeeze breakout
InpReaper_Enabled = true          // Grid/martingale
InpSiliconX_Enabled = true        // True North grid
InpChronos_Enabled = true         // M15 scalper
```

## Troubleshooting

### "Trade not allowed" Error
- Check that "Allow live trading" is enabled in EA properties
- Verify AutoTrading button is green (top toolbar)
- Check that your broker allows EA trading

### No Trades After 1 Week
- Check the **Experts** tab for error messages
- Verify spread is within InpMax_Spread_Pips (default 55)
- Check time filter (default 08:00-18:00 server time)
- Ensure InpEnableMarketFilters = true isn't blocking all setups

### Excessive Drawdown
- Reduce InpBase_Risk_Percent to 0.25
- Reduce InpMaxOpenTrades to 3
- Lower InpDefensiveDD_Percent to 5.0
- The V34 circuit breaker should prevent this, but always monitor

## Support
- GitHub: destroyertradingfx-uxdestroyer/vibe-trading
- Project: destroyer-v26-rebuild/
- Report issues in GitHub Issues
