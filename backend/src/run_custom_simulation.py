#!/usr/bin/env python3
"""
Run simulation with a custom strategy file

Usage:
    python run_custom_simulation.py <strategy_file> [options]
    
Example:
    python run_custom_simulation.py dad_strategy.py --hands 10000 --simulations 10
"""

import argparse
import sys
from pathlib import Path
import json

from simulator import BlackjackSimulator
from custom_strategy import CustomStrategy
from strategy import ComputerPlayer, StrategyType, BettingStrategy
from hand import Hand
from card import Card
from game import Action


class CustomStrategyPlayer(ComputerPlayer):
    """Computer player that uses a custom strategy"""
    
    def __init__(self, strategy_file: str, bankroll: int = 1000):
        self.custom_strategy = CustomStrategy(strategy_file)
        self.bankroll = bankroll
        self.betting_config = self.custom_strategy.betting_config
        self.base_bet = self.betting_config.get('base_bet', 25)
        
        # Track results for betting
        self.last_result = None
        self.win_streak = 0
        self.loss_streak = 0
    
    def get_action(self, player_hand: Hand, dealer_up_card: Card, 
                   valid_actions: list, true_count: float = 0) -> Action:
        """Use custom strategy for decisions"""
        can_double = Action.DOUBLE in valid_actions
        can_split = Action.SPLIT in valid_actions
        return self.custom_strategy.get_action(player_hand, dealer_up_card, can_double, can_split)
    
    def get_bet(self, true_count: float = 0) -> int:
        """Use custom betting strategy"""
        return self.custom_strategy.get_bet(
            self.base_bet, 
            self.last_result,
            self.win_streak,
            self.loss_streak,
            true_count,
            self.bankroll
        )
    
    def update_result(self, result: str, payout: int, bet: int):
        """Update player state after round"""
        self.last_result = result
        
        if result in ['win', 'blackjack']:
            self.win_streak += 1
            self.loss_streak = 0
            self.bankroll += payout - bet
        elif result == 'lose':
            self.win_streak = 0
            self.loss_streak += 1
            self.bankroll -= bet
        elif result == 'push':
            # No change to streaks
            pass


def main():
    parser = argparse.ArgumentParser(description='Run blackjack simulation with custom strategy')
    parser.add_argument('strategy_file', help='Path to custom strategy file')
    parser.add_argument('--hands', type=int, default=10000, help='Number of hands to simulate (default: 10000)')
    parser.add_argument('--simulations', type=int, default=10, help='Number of simulations to run (default: 10)')
    parser.add_argument('--bankroll', type=int, default=1000, help='Starting bankroll (default: 1000)')
    parser.add_argument('--decks', type=int, default=6, help='Number of decks (default: 6)')
    parser.add_argument('--output', help='Output file for detailed results (JSON)')
    parser.add_argument('--compare', action='store_true', help='Compare with basic strategy')
    
    args = parser.parse_args()
    
    # Check if strategy file exists
    if not Path(args.strategy_file).exists():
        print(f"Error: Strategy file '{args.strategy_file}' not found")
        sys.exit(1)
    
    print(f"Loading custom strategy from: {args.strategy_file}")
    print(f"Running {args.simulations} simulations of {args.hands} hands each")
    print(f"Starting bankroll: ${args.bankroll}")
    print("-" * 60)
    
    # Create simulator
    simulator = BlackjackSimulator(num_decks=args.decks)
    
    # Run simulations with custom strategy
    all_results = []
    total_profit = 0
    total_roi = 0
    bust_count = 0
    
    for i in range(args.simulations):
        # Create new player for each simulation
        player = CustomStrategyPlayer(args.strategy_file, args.bankroll)
        
        # Run simulation
        result = simulator.simulate_hands(player, args.hands, verbose=False)
        all_results.append(result)
        
        total_profit += result.profit_loss
        total_roi += result.roi
        if result.bust_out:
            bust_count += 1
        
        print(f"Simulation {i+1}: Final bankroll=${result.ending_bankroll}, "
              f"ROI={result.roi:.2f}%, Win rate={result.win_rate:.2f}%")
    
    # Calculate summary statistics
    avg_profit = total_profit / args.simulations
    avg_roi = total_roi / args.simulations
    bust_rate = (bust_count / args.simulations) * 100
    
    print("\n" + "=" * 60)
    print("CUSTOM STRATEGY RESULTS SUMMARY")
    print("=" * 60)
    print(f"Average profit/loss: ${avg_profit:.2f}")
    print(f"Average ROI: {avg_roi:.2f}%")
    print(f"Bust rate: {bust_rate:.1f}%")
    print(f"Average win rate: {sum(r.win_rate for r in all_results)/len(all_results):.2f}%")
    
    # Compare with basic strategy if requested
    if args.compare:
        print("\n" + "-" * 60)
        print("BASIC STRATEGY COMPARISON")
        print("-" * 60)
        
        basic_results = []
        basic_profit = 0
        basic_roi = 0
        basic_bust = 0
        
        for i in range(args.simulations):
            player = ComputerPlayer(
                playing_strategy=StrategyType.BASIC,
                betting_strategy=BettingStrategy.FLAT,
                base_bet=25,
                bankroll=args.bankroll
            )
            result = simulator.simulate_hands(player, args.hands, verbose=False)
            basic_results.append(result)
            basic_profit += result.profit_loss
            basic_roi += result.roi
            if result.bust_out:
                basic_bust += 1
        
        basic_avg_profit = basic_profit / args.simulations
        basic_avg_roi = basic_roi / args.simulations
        basic_bust_rate = (basic_bust / args.simulations) * 100
        
        print(f"Basic strategy avg profit: ${basic_avg_profit:.2f}")
        print(f"Basic strategy avg ROI: {basic_avg_roi:.2f}%")
        print(f"Basic strategy bust rate: {basic_bust_rate:.1f}%")
        
        print("\n" + "-" * 60)
        print("COMPARISON")
        print("-" * 60)
        print(f"Your strategy vs Basic strategy:")
        print(f"  Profit difference: ${avg_profit - basic_avg_profit:.2f}")
        print(f"  ROI difference: {avg_roi - basic_avg_roi:.2f}%")
        print(f"  Bust rate difference: {bust_rate - basic_bust_rate:.1f}%")
        
        if avg_roi > basic_avg_roi:
            print("\n✅ Your strategy outperforms basic strategy!")
        else:
            print("\n❌ Your strategy underperforms basic strategy")
    
    # Save detailed results if requested
    if args.output:
        output_data = {
            'strategy_file': args.strategy_file,
            'parameters': {
                'hands': args.hands,
                'simulations': args.simulations,
                'starting_bankroll': args.bankroll,
                'decks': args.decks
            },
            'summary': {
                'avg_profit': avg_profit,
                'avg_roi': avg_roi,
                'bust_rate': bust_rate
            },
            'simulations': [r.to_dict() for r in all_results]
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    main()