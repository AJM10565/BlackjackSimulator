import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

const SimulationPanel = () => {
  const [strategies, setStrategies] = useState({
    playing_strategies: [],
    betting_strategies: []
  });
  
  const [simulationConfig, setSimulationConfig] = useState({
    playing_strategy: 'basic',
    betting_strategy: 'flat',
    num_hands: 1000,
    starting_bankroll: 1000,
    base_bet: 10,
    num_simulations: 5
  });
  
  const [simulationResults, setSimulationResults] = useState(null);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available strategies
    axios.get(`${API_BASE}/strategies`)
      .then(response => setStrategies(response.data))
      .catch(error => console.error('Error fetching strategies:', error));
  }, []);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/simulation/run`, simulationConfig);
      setSimulationResults(response.data);
      setComparisonResults(null);
    } catch (error) {
      console.error('Error running simulation:', error);
    }
    setLoading(false);
  };

  const compareStrategies = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/simulation/compare-strategies`, {
        num_hands: simulationConfig.num_hands,
        num_simulations: simulationConfig.num_simulations,
        starting_bankroll: simulationConfig.starting_bankroll,
        base_bet: simulationConfig.base_bet
      });
      setComparisonResults(response.data);
      setSimulationResults(null);
    } catch (error) {
      console.error('Error comparing strategies:', error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 text-white">
      <h2 className="text-2xl font-bold mb-6">Strategy Simulator</h2>
      
      {/* Configuration Form */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Playing Strategy</label>
          <select 
            value={simulationConfig.playing_strategy}
            onChange={(e) => setSimulationConfig({...simulationConfig, playing_strategy: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
          >
            {strategies.playing_strategies.map(strategy => (
              <option key={strategy} value={strategy}>{strategy}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Betting Strategy</label>
          <select 
            value={simulationConfig.betting_strategy}
            onChange={(e) => setSimulationConfig({...simulationConfig, betting_strategy: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
          >
            {strategies.betting_strategies.map(strategy => (
              <option key={strategy} value={strategy}>{strategy}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Number of Hands</label>
          <input 
            type="number"
            value={simulationConfig.num_hands}
            onChange={(e) => setSimulationConfig({...simulationConfig, num_hands: parseInt(e.target.value)})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
            min="100"
            max="100000"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Starting Bankroll</label>
          <input 
            type="number"
            value={simulationConfig.starting_bankroll}
            onChange={(e) => setSimulationConfig({...simulationConfig, starting_bankroll: parseInt(e.target.value)})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
            min="100"
            max="100000"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Base Bet</label>
          <input 
            type="number"
            value={simulationConfig.base_bet}
            onChange={(e) => setSimulationConfig({...simulationConfig, base_bet: parseInt(e.target.value)})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
            min="5"
            max="500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Number of Simulations</label>
          <input 
            type="number"
            value={simulationConfig.num_simulations}
            onChange={(e) => setSimulationConfig({...simulationConfig, num_simulations: parseInt(e.target.value)})}
            className="w-full px-3 py-2 bg-gray-700 rounded"
            min="1"
            max="50"
          />
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={runSimulation}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          Run Simulation
        </button>
        
        <button
          onClick={compareStrategies}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          Compare All Strategies
        </button>
      </div>
      
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <p className="mt-4">Running simulations...</p>
        </div>
      )}
      
      {/* Simulation Results */}
      {simulationResults && !loading && (
        <div className="bg-gray-700 rounded p-4">
          <h3 className="text-xl font-semibold mb-4">Simulation Results</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-400">Average ROI</p>
              <p className={`text-2xl font-bold ${simulationResults.summary.avg_roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {simulationResults.summary.avg_roi.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Average Final Bankroll</p>
              <p className="text-2xl font-bold">${simulationResults.summary.avg_final_bankroll.toFixed(0)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Bust Rate</p>
              <p className="text-2xl font-bold text-red-400">{simulationResults.summary.bust_rate.toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Simulations Run</p>
              <p className="text-2xl font-bold">{simulationResults.summary.num_simulations}</p>
            </div>
          </div>
          
          {/* Individual Simulation Details */}
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Individual Runs:</h4>
            <div className="max-h-40 overflow-y-auto">
              {simulationResults.simulations.map((sim, index) => (
                <div key={index} className="text-sm py-1 border-b border-gray-600">
                  Run {index + 1}: ${sim.starting_bankroll} → ${sim.ending_bankroll} 
                  ({sim.roi >= 0 ? '+' : ''}{sim.roi.toFixed(1)}%)
                  {sim.bust_out && <span className="text-red-400 ml-2">BUST</span>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Strategy Comparison Results */}
      {comparisonResults && !loading && (
        <div className="bg-gray-700 rounded p-4">
          <h3 className="text-xl font-semibold mb-4">Strategy Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left py-2">Strategy</th>
                  <th className="text-right py-2">Avg ROI</th>
                  <th className="text-right py-2">Std Dev</th>
                  <th className="text-right py-2">Avg Final</th>
                  <th className="text-right py-2">Bust %</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(comparisonResults).map(([key, data]) => (
                  <tr key={key} className="border-b border-gray-600">
                    <td className="py-2">
                      <div>
                        <div className="font-medium">{data.playing_strategy}</div>
                        <div className="text-xs text-gray-400">{data.betting_strategy}</div>
                      </div>
                    </td>
                    <td className={`text-right py-2 ${data.avg_roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {data.avg_roi.toFixed(2)}%
                    </td>
                    <td className="text-right py-2">{data.std_roi.toFixed(2)}%</td>
                    <td className="text-right py-2">${data.avg_final_bankroll.toFixed(0)}</td>
                    <td className="text-right py-2 text-red-400">{data.bust_rate.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationPanel;