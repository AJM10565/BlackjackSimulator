"""
Dad's Custom Blackjack Strategy Implementation
"""

from typing import List, Tuple, Dict
from card import Card, Rank
from hand import Hand
from strategy import BasicStrategy
from game import Action


class DadCountingSystem:
    """Dad's custom card counting system"""
    
    def __init__(self):
        # Card counting values
        self.count_values = {
            Rank.TWO: 0,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 3,
            Rank.SEVEN: 0,
            Rank.EIGHT: -1,
            Rank.NINE: -2,
            Rank.TEN: -3,
            Rank.JACK: -3,
            Rank.QUEEN: -3,
            Rank.KING: -3,
            Rank.ACE: -3
        }
        
        self.running_count = 0
        self.aces_seen = 0
        self.cards_seen = 0
        
    def reset(self):
        """Reset counts for new shoe"""
        self.running_count = 0
        self.aces_seen = 0
        self.cards_seen = 0
        
    def count_card(self, card: Card):
        """Update count based on card"""
        self.running_count += self.count_values[card.rank]
        self.cards_seen += 1
        if card.rank == Rank.ACE:
            self.aces_seen += 1
            
    def get_true_count(self, total_decks: int = 6) -> float:
        """Calculate true count including ace adjustment"""
        cards_remaining = (total_decks * 52) - self.cards_seen
        if cards_remaining <= 0:
            return 0
            
        decks_remaining = cards_remaining / 52
        
        # Calculate ace adjustment
        total_aces = total_decks * 4
        aces_remaining = total_aces - self.aces_seen
        expected_aces = decks_remaining * 4
        extra_aces = aces_remaining - expected_aces
        
        # True count = (running count + ace adjustment) / decks remaining
        adjusted_count = self.running_count + extra_aces
        true_count = adjusted_count / decks_remaining if decks_remaining > 0 else 0
        
        return true_count
        
    def get_ace_excess_per_deck(self, total_decks: int = 6) -> float:
        """Calculate extra aces per remaining deck for insurance decision"""
        cards_remaining = (total_decks * 52) - self.cards_seen
        if cards_remaining <= 0:
            return 0
            
        decks_remaining = cards_remaining / 52
        total_aces = total_decks * 4
        aces_remaining = total_aces - self.aces_seen
        expected_aces = decks_remaining * 4
        extra_aces = aces_remaining - expected_aces
        
        return extra_aces / decks_remaining if decks_remaining > 0 else 0


class DadStrategy(BasicStrategy):
    """Dad's complete strategy with counting and deviations"""
    
    def __init__(self, total_decks: int = 6):
        super().__init__()
        self.counting_system = DadCountingSystem()
        self.total_decks = total_decks
        self.min_bet = 1  # Units
        self.max_bet = 20  # Units (20x minimum)
        
    def observe_card(self, card: Card):
        """Update count when card is seen"""
        self.counting_system.count_card(card)
        
    def reset_count(self):
        """Reset for new shoe"""
        self.counting_system.reset()
        
    def get_bet_amount(self, min_bet: float) -> float:
        """Calculate bet based on true count"""
        true_count = self.counting_system.get_true_count(self.total_decks)
        
        if true_count < 5:
            return min_bet
        
        # For each +5 increment, add one unit
        units = 1 + int(true_count / 5)
        
        # Cap at max bet
        units = min(units, self.max_bet)
        
        return min_bet * units
        
    def should_take_insurance(self, dealer_up_card: Card) -> bool:
        """Take insurance if ace excess >= 1 per deck"""
        if dealer_up_card.rank != Rank.ACE:
            return False
            
        ace_excess_per_deck = self.counting_system.get_ace_excess_per_deck(self.total_decks)
        return ace_excess_per_deck >= 1
        
    def get_action(self, player_hand: Hand, dealer_up_card: Card, can_split: bool = True) -> Action:
        """Get action with count-based deviations"""
        true_count = self.counting_system.get_true_count(self.total_decks)
        
        # Check for count-based deviations
        _, player_total = player_hand.get_values()  # Get hard total
        dealer_value = dealer_up_card.value
        
        # 16 vs 10: Stand if true count > 0
        if player_total == 16 and dealer_value == 10 and true_count > 0:
            return Action.STAND
            
        # 12 vs 3: Stand if true count >= +5
        if player_total == 12 and dealer_value == 3 and true_count >= 5:
            return Action.STAND
            
        # 12 vs 2: Stand if true count >= +10
        if player_total == 12 and dealer_value == 2 and true_count >= 10:
            return Action.STAND
            
        # 13 vs 2: Hit if true count < -5
        if player_total == 13 and dealer_value == 2 and true_count < -5:
            return Action.HIT
            
        # 13 vs 3: Hit if true count < -10
        if player_total == 13 and dealer_value == 3 and true_count < -10:
            return Action.HIT
            
        # 11 vs 5 or 6: Double if true count > +10
        if player_total == 11 and dealer_value in [5, 6] and true_count > 10:
            if len(player_hand.cards) == 2:  # Can only double on first two cards
                return Action.DOUBLE
                
        # 8,8 vs 10: Stand (don't split) if count is positive
        if (can_split and len(player_hand.cards) == 2 and 
            all(c.rank == Rank.EIGHT for c in player_hand.cards) and 
            dealer_value == 10 and true_count > 0):
            return Action.STAND
            
        # Otherwise use basic strategy
        return super().get_action(player_hand, dealer_up_card, can_split)