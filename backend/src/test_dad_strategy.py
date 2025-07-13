"""
Unit tests for Dad's strategy implementation
"""

import pytest
from dad_strategy import DadStrategy, DadCountingSystem
from game import BlackjackGame, GameState, Action
from card import Card, Rank, Suit
from hand import Hand


class TestDadCountingSystem:
    """Test the card counting system"""
    
    def test_count_values(self):
        """Test that card values are counted correctly"""
        counter = DadCountingSystem()
        
        # Test individual card values
        test_cards = [
            (Card(Rank.TWO, Suit.HEARTS), 0),
            (Card(Rank.THREE, Suit.HEARTS), 3),
            (Card(Rank.FOUR, Suit.HEARTS), 4),
            (Card(Rank.FIVE, Suit.HEARTS), 5),
            (Card(Rank.SIX, Suit.HEARTS), 3),
            (Card(Rank.SEVEN, Suit.HEARTS), 0),
            (Card(Rank.EIGHT, Suit.HEARTS), -1),
            (Card(Rank.NINE, Suit.HEARTS), -2),
            (Card(Rank.TEN, Suit.HEARTS), -3),
            (Card(Rank.JACK, Suit.HEARTS), -3),
            (Card(Rank.QUEEN, Suit.HEARTS), -3),
            (Card(Rank.KING, Suit.HEARTS), -3),
            (Card(Rank.ACE, Suit.HEARTS), -3),
        ]
        
        for card, expected_value in test_cards:
            counter.reset()
            counter.count_card(card)
            assert counter.running_count == expected_value, f"Card {card} should have value {expected_value}"
    
    def test_ace_tracking(self):
        """Test ace side count"""
        counter = DadCountingSystem()
        
        # Add 4 aces
        for _ in range(4):
            counter.count_card(Card(Rank.ACE, Suit.HEARTS))
        
        assert counter.aces_seen == 4
        assert counter.cards_seen == 4
    
    def test_true_count_calculation(self):
        """Test true count with ace adjustment"""
        counter = DadCountingSystem()
        
        # Scenario: 6 decks, half dealt
        # Running count: +10
        # 8 aces seen (should be 12 for 3 decks)
        # Extra aces: 16 - 8 - 12 = -4
        # True count: (10 + (-4)) / 3 = 2
        
        counter.running_count = 10
        counter.cards_seen = 156  # Half of 6 decks
        counter.aces_seen = 8
        
        true_count = counter.get_true_count(total_decks=6)
        expected = (10 + (16 - 12)) / 3  # (running + extra_aces) / decks_remaining
        assert abs(true_count - expected) < 0.01


class TestDadStrategy:
    """Test Dad's complete strategy"""
    
    def test_betting_strategy(self):
        """Test betting increases with count"""
        strategy = DadStrategy(total_decks=6)
        
        # Test different true counts
        test_cases = [
            (0, 1),    # Below +5: min bet
            (4.9, 1),  # Just below +5: min bet
            (5, 2),    # At +5: 2 units
            (9.9, 2),  # Below +10: 2 units
            (10, 3),   # At +10: 3 units
            (14.9, 3), # Below +15: 3 units
            (15, 4),   # At +15: 4 units
            (95, 20),  # Very high count: capped at 20
        ]
        
        for count, expected_units in test_cases:
            strategy.counting_system.running_count = count * 3  # 3 decks remaining
            strategy.counting_system.cards_seen = 156  # Half shoe
            strategy.counting_system.aces_seen = 12  # Normal
            
            bet = strategy.get_bet_amount(min_bet=10)
            assert bet == expected_units * 10, f"Count {count} should bet {expected_units} units"
    
    def test_playing_deviations(self):
        """Test count-based playing deviations"""
        strategy = DadStrategy(total_decks=6)
        
        # Test 16 vs 10: Stand if count > 0
        hand_16 = Hand()
        hand_16.add_card(Card(Rank.TEN, Suit.HEARTS))
        hand_16.add_card(Card(Rank.SIX, Suit.HEARTS))
        dealer_10 = Card(Rank.TEN, Suit.SPADES)
        
        # Negative count: should hit
        strategy.counting_system.running_count = -3
        strategy.counting_system.cards_seen = 156
        action = strategy.get_action(hand_16, dealer_10)
        assert action == Action.HIT
        
        # Positive count: should stand
        strategy.counting_system.running_count = 3
        action = strategy.get_action(hand_16, dealer_10)
        assert action == Action.STAND
    
    def test_game_flow(self):
        """Test a complete hand flow"""
        game = BlackjackGame(num_decks=6)
        strategy = DadStrategy(total_decks=6)
        
        # Place bet
        game.place_bet(10)
        assert game.state == GameState.DEALING
        
        # Deal cards
        game.deal_initial_cards()
        assert game.state == GameState.PLAYER_TURN
        
        # Track dealt cards
        for card in game.player_hands[0].cards:
            strategy.observe_card(card)
        strategy.observe_card(game.dealer_hand.cards[0])
        
        # Play out the hand
        actions_taken = 0
        while game.state == GameState.PLAYER_TURN:
            hand = game.player_hands[game.current_hand_index]
            dealer_card = game.dealer_hand.cards[0]
            
            action = strategy.get_action(hand, dealer_card)
            result = game.player_action(action)
            assert result, f"Action {action} should be valid"
            
            actions_taken += 1
            assert actions_taken < 20, "Too many actions, possible infinite loop"
        
        # Dealer should play if needed
        if game.state == GameState.DEALER_TURN:
            game._play_dealer_hand()
        
        # Should be able to get results
        assert game.state == GameState.ROUND_OVER
        results = game.get_round_results()
        assert len(results) > 0, "Should have at least one result"
        
        # Result should have required fields
        result = results[0]
        assert 'result' in result
        assert 'payout' in result
        assert result['result'] in ['win', 'lose', 'push', 'blackjack win', 'bust']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])