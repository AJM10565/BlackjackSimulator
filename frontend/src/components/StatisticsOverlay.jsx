import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

const StatisticsOverlay = ({ sessionId, gameState, enabled }) => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (enabled && sessionId && gameState.state === 'player_turn') {
      fetchStatistics();
    }
  }, [enabled, sessionId, gameState.state, gameState.current_hand_index]);

  const fetchStatistics = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/game/${sessionId}/statistics`);
      if (response.data.available) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
    setLoading(false);
  };

  if (!enabled || !statistics || !statistics.available) {
    return null;
  }

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;
  const formatEV = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}`;
  };

  return (
    <div className="fixed top-20 right-4 w-80 bg-gray-900 bg-opacity-95 text-white rounded-lg shadow-2xl p-4 z-50">
      <h3 className="text-lg font-bold mb-3 text-yellow-400">Statistics & Analysis</h3>
      
      {/* Player Hand Info */}
      {statistics.player_hand && (
        <div className="mb-4 pb-4 border-b border-gray-700">
          <h4 className="font-semibold mb-2">Your Hand</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-400">Value:</span>
              <span className="ml-2 font-semibold">{statistics.player_hand.value}</span>
              {statistics.player_hand.is_soft && <span className="text-xs ml-1">(soft)</span>}
            </div>
            <div>
              <span className="text-gray-400">Strength:</span>
              <span className={`ml-2 font-semibold ${
                statistics.player_hand.strength === 'Very Strong' ? 'text-green-400' :
                statistics.player_hand.strength === 'Strong' ? 'text-green-300' :
                statistics.player_hand.strength === 'Moderate' ? 'text-yellow-300' :
                'text-red-300'
              }`}>{statistics.player_hand.strength}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-400">Bust if hit:</span>
              <span className={`ml-2 font-semibold ${
                statistics.player_hand.bust_probability > 0.5 ? 'text-red-400' :
                statistics.player_hand.bust_probability > 0.3 ? 'text-yellow-400' :
                'text-green-400'
              }`}>{formatPercentage(statistics.player_hand.bust_probability)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Dealer Info */}
      {statistics.dealer && (
        <div className="mb-4 pb-4 border-b border-gray-700">
          <h4 className="font-semibold mb-2">Dealer</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-400">Showing:</span>
              <span className="ml-2 font-semibold">
                {statistics.dealer.up_card.rank} {statistics.dealer.up_card.suit}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Bust chance:</span>
              <span className={`ml-2 font-semibold ${
                statistics.dealer.bust_probability > 0.4 ? 'text-green-400' :
                statistics.dealer.bust_probability > 0.3 ? 'text-yellow-400' :
                'text-red-400'
              }`}>{formatPercentage(statistics.dealer.bust_probability)}</span>
            </div>
          </div>
          
          {/* Dealer final value probabilities */}
          {statistics.dealer.final_value_probabilities && (
            <div className="mt-2">
              <p className="text-xs text-gray-400 mb-1">Dealer likely outcomes:</p>
              <div className="grid grid-cols-3 gap-1 text-xs">
                {Object.entries(statistics.dealer.final_value_probabilities)
                  .filter(([key, val]) => val > 0.05)
                  .sort(([a], [b]) => {
                    if (a === 'bust') return 1;
                    if (b === 'bust') return -1;
                    return parseInt(a) - parseInt(b);
                  })
                  .map(([value, prob]) => (
                    <div key={value} className="bg-gray-800 rounded px-1 py-0.5">
                      <span className={value === 'bust' ? 'text-red-400' : ''}>{value}:</span>
                      <span className="ml-1">{formatPercentage(prob)}</span>
                    </div>
                  ))
                }
              </div>
            </div>
          )}
        </div>
      )}

      {/* Win/Lose/Push Probabilities */}
      {statistics.outcome_probabilities && (
        <div className="mb-4 pb-4 border-b border-gray-700">
          <h4 className="font-semibold mb-2">Outcome Probabilities</h4>
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Win:</span>
              <span className="font-semibold text-green-400">
                {formatPercentage(statistics.outcome_probabilities.win)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Lose:</span>
              <span className="font-semibold text-red-400">
                {formatPercentage(statistics.outcome_probabilities.lose)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Push:</span>
              <span className="font-semibold text-yellow-400">
                {formatPercentage(statistics.outcome_probabilities.push)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation */}
      {statistics.recommendation && (
        <div className="mb-4 pb-4 border-b border-gray-700">
          <h4 className="font-semibold mb-2">Basic Strategy Says</h4>
          <div className="bg-blue-900 bg-opacity-50 rounded p-2">
            <p className="font-bold text-blue-300 uppercase">
              {statistics.recommendation.action}
            </p>
            <p className="text-xs text-gray-300 mt-1">
              {statistics.recommendation.explanation}
            </p>
          </div>
        </div>
      )}

      {/* Expected Values */}
      {statistics.expected_values && Object.keys(statistics.expected_values).length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold mb-2">Expected Value by Action</h4>
          <div className="space-y-1 text-sm">
            {Object.entries(statistics.expected_values)
              .sort(([, a], [, b]) => b - a)
              .map(([action, ev]) => (
                <div key={action} className="flex justify-between">
                  <span className="text-gray-400 capitalize">{action}:</span>
                  <span className={`font-mono ${ev >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatEV(ev)}
                  </span>
                </div>
              ))
            }
          </div>
        </div>
      )}

      {/* True Count */}
      {statistics.true_count !== undefined && (
        <div className="text-sm">
          <span className="text-gray-400">True Count:</span>
          <span className={`ml-2 font-semibold ${
            statistics.true_count >= 2 ? 'text-green-400' :
            statistics.true_count <= -2 ? 'text-red-400' :
            'text-yellow-400'
          }`}>{statistics.true_count.toFixed(1)}</span>
          {statistics.true_count >= 2 && (
            <span className="text-xs text-green-400 ml-2">(Player advantage)</span>
          )}
          {statistics.true_count <= -2 && (
            <span className="text-xs text-red-400 ml-2">(House advantage)</span>
          )}
        </div>
      )}
    </div>
  );
};

export default StatisticsOverlay;