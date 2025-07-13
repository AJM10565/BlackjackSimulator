"""
CUSTOM STRATEGY TEMPLATE
Fill in your strategy decisions below. 
Save this file as 'dad_strategy.py' and we'll run simulations with it.
"""

# PLAYING STRATEGY
# For each combination, specify: 'H' (Hit), 'S' (Stand), 'D' (Double), 'P' (Split), 'R' (Surrender)

# HARD TOTALS (no ace or ace counted as 1)
HARD_STRATEGY = {
    # Player total: {Dealer up card: Action}
    # Example: 16: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},

    5: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    6: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    7: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    8: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    9: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    10: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    11: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    12: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    13: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    14: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    15: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    16: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    17: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    18: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    19: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    20: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},
    21: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
}

# SOFT TOTALS (ace counted as 11)
SOFT_STRATEGY = {
    # Soft total: {Dealer up card: Action}
    13: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,2
    14: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,3
    15: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,4
    16: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,5
    17: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,6
    18: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,7
    19: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,8
    20: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,9
    21: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},  # Blackjack
}

# PAIR SPLITTING
SPLIT_STRATEGY = {
    # Pair value: {Dealer up card: 'Y' or 'N'}
    2: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 2,2
    3: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 3,3
    4: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 4,4
    5: {2: 'N', 3: 'N', 4: 'N', 5: 'N', 6: 'N', 7: 'N', 8: 'N', 9: 'N', 10: 'N', 'A': 'N'},  # 5,5 (never split)
    6: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 6,6
    7: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 7,7
    8: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 8,8
    9: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 9,9
    10: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # 10,10
    11: {2: '?', 3: '?', 4: '?', 5: '?', 6: '?', 7: '?', 8: '?', 9: '?', 10: '?', 'A': '?'},  # A,A
}

# BETTING STRATEGY CONFIGURATION
BETTING_CONFIG = {
    'base_bet': 25,  # Starting bet amount
    'max_bet': 500,  # Maximum allowed bet
    'strategy_type': 'flat',  # Options: 'flat', 'progressive', 'count_based', 'custom'

    # For progressive betting
    'win_multiplier': 1.0,  # Multiply bet by this after a win
    'loss_multiplier': 1.0,  # Multiply bet by this after a loss
    'reset_on_loss': True,  # Return to base bet after loss?

    # For count-based betting
    'count_threshold': 2,  # Increase bets when true count exceeds this
    'count_multiplier': 2  # Multiply bet by this when count is favorable
}


# Custom betting logic (if strategy_type = 'custom')
# Define your own function here
def custom_bet_logic(base_bet, last_result, win_streak, loss_streak, true_count, bankroll, max_bet=None):
    """
    Custom betting logic

    Args:
        base_bet: The base betting unit
        last_result: 'win', 'lose', 'push', or None (first hand)
        win_streak: Number of consecutive wins
        loss_streak: Number of consecutive losses
        true_count: Current true count from card counting
        bankroll: Current bankroll

    Returns:
        int: The bet amount for the next hand
        :param max_bet:
    """
    # Example: Double after 2 wins, reset after any loss
    if win_streak >= 2:
        return min(base_bet * 2, max_bet)
    else:
        return base_bet


