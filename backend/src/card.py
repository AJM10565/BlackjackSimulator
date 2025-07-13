from enum import Enum
from typing import List, Tuple


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (10, "J")
    QUEEN = (10, "Q")
    KING = (10, "K")
    ACE = (11, "A")  # Can be 1 or 11
    
    def __init__(self, points: int, symbol: str):
        self.points = points
        self.symbol = symbol


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self._count_value = self._calculate_count_value()
    
    def _calculate_count_value(self) -> int:
        """Hi-Lo card counting value"""
        if self.rank.points <= 6:
            return 1
        elif self.rank.points >= 10:
            return -1
        return 0
    
    @property
    def value(self) -> int:
        return self.rank.points
    
    @property
    def count_value(self) -> int:
        return self._count_value
    
    def __str__(self) -> str:
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank.symbol}{self.suit.value})"
    
    def to_dict(self) -> dict:
        return {
            "rank": self.rank.symbol,
            "suit": self.suit.value,
            "value": self.value
        }