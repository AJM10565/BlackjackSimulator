"""Test the complete simulation flow"""

from game import BlackjackGame, GameState, Action
from dad_strategy import DadStrategy
from card import Card, Rank, Suit
import time

def test_single_hand():
    """Test a single hand flow"""
    print("=== Testing Single Hand ===")
    
    game = BlackjackGame(num_decks=6)
    strategy = DadStrategy(total_decks=6)
    
    # Place bet
    print(f"1. State: {game.state}")
    result = game.place_bet(10)
    print(f"2. Bet placed: {result}, State: {game.state}")
    
    # Deal
    game.deal_initial_cards()
    print(f"3. Cards dealt, State: {game.state}")
    
    # Check player hand
    player_hand = game.player_hands[0]
    print(f"4. Player: {[str(c) for c in player_hand.cards]}, value: {player_hand.value}")
    print(f"   Dealer: {game.dealer_hand.cards[0]}")
    print(f"   Player bet: ${player_hand.bet}")
    
    # Play
    actions = 0
    while game.state == GameState.PLAYER_TURN and actions < 10:
        action = strategy.get_action(player_hand, game.dealer_hand.cards[0])
        print(f"5.{actions+1} Action: {action}")
        result = game.player_action(action)
        print(f"     Result: {result}, State: {game.state}")
        actions += 1
    
    # Dealer
    if game.state == GameState.DEALER_TURN:
        print("6. Dealer plays...")
        game._play_dealer_hand()
        print(f"   Dealer final: {[str(c) for c in game.dealer_hand.cards]}, value: {game.dealer_hand.value}")
    
    # Results
    print(f"7. Final state: {game.state}")
    results = game.get_round_results()
    print(f"8. Results: {results}")
    
    return results

def test_multiple_hands():
    """Test multiple hands to check for issues"""
    print("\n=== Testing 20 Hands ===")
    
    game = BlackjackGame(num_decks=6)
    strategy = DadStrategy(total_decks=6)
    
    stats = {'wins': 0, 'losses': 0, 'pushes': 0, 'blackjacks': 0}
    bankroll = 1000
    
    for i in range(20):
        # Reset
        game.reset_round()
        game.player_bankroll = bankroll
        
        # Bet
        if not game.place_bet(10):
            print(f"Hand {i+1}: Failed to place bet")
            continue
            
        # Deal
        game.deal_initial_cards()
        
        # Track cards for counting
        for card in game.player_hands[0].cards:
            strategy.observe_card(card)
        strategy.observe_card(game.dealer_hand.cards[0])
        
        # Play
        while game.state == GameState.PLAYER_TURN:
            hand = game.player_hands[game.current_hand_index]
            action = strategy.get_action(hand, game.dealer_hand.cards[0])
            if not game.player_action(action):
                break
                
        # Dealer
        if game.state == GameState.DEALER_TURN:
            game._play_dealer_hand()
            
        # Results
        results = game.get_round_results()
        for result in results:
            if 'win' in result['result'] or result['result'] == 'blackjack':
                stats['wins'] += 1
                if result['result'] == 'blackjack':
                    stats['blackjacks'] += 1
            elif 'lose' in result['result']:
                stats['losses'] += 1
            else:
                stats['pushes'] += 1
            bankroll += result['net']
            
        print(f"Hand {i+1}: {result['result']}, bankroll: ${bankroll}")
    
    print(f"\nStats: {stats}")
    print(f"Win rate: {stats['wins']/20:.1%}")

if __name__ == "__main__":
    test_single_hand()
    test_multiple_hands()