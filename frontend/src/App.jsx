import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Hand from './components/Hand';
import SimulationPanel from './components/SimulationPanel';
import StatisticsOverlay from './components/StatisticsOverlay';
import StrategyTester from './components/StrategyTester';

const API_BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [betAmount, setBetAmount] = useState(25);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('play'); // 'play', 'simulate', or 'strategy'
  const [showStatistics, setShowStatistics] = useState(false);

  // Initialize new game session
  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = async () => {
    try {
      const response = await axios.post(`${API_BASE}/game/new`);
      setSessionId(response.data.session_id);
      setGameState(response.data.game_state);
      setResults(null);
    } catch (error) {
      console.error('Error starting new game:', error);
    }
  };

  const placeBet = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/game/${sessionId}/bet`, {
        amount: betAmount
      });
      setGameState(response.data);
      setResults(null);
    } catch (error) {
      console.error('Error placing bet:', error);
    }
    setLoading(false);
  };

  const performAction = async (action) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/game/${sessionId}/action`, {
        action: action
      });
      setGameState(response.data);
      
      // Check if round is over and get results
      if (response.data.state === 'round_over') {
        const resultsResponse = await axios.get(`${API_BASE}/game/${sessionId}/results`);
        setResults(resultsResponse.data.results);
      }
    } catch (error) {
      console.error('Error performing action:', error);
    }
    setLoading(false);
  };

  const startNewRound = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/game/${sessionId}/new-round`);
      setGameState(response.data.game_state);
      setResults(null);
    } catch (error) {
      console.error('Error starting new round:', error);
    }
    setLoading(false);
  };

  if (!gameState) {
    return <div className="min-h-screen bg-felt-green flex items-center justify-center">
      <p className="text-white text-xl">Loading...</p>
    </div>;
  }

  const isPlayerTurn = gameState.state === 'player_turn';
  const isDealerTurn = gameState.state === 'dealer_turn';
  const isRoundOver = gameState.state === 'round_over';
  const isBetting = gameState.state === 'betting';

  return (
    <div className="min-h-screen bg-felt-green">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-white text-center mb-8">
          Blackjack Simulator
        </h1>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('play')}
              className={`px-6 py-2 rounded font-semibold transition-colors ${
                activeTab === 'play' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Play Game
            </button>
            <button
              onClick={() => setActiveTab('simulate')}
              className={`px-6 py-2 rounded font-semibold transition-colors ${
                activeTab === 'simulate' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Run Simulations
            </button>
            <button
              onClick={() => setActiveTab('strategy')}
              className={`px-6 py-2 rounded font-semibold transition-colors ${
                activeTab === 'strategy' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Test Strategy
            </button>
          </div>
        </div>

        {activeTab === 'play' ? (
          <>
            {/* Statistics Toggle */}
            <div className="flex justify-end mb-4">
              <button
                onClick={() => setShowStatistics(!showStatistics)}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  showStatistics 
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {showStatistics ? '📊 Hide Statistics' : '📊 Show Statistics'}
              </button>
            </div>

            {/* Statistics Overlay */}
            <StatisticsOverlay 
              sessionId={sessionId}
              gameState={gameState}
              enabled={showStatistics}
            />

            {/* Game Info */}
            <div className="bg-gray-800 rounded-lg p-4 mb-6 text-white">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-lg">Bankroll: <span className="font-bold text-yellow-300">${gameState.player_bankroll}</span></p>
                </div>
                <div className="text-right">
                  <p className="text-sm">Cards Remaining: {gameState.deck_info.remaining_cards}</p>
                  <p className="text-sm">True Count: {gameState.deck_info.true_count.toFixed(1)}</p>
                </div>
              </div>
            </div>

        {/* Dealer Hand */}
        <div className="mb-8">
          <Hand 
            hand={gameState.dealer_hand} 
            isDealer={true} 
            hideFirstCard={!isRoundOver && !isDealerTurn}
          />
        </div>

        {/* Player Hands */}
        <div className="mb-8">
          <div className="flex justify-center gap-4">
            {gameState.player_hands.map((hand, index) => (
              <Hand 
                key={index} 
                hand={hand} 
                isActive={isPlayerTurn && index === gameState.current_hand_index}
              />
            ))}
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-gray-800 rounded-lg p-4 mb-6 text-white text-center">
            {results.map((result, index) => (
              <div key={index} className="mb-2">
                <p className="text-lg">
                  Hand {index + 1}: 
                  <span className={`font-bold ml-2 ${
                    result.result === 'win' || result.result === 'blackjack' ? 'text-green-400' : 
                    result.result === 'lose' ? 'text-red-400' : 
                    'text-yellow-400'
                  }`}>
                    {result.result.toUpperCase()}
                  </span>
                  <span className="ml-4">
                    {result.net > 0 ? '+' : ''}{result.net}
                  </span>
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-center gap-4">
          {isBetting && (
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-4 mb-4">
                <label className="text-white">Bet Amount:</label>
                <input 
                  type="number" 
                  value={betAmount} 
                  onChange={(e) => setBetAmount(Number(e.target.value))}
                  min="5" 
                  max="500" 
                  step="5"
                  className="px-3 py-2 rounded bg-gray-700 text-white"
                />
              </div>
              <button 
                onClick={placeBet}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded disabled:opacity-50"
              >
                Place Bet & Deal
              </button>
            </div>
          )}

          {isPlayerTurn && (
            <div className="flex gap-2">
              {gameState.valid_actions.map(action => (
                <button
                  key={action}
                  onClick={() => performAction(action)}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                >
                  {action.charAt(0).toUpperCase() + action.slice(1)}
                </button>
              ))}
            </div>
          )}

          {isRoundOver && (
            <button
              onClick={startNewRound}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded disabled:opacity-50"
            >
              New Round
            </button>
          )}
        </div>
          </>
        ) : activeTab === 'simulate' ? (
          <SimulationPanel />
        ) : (
          <StrategyTester />
        )}
      </div>
    </div>
  );
}

export default App;