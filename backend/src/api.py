from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from game import BlackjackGame, Action, GameState
from strategy import ComputerPlayer, StrategyType, BettingStrategy, BasicStrategy
from simulator import BlackjackSimulator
from statistics import BlackjackStatistics
from configurable_strategy import ConfigurableStrategy
import json
import time


class BetRequest(BaseModel):
    amount: int


class ActionRequest(BaseModel):
    action: str


class SimulationRequest(BaseModel):
    playing_strategy: str = "basic"
    betting_strategy: str = "flat"
    num_hands: int = 1000
    starting_bankroll: int = 1000
    base_bet: int = 10
    num_simulations: int = 1


class StrategyComparisonRequest(BaseModel):
    num_hands: int = 1000
    num_simulations: int = 5
    starting_bankroll: int = 1000
    base_bet: int = 10


class CustomStrategyRequest(BaseModel):
    card_values: Dict[str, int]
    ace_adjustment: int = 4
    bet_threshold: int = 5
    bet_increment: int = 5
    max_bet_units: int = 20
    num_hands: int = 10000
    starting_bankroll: float = 10000
    min_bet: float = 10
    num_decks: int = 6
    penetration: float = 72


class StrategyConfig(BaseModel):
    counting: Dict[str, Any]
    betting: Dict[str, Any]
    deviations: Dict[str, Any]
    insurance: Dict[str, Any]


class GameSession:
    def __init__(self):
        self.game = BlackjackGame()
        self.session_id = str(uuid.uuid4())
        self.history = []


# In-memory game sessions (in production, use Redis or similar)
game_sessions: Dict[str, GameSession] = {}

# Thread pool for running simulations
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Blackjack Simulator API"}


@app.post("/api/game/new")
def new_game():
    """Create a new game session"""
    session = GameSession()
    game_sessions[session.session_id] = session
    return {
        "session_id": session.session_id,
        "game_state": session.game.get_game_state()
    }


@app.get("/api/game/{session_id}/state")
def get_game_state(session_id: str):
    """Get current game state"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    return session.game.get_game_state()


@app.post("/api/game/{session_id}/bet")
def place_bet(session_id: str, bet_request: BetRequest):
    """Place a bet to start a new round"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state != GameState.BETTING:
        raise HTTPException(status_code=400, detail="Not in betting phase")
    
    if not game.place_bet(bet_request.amount):
        raise HTTPException(status_code=400, detail="Invalid bet amount")
    
    # Deal initial cards after bet is placed
    game.deal_initial_cards()
    
    # Add to history
    session.history.append({
        "action": "bet",
        "amount": bet_request.amount,
        "state": game.get_game_state()
    })
    
    return game.get_game_state()


@app.post("/api/game/{session_id}/action")
def player_action(session_id: str, action_request: ActionRequest):
    """Perform a player action (hit, stand, double, split, surrender)"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state != GameState.PLAYER_TURN:
        raise HTTPException(status_code=400, detail="Not player's turn")
    
    try:
        action = Action(action_request.action)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    if not game.player_action(action):
        raise HTTPException(status_code=400, detail="Action not allowed")
    
    # Add to history
    session.history.append({
        "action": action_request.action,
        "state": game.get_game_state()
    })
    
    return game.get_game_state()


@app.post("/api/game/{session_id}/new-round")
def new_round(session_id: str):
    """Start a new round"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state != GameState.ROUND_OVER:
        raise HTTPException(status_code=400, detail="Current round not finished")
    
    # Get results before resetting
    results = game.get_round_results()
    
    # Reset for new round
    game.reset_round()
    
    return {
        "previous_results": results,
        "game_state": game.get_game_state()
    }


@app.get("/api/game/{session_id}/results")
def get_results(session_id: str):
    """Get results of the current round"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state != GameState.ROUND_OVER:
        raise HTTPException(status_code=400, detail="Round not finished")
    
    return {
        "results": game.get_round_results(),
        "game_state": game.get_game_state()
    }


@app.get("/api/game/{session_id}/history")
def get_history(session_id: str):
    """Get game history"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return {"history": game_sessions[session_id].history}


@app.post("/api/simulation/run")
async def run_simulation(request: SimulationRequest):
    """Run a blackjack simulation with specified parameters"""
    try:
        # Create simulator
        simulator = BlackjackSimulator()
        
        # Run simulations asynchronously
        loop = asyncio.get_event_loop()
        results = []
        
        for _ in range(request.num_simulations):
            player = ComputerPlayer(
                playing_strategy=StrategyType(request.playing_strategy),
                betting_strategy=BettingStrategy(request.betting_strategy),
                base_bet=request.base_bet,
                bankroll=request.starting_bankroll
            )
            
            result = await loop.run_in_executor(
                executor,
                simulator.simulate_hands,
                player,
                request.num_hands,
                False
            )
            results.append(result.to_dict())
        
        # Calculate aggregate statistics
        avg_roi = sum(r['roi'] for r in results) / len(results)
        avg_final_bankroll = sum(r['ending_bankroll'] for r in results) / len(results)
        bust_rate = sum(1 for r in results if r['bust_out']) / len(results) * 100
        
        return {
            "summary": {
                "avg_roi": avg_roi,
                "avg_final_bankroll": avg_final_bankroll,
                "bust_rate": bust_rate,
                "num_simulations": request.num_simulations
            },
            "simulations": results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulation/compare-strategies")
async def compare_strategies(request: StrategyComparisonRequest):
    """Compare multiple strategies"""
    simulator = BlackjackSimulator()
    
    # Run comparison asynchronously
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        executor,
        simulator.compare_strategies,
        request.num_hands,
        request.num_simulations,
        request.starting_bankroll,
        request.base_bet
    )
    
    return results


@app.get("/api/strategies")
def get_available_strategies():
    """Get list of available playing and betting strategies"""
    return {
        "playing_strategies": [s.value for s in StrategyType],
        "betting_strategies": [s.value for s in BettingStrategy]
    }


@app.post("/api/game/{session_id}/auto-play")
async def auto_play_hand(session_id: str, strategy: str = "basic"):
    """Play a single hand automatically using specified strategy"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state != GameState.PLAYER_TURN:
        raise HTTPException(status_code=400, detail="Not player's turn")
    
    # Create a computer player with the specified strategy
    player = ComputerPlayer(playing_strategy=StrategyType(strategy))
    
    # Play all hands
    while game.state == GameState.PLAYER_TURN:
        current_hand = game.player_hands[game.current_hand_index]
        dealer_up_card = game.dealer_hand.cards[0]
        valid_actions = [Action(a) for a in game.get_valid_actions()]
        true_count = game.deck.get_true_count()
        
        action = player.get_action(current_hand, dealer_up_card, valid_actions, true_count)
        game.player_action(action)
        
        # Add to history
        session.history.append({
            "action": action.value,
            "state": game.get_game_state()
        })
    
    return game.get_game_state()


@app.get("/api/game/{session_id}/statistics")
def get_statistics(session_id: str):
    """Get statistical analysis for current game state"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    game = session.game
    
    if game.state not in [GameState.PLAYER_TURN, GameState.DEALER_TURN, GameState.ROUND_OVER]:
        return {"available": False}
    
    stats = {}
    
    # Get current hand statistics
    if game.state == GameState.PLAYER_TURN and game.player_hands:
        current_hand = game.player_hands[game.current_hand_index]
        dealer_up_card = game.dealer_hand.cards[0]
        
        # Calculate bust probability
        bust_prob = BlackjackStatistics.calculate_bust_probability(current_hand)
        
        # Calculate dealer bust probability
        dealer_bust_prob = BlackjackStatistics.calculate_dealer_bust_probability(dealer_up_card)
        
        # Get win/lose/push probabilities
        outcome_probs = BlackjackStatistics.calculate_win_probability(current_hand, dealer_up_card)
        
        # Get recommended action
        basic_strategy = BasicStrategy()
        valid_actions = game.get_valid_actions()
        can_double = Action.DOUBLE in valid_actions
        can_split = Action.SPLIT in valid_actions
        recommended_action = basic_strategy.get_action(current_hand, dealer_up_card, can_double, can_split)
        
        # Get explanation for recommendation
        explanation = BlackjackStatistics.get_recommended_action_explanation(
            current_hand, dealer_up_card, recommended_action.value
        )
        
        # Calculate expected values for each action
        ev_by_action = {}
        for action in valid_actions:
            ev = BlackjackStatistics.calculate_expected_value(
                action.value, current_hand, dealer_up_card, current_hand.bet
            )
            ev_by_action[action.value] = ev
        
        stats = {
            "available": True,
            "player_hand": {
                "value": current_hand.value,
                "is_soft": current_hand.is_soft,
                "strength": BlackjackStatistics.get_hand_strength(current_hand),
                "bust_probability": bust_prob,
                "cards": [card.to_dict() for card in current_hand.cards]
            },
            "dealer": {
                "up_card": dealer_up_card.to_dict(),
                "bust_probability": dealer_bust_prob,
                "final_value_probabilities": BlackjackStatistics.calculate_dealer_final_value_probabilities(dealer_up_card)
            },
            "outcome_probabilities": outcome_probs,
            "recommendation": {
                "action": recommended_action.value,
                "explanation": explanation
            },
            "expected_values": ev_by_action,
            "true_count": game.deck.get_true_count()
        }
    
    elif game.state in [GameState.DEALER_TURN, GameState.ROUND_OVER]:
        # Show dealer statistics
        dealer_up_card = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
        
        if dealer_up_card:
            stats = {
                "available": True,
                "dealer": {
                    "current_value": game.dealer_hand.value,
                    "is_bust": game.dealer_hand.is_bust,
                    "cards": [card.to_dict() for card in game.dealer_hand.cards]
                },
                "true_count": game.deck.get_true_count()
            }
        else:
            stats = {"available": False}
    else:
        stats = {"available": False}
    
    return stats


@app.post("/api/strategy/simulate")
async def simulate_custom_strategy(request: CustomStrategyRequest):
    """Run simulation with custom strategy parameters"""
    
    # Build strategy config
    config = {
        'counting': {
            'card_values': request.card_values,
            'ace_adjustment': request.ace_adjustment
        },
        'betting': {
            'count_threshold': request.bet_threshold,
            'count_increment': request.bet_increment,
            'max_bet_units': request.max_bet_units
        },
        'deviations': {  # Use default deviations for now
            '16_vs_10_stand': {'player_total': 16, 'dealer_card': 10, 'action': 'STAND', 'count_threshold': 0, 'comparison': 'greater'},
            '12_vs_3_stand': {'player_total': 12, 'dealer_card': 3, 'action': 'STAND', 'count_threshold': 5, 'comparison': 'greater_equal'},
            '12_vs_2_stand': {'player_total': 12, 'dealer_card': 2, 'action': 'STAND', 'count_threshold': 10, 'comparison': 'greater_equal'},
            '13_vs_2_hit': {'player_total': 13, 'dealer_card': 2, 'action': 'HIT', 'count_threshold': -5, 'comparison': 'less'},
            '13_vs_3_hit': {'player_total': 13, 'dealer_card': 3, 'action': 'HIT', 'count_threshold': -10, 'comparison': 'less'},
            '11_vs_5_double': {'player_total': 11, 'dealer_card': 5, 'action': 'DOUBLE', 'count_threshold': 10, 'comparison': 'greater'},
            '11_vs_6_double': {'player_total': 11, 'dealer_card': 6, 'action': 'DOUBLE', 'count_threshold': 10, 'comparison': 'greater'},
            '88_vs_10_no_split': {'player_total': 16, 'dealer_card': 10, 'action': 'NO_SPLIT', 'count_threshold': 0, 'comparison': 'greater'}
        },
        'insurance': {
            'ace_excess_threshold': 1.0
        }
    }
    
    # Run simulation
    strategy = ConfigurableStrategy(config, total_decks=request.num_decks)
    game = BlackjackGame(num_decks=request.num_decks, shuffle_threshold=request.penetration/100)
    
    stats = {
        'total_hands': 0,
        'wins': 0,
        'losses': 0,
        'pushes': 0,
        'blackjacks': 0,
        'total_wagered': 0,
        'total_won_lost': 0,
        'bet_distribution': {}
    }
    
    bankroll = request.starting_bankroll
    max_bankroll = bankroll
    min_bankroll = bankroll
    
    start_time = time.time()
    strategy.reset_count()
    
    for hand_num in range(request.num_hands):
        if bankroll < request.min_bet:
            break
            
        if game.deck.needs_shuffle():
            game.deck.shuffle()
            strategy.reset_count()
            
        bet_amount = strategy.get_bet_amount(request.min_bet)
        bet_amount = min(bet_amount, bankroll)
        
        bet_key = int(bet_amount / request.min_bet)
        stats['bet_distribution'][str(bet_key)] = stats['bet_distribution'].get(str(bet_key), 0) + 1
        
        game.player_bankroll = bankroll
        game.place_bet(bet_amount)
        game.deal_initial_cards()
        
        for card in game.player_hands[0].cards:
            strategy.observe_card(card)
        strategy.observe_card(game.dealer_hand.cards[0])
        
        while game.state == GameState.PLAYER_TURN:
            current_hand = game.player_hands[game.current_hand_index]
            dealer_up_card = game.dealer_hand.cards[0]
            can_split = len(game.player_hands) == 1 and game.player_hands[0].can_split()
            
            action = strategy.get_action(current_hand, dealer_up_card, can_split)
            result = game.player_action(action)
            if not result:
                break
                
            if action in [Action.HIT, Action.DOUBLE]:
                if game.state == GameState.PLAYER_TURN and game.current_hand_index < len(game.player_hands):
                    new_hand = game.player_hands[game.current_hand_index]
                    if len(new_hand.cards) > len(current_hand.cards):
                        strategy.observe_card(new_hand.cards[-1])
        
        if game.state == GameState.DEALER_TURN:
            dealer_start_cards = len(game.dealer_hand.cards)
            game._play_dealer_hand()
            for i in range(dealer_start_cards, len(game.dealer_hand.cards)):
                strategy.observe_card(game.dealer_hand.cards[i])
        
        stats['total_hands'] += 1
        stats['total_wagered'] += bet_amount * len(game.player_hands)
        
        for hand_result in game.get_round_results():
            result = hand_result['result']
            net = hand_result['net']
            
            if 'win' in result.lower() or result == 'blackjack':
                stats['wins'] += 1
                if result == 'blackjack':
                    stats['blackjacks'] += 1
            elif 'lose' in result.lower() or 'bust' in result.lower():
                stats['losses'] += 1
            else:
                stats['pushes'] += 1
                
            stats['total_won_lost'] += net
            bankroll += net
        
        max_bankroll = max(max_bankroll, bankroll)
        min_bankroll = min(min_bankroll, bankroll)
        
        game.reset_round()
    
    elapsed_time = time.time() - start_time
    
    return {
        'final_bankroll': bankroll,
        'starting_bankroll': request.starting_bankroll,
        'win_rate': stats['wins'] / stats['total_hands'] if stats['total_hands'] > 0 else 0,
        'loss_rate': stats['losses'] / stats['total_hands'] if stats['total_hands'] > 0 else 0,
        'push_rate': stats['pushes'] / stats['total_hands'] if stats['total_hands'] > 0 else 0,
        'avg_bet': stats['total_wagered'] / stats['total_hands'] if stats['total_hands'] > 0 else 0,
        'roi': stats['total_won_lost'] / stats['total_wagered'] if stats['total_wagered'] > 0 else 0,
        'hands_per_hour': (stats['total_hands'] / elapsed_time * 3600) if elapsed_time > 0 else 0,
        'max_bankroll': max_bankroll,
        'min_bankroll': min_bankroll,
        'total_hands': stats['total_hands'],
        'wins': stats['wins'],
        'losses': stats['losses'],
        'pushes': stats['pushes'],
        'blackjacks': stats['blackjacks'],
        'total_wagered': stats['total_wagered'],
        'total_won_lost': stats['total_won_lost'],
        'bet_distribution': stats['bet_distribution']
    }


@app.get("/api/strategy/default-config")
def get_default_strategy_config():
    """Get default strategy configuration"""
    return {
        "card_values": {
            "2": 0,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 3,
            "7": 0,
            "8": -1,
            "9": -2,
            "10": -3,
            "J": -3,
            "Q": -3,
            "K": -3,
            "A": -3
        },
        "ace_adjustment": 4,
        "bet_threshold": 5,
        "bet_increment": 5,
        "max_bet_units": 20
    }


@app.get("/api/strategy/optimized-config")
def get_optimized_strategy_config():
    """Get optimized strategy configuration"""
    return {
        "card_values": {
            "2": 0,
            "3": 3,
            "4": 3,
            "5": 4,
            "6": 4,
            "7": 0,
            "8": 0,
            "9": -3,
            "10": -3,
            "J": -3,
            "Q": -3,
            "K": -3,
            "A": -3
        },
        "ace_adjustment": 5,
        "bet_threshold": 3,
        "bet_increment": 5,
        "max_bet_units": 20
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)