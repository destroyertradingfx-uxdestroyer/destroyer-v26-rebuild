#!/usr/bin/env python3
"""Mean-Reversion Signal Generator — SSRN 2478345 Implementation

Implements statistical arbitrage framework from "Mean-Reversion and Optimization"
by Zura Kakushadze. Adapts pair trading and cross-sectional mean-reversion for forex.

Core Concepts (from the paper):
1. Pair Trading — Find correlated pairs, trade when spread diverges
2. Cross-Sectional Regression — Rank all pairs by deviation from mean
3. Z-Score Mean-Reversion — When |z| > 2, bet on reversion to mean
4. Optimization with Constraints — Maximize Sharpe within risk budget

Forex Adaptations:
- Pairs: XAUUSD/XAGUSD (gold-silver), EURUSD/GBPUSD (euro-cable), etc.
- Z-Score: Based on 20-period rolling mean and std of price ratio
- Signal: When |z| > 2 → mean-reversion entry, exit when |z| < 0.5
- Cross-sectional: Rank all 8 watchlist pairs by RSI deviation from 50

Usage:
    python3 mean_reversion.py --pair XAUUSD/XAGUSD --ratio 62.5 --mean 60.0 --std 1.5
    python3 mean_reversion.py --scan-all  # Scan all forex pairs for mean-reversion setups
    python3 mean_reversion.py --cross-section  # Rank all pairs by deviation
"""

import argparse
import json
import math

# Correlated forex pairs for pair trading
CORRELATED_PAIRS = {
    "XAUUSD_XAGUSD": {
        "name": "Gold/Silver Ratio",
        "correlation": 0.85,
        "typical_ratio": 80.0,  # XAUUSD / XAGUSD typically ~80
        "mean_reversion_speed": "Medium",
    },
    "EURUSD_GBPUSD": {
        "name": "Euro/Cable Spread",
        "correlation": 0.75,
        "typical_ratio": 0.88,  # EURUSD / GBPUSD typically ~0.88
        "mean_reversion_speed": "Fast",
    },
    "AUDUSD_NZDUSD": {
        "name": "Aussie/Kiwi Spread",
        "correlation": 0.80,
        "typical_ratio": 1.08,  # AUDUSD / NZDUSD typically ~1.08
        "mean_reversion_speed": "Fast",
    },
    "USDCAD_USDCHF": {
        "name": "Loonie/Swissie Spread",
        "correlation": 0.65,
        "typical_ratio": 1.30,
        "mean_reversion_speed": "Medium",
    },
    "USDJPY_EURJPY": {
        "name": "USD/EUR vs Yen",
        "correlation": 0.60,
        "typical_ratio": 0.68,
        "mean_reversion_speed": "Slow",
    },
}

# Z-Score thresholds (from paper: 2 std deviations = mean-reversion signal)
Z_THRESHOLDS = {
    "ENTRY": 2.0,     # |z| > 2.0 → enter mean-reversion trade
    "EXIT": 0.5,      # |z| < 0.5 → exit, mean restored
    "EXTREME": 3.0,   # |z| > 3.0 → extreme divergence, high conviction
}

def calculate_z_score(current, mean, std):
    """Calculate z-score for mean-reversion detection.
    
    z = (current - mean) / std
    
    Args:
        current: Current value (price, ratio, or indicator)
        mean: Rolling mean (20-period typical)
        std: Rolling standard deviation
    
    Returns:
        float: z-score
    """
    if std <= 0:
        return 0.0
    return (current - mean) / std

def analyze_pair(pair_name, current_ratio, mean_ratio, std_ratio):
    """Analyze a correlated pair for mean-reversion opportunity.
    
    Args:
        pair_name: Name of the pair (e.g., "XAUUSD_XAGUSD")
        current_ratio: Current ratio between the two instruments
        mean_ratio: Historical mean of the ratio
        std_ratio: Standard deviation of the ratio
    
    Returns:
        dict with analysis and trade signal
    """
    z = calculate_z_score(current_ratio, mean_ratio, std_ratio)
    abs_z = abs(z)
    
    # Determine signal
    if abs_z >= Z_THRESHOLDS["EXTREME"]:
        signal = "STRONG_REVERT"
        confidence = "HIGH"
        action = "ENTER — extreme divergence"
    elif abs_z >= Z_THRESHOLDS["ENTRY"]:
        signal = "REVERT"
        confidence = "MEDIUM"
        action = "ENTER — divergence detected"
    elif abs_z <= Z_THRESHOLDS["EXIT"]:
        signal = "MEAN_RESTORED"
        confidence = "N/A"
        action = "EXIT — mean restored"
    else:
        signal = "NO_SIGNAL"
        confidence = "N/A"
        action = "WAIT — within normal range"
    
    # Determine trade direction
    if z > 0:
        trade = f"SHORT {pair_name.split('_')[0]} / LONG {pair_name.split('_')[1]}"
    else:
        trade = f"LONG {pair_name.split('_')[0]} / SHORT {pair_name.split('_')[1]}"
    
    return {
        "pair": pair_name,
        "name": CORRELATED_PAIRS.get(pair_name, {}).get("name", pair_name),
        "current_ratio": round(current_ratio, 4),
        "mean_ratio": round(mean_ratio, 4),
        "std_ratio": round(std_ratio, 4),
        "z_score": round(z, 2),
        "abs_z": round(abs_z, 2),
        "signal": signal,
        "confidence": confidence,
        "action": action,
        "trade_direction": trade if signal in ["STRONG_REVERT", "REVERT"] else None,
    }

def cross_sectional_scan(pair_data):
    """Cross-sectional mean-reversion scan across all pairs.
    
    Based on paper's cross-sectional regression approach:
    1. Calculate RSI deviation from 50 for each pair
    2. Rank pairs by deviation
    3. Go long the most oversold, short the most overbought
    
    Args:
        pair_data: List of dicts with symbol, price, rsi
    
    Returns:
        dict with ranked pairs and mean-reversion signals
    """
    if not pair_data:
        return {"error": "No pair data provided"}
    
    # Calculate deviations
    for p in pair_data:
        p["rsi_deviation"] = p.get("rsi", 50) - 50
        p["abs_deviation"] = abs(p["rsi_deviation"])
    
    # Sort by absolute deviation
    ranked = sorted(pair_data, key=lambda x: x["abs_deviation"], reverse=True)
    
    # Identify extremes
    oversold = [p for p in ranked if p["rsi_deviation"] < -15]  # RSI < 35
    overbought = [p for p in ranked if p["rsi_deviation"] > 15]  # RSI > 65
    
    # Generate cross-sectional signal
    if oversold and overbought:
        # Classic pair: long most oversold, short most overbought
        long_pair = oversold[0]
        short_pair = overbought[0]
        
        signal = {
            "type": "CROSS_SECTIONAL_PAIR",
            "long": {
                "symbol": long_pair["symbol"],
                "rsi": long_pair["rsi"],
                "deviation": long_pair["rsi_deviation"],
            },
            "short": {
                "symbol": short_pair["symbol"],
                "rsi": short_pair["rsi"],
                "deviation": short_pair["rsi_deviation"],
            },
            "rationale": f"Long {long_pair['symbol']} (RSI {long_pair['rsi']}) vs Short {short_pair['symbol']} (RSI {short_pair['rsi']}) — mean-reversion play",
        }
    elif oversold:
        signal = {
            "type": "SINGLE_REVERSION",
            "long": {
                "symbol": oversold[0]["symbol"],
                "rsi": oversold[0]["rsi"],
                "deviation": oversold[0]["rsi_deviation"],
            },
            "rationale": f"Mean-reversion LONG on {oversold[0]['symbol']} — RSI {oversold[0]['rsi']} is extreme oversold",
        }
    elif overbought:
        signal = {
            "type": "SINGLE_REVERSION",
            "short": {
                "symbol": overbought[0]["symbol"],
                "rsi": overbought[0]["rsi"],
                "deviation": overbought[0]["rsi_deviation"],
            },
            "rationale": f"Mean-reversion SHORT on {overbought[0]['symbol']} — RSI {overbought[0]['rsi']} is extreme overbought",
        }
    else:
        signal = {
            "type": "NO_SIGNAL",
            "rationale": "No extreme deviations detected — market in equilibrium",
        }
    
    return {
        "ranked_pairs": [{"symbol": p["symbol"], "rsi": p["rsi"], "deviation": p["rsi_deviation"]} for p in ranked],
        "signal": signal,
    }

def main():
    parser = argparse.ArgumentParser(description="Mean-Reversion Signal Generator (SSRN 2478345)")
    parser.add_argument("--pair", help="Pair name (e.g., XAUUSD_XAGUSD)")
    parser.add_argument("--ratio", type=float, help="Current ratio")
    parser.add_argument("--mean", type=float, help="Historical mean ratio")
    parser.add_argument("--std", type=float, help="Standard deviation of ratio")
    parser.add_argument("--scan-all", action="store_true", help="Scan all correlated pairs")
    parser.add_argument("--cross-section", action="store_true", help="Cross-sectional RSI scan")
    
    args = parser.parse_args()
    
    if args.scan_all:
        print("=" * 80)
        print("MEAN-REVERSION PAIR SCAN — SSRN 2478345")
        print("=" * 80)
        
        # Example data — replace with live data in production
        examples = [
            ("XAUUSD_XAGUSD", 62.5, 60.0, 1.5),  # Gold/Silver ratio
            ("EURUSD_GBPUSD", 0.882, 0.880, 0.005),
            ("AUDUSD_NZDUSD", 1.09, 1.08, 0.01),
        ]
        
        results = []
        for pair, ratio, mean, std in examples:
            result = analyze_pair(pair, ratio, mean, std)
            results.append(result)
        
        print(f"{'Pair':<25} {'Ratio':>8} {'Mean':>8} {'Std':>8} {'Z':>6} {'Signal':>15}")
        print("-" * 80)
        for r in results:
            print(f"{r['pair']:<25} {r['current_ratio']:>8.4f} {r['mean_ratio']:>8.4f} {r['std_ratio']:>8.4f} {r['z_score']:>6.2f} {r['signal']:>15}")
        
        # Highlight opportunities
        opportunities = [r for r in results if r['signal'] in ['STRONG_REVERT', 'REVERT']]
        if opportunities:
            print(f"\n=== MEAN-REVERSION OPPORTUNITIES ===")
            for o in opportunities:
                print(f"  {o['pair']}: {o['action']}")
                print(f"    Trade: {o['trade_direction']}")
                print(f"    Z-Score: {o['z_score']} ({o['confidence']} confidence)")
    
    elif args.cross_section:
        # Cross-sectional scan with example RSI data
        print("=" * 80)
        print("CROSS-SECTIONAL MEAN-REVERSION SCAN")
        print("=" * 80)
        
        example_pairs = [
            {"symbol": "XAUUSD", "price": 4790, "rsi": 28},
            {"symbol": "XAGUSD", "price": 76.34, "rsi": 65},
            {"symbol": "EURUSD", "price": 1.1680, "rsi": 52},
            {"symbol": "GBPUSD", "price": 1.3350, "rsi": 73},
            {"symbol": "USDJPY", "price": 159.00, "rsi": 45},
            {"symbol": "AUDUSD", "price": 0.6580, "rsi": 32},
            {"symbol": "USDCAD", "price": 1.3850, "rsi": 38},
            {"symbol": "USDZAR", "price": 16.45, "rsi": 58},
        ]
        
        result = cross_sectional_scan(example_pairs)
        print(json.dumps(result, indent=2))
    
    elif args.pair and args.ratio and args.mean and args.std:
        result = analyze_pair(args.pair, args.ratio, args.mean, args.std)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python3 mean_reversion.py --pair XAUUSD_XAGUSD --ratio 62.5 --mean 60.0 --std 1.5")
        print("  python3 mean_reversion.py --scan-all")
        print("  python3 mean_reversion.py --cross-section")

if __name__ == "__main__":
    main()
