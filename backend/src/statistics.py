from typing import Dict, List, Tuple
from hand import Hand
from card import Card, Rank
from strategy import BasicStrategy


class BlackjackStatistics:
    """Calculate various probabilities and statistics for blackjack"""
    
    # Probability of getting each card value (2-11) in a standard deck
    # 16 tens (10, J, Q, K), 4 of each other rank
    CARD_PROBABILITIES = {
        2: 4/52, 3: 4/52, 4: 4/52, 5: 4/52, 6: 4/52,
        7: 4/52, 8: 4/52, 9: 4/52, 10: 16/52, 11: 4/52  # 11 is Ace
    }
    
    @classmethod
    def calculate_bust_probability(cls, hand: Hand, remaining_cards: int = 52) -> float:
        """Calculate the probability of busting if we take one more card"""
        current_value = hand.value
        
        if current_value >= 21:
            return 0.0  # Can't bust if already at 21 or bust
        
        # Count how many cards would cause a bust
        bust_threshold = 21 - current_value
        bust_probability = 0.0
        
        # For each possible card value
        for card_value in range(2, 12):  # 2 through 11 (Ace)
            if card_value > bust_threshold:
                # This card would cause a bust
                if card_value == 11 and current_value + 1 <= 21:
                    # Ace can be counted as 1, so it won't bust
                    continue
                bust_probability += cls.CARD_PROBABILITIES[card_value]
        
        return bust_probability
    
    @classmethod
    def calculate_dealer_bust_probability(cls, dealer_up_card: Card) -> float:
        """Calculate probability of dealer busting based on up card"""
        # These are approximate probabilities based on simulations
        # Dealer hits on 16 and below, stands on 17 and above
        dealer_bust_probabilities = {
            2: 0.353,   # Dealer showing 2
            3: 0.373,   # Dealer showing 3
            4: 0.402,   # Dealer showing 4
            5: 0.428,   # Dealer showing 5
            6: 0.424,   # Dealer showing 6
            7: 0.262,   # Dealer showing 7
            8: 0.236,   # Dealer showing 8
            9: 0.228,   # Dealer showing 9
            10: 0.214,  # Dealer showing 10
            11: 0.115   # Dealer showing Ace
        }
        
        up_value = dealer_up_card.value
        return dealer_bust_probabilities.get(up_value, 0.25)
    
    @classmethod
    def calculate_dealer_final_value_probabilities(cls, dealer_up_card: Card) -> Dict[int, float]:
        """Calculate probability distribution of dealer's final hand value"""
        # Simplified probabilities based on dealer up card
        # In reality, these depend on deck composition
        up_value = dealer_up_card.value
        
        # These are approximate probabilities
        if up_value == 11:  # Ace
            return {
                17: 0.130, 18: 0.130, 19: 0.130, 20: 0.130, 
                21: 0.365,  # Higher chance of 21 with Ace
                'bust': 0.115
            }
        elif up_value >= 7:  # 7, 8, 9, 10
            return {
                17: 0.370 if up_value == 7 else 0.130,
                18: 0.140 if up_value == 8 else 0.130,
                19: 0.120 if up_value == 9 else 0.120,
                20: 0.180 if up_value == 10 else 0.120,
                21: 0.075,
                'bust': cls.calculate_dealer_bust_probability(dealer_up_card)
            }
        else:  # 2-6 (dealer weak cards)
            base_prob = 0.155
            return {
                17: base_prob,
                18: base_prob,
                19: base_prob,
                20: base_prob,
                21: base_prob,
                'bust': cls.calculate_dealer_bust_probability(dealer_up_card)
            }
    
    @classmethod
    def calculate_win_probability(cls, player_hand: Hand, dealer_up_card: Card) -> Dict[str, float]:
        """Calculate win/lose/push probabilities for current hand"""
        player_value = player_hand.value
        
        if player_value > 21:
            return {'win': 0.0, 'lose': 1.0, 'push': 0.0}
        
        dealer_probs = cls.calculate_dealer_final_value_probabilities(dealer_up_card)
        
        win_prob = 0.0
        lose_prob = 0.0
        push_prob = 0.0
        
        for dealer_outcome, prob in dealer_probs.items():
            if dealer_outcome == 'bust':
                win_prob += prob
            elif isinstance(dealer_outcome, int):
                if player_value > dealer_outcome:
                    win_prob += prob
                elif player_value < dealer_outcome:
                    lose_prob += prob
                else:
                    push_prob += prob
        
        return {
            'win': win_prob,
            'lose': lose_prob,
            'push': push_prob
        }
    
    @classmethod
    def get_hand_strength(cls, hand: Hand) -> str:
        """Categorize hand strength"""
        value = hand.value
        
        if hand.is_blackjack:
            return "Blackjack!"
        elif value >= 20:
            return "Very Strong"
        elif value >= 18:
            return "Strong"
        elif value >= 15:
            return "Moderate"
        elif value >= 12:
            return "Weak"
        else:
            return "Very Weak"
    
    @classmethod
    def get_recommended_action_explanation(cls, player_hand: Hand, dealer_up_card: Card, 
                                         recommended_action: str) -> str:
        """Explain why a certain action is recommended"""
        player_value = player_hand.value
        dealer_value = dealer_up_card.value
        is_soft = player_hand.is_soft
        
        explanations = {
            'hit': {
                'weak_hand': f"With {player_value}, you need to improve against dealer's {dealer_value}",
                'soft_hand': f"Soft {player_value} can't bust, worth trying to improve",
                'dealer_strong': f"Dealer showing {dealer_value} is strong, need better than {player_value}"
            },
            'stand': {
                'bust_risk': f"Too risky to hit with {player_value}, let dealer risk busting",
                'dealer_weak': f"Dealer showing {dealer_value} has high bust chance ({cls.calculate_dealer_bust_probability(dealer_up_card):.1%})",
                'good_hand': f"{player_value} is strong enough against dealer's {dealer_value}"
            },
            'double': {
                'strong_position': f"Great opportunity! {player_value} vs dealer {dealer_value}",
                'dealer_weak': f"Double against weak dealer {dealer_value} (bust chance: {cls.calculate_dealer_bust_probability(dealer_up_card):.1%})",
                'eleven': "11 is the best doubling hand - any 10 gives you 21!"
            },
            'split': {
                'aces': "Always split Aces - two chances at 21!",
                'eights': "Always split 8s - turn weak 16 into two decent hands",
                'dealer_weak': f"Split against dealer's weak {dealer_value}",
                'pair': f"Splitting {player_hand.cards[0].value}s gives better expected value"
            },
            'surrender': {
                'bad_odds': f"16 vs dealer {dealer_value} has very poor odds, cut losses",
                'hard_15': f"Hard 15 vs dealer 10 is a losing position"
            }
        }
        
        # Select appropriate explanation
        if recommended_action == 'hit':
            if player_value <= 11:
                return explanations['hit']['weak_hand']
            elif is_soft:
                return explanations['hit']['soft_hand']
            else:
                return explanations['hit']['dealer_strong']
        
        elif recommended_action == 'stand':
            if player_value >= 17:
                return explanations['stand']['good_hand']
            elif dealer_value <= 6:
                return explanations['stand']['dealer_weak']
            else:
                return explanations['stand']['bust_risk']
        
        elif recommended_action == 'double':
            if player_value == 11:
                return explanations['double']['eleven']
            elif dealer_value <= 6:
                return explanations['double']['dealer_weak']
            else:
                return explanations['double']['strong_position']
        
        elif recommended_action == 'split':
            if player_hand.cards[0].rank == Rank.ACE:
                return explanations['split']['aces']
            elif player_hand.cards[0].value == 8:
                return explanations['split']['eights']
            elif dealer_value <= 6:
                return explanations['split']['dealer_weak']
            else:
                return explanations['split']['pair']
        
        elif recommended_action == 'surrender':
            return explanations['surrender']['bad_odds']
        
        return f"Basic strategy recommends: {recommended_action}"
    
    @classmethod
    def calculate_expected_value(cls, action: str, player_hand: Hand, 
                                dealer_up_card: Card, bet: int = 1) -> float:
        """Calculate expected value of an action (simplified)"""
        # This is a simplified EV calculation
        # Real EV would require full deck composition analysis
        
        win_probs = cls.calculate_win_probability(player_hand, dealer_up_card)
        
        if action == 'stand':
            ev = (win_probs['win'] * bet) - (win_probs['lose'] * bet)
        elif action == 'hit':
            # Simplified: assume hitting improves hand by average of 5
            # and has bust probability
            bust_prob = cls.calculate_bust_probability(player_hand)
            if bust_prob > 0.5:
                ev = -bet * bust_prob
            else:
                ev = (win_probs['win'] * bet * 0.9) - (win_probs['lose'] * bet * 1.1)
        elif action == 'double':
            # Double the bet, but only get one card
            ev = 2 * ((win_probs['win'] * bet) - (win_probs['lose'] * bet)) * 0.95
        elif action == 'split':
            # Assume each split hand has 75% of original EV
            ev = 1.5 * ((win_probs['win'] * bet) - (win_probs['lose'] * bet))
        elif action == 'surrender':
            ev = -0.5 * bet
        else:
            ev = 0
        
        return ev