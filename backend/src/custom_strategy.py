import importlib.util
import sys
from typing import Dict, Any
from pathlib import Path

from strategy import StrategyType, BettingStrategy, BasicStrategy
from hand import Hand
from card import Card
from game import Action


class CustomStrategy:
    """Loads and executes a custom strategy from a file"""
    
    def __init__(self, strategy_file_path: str):
        self.strategy_file = Path(strategy_file_path)
        if not self.strategy_file.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_file_path}")
        
        # Load the strategy module
        spec = importlib.util.spec_from_file_location("custom_strategy", strategy_file_path)
        self.module = importlib.util.module_from_spec(spec)
        sys.modules["custom_strategy"] = self.module
        spec.loader.exec_module(self.module)
        
        # Load strategy tables
        self.hard_strategy = getattr(self.module, 'HARD_STRATEGY', {})
        self.soft_strategy = getattr(self.module, 'SOFT_STRATEGY', {})
        self.split_strategy = getattr(self.module, 'SPLIT_STRATEGY', {})
        self.betting_config = getattr(self.module, 'BETTING_CONFIG', {})
        
        # Validate the strategy
        self._validate_strategy()
    
    def _validate_strategy(self):
        """Validate that the strategy tables are complete"""
        # Check for missing entries
        missing = []
        
        # Validate hard strategy
        for total in range(5, 22):
            if total not in self.hard_strategy:
                missing.append(f"Hard {total}")
            else:
                for dealer in [2,3,4,5,6,7,8,9,10,'A']:
                    if dealer not in self.hard_strategy[total] or self.hard_strategy[total][dealer] == '?':
                        missing.append(f"Hard {total} vs dealer {dealer}")
        
        # Validate soft strategy
        for total in range(13, 22):
            if total not in self.soft_strategy:
                missing.append(f"Soft {total}")
            else:
                for dealer in [2,3,4,5,6,7,8,9,10,'A']:
                    if dealer not in self.soft_strategy[total] or self.soft_strategy[total][dealer] == '?':
                        missing.append(f"Soft {total} vs dealer {dealer}")
        
        if missing:
            print(f"Warning: Strategy has {len(missing)} missing decisions:")
            for m in missing[:10]:  # Show first 10
                print(f"  - {m}")
            if len(missing) > 10:
                print(f"  ... and {len(missing) - 10} more")
    
    def get_action(self, player_hand: Hand, dealer_up_card: Card, 
                   can_double: bool = True, can_split: bool = True) -> Action:
        """Get action based on custom strategy"""
        dealer_key = 'A' if dealer_up_card.rank.symbol == 'A' else dealer_up_card.value
        
        # Check for splitting pairs first
        if can_split and player_hand.can_split() and len(player_hand.cards) == 2:
            pair_value = player_hand.cards[0].value
            if pair_value in self.split_strategy and dealer_key in self.split_strategy[pair_value]:
                if self.split_strategy[pair_value][dealer_key] == 'Y':
                    return Action.SPLIT
        
        # Check soft vs hard hands
        if player_hand.is_soft:
            strategy_table = self.soft_strategy
        else:
            strategy_table = self.hard_strategy
        
        total = player_hand.value
        
        # Get action from strategy table
        if total in strategy_table and dealer_key in strategy_table[total]:
            action_code = strategy_table[total][dealer_key]
        else:
            # Fallback to basic strategy if not defined
            print(f"No custom strategy for {total} vs {dealer_key}, using basic strategy")
            return BasicStrategy.get_action(player_hand, dealer_up_card, can_double, can_split)
        
        # Convert strategy code to Action
        if action_code == 'H':
            return Action.HIT
        elif action_code == 'S':
            return Action.STAND
        elif action_code == 'D':
            return Action.DOUBLE if can_double else Action.HIT
        elif action_code == 'R':
            return Action.SURRENDER
        elif action_code == '?':
            # Fallback to basic strategy for undefined
            return BasicStrategy.get_action(player_hand, dealer_up_card, can_double, can_split)
        else:
            return Action.STAND
    
    def get_bet(self, base_bet: int, last_result: str = None, 
                win_streak: int = 0, loss_streak: int = 0,
                true_count: float = 0, bankroll: int = 1000) -> int:
        """Calculate bet based on custom betting strategy"""
        config = self.betting_config
        max_bet = config.get('max_bet', 500)
        
        strategy_type = config.get('strategy_type', 'flat')
        
        if strategy_type == 'flat':
            return config.get('base_bet', base_bet)
        
        elif strategy_type == 'progressive':
            if last_result == 'win':
                new_bet = base_bet * config.get('win_multiplier', 1.0)
            elif last_result == 'lose':
                if config.get('reset_on_loss', True):
                    new_bet = config.get('base_bet', base_bet)
                else:
                    new_bet = base_bet * config.get('loss_multiplier', 1.0)
            else:
                new_bet = config.get('base_bet', base_bet)
            
            return int(min(new_bet, max_bet))
        
        elif strategy_type == 'count_based':
            threshold = config.get('count_threshold', 2)
            if true_count >= threshold:
                multiplier = config.get('count_multiplier', 2)
                return int(min(base_bet * multiplier, max_bet))
            else:
                return config.get('base_bet', base_bet)
        
        elif strategy_type == 'custom':
            # Use custom function if defined
            if hasattr(config, 'custom_bet_logic'):
                return config['custom_bet_logic'](
                    base_bet, last_result, win_streak, loss_streak, true_count, bankroll
                )
            else:
                return config.get('base_bet', base_bet)
        
        return base_bet