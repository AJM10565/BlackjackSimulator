"""
Configurable version of Dad's strategy for optimization
"""

from typing import Dict, Any
from card import Card, Rank
from hand import Hand
from strategy import BasicStrategy
from game import Action
import dad_strategy_config as default_config


class ConfigurableCountingSystem:
    """Configurable card counting system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {
                'card_values': default_config.CARD_VALUES,
                'ace_adjustment': default_config.ACE_ADJUSTMENT_PER_EXTRA
            }
        
        # Map string keys to Rank enum
        self.count_values = {}
        for rank_name, value in config['card_values'].items():
            rank = getattr(Rank, rank_name)
            self.count_values[rank] = value
        
        self.ace_adjustment = config['ace_adjustment']
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
        self.running_count += self.count_values.get(card.rank, 0)
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
        
        # Apply ace adjustment
        adjusted_count = self.running_count + (extra_aces * self.ace_adjustment)
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


class ConfigurableStrategy(BasicStrategy):
    """Configurable strategy for optimization"""
    
    def __init__(self, config: Dict[str, Any] = None, total_decks: int = 6):
        super().__init__()
        
        if config is None:
            # Use default config
            config = {
                'counting': {
                    'card_values': default_config.CARD_VALUES,
                    'ace_adjustment': default_config.ACE_ADJUSTMENT_PER_EXTRA
                },
                'betting': default_config.BETTING_CONFIG,
                'deviations': default_config.PLAY_DEVIATIONS,
                'insurance': default_config.INSURANCE_CONFIG
            }
        
        self.config = config
        self.counting_system = ConfigurableCountingSystem(config['counting'])
        self.total_decks = total_decks
        self.betting_config = config['betting']
        self.deviations = config['deviations']
        self.insurance_config = config['insurance']
        
    def observe_card(self, card: Card):
        """Update count when card is seen"""
        self.counting_system.count_card(card)
        
    def reset_count(self):
        """Reset for new shoe"""
        self.counting_system.reset()
        
    def get_bet_amount(self, min_bet: float) -> float:
        """Calculate bet based on true count"""
        true_count = self.counting_system.get_true_count(self.total_decks)
        
        threshold = self.betting_config['count_threshold']
        increment = self.betting_config['count_increment']
        max_units = self.betting_config['max_bet_units']
        
        if true_count < threshold:
            return min_bet
        
        # Calculate units based on count
        units = 1 + int((true_count - threshold) / increment)
        units = min(units, max_units)
        
        return min_bet * units
        
    def should_take_insurance(self, dealer_up_card: Card) -> bool:
        """Take insurance if ace excess >= threshold"""
        if dealer_up_card.rank != Rank.ACE:
            return False
            
        ace_excess_per_deck = self.counting_system.get_ace_excess_per_deck(self.total_decks)
        threshold = self.insurance_config['ace_excess_threshold']
        return ace_excess_per_deck >= threshold
        
    def get_action(self, player_hand: Hand, dealer_up_card: Card, can_split: bool = True) -> Action:
        """Get action with configurable deviations"""
        true_count = self.counting_system.get_true_count(self.total_decks)
        
        # Get basic values
        _, player_total = player_hand.get_values()  # Hard total
        dealer_value = dealer_up_card.value
        
        # Check for applicable deviations
        for dev_name, deviation in self.deviations.items():
            if (player_total == deviation['player_total'] and 
                dealer_value == deviation['dealer_card']):
                
                # Special case for 8,8 vs 10
                if 'no_split' in dev_name.lower() and can_split:
                    if len(player_hand.cards) == 2 and all(c.rank == Rank.EIGHT for c in player_hand.cards):
                        if self._check_count_condition(true_count, deviation):
                            return Action.STAND  # Don't split
                
                # Regular deviations
                elif self._check_count_condition(true_count, deviation):
                    action_str = deviation['action']
                    if action_str == 'HIT':
                        return Action.HIT
                    elif action_str == 'STAND':
                        return Action.STAND
                    elif action_str == 'DOUBLE':
                        if len(player_hand.cards) == 2:
                            return Action.DOUBLE
                    
        # Otherwise use basic strategy
        return super().get_action(player_hand, dealer_up_card, can_split)
    
    def _check_count_condition(self, true_count: float, deviation: Dict) -> bool:
        """Check if count meets deviation condition"""
        threshold = deviation['count_threshold']
        comparison = deviation['comparison']
        
        if comparison == 'greater':
            return true_count > threshold
        elif comparison == 'greater_equal':
            return true_count >= threshold
        elif comparison == 'less':
            return true_count < threshold
        elif comparison == 'less_equal':
            return true_count <= threshold
        else:
            return False