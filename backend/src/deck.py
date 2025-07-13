import random
from typing import List, Optional
from card import Card, Suit, Rank


class Deck:
    def __init__(self, num_decks: int = 1, shuffle_threshold: float = 0.25):
        self.num_decks = num_decks
        self.shuffle_threshold = shuffle_threshold
        self.cards: List[Card] = []
        self.dealt_cards: List[Card] = []
        self._initialize_deck()
        self.shuffle()
    
    def _initialize_deck(self):
        """Create a fresh deck with specified number of standard decks"""
        self.cards = []
        self.dealt_cards = []
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(rank, suit))
    
    def shuffle(self):
        """Shuffle the deck and reset dealt cards"""
        self.cards.extend(self.dealt_cards)
        self.dealt_cards = []
        random.shuffle(self.cards)
    
    def deal(self) -> Optional[Card]:
        """Deal a single card from the deck"""
        if not self.cards:
            return None
        
        card = self.cards.pop()
        self.dealt_cards.append(card)
        
        # Check if we need to shuffle
        if self.needs_shuffle():
            self.shuffle()
        
        return card
    
    def needs_shuffle(self) -> bool:
        """Check if deck needs shuffling based on threshold"""
        total_cards = len(self.cards) + len(self.dealt_cards)
        remaining_ratio = len(self.cards) / total_cards if total_cards > 0 else 0
        return remaining_ratio <= self.shuffle_threshold
    
    @property
    def remaining_cards(self) -> int:
        return len(self.cards)
    
    @property
    def penetration(self) -> float:
        """Return the percentage of cards dealt"""
        total_cards = len(self.cards) + len(self.dealt_cards)
        if total_cards == 0:
            return 0
        return len(self.dealt_cards) / total_cards
    
    def get_running_count(self) -> int:
        """Get the running count for card counting"""
        return sum(card.count_value for card in self.dealt_cards)
    
    def get_true_count(self) -> float:
        """Get the true count (running count / decks remaining)"""
        running_count = self.get_running_count()
        decks_remaining = self.remaining_cards / 52
        if decks_remaining < 0.5:  # Avoid division by very small numbers
            decks_remaining = 0.5
        return running_count / decks_remaining