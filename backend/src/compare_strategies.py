#!/usr/bin/env python3
"""
Compare original and optimized strategies side by side
"""

import json
from simulate_with_config import run_custom_simulation
from simulate_dad_strategy import print_results
import argparse


class Args:
    def __init__(self, config_file, hands=100000):
        self.config = config_file
        self.hands = hands
        self.decks = 6
        self.penetration = 72
        self.min_bet = 10
        self.bankroll = 50000  # Larger bankroll to avoid bust
        self.verbose = False
        self.output = None


def main():
    print("=== Strategy Comparison ===\n")
    
    # Load configurations
    with open('strategy_config.json', 'r') as f:
        original_config = json.load(f)
    
    with open('optimized_strategy_config.json', 'r') as f:
        optimized_config = json.load(f)
    
    # Run original strategy
    print("1. ORIGINAL STRATEGY (Dad's)")
    print("-" * 40)
    args = Args('strategy_config.json', hands=100000)
    original_results = run_custom_simulation(args, original_config)
    print_results(original_results, False)
    
    print("\n" + "="*60 + "\n")
    
    # Run optimized strategy
    print("2. OPTIMIZED STRATEGY")
    print("-" * 40)
    args = Args('optimized_strategy_config.json', hands=100000)
    optimized_results = run_custom_simulation(args, optimized_config)
    print_results(optimized_results, False)
    
    # Summary comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    print(f"\nROI:")
    print(f"  Original:  {original_results['roi']:.4%}")
    print(f"  Optimized: {optimized_results['roi']:.4%}")
    print(f"  Difference: {(optimized_results['roi'] - original_results['roi']):.4%}")
    
    print(f"\nWin Rate:")
    print(f"  Original:  {original_results['win_rate']:.2%}")
    print(f"  Optimized: {optimized_results['win_rate']:.2%}")
    
    print(f"\nAverage Bet:")
    print(f"  Original:  ${original_results['avg_bet']:.2f}")
    print(f"  Optimized: ${optimized_results['avg_bet']:.2f}")
    
    print(f"\nFinal Bankroll (from $50k):")
    print(f"  Original:  ${original_results['final_bankroll']:,.0f}")
    print(f"  Optimized: ${optimized_results['final_bankroll']:,.0f}")


if __name__ == "__main__":
    main()