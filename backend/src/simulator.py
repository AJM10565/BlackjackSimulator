import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from game import BlackjackGame, GameState, Action
from strategy import ComputerPlayer, StrategyType, BettingStrategy
from deck import Deck


@dataclass
class SimulationResult:
    """Results from a simulation run"""
    total_hands: int
    total_wins: int
    total_losses: int
    total_pushes: int
    total_blackjacks: int
    total_surrenders: int
    starting_bankroll: int
    ending_bankroll: int
    profit_loss: int
    win_rate: float
    roi: float  # Return on investment
    hands_per_hour: float
    max_bankroll: int
    min_bankroll: int
    bust_out: bool  # Did player lose all money
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_hands': self.total_hands,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'total_pushes': self.total_pushes,
            'total_blackjacks': self.total_blackjacks,
            'total_surrenders': self.total_surrenders,
            'starting_bankroll': self.starting_bankroll,
            'ending_bankroll': self.ending_bankroll,
            'profit_loss': self.profit_loss,
            'win_rate': self.win_rate,
            'roi': self.roi,
            'hands_per_hour': self.hands_per_hour,
            'max_bankroll': self.max_bankroll,
            'min_bankroll': self.min_bankroll,
            'bust_out': self.bust_out
        }


class BlackjackSimulator:
    """Runs simulations of blackjack games with computer players"""
    
    def __init__(self, 
                 num_decks: int = 6,
                 shuffle_threshold: float = 0.25,
                 min_bet: int = 5,
                 max_bet: int = 500):
        self.num_decks = num_decks
        self.shuffle_threshold = shuffle_threshold
        self.min_bet = min_bet
        self.max_bet = max_bet
        
    def simulate_hands(self,
                      player: ComputerPlayer,
                      num_hands: int,
                      verbose: bool = False) -> SimulationResult:
        """Simulate a number of hands with a computer player"""
        
        game = BlackjackGame(self.num_decks, self.shuffle_threshold)
        game.min_bet = self.min_bet
        game.max_bet = self.max_bet
        
        # Track statistics
        stats = {
            'wins': 0,
            'losses': 0,
            'pushes': 0,
            'blackjacks': 0,
            'surrenders': 0
        }
        
        starting_bankroll = player.betting_system.bankroll
        max_bankroll = starting_bankroll
        min_bankroll = starting_bankroll
        
        start_time = time.time()
        
        for hand_num in range(num_hands):
            # Check if player is bust
            if player.betting_system.bankroll < self.min_bet:
                if verbose:
                    print(f"Player bust out after {hand_num} hands")
                break
                
            # Get bet amount
            true_count = game.deck.get_true_count()
            bet_amount = player.get_bet(true_count)
            bet_amount = min(bet_amount, player.betting_system.bankroll)
            bet_amount = max(self.min_bet, min(bet_amount, self.max_bet))
            
            # Start new round
            game.player_bankroll = player.betting_system.bankroll
            game.place_bet(bet_amount)
            game.deal_initial_cards()
            
            # Play the hand
            while game.state == GameState.PLAYER_TURN:
                current_hand = game.player_hands[game.current_hand_index]
                dealer_up_card = game.dealer_hand.cards[0]
                valid_actions = game.get_valid_actions()
                
                action = player.get_action(current_hand, dealer_up_card, valid_actions, true_count)
                game.player_action(action)
                
                if action == Action.SURRENDER:
                    stats['surrenders'] += 1
            
            # Get results
            if game.state == GameState.ROUND_OVER:
                results = game.get_round_results()
                
                for result in results:
                    if result['result'] == 'win':
                        stats['wins'] += 1
                    elif result['result'] == 'lose':
                        stats['losses'] += 1
                    elif result['result'] == 'push':
                        stats['pushes'] += 1
                    elif result['result'] == 'blackjack':
                        stats['blackjacks'] += 1
                        stats['wins'] += 1
                    
                    # Update player's betting system
                    player.betting_system.update_result(result['result'], result['payout'])
                
                # Update bankroll tracking
                player.betting_system.bankroll = game.player_bankroll
                max_bankroll = max(max_bankroll, player.betting_system.bankroll)
                min_bankroll = min(min_bankroll, player.betting_system.bankroll)
                
                if verbose and hand_num % 100 == 0:
                    print(f"Hand {hand_num}: Bankroll = ${player.betting_system.bankroll}")
            
            # Reset for next round
            game.reset_round()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Calculate final statistics
        total_hands_played = hand_num + 1
        hands_per_hour = (total_hands_played / elapsed_time) * 3600 if elapsed_time > 0 else 0
        
        total_decisions = stats['wins'] + stats['losses'] + stats['pushes']
        win_rate = (stats['wins'] / total_decisions * 100) if total_decisions > 0 else 0
        
        ending_bankroll = player.betting_system.bankroll
        profit_loss = ending_bankroll - starting_bankroll
        roi = (profit_loss / starting_bankroll * 100) if starting_bankroll > 0 else 0
        
        return SimulationResult(
            total_hands=total_hands_played,
            total_wins=stats['wins'],
            total_losses=stats['losses'],
            total_pushes=stats['pushes'],
            total_blackjacks=stats['blackjacks'],
            total_surrenders=stats['surrenders'],
            starting_bankroll=starting_bankroll,
            ending_bankroll=ending_bankroll,
            profit_loss=profit_loss,
            win_rate=win_rate,
            roi=roi,
            hands_per_hour=hands_per_hour,
            max_bankroll=max_bankroll,
            min_bankroll=min_bankroll,
            bust_out=ending_bankroll < self.min_bet
        )
    
    def compare_strategies(self,
                          num_hands: int = 10000,
                          num_simulations: int = 10,
                          starting_bankroll: int = 1000,
                          base_bet: int = 10) -> Dict[str, Dict[str, Any]]:
        """Run simulations comparing different strategies"""
        
        strategies_to_test = [
            (StrategyType.BASIC, BettingStrategy.FLAT),
            (StrategyType.BASIC, BettingStrategy.MARTINGALE),
            (StrategyType.BASIC, BettingStrategy.KELLY_CRITERION),
            (StrategyType.CARD_COUNTING, BettingStrategy.KELLY_CRITERION),
            (StrategyType.CONSERVATIVE, BettingStrategy.FLAT),
            (StrategyType.AGGRESSIVE, BettingStrategy.FLAT),
        ]
        
        results = {}
        
        for playing_strat, betting_strat in strategies_to_test:
            strategy_name = f"{playing_strat.value}_{betting_strat.value}"
            print(f"\nTesting {strategy_name}...")
            
            strategy_results = []
            
            # Run multiple simulations for statistical significance
            for sim_num in range(num_simulations):
                player = ComputerPlayer(
                    playing_strategy=playing_strat,
                    betting_strategy=betting_strat,
                    base_bet=base_bet,
                    bankroll=starting_bankroll
                )
                
                result = self.simulate_hands(player, num_hands, verbose=False)
                strategy_results.append(result)
                
                print(f"  Simulation {sim_num + 1}/{num_simulations}: "
                      f"ROI={result.roi:.2f}%, Final=${result.ending_bankroll}")
            
            # Calculate aggregate statistics
            avg_roi = np.mean([r.roi for r in strategy_results])
            std_roi = np.std([r.roi for r in strategy_results])
            avg_final_bankroll = np.mean([r.ending_bankroll for r in strategy_results])
            bust_rate = sum(1 for r in strategy_results if r.bust_out) / num_simulations * 100
            
            results[strategy_name] = {
                'playing_strategy': playing_strat.value,
                'betting_strategy': betting_strat.value,
                'avg_roi': avg_roi,
                'std_roi': std_roi,
                'avg_final_bankroll': avg_final_bankroll,
                'bust_rate': bust_rate,
                'simulations': [r.to_dict() for r in strategy_results]
            }
        
        return results
    
    def run_parallel_simulations(self,
                               strategy_configs: List[Dict[str, Any]],
                               num_hands: int = 10000,
                               max_workers: Optional[int] = None) -> List[SimulationResult]:
        """Run multiple simulations in parallel"""
        
        results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all simulations
            future_to_config = {}
            for config in strategy_configs:
                player = ComputerPlayer(
                    playing_strategy=StrategyType(config['playing_strategy']),
                    betting_strategy=BettingStrategy(config['betting_strategy']),
                    base_bet=config.get('base_bet', 10),
                    bankroll=config.get('bankroll', 1000)
                )
                
                future = executor.submit(self.simulate_hands, player, num_hands, False)
                future_to_config[future] = config
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    result = future.result()
                    results.append({
                        'config': config,
                        'result': result.to_dict()
                    })
                except Exception as exc:
                    print(f"Simulation with config {config} generated an exception: {exc}")
        
        return results


def main():
    """Example usage of the simulator"""
    simulator = BlackjackSimulator()
    
    # Test a single strategy
    print("Testing Basic Strategy with Flat Betting...")
    player = ComputerPlayer(
        playing_strategy=StrategyType.BASIC,
        betting_strategy=BettingStrategy.FLAT,
        base_bet=25,
        bankroll=1000
    )
    
    result = simulator.simulate_hands(player, num_hands=1000, verbose=True)
    print(f"\nFinal Results:")
    print(f"  Hands Played: {result.total_hands}")
    print(f"  Win Rate: {result.win_rate:.2f}%")
    print(f"  ROI: {result.roi:.2f}%")
    print(f"  Final Bankroll: ${result.ending_bankroll}")
    
    # Compare multiple strategies
    print("\n" + "="*50)
    print("Comparing Multiple Strategies...")
    comparison_results = simulator.compare_strategies(
        num_hands=1000,
        num_simulations=5
    )
    
    # Print summary
    print("\nStrategy Comparison Summary:")
    print("-" * 80)
    print(f"{'Strategy':<30} {'Avg ROI':<12} {'Std Dev':<12} {'Avg Final $':<15} {'Bust Rate'}")
    print("-" * 80)
    
    for strategy_name, stats in comparison_results.items():
        print(f"{strategy_name:<30} "
              f"{stats['avg_roi']:>10.2f}% "
              f"{stats['std_roi']:>10.2f}% "
              f"${stats['avg_final_bankroll']:>13.2f} "
              f"{stats['bust_rate']:>9.1f}%")


if __name__ == "__main__":
    main()