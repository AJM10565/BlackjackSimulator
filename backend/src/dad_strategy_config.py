"""
Configuration file for Dad's strategy parameters
All numeric values that can be optimized via grid search
"""

# Card Counting Values
CARD_VALUES = {
    'TWO': 0,
    'THREE': 3,
    'FOUR': 4,
    'FIVE': 5,
    'SIX': 3,
    'SEVEN': 0,
    'EIGHT': -1,
    'NINE': -2,
    'TEN': -3,
    'JACK': -3,
    'QUEEN': -3,
    'KING': -3,
    'ACE': -3
}

# Ace Side Count
ACE_ADJUSTMENT_PER_EXTRA = 4  # Points to add per extra ace

# Betting Thresholds and Multipliers
BETTING_CONFIG = {
    'count_threshold': 5,           # Start increasing bets at this true count
    'count_increment': 5,           # Increase bet for each increment of this
    'max_bet_units': 20,           # Maximum bet in units of minimum bet
}

# Playing Deviations (true count thresholds)
PLAY_DEVIATIONS = {
    # Format: (player_total, dealer_card, action_if_above_threshold, threshold)
    # Positive threshold means: take action if count >= threshold
    # Negative threshold means: take action if count <= threshold
    
    '16_vs_10_stand': {
        'player_total': 16,
        'dealer_card': 10,
        'action': 'STAND',
        'count_threshold': 0,      # Stand if count > 0
        'comparison': 'greater'    # greater, greater_equal, less, less_equal
    },
    
    '12_vs_3_stand': {
        'player_total': 12,
        'dealer_card': 3,
        'action': 'STAND', 
        'count_threshold': 5,
        'comparison': 'greater_equal'
    },
    
    '12_vs_2_stand': {
        'player_total': 12,
        'dealer_card': 2,
        'action': 'STAND',
        'count_threshold': 10,
        'comparison': 'greater_equal'
    },
    
    '13_vs_2_hit': {
        'player_total': 13,
        'dealer_card': 2,
        'action': 'HIT',
        'count_threshold': -5,
        'comparison': 'less'
    },
    
    '13_vs_3_hit': {
        'player_total': 13,
        'dealer_card': 3,
        'action': 'HIT',
        'count_threshold': -10,
        'comparison': 'less'
    },
    
    '11_vs_5_double': {
        'player_total': 11,
        'dealer_card': 5,
        'action': 'DOUBLE',
        'count_threshold': 10,
        'comparison': 'greater'
    },
    
    '11_vs_6_double': {
        'player_total': 11,
        'dealer_card': 6,
        'action': 'DOUBLE',
        'count_threshold': 10,
        'comparison': 'greater'
    },
    
    '88_vs_10_no_split': {
        'player_total': 16,  # Two 8s = 16
        'dealer_card': 10,
        'action': 'NO_SPLIT',  # Special case - don't split
        'count_threshold': 0,
        'comparison': 'greater'
    }
}

# Insurance Decision
INSURANCE_CONFIG = {
    'ace_excess_threshold': 1.0  # Take insurance if excess aces per deck >= this
}

# Deck Penetration
DECK_PENETRATION = 0.72  # 72% penetration