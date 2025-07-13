#!/usr/bin/env python3
"""
Grid search optimizer for blackjack strategy parameters
"""

import argparse
import itertools
import json
import time
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import dad_strategy_config as default_config
from configurable_strategy import ConfigurableStrategy
from game import BlackjackGame, GameState
from card import Rank


def run_simulation_with_config(config: Dict[str, Any], num_hands: int = 10000, 
                              num_decks: int = 6, bankroll: float = 10000,
                              min_bet: float = 10) -> Dict[str, float]:
    """Run simulation with specific configuration"""
    
    strategy = ConfigurableStrategy(config, total_decks=num_decks)
    game = BlackjackGame(num_decks=num_decks, shuffle_threshold=0.72)
    
    stats = {
        'hands': 0,
        'wins': 0,
        'losses': 0,
        'pushes': 0,
        'total_wagered': 0,
        'total_won_lost': 0
    }
    
    current_bankroll = bankroll
    strategy.reset_count()
    
    for hand_num in range(num_hands):
        if current_bankroll < min_bet:
            break
            
        # Check for shuffle
        if game.deck.needs_shuffle():
            game.deck.shuffle()
            strategy.reset_count()
            
        # Get bet
        bet_amount = strategy.get_bet_amount(min_bet)
        bet_amount = min(bet_amount, current_bankroll)
        
        # Play hand
        game.reset_round()
        game.player_bankroll = current_bankroll
        game.place_bet(bet_amount)
        game.deal_initial_cards()
        
        # Count cards
        for card in game.player_hands[0].cards:
            strategy.observe_card(card)
        strategy.observe_card(game.dealer_hand.cards[0])
        
        # Play out hand
        while game.state == GameState.PLAYER_TURN:
            hand = game.player_hands[game.current_hand_index]
            action = strategy.get_action(hand, game.dealer_hand.cards[0])
            if not game.player_action(action):
                break
                
        # Dealer plays
        if game.state == GameState.DEALER_TURN:
            dealer_start = len(game.dealer_hand.cards)
            game._play_dealer_hand()
            for i in range(dealer_start, len(game.dealer_hand.cards)):
                strategy.observe_card(game.dealer_hand.cards[i])
                
        # Results
        stats['hands'] += 1
        stats['total_wagered'] += bet_amount * len(game.player_hands)
        
        for result in game.get_round_results():
            if 'win' in result['result'] or result['result'] == 'blackjack':
                stats['wins'] += 1
            elif 'lose' in result['result']:
                stats['losses'] += 1
            else:
                stats['pushes'] += 1
            stats['total_won_lost'] += result['net']
            current_bankroll += result['net']
    
    # Calculate metrics
    roi = stats['total_won_lost'] / stats['total_wagered'] if stats['total_wagered'] > 0 else 0
    win_rate = stats['wins'] / stats['hands'] if stats['hands'] > 0 else 0
    
    return {
        'roi': roi,
        'win_rate': win_rate,
        'hands_played': stats['hands'],
        'final_bankroll': current_bankroll
    }


def generate_parameter_grid():
    """Generate parameter combinations to test"""
    
    # Define search ranges
    card_value_ranges = {
        # Keep some fixed (2, 7 always 0)
        'THREE': [2, 3, 4],
        'FOUR': [3, 4, 5],
        'FIVE': [4, 5, 6],
        'SIX': [2, 3, 4],
        'EIGHT': [-2, -1, 0],
        'NINE': [-3, -2, -1],
        # High cards fixed at -3
    }
    
    ace_adjustments = [3, 4, 5]
    
    betting_thresholds = [3, 4, 5, 6]
    betting_increments = [3, 5, 7]
    
    deviation_thresholds = {
        '16_vs_10': [-1, 0, 1],
        '12_vs_3': [3, 5, 7],
        '12_vs_2': [8, 10, 12],
        '13_vs_2': [-7, -5, -3],
        '13_vs_3': [-12, -10, -8],
        '11_vs_56': [8, 10, 12],
        '88_vs_10': [-1, 0, 1]
    }
    
    for params in itertools.product(
        *card_value_ranges.values(),
        ace_adjustments,
        betting_thresholds,
        betting_increments
    ):
        # Unpack parameters
        three_val, four_val, five_val, six_val, eight_val, nine_val = params[:6]
        ace_adj, bet_thresh, bet_incr = params[6:]
        
        # Build config
        config = {
            'counting': {
                'card_values': {
                    'TWO': 0,
                    'THREE': three_val,
                    'FOUR': four_val,
                    'FIVE': five_val,
                    'SIX': six_val,
                    'SEVEN': 0,
                    'EIGHT': eight_val,
                    'NINE': nine_val,
                    'TEN': -3,
                    'JACK': -3,
                    'QUEEN': -3,
                    'KING': -3,
                    'ACE': -3
                },
                'ace_adjustment': ace_adj
            },
            'betting': {
                'count_threshold': bet_thresh,
                'count_increment': bet_incr,
                'max_bet_units': 20
            },
            'deviations': default_config.PLAY_DEVIATIONS,  # Keep deviations fixed for now
            'insurance': default_config.INSURANCE_CONFIG
        }
        
        yield config


def optimize_strategy(num_hands: int = 10000, max_workers: int = 4, output_dir: str = 'optimization_results'):
    """Run grid search optimization"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f'grid_search_{timestamp}.csv')
    
    print(f"Starting grid search optimization...")
    print(f"Hands per simulation: {num_hands:,}")
    print(f"Workers: {max_workers}")
    print(f"Results will be saved to: {csv_filename}")
    
    best_config = None
    best_roi = float('-inf')
    results = []
    
    # Open CSV file for writing
    csv_file = open(csv_filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    
    # Write header
    csv_writer.writerow([
        'roi', 'win_rate', 'hands_played', 'final_bankroll',
        'card_2', 'card_3', 'card_4', 'card_5', 'card_6', 'card_7',
        'card_8', 'card_9', 'card_10', 'card_J', 'card_Q', 'card_K', 'card_A',
        'ace_adjustment', 'bet_threshold', 'bet_increment', 'max_bet_units'
    ])
    
    # Generate all configurations
    configs = list(generate_parameter_grid())
    total_configs = len(configs)
    print(f"Total configurations to test: {total_configs}")
    
    start_time = time.time()
    completed = 0
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_config = {
            executor.submit(run_simulation_with_config, config, num_hands): config
            for config in configs
        }
        
        # Process results as they complete
        for future in as_completed(future_to_config):
            config = future_to_config[future]
            try:
                result = future.result()
                completed += 1
                
                # Track result
                results.append({
                    'config': config,
                    'roi': result['roi'],
                    'win_rate': result['win_rate'],
                    'hands_played': result['hands_played'],
                    'final_bankroll': result['final_bankroll']
                })
                
                # Write to CSV
                card_vals = config['counting']['card_values']
                csv_writer.writerow([
                    result['roi'], result['win_rate'], result['hands_played'], result['final_bankroll'],
                    card_vals['TWO'], card_vals['THREE'], card_vals['FOUR'], card_vals['FIVE'],
                    card_vals['SIX'], card_vals['SEVEN'], card_vals['EIGHT'], card_vals['NINE'],
                    card_vals['TEN'], card_vals['JACK'], card_vals['QUEEN'], card_vals['KING'],
                    card_vals['ACE'], config['counting']['ace_adjustment'],
                    config['betting']['count_threshold'], config['betting']['count_increment'],
                    config['betting']['max_bet_units']
                ])
                csv_file.flush()  # Ensure data is written
                
                # Update best if needed
                if result['roi'] > best_roi:
                    best_roi = result['roi']
                    best_config = config
                    print(f"\nNew best! ROI: {best_roi:.4%}")
                    print(f"Card values: THREE={config['counting']['card_values']['THREE']}, "
                          f"FOUR={config['counting']['card_values']['FOUR']}, "
                          f"FIVE={config['counting']['card_values']['FIVE']}")
                    print(f"Betting: threshold={config['betting']['count_threshold']}, "
                          f"increment={config['betting']['count_increment']}")
                
                # Progress update
                if completed % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed
                    eta = (total_configs - completed) / rate
                    print(f"\rProgress: {completed}/{total_configs} "
                          f"({completed/total_configs:.1%}) "
                          f"ETA: {eta/60:.1f} min", end='', flush=True)
                    
            except Exception as e:
                print(f"\nError with config: {e}")
    
    # Close CSV file
    csv_file.close()
    
    print(f"\n\nOptimization complete!")
    print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
    print(f"Results saved to: {csv_filename}")
    
    # Sort results by ROI
    results.sort(key=lambda x: x['roi'], reverse=True)
    
    # Print top 5
    print("\nTop 5 configurations:")
    for i, result in enumerate(results[:5]):
        print(f"\n{i+1}. ROI: {result['roi']:.4%}, Win Rate: {result['win_rate']:.2%}")
        cfg = result['config']
        print(f"   Cards: 3={cfg['counting']['card_values']['THREE']}, "
              f"4={cfg['counting']['card_values']['FOUR']}, "
              f"5={cfg['counting']['card_values']['FIVE']}, "
              f"6={cfg['counting']['card_values']['SIX']}, "
              f"8={cfg['counting']['card_values']['EIGHT']}, "
              f"9={cfg['counting']['card_values']['NINE']}")
        print(f"   Ace adj: {cfg['counting']['ace_adjustment']}")
        print(f"   Betting: threshold={cfg['betting']['count_threshold']}, "
              f"increment={cfg['betting']['count_increment']}")
    
    return best_config, results, csv_filename


def main():
    parser = argparse.ArgumentParser(description='Optimize blackjack strategy parameters')
    parser.add_argument('--hands', type=int, default=10000,
                        help='Hands per simulation (default: 10,000)')
    parser.add_argument('--workers', type=int, default=4,
                        help='Number of parallel workers (default: 4)')
    parser.add_argument('--output', type=str,
                        help='Save results to JSON file')
    parser.add_argument('--quick', action='store_true',
                        help='Quick test with fewer parameters')
    
    args = parser.parse_args()
    
    if args.quick:
        # Quick test with limited search space
        print("Running quick test with limited parameter space...")
        args.hands = 1000
    
    best_config, results, csv_file = optimize_strategy(args.hands, args.workers)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'best_config': best_config,
                'best_roi': results[0]['roi'],
                'top_10': results[:10]
            }, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()