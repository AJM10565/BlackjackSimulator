from enum import Enum
from typing import Dict, Tuple, Optional
from hand import Hand
from card import Card, Rank
from game import Action


class StrategyType(Enum):
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    CARD_COUNTING = "card_counting"


class BettingStrategy(Enum):
    FLAT = "flat"
    MARTINGALE = "martingale"
    REVERSE_MARTINGALE = "reverse_martingale"
    KELLY_CRITERION = "kelly_criterion"
    ONE_THREE_TWO_SIX = "1-3-2-6"


class BasicStrategy:
    """Implements basic blackjack strategy based on mathematical probabilities"""
    
    # Hard totals (no ace or ace counted as 1)
    HARD_STRATEGY = {
        # Player total: {Dealer up card: Action}
        5: {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        6: {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        7: {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        8: {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        9: {2: 'H', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        10: {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'H', 'A': 'H'},
        11: {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'D', 'A': 'D'},
        12: {2: 'H', 3: 'H', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        13: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        14: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        15: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        16: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        17: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        18: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        19: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        20: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        21: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    }
    
    # Soft totals (ace counted as 11)
    SOFT_STRATEGY = {
        # A,2 (soft 13)
        13: {2: 'H', 3: 'H', 4: 'H', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        14: {2: 'H', 3: 'H', 4: 'H', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        15: {2: 'H', 3: 'H', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        16: {2: 'H', 3: 'H', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        17: {2: 'H', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
        18: {2: 'S', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'S', 8: 'S', 9: 'H', 10: 'H', 'A': 'H'},
        19: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        20: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
        21: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    }
    
    # Pair splitting strategy
    SPLIT_STRATEGY = {
        # Pair value: {Dealer up card: Split?}
        2: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'Y', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        3: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'Y', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        4: {2: 'N', 3: 'N', 4: 'N', 5: 'Y', 6: 'Y', 7: 'N', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        5: {2: 'N', 3: 'N', 4: 'N', 5: 'N', 6: 'N', 7: 'N', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        6: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'N', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        7: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'Y', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        8: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'Y', 8: 'Y', 9: 'Y', 10: 'Y', 'A': 'Y'},
        9: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'N', 8: 'Y', 9: 'Y', 10: 'N', 'A': 'N'},
        10: {2: 'N', 3: 'N', 4: 'N', 5: 'N', 6: 'N', 7: 'N', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},
        11: {2: 'Y', 3: 'Y', 4: 'Y', 5: 'Y', 6: 'Y', 7: 'Y', 8: 'Y', 9: 'Y', 10: 'Y', 'A': 'Y'},
    }
    
    @staticmethod
    def get_dealer_up_card_key(dealer_card: Card):
        """Convert dealer card to strategy table key"""
        if dealer_card.rank == Rank.ACE:
            return 'A'
        return dealer_card.value
    
    @classmethod
    def get_action(cls, player_hand: Hand, dealer_up_card: Card, can_double: bool = True, can_split: bool = True) -> Action:
        """Get recommended action based on basic strategy"""
        dealer_key = cls.get_dealer_up_card_key(dealer_up_card)
        
        # Check for splitting pairs first
        if can_split and player_hand.can_split() and len(player_hand.cards) == 2:
            pair_value = player_hand.cards[0].value
            if pair_value in cls.SPLIT_STRATEGY and dealer_key in cls.SPLIT_STRATEGY[pair_value]:
                if cls.SPLIT_STRATEGY[pair_value][dealer_key] == 'Y':
                    return Action.SPLIT
        
        # Check soft hands
        if player_hand.is_soft:
            soft_total = player_hand.value
            if soft_total in cls.SOFT_STRATEGY and dealer_key in cls.SOFT_STRATEGY[soft_total]:
                action_code = cls.SOFT_STRATEGY[soft_total][dealer_key]
            else:
                action_code = 'S'  # Default to stand
        else:
            # Hard hands
            hard_total = player_hand.value
            if hard_total in cls.HARD_STRATEGY and dealer_key in cls.HARD_STRATEGY[hard_total]:
                action_code = cls.HARD_STRATEGY[hard_total][dealer_key]
            else:
                action_code = 'S'  # Default to stand
        
        # Convert strategy code to Action
        if action_code == 'H':
            return Action.HIT
        elif action_code == 'S':
            return Action.STAND
        elif action_code == 'D':
            return Action.DOUBLE if can_double else Action.HIT
        else:
            return Action.STAND


class BettingSystem:
    """Manages betting strategies"""
    
    def __init__(self, strategy: BettingStrategy, base_bet: int = 10, bankroll: int = 1000):
        self.strategy = strategy
        self.base_bet = base_bet
        self.bankroll = bankroll
        self.current_bet = base_bet
        self.last_result = None
        self.win_streak = 0
        self.loss_streak = 0
        self.sequence_position = 0  # For 1-3-2-6 system
        
    def get_next_bet(self, true_count: float = 0) -> int:
        """Calculate next bet based on strategy"""
        if self.strategy == BettingStrategy.FLAT:
            return self.base_bet
            
        elif self.strategy == BettingStrategy.MARTINGALE:
            if self.last_result == 'lose':
                return min(self.current_bet * 2, self.bankroll)
            else:
                return self.base_bet
                
        elif self.strategy == BettingStrategy.REVERSE_MARTINGALE:
            if self.last_result == 'win':
                return min(self.current_bet * 2, self.bankroll)
            else:
                return self.base_bet
                
        elif self.strategy == BettingStrategy.KELLY_CRITERION:
            # Simplified Kelly: bet more with higher true count
            if true_count <= 0:
                return self.base_bet
            else:
                # Kelly fraction based on true count advantage
                edge = true_count * 0.005  # Roughly 0.5% edge per true count
                kelly_fraction = edge / 1  # Simplified (edge / odds)
                bet = int(self.bankroll * kelly_fraction)
                return max(self.base_bet, min(bet, self.bankroll // 4))
                
        elif self.strategy == BettingStrategy.ONE_THREE_TWO_SIX:
            sequence = [1, 3, 2, 6]
            if self.last_result == 'win':
                self.sequence_position = min(self.sequence_position + 1, 3)
            else:
                self.sequence_position = 0
            return self.base_bet * sequence[self.sequence_position]
            
        return self.base_bet
    
    def update_result(self, result: str, payout: int):
        """Update betting system with round result"""
        self.last_result = result
        
        if result == 'win' or result == 'blackjack':
            self.win_streak += 1
            self.loss_streak = 0
            self.bankroll += payout - self.current_bet
        elif result == 'lose':
            self.win_streak = 0
            self.loss_streak += 1
            self.bankroll -= self.current_bet
        elif result == 'push':
            # No change to streaks or bankroll
            pass
            
        # Update current bet for next round
        self.current_bet = self.get_next_bet()


class ComputerPlayer:
    """AI player that uses strategies to play blackjack"""
    
    def __init__(self, 
                 playing_strategy: StrategyType = StrategyType.BASIC,
                 betting_strategy: BettingStrategy = BettingStrategy.FLAT,
                 base_bet: int = 10,
                 bankroll: int = 1000):
        self.playing_strategy = playing_strategy
        self.betting_system = BettingSystem(betting_strategy, base_bet, bankroll)
        self.basic_strategy = BasicStrategy()
        
    def get_bet(self, true_count: float = 0) -> int:
        """Get bet amount for next round"""
        return self.betting_system.get_next_bet(true_count)
    
    def get_action(self, player_hand: Hand, dealer_up_card: Card, 
                   valid_actions: list, true_count: float = 0) -> Action:
        """Decide on action based on strategy"""
        
        if self.playing_strategy == StrategyType.BASIC:
            # Use basic strategy
            can_double = Action.DOUBLE in valid_actions
            can_split = Action.SPLIT in valid_actions
            return self.basic_strategy.get_action(player_hand, dealer_up_card, can_double, can_split)
            
        elif self.playing_strategy == StrategyType.CONSERVATIVE:
            # More conservative: stand on 12+ vs dealer 2-6
            if player_hand.value >= 12 and dealer_up_card.value <= 6:
                return Action.STAND
            return self.basic_strategy.get_action(player_hand, dealer_up_card)
            
        elif self.playing_strategy == StrategyType.AGGRESSIVE:
            # More aggressive: double more often
            if player_hand.value in [9, 10, 11] and Action.DOUBLE in valid_actions:
                return Action.DOUBLE
            return self.basic_strategy.get_action(player_hand, dealer_up_card)
            
        elif self.playing_strategy == StrategyType.CARD_COUNTING:
            # Adjust strategy based on count
            basic_action = self.basic_strategy.get_action(player_hand, dealer_up_card)
            
            # With high count, be more aggressive
            if true_count >= 3:
                if player_hand.value == 12 and dealer_up_card.value in [2, 3]:
                    return Action.STAND
                if player_hand.value == 16 and dealer_up_card.value == 10 and Action.SURRENDER in valid_actions:
                    return Action.STAND  # Don't surrender with high count
                    
            # With low count, be more conservative  
            elif true_count <= -2:
                if player_hand.value == 12 and dealer_up_card.value == 4:
                    return Action.HIT
                if player_hand.value == 13 and dealer_up_card.value == 2:
                    return Action.HIT
                    
            return basic_action
        
        # Default to basic strategy
        return self.basic_strategy.get_action(player_hand, dealer_up_card)