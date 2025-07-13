"""Simple test for Dad's strategy"""

from dad_strategy import DadStrategy, DadCountingSystem
from card import Card, Rank, Suit
from hand import Hand
from game import Action

# Test counting system
counter = DadCountingSystem()
print("=== Testing Card Counting ===")

test_cards = [
    (Card(Rank.THREE, Suit.HEARTS), 3),
    (Card(Rank.FOUR, Suit.HEARTS), 4), 
    (Card(Rank.FIVE, Suit.HEARTS), 5),
    (Card(Rank.ACE, Suit.HEARTS), -3),
]

for card, expected in test_cards:
    counter.reset()
    counter.count_card(card)
    print(f"{card}: count = {counter.running_count} (expected {expected})")

# Test true count with ace adjustment
print("\n=== Testing True Count ===")
counter.reset()
counter.running_count = 10
counter.cards_seen = 156  # 3 decks remaining
counter.aces_seen = 8    # 16 total - 8 seen = 8 remaining, expected 12
true_count = counter.get_true_count(6)
print(f"Running: {counter.running_count}, Cards seen: {counter.cards_seen}")
print(f"Aces seen: {counter.aces_seen}, True count: {true_count:.2f}")
print(f"Expected: {(10 + (8 - 12)) / 3:.2f}")

# Test betting
print("\n=== Testing Betting ===")
strategy = DadStrategy(6)
for count in [0, 4, 5, 9, 10, 15, 20, 100]:
    strategy.counting_system.running_count = count * 3
    strategy.counting_system.cards_seen = 156
    strategy.counting_system.aces_seen = 12
    bet = strategy.get_bet_amount(10)
    print(f"True count {count}: bet = ${bet}")

# Test playing decisions
print("\n=== Testing Play Decisions ===")
strategy = DadStrategy(6)

# Test 16 vs 10
hand = Hand()
hand.add_card(Card(Rank.TEN, Suit.HEARTS))
hand.add_card(Card(Rank.SIX, Suit.HEARTS))
dealer = Card(Rank.TEN, Suit.SPADES)

strategy.counting_system.running_count = -3
action = strategy.get_action(hand, dealer)
print(f"16 vs 10, count -1: {action} (should be HIT)")

strategy.counting_system.running_count = 3
action = strategy.get_action(hand, dealer)
print(f"16 vs 10, count +1: {action} (should be STAND)")