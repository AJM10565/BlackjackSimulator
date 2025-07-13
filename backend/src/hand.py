from typing import List, Tuple
from card import Card, Rank


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.is_split_hand = False
        self.has_doubled = False
        self.bet = 0
    
    def add_card(self, card: Card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_values(self) -> Tuple[int, int]:
        """
        Get both possible values for the hand (soft and hard).
        Returns (soft_value, hard_value)
        """
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == Rank.ACE:
                aces += 1
                total += 11
            else:
                total += card.value
        
        # Adjust for aces
        hard_total = total
        while hard_total > 21 and aces > 0:
            hard_total -= 10
            aces -= 1
        
        # Soft total is when we have at least one ace counted as 11
        soft_total = total if aces > 0 and total <= 21 else hard_total
        
        return (soft_total, hard_total)
    
    @property
    def value(self) -> int:
        """Get the best valid value for the hand"""
        soft, hard = self.get_values()
        if soft <= 21:
            return soft
        return hard
    
    @property
    def is_soft(self) -> bool:
        """Check if hand is soft (has ace counted as 11)"""
        soft, hard = self.get_values()
        return soft != hard and soft <= 21
    
    @property
    def is_bust(self) -> bool:
        """Check if hand is bust (over 21)"""
        return self.value > 21
    
    @property
    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack"""
        return len(self.cards) == 2 and self.value == 21 and not self.is_split_hand
    
    def can_split(self) -> bool:
        """Check if hand can be split"""
        if len(self.cards) != 2 or self.is_split_hand:
            return False
        # In most casinos, you can split any pair (including different 10-value cards)
        return self.cards[0].value == self.cards[1].value
    
    def can_double(self) -> bool:
        """Check if hand can be doubled down"""
        return len(self.cards) == 2 and not self.has_doubled
    
    def clear(self):
        """Clear the hand for a new round"""
        self.cards = []
        self.is_split_hand = False
        self.has_doubled = False
        self.bet = 0
    
    def to_dict(self) -> dict:
        """Convert hand to dictionary for JSON serialization"""
        soft, hard = self.get_values()
        return {
            "cards": [card.to_dict() for card in self.cards],
            "value": self.value,
            "soft_value": soft if soft <= 21 else None,
            "hard_value": hard,
            "is_soft": self.is_soft,
            "is_bust": self.is_bust,
            "is_blackjack": self.is_blackjack,
            "can_split": self.can_split(),
            "can_double": self.can_double(),
            "bet": self.bet
        }
    
    def __str__(self) -> str:
        cards_str = " ".join(str(card) for card in self.cards)
        return f"{cards_str} (value: {self.value})"