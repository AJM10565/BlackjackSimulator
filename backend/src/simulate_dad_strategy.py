#!/usr/bin/env python3
"""
CLI script to simulate Dad's blackjack strategy
"""

import argparse
import json
from typing import Dict, List
from dad_strategy import DadStrategy
from strategy import BasicStrategy
from game import BlackjackGame, GameState, Action
from card import Rank
import time


def run_simulation(args) -> Dict:
    """Run simulation with given parameters"""
    
    # Create Dad's strategy
    dad_strategy = DadStrategy(total_decks=args.decks)
    
    # Run simulation
    print(f"\nRunning {args.hands:,} hands simulation...")
    print(f"Decks: {args.decks}, Penetration: {args.penetration}%")
    print(f"Min bet: ${args.min_bet}, Bankroll: ${args.bankroll}")
    print(f"Using Dad's counting strategy\n")
    
    # Initialize game
    game = BlackjackGame(num_decks=args.decks, shuffle_threshold=args.penetration/100)
    
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
    
    # Reset strategy count for new shoe
    dad_strategy.reset_count()
    
    for hand_num in range(args.hands):
        # Check if player is bust
        if bankroll < args.min_bet:
            print(f"Bust out after {hand_num} hands!")
            break
            
        # Check for shuffle
        if game.deck.needs_shuffle():
            game.deck.shuffle()
            dad_strategy.reset_count()
            
        # Get bet amount
        bet_amount = dad_strategy.get_bet_amount(args.min_bet)
        bet_amount = min(bet_amount, bankroll)  # Can't bet more than bankroll
        
        # Track bet distribution
        bet_key = int(bet_amount / args.min_bet)
        stats['bet_distribution'][bet_key] = stats['bet_distribution'].get(bet_key, 0) + 1
        
        # Start new round
        game.player_bankroll = bankroll
        game.place_bet(bet_amount)
        game.deal_initial_cards()
        
        # Update count with dealt cards
        for card in game.player_hands[0].cards:
            dad_strategy.observe_card(card)
        dad_strategy.observe_card(game.dealer_hand.cards[0])  # Dealer up card
        
        # TODO: Add insurance when implemented in game
        # if game.dealer_hand.cards[0].rank == Rank.ACE:
        #     if dad_strategy.should_take_insurance(game.dealer_hand.cards[0]):
        #         game.place_insurance_bet()
        
        # Play the hand
        while game.state == GameState.PLAYER_TURN:
            current_hand = game.player_hands[game.current_hand_index]
            dealer_up_card = game.dealer_hand.cards[0]
            can_split = len(game.player_hands) == 1 and game.player_hands[0].can_split()
            
            action = dad_strategy.get_action(current_hand, dealer_up_card, can_split)
            
            # Execute action
            result = game.player_action(action)
            if not result:
                print(f"  Action {action} failed!")
                break
                
            # Track new cards if any were dealt
            if action in [Action.HIT, Action.DOUBLE]:
                # Check if we're still on a valid hand (might have moved to next hand or dealer turn)
                if game.state == GameState.PLAYER_TURN and game.current_hand_index < len(game.player_hands):
                    new_hand = game.player_hands[game.current_hand_index]
                    if len(new_hand.cards) > len(current_hand.cards):
                        dad_strategy.observe_card(new_hand.cards[-1])
        
        # Dealer plays
        if game.state == GameState.DEALER_TURN:
            dealer_start_cards = len(game.dealer_hand.cards)
            game._play_dealer_hand()
            # Count any new dealer cards
            for i in range(dealer_start_cards, len(game.dealer_hand.cards)):
                dad_strategy.observe_card(game.dealer_hand.cards[i])
        
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


def run_comparison(args) -> Dict:
    """Compare Dad's strategy with basic strategy"""
    
    print(f"\nComparing strategies over {args.hands:,} hands...")
    print(f"Decks: {args.decks}, Penetration: {args.penetration}%")
    print(f"Min bet: ${args.min_bet}, Bankroll: ${args.bankroll}\n")
    
    results = {'strategies': {}}
    
    # Run Dad's strategy
    print("Running Dad's Strategy...")
    dad_results = run_simulation(args)
    results['strategies']["Dad's Strategy"] = dad_results
    
    # Run basic strategy with flat betting
    print("\nRunning Basic Strategy...")
    # For basic strategy, we'll run a simplified version with flat betting
    basic_results = run_basic_strategy_simulation(args)
    results['strategies']["Basic Strategy (Flat Bet)"] = basic_results
    
    return results


def run_basic_strategy_simulation(args) -> Dict:
    """Run simulation with basic strategy and flat betting"""
    from strategy import BasicStrategy
    
    basic_strategy = BasicStrategy()
    
    # Initialize game
    game = BlackjackGame(num_decks=args.decks, shuffle_threshold=args.penetration/100)
    
    # Track statistics
    stats = {
        'total_hands': 0,
        'wins': 0,
        'losses': 0,
        'pushes': 0,
        'blackjacks': 0,
        'total_wagered': 0,
        'total_won_lost': 0,
        'bet_distribution': {1: 0}  # Always bet 1 unit
    }
    
    bankroll = args.bankroll
    max_bankroll = bankroll
    min_bankroll = bankroll
    
    start_time = time.time()
    
    for hand_num in range(args.hands):
        # Check if player is bust
        if bankroll < args.min_bet:
            print(f"Bust out after {hand_num} hands!")
            break
            
        # Flat bet
        bet_amount = args.min_bet
        stats['bet_distribution'][1] += 1
        
        # Start new round
        game.player_bankroll = bankroll
        game.place_bet(bet_amount)
        game.deal_initial_cards()
        
        # Play the hand
        while game.state == GameState.PLAYER_TURN:
            current_hand = game.player_hands[game.current_hand_index]
            dealer_up_card = game.dealer_hand.cards[0]
            can_split = len(game.player_hands) == 1 and game.player_hands[0].can_split()
            
            action = basic_strategy.get_action(current_hand, dealer_up_card, can_split)
            
            # Execute action
            if action == 'hit':
                game.player_action(Action.HIT)
            elif action == 'stand':
                game.player_action(Action.STAND)
            elif action == 'double':
                if game.player_hands[game.current_hand_index].can_double():
                    game.player_action(Action.DOUBLE)
                else:
                    game.player_action(Action.HIT)
            elif action == 'split':
                if can_split:
                    game.player_action(Action.SPLIT)
        
        # Dealer plays
        if game.state == GameState.DEALER_TURN:
            while game.dealer_plays():
                pass
        
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


def print_results(results: Dict, verbose: bool = False):
    """Print simulation results"""
    
    if 'strategies' in results:
        # Comparison results
        for name, stats in results['strategies'].items():
            print(f"\n{name}:")
            print(f"  Win Rate: {stats['win_rate']:.2%}")
            print(f"  Average Bet: ${stats['avg_bet']:.2f}")
            print(f"  Total Wagered: ${stats['total_wagered']:,.2f}")
            print(f"  Total Won/Lost: ${stats['total_won_lost']:+,.2f}")
            print(f"  ROI: {stats['roi']:.2%}")
            print(f"  Hands per Hour: {stats['hands_per_hour']:.0f}")
            if stats.get('final_bankroll'):
                print(f"  Final Bankroll: ${stats['final_bankroll']:,.2f}")
    else:
        # Single simulation results
        print("Results:")
        print(f"  Total Hands: {results['total_hands']:,}")
        print(f"  Wins: {results['wins']:,} ({results['win_rate']:.2%})")
        print(f"  Losses: {results['losses']:,} ({results['loss_rate']:.2%})")
        print(f"  Pushes: {results['pushes']:,} ({results['push_rate']:.2%})")
        print(f"  Blackjacks: {results['blackjacks']:,}")
        print(f"  Average Bet: ${results['avg_bet']:.2f}")
        print(f"  Total Wagered: ${results['total_wagered']:,.2f}")
        print(f"  Total Won/Lost: ${results['total_won_lost']:+,.2f}")
        print(f"  ROI: {results['roi']:.2%}")
        print(f"  Hands per Hour: {results['hands_per_hour']:.0f}")
        
        if results.get('final_bankroll') is not None:
            print(f"  Final Bankroll: ${results['final_bankroll']:,.2f}")
            
        if verbose and 'bet_distribution' in results:
            print("\n  Bet Distribution:")
            for bet, count in sorted(results['bet_distribution'].items()):
                print(f"    ${bet}: {count:,} hands")


def main():
    parser = argparse.ArgumentParser(
        description="Simulate Dad's Blackjack Strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick simulation with defaults
  python simulate_dad_strategy.py
  
  # Long simulation with custom parameters
  python simulate_dad_strategy.py --hands 1000000 --bankroll 10000 --min-bet 25
  
  # Compare with basic strategy
  python simulate_dad_strategy.py --compare --hands 100000
  
  # Save results to file
  python simulate_dad_strategy.py --hands 500000 --output results.json
        """
    )
    
    parser.add_argument('--hands', type=int, default=100000,
                        help='Number of hands to simulate (default: 100,000)')
    parser.add_argument('--decks', type=int, default=6,
                        help='Number of decks (default: 6)')
    parser.add_argument('--penetration', type=float, default=72,
                        help='Deck penetration percentage (default: 72)')
    parser.add_argument('--min-bet', type=float, default=10,
                        help='Minimum bet amount (default: $10)')
    parser.add_argument('--bankroll', type=float, default=1000,
                        help='Starting bankroll (default: $1,000)')
    parser.add_argument('--compare', action='store_true',
                        help='Compare with basic strategy')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed results')
    parser.add_argument('--output', '-o', type=str,
                        help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Run simulation
    if args.compare:
        results = run_comparison(args)
    else:
        results = run_simulation(args)
    
    # Print results
    print_results(results, args.verbose)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()