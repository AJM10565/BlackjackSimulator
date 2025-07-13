from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from deck import Deck
from hand import Hand
from card import Card


class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"


class GameState(Enum):
    BETTING = "betting"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    ROUND_OVER = "round_over"


class BlackjackGame:
    def __init__(self, num_decks: int = 6, shuffle_threshold: float = 0.25):
        self.deck = Deck(num_decks, shuffle_threshold)
        self.dealer_hand = Hand()
        self.player_hands: List[Hand] = [Hand()]
        self.current_hand_index = 0
        self.state = GameState.BETTING
        self.player_bankroll = 1000  # Starting bankroll
        self.min_bet = 5
        self.max_bet = 500
        
    def place_bet(self, amount: int) -> bool:
        """Place initial bet for the round"""
        if self.state != GameState.BETTING:
            return False
        
        if amount < self.min_bet or amount > self.max_bet:
            return False
        
        if amount > self.player_bankroll:
            return False
        
        self.player_hands[0].bet = amount
        self.player_bankroll -= amount
        return True
    
    def deal_initial_cards(self):
        """Deal initial two cards to player and dealer"""
        if self.state != GameState.BETTING:
            return
        
        # Clear hands but preserve bet
        saved_bet = self.player_hands[0].bet
        self.dealer_hand.clear()
        for hand in self.player_hands:
            hand.clear()
        self.player_hands = [Hand()]
        self.player_hands[0].bet = saved_bet
        self.current_hand_index = 0
        
        # Deal cards (player, dealer, player, dealer)
        self.player_hands[0].add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hands[0].add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        
        # Check for blackjacks
        if self.player_hands[0].is_blackjack and self.dealer_hand.is_blackjack:
            self.state = GameState.ROUND_OVER
        elif self.player_hands[0].is_blackjack:
            self.state = GameState.DEALER_TURN
        elif self.dealer_hand.is_blackjack:
            self.state = GameState.ROUND_OVER
        else:
            self.state = GameState.PLAYER_TURN
    
    def get_valid_actions(self) -> List[Action]:
        """Get valid actions for current hand"""
        if self.state != GameState.PLAYER_TURN:
            return []
        
        hand = self.player_hands[self.current_hand_index]
        actions = [Action.HIT, Action.STAND]
        
        if hand.can_double() and hand.bet <= self.player_bankroll:
            actions.append(Action.DOUBLE)
        
        if hand.can_split() and hand.bet <= self.player_bankroll:
            actions.append(Action.SPLIT)
        
        # Surrender typically only allowed on first two cards of original hand
        if len(hand.cards) == 2 and not hand.is_split_hand:
            actions.append(Action.SURRENDER)
        
        return actions
    
    def player_action(self, action: Action) -> bool:
        """Process player action"""
        if self.state != GameState.PLAYER_TURN:
            return False
        
        if action not in self.get_valid_actions():
            return False
        
        hand = self.player_hands[self.current_hand_index]
        
        if action == Action.HIT:
            hand.add_card(self.deck.deal())
            if hand.is_bust:
                self._next_hand()
        
        elif action == Action.STAND:
            self._next_hand()
        
        elif action == Action.DOUBLE:
            self.player_bankroll -= hand.bet
            hand.bet *= 2
            hand.has_doubled = True
            hand.add_card(self.deck.deal())
            self._next_hand()
        
        elif action == Action.SPLIT:
            # Create new hand with one card from current hand
            new_hand = Hand()
            new_hand.is_split_hand = True
            new_hand.add_card(hand.cards.pop())
            new_hand.bet = hand.bet
            self.player_bankroll -= hand.bet
            
            # Add new hand to list
            self.player_hands.insert(self.current_hand_index + 1, new_hand)
            
            # Deal new cards to both hands
            hand.add_card(self.deck.deal())
            new_hand.add_card(self.deck.deal())
        
        elif action == Action.SURRENDER:
            # Return half the bet
            self.player_bankroll += hand.bet // 2
            hand.bet = 0
            self._next_hand()
        
        return True
    
    def _next_hand(self):
        """Move to next hand or dealer turn"""
        self.current_hand_index += 1
        if self.current_hand_index >= len(self.player_hands):
            self.state = GameState.DEALER_TURN
            self._play_dealer_hand()
    
    def _play_dealer_hand(self):
        """Play out dealer hand according to house rules"""
        if self.state != GameState.DEALER_TURN:
            return
        
        # Dealer doesn't play if all player hands are bust or surrendered
        all_bust = all(hand.is_bust or hand.bet == 0 for hand in self.player_hands)
        if all_bust:
            self.state = GameState.ROUND_OVER
            return
        
        # Dealer hits on 16 and below, stands on 17 and above
        # Most casinos hit on soft 17
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())
        
        self.state = GameState.ROUND_OVER
    
    def get_round_results(self) -> List[Dict[str, Any]]:
        """Calculate results for each player hand"""
        if self.state != GameState.ROUND_OVER:
            return []
        
        results = []
        dealer_value = self.dealer_hand.value
        dealer_blackjack = self.dealer_hand.is_blackjack
        
        for hand in self.player_hands:
            if hand.bet == 0:  # Surrendered
                results.append({
                    "result": "surrender",
                    "payout": 0,
                    "net": -hand.bet // 2
                })
                continue
            
            player_value = hand.value
            player_blackjack = hand.is_blackjack
            
            if hand.is_bust:
                result = "lose"
                payout = 0
            elif self.dealer_hand.is_bust:
                result = "win"
                payout = hand.bet * 2
            elif player_blackjack and not dealer_blackjack:
                result = "blackjack"
                payout = int(hand.bet * 2.5)  # 3:2 payout
            elif dealer_blackjack and not player_blackjack:
                result = "lose"
                payout = 0
            elif player_value > dealer_value:
                result = "win"
                payout = hand.bet * 2
            elif player_value < dealer_value:
                result = "lose"
                payout = 0
            else:
                result = "push"
                payout = hand.bet
            
            self.player_bankroll += payout
            
            results.append({
                "result": result,
                "payout": payout,
                "net": payout - hand.bet,
                "player_value": player_value,
                "dealer_value": dealer_value
            })
        
        return results
    
    def reset_round(self):
        """Reset for new round"""
        self.dealer_hand.clear()
        self.player_hands = [Hand()]
        self.current_hand_index = 0
        self.state = GameState.BETTING
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state for API/UI"""
        return {
            "state": self.state.value,
            "dealer_hand": self.dealer_hand.to_dict(),
            "player_hands": [hand.to_dict() for hand in self.player_hands],
            "current_hand_index": self.current_hand_index,
            "player_bankroll": self.player_bankroll,
            "valid_actions": [action.value for action in self.get_valid_actions()],
            "deck_info": {
                "remaining_cards": self.deck.remaining_cards,
                "penetration": self.deck.penetration,
                "running_count": self.deck.get_running_count(),
                "true_count": self.deck.get_true_count()
            }
        }