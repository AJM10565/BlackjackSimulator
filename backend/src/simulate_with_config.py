#!/usr/bin/env python3
"""
Run simulation with a custom strategy configuration file
"""

import argparse
import json
from configurable_strategy import ConfigurableStrategy
from simulate_dad_strategy import run_simulation, print_results
from game import BlackjackGame, GameState, Action
import time


def run_custom_simulation(args, config):
    """Run simulation with custom configuration"""
    
    strategy = ConfigurableStrategy(config, total_decks=args.decks)
    game = BlackjackGame(num_decks=args.decks, shuffle_threshold=args.penetration/100)
    
    print(f"\nRunning {args.hands:,} hands simulation with custom config...")
    print(f"Decks: {args.decks}, Penetration: {args.penetration}%")
    print(f"Min bet: ${args.min_bet}, Bankroll: ${args.bankroll}")
    print(f"Config file: {args.config}")
    
    # Show key parameters
    print("\nStrategy parameters:")
    print(f"  Card values: 3={config['counting']['card_values']['THREE']}, "
          f"4={config['counting']['card_values']['FOUR']}, "
          f"5={config['counting']['card_values']['FIVE']}, "
          f"6={config['counting']['card_values']['SIX']}")
    print(f"  Ace adjustment: {config['counting']['ace_adjustment']}")
    print(f"  Betting: threshold={config['betting']['count_threshold']}, "
          f"increment={config['betting']['count_increment']}")
    print()
    
    # Track statistics
    stats = {
        'total_hands': 0,
        'wins': 0,
        'losses': 0,
        'pushes': 0,
        'blackjacks': 0,
        'total_wagered': 0,
        'total_won_lost': 0,
        'bet_distribution': {}
    }
    
    bankroll = args.bankroll
    max_bankroll = bankroll
    min_bankroll = bankroll
    
    start_time = time.time()
    strategy.reset_count()
    
    for hand_num in range(args.hands):
        # Check if player is bust
        if bankroll < args.min_bet:
            print(f"Bust out after {hand_num} hands!")
            break
            
        # Check for shuffle
        if game.deck.needs_shuffle():
            game.deck.shuffle()
            strategy.reset_count()
            
        # Get bet amount
        bet_amount = strategy.get_bet_amount(args.min_bet)
        bet_amount = min(bet_amount, bankroll)
        
        # Track bet distribution
        bet_key = int(bet_amount / args.min_bet)
        stats['bet_distribution'][bet_key] = stats['bet_distribution'].get(bet_key, 0) + 1
        
        # Start new round
        game.player_bankroll = bankroll
        game.place_bet(bet_amount)
        game.deal_initial_cards()
        
        # Update count with dealt cards
        for card in game.player_hands[0].cards:
            strategy.observe_card(card)
        strategy.observe_card(game.dealer_hand.cards[0])
        
        # Play the hand
        while game.state == GameState.PLAYER_TURN:
            current_hand = game.player_hands[game.current_hand_index]
            dealer_up_card = game.dealer_hand.cards[0]
            can_split = len(game.player_hands) == 1 and game.player_hands[0].can_split()
            
            action = strategy.get_action(current_hand, dealer_up_card, can_split)
            result = game.player_action(action)
            if not result:
                break
                
            # Track new cards if any were dealt
            if action in [Action.HIT, Action.DOUBLE]:
                if game.state == GameState.PLAYER_TURN and game.current_hand_index < len(game.player_hands):
                    new_hand = game.player_hands[game.current_hand_index]
                    if len(new_hand.cards) > len(current_hand.cards):
                        strategy.observe_card(new_hand.cards[-1])
        
        # Dealer plays
        if game.state == GameState.DEALER_TURN:
            dealer_start_cards = len(game.dealer_hand.cards)
            game._play_dealer_hand()
            for i in range(dealer_start_cards, len(game.dealer_hand.cards)):
                strategy.observe_card(game.dealer_hand.cards[i])
        
        # Update stats
        stats['total_hands'] += 1
        stats['total_wagered'] += bet_amount * len(game.player_hands)
        
        # Calculate results
        for hand_result in game.get_round_results():
            result = hand_result['result']
            net = hand_result['net']
            
            if 'win' in result.lower() or result == 'blackjack':
                stats['wins'] += 1
                if result == 'blackjack':
                    stats['blackjacks'] += 1
            elif 'lose' in result.lower() or 'bust' in result.lower():
                stats['losses'] += 1
            else:
                stats['pushes'] += 1
                
            stats['total_won_lost'] += net
            bankroll += net
        
        # Update bankroll tracking
        max_bankroll = max(max_bankroll, bankroll)
        min_bankroll = min(min_bankroll, bankroll)
        
        # Reset for next hand
        game.reset_round()
        
        # Progress update
        if hand_num > 0 and hand_num % 10000 == 0:
            print(f"Progress: {hand_num:,} hands, bankroll: ${bankroll:,.0f}")
    
    # Calculate final stats
    elapsed_time = time.time() - start_time
    stats['final_bankroll'] = bankroll
    stats['starting_bankroll'] = args.bankroll
    stats['win_rate'] = stats['wins'] / stats['total_hands'] if stats['total_hands'] > 0 else 0
    stats['loss_rate'] = stats['losses'] / stats['total_hands'] if stats['total_hands'] > 0 else 0
    stats['push_rate'] = stats['pushes'] / stats['total_hands'] if stats['total_hands'] > 0 else 0
    stats['avg_bet'] = stats['total_wagered'] / stats['total_hands'] if stats['total_hands'] > 0 else 0
    stats['roi'] = stats['total_won_lost'] / stats['total_wagered'] if stats['total_wagered'] > 0 else 0
    stats['hands_per_hour'] = (stats['total_hands'] / elapsed_time * 3600) if elapsed_time > 0 else 0
    stats['max_bankroll'] = max_bankroll
    stats['min_bankroll'] = min_bankroll
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Simulate Blackjack with Custom Strategy Configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default config
  python simulate_with_config.py
  
  # Use custom config file
  python simulate_with_config.py --config my_strategy.json
  
  # Long simulation with custom config
  python simulate_with_config.py --config optimized.json --hands 1000000
        """
    )
    
    parser.add_argument('--config', type=str, default='strategy_config.json',
                        help='Strategy configuration JSON file')
    parser.add_argument('--hands', type=int, default=100000,
                        help='Number of hands to simulate')
    parser.add_argument('--decks', type=int, default=6,
                        help='Number of decks')
    parser.add_argument('--penetration', type=float, default=72,
                        help='Deck penetration percentage')
    parser.add_argument('--min-bet', type=float, default=10,
                        help='Minimum bet amount')
    parser.add_argument('--bankroll', type=float, default=10000,
                        help='Starting bankroll')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed results')
    parser.add_argument('--output', '-o', type=str,
                        help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Load config
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return
    
    # Import Action for the config
    from game import Action
    
    # Run simulation
    results = run_custom_simulation(args, config)
    
    # Print results
    print_results(results, args.verbose)
    
    # Save results if requested
    if args.output:
        output_data = {
            'config_file': args.config,
            'config': config,
            'parameters': vars(args),
            'results': results
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()