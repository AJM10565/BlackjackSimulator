"""Debug game flow to understand the issue"""

from game import BlackjackGame, GameState
from dad_strategy import DadStrategy

# Create game and strategy
game = BlackjackGame(num_decks=6)
strategy = DadStrategy(total_decks=6)

print("=== Testing Game Flow ===")

# Place bet
print(f"1. Initial state: {game.state}")
game.place_bet(10)
print(f"2. After bet: {game.state}")

# Deal cards
game.deal_initial_cards()
print(f"3. After deal: {game.state}")
print(f"   Player hand: {[str(c) for c in game.player_hands[0].cards]}")
print(f"   Dealer showing: {game.dealer_hand.cards[0]}")

# Play one action
if game.state == GameState.PLAYER_TURN:
    hand = game.player_hands[0]
    action = strategy.get_action(hand, game.dealer_hand.cards[0])
    print(f"4. Strategy says: {action}")
    result = game.player_action(action)
    print(f"5. Action result: {result}, new state: {game.state}")

# Check if we need dealer play
if game.state == GameState.DEALER_TURN:
    print("6. Dealer's turn")
    game._play_dealer_hand()
    print(f"7. After dealer: {game.state}")

# Get results
print(f"8. Final state: {game.state}")
results = game.get_round_results()
print(f"9. Results: {results}")

# Test a few more hands
print("\n=== Testing Multiple Hands ===")
for i in range(5):
    game.reset_round()
    game.place_bet(10)
    game.deal_initial_cards()
    
    # Simple play - just stand
    while game.state == GameState.PLAYER_TURN:
        game.player_action(Action.STAND)
    
    if game.state == GameState.DEALER_TURN:
        game._play_dealer_hand()
    
    results = game.get_round_results()
    if results:
        print(f"Hand {i+1}: {results[0]['result']}")
    else:
        print(f"Hand {i+1}: No results! State: {game.state}")