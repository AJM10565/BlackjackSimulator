import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './StrategyTester.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const StrategyTester = () => {
  const [cardValues, setCardValues] = useState({});
  const [aceAdjustment, setAceAdjustment] = useState(4);
  const [betThreshold, setBetThreshold] = useState(5);
  const [betIncrement, setBetIncrement] = useState(5);
  const [maxBetUnits, setMaxBetUnits] = useState(20);
  
  const [numHands, setNumHands] = useState(10000);
  const [startingBankroll, setStartingBankroll] = useState(10000);
  const [minBet, setMinBet] = useState(10);
  const [numDecks, setNumDecks] = useState(6);
  const [penetration, setPenetration] = useState(72);
  
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState(null);
  const [savedConfigs, setSavedConfigs] = useState([]);
  const [configName, setConfigName] = useState('');

  // Load default configuration on mount
  useEffect(() => {
    loadDefaultConfig();
  }, []);

  const loadDefaultConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/strategy/default-config`);
      const config = response.data;
      setCardValues(config.card_values);
      setAceAdjustment(config.ace_adjustment);
      setBetThreshold(config.bet_threshold);
      setBetIncrement(config.bet_increment);
      setMaxBetUnits(config.max_bet_units);
    } catch (error) {
      console.error('Error loading default config:', error);
    }
  };

  const loadOptimizedConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/strategy/optimized-config`);
      const config = response.data;
      setCardValues(config.card_values);
      setAceAdjustment(config.ace_adjustment);
      setBetThreshold(config.bet_threshold);
      setBetIncrement(config.bet_increment);
      setMaxBetUnits(config.max_bet_units);
    } catch (error) {
      console.error('Error loading optimized config:', error);
    }
  };

  const handleCardValueChange = (card, value) => {
    setCardValues(prev => ({
      ...prev,
      [card]: parseInt(value) || 0
    }));
  };

  const runSimulation = async () => {
    setIsSimulating(true);
    setResults(null);

    // Convert card values to format expected by API
    const apiCardValues = {};
    Object.entries(cardValues).forEach(([card, value]) => {
      apiCardValues[card.toUpperCase()] = value;
    });

    try {
      const response = await axios.post(`${API_URL}/api/strategy/simulate`, {
        card_values: apiCardValues,
        ace_adjustment: aceAdjustment,
        bet_threshold: betThreshold,
        bet_increment: betIncrement,
        max_bet_units: maxBetUnits,
        num_hands: numHands,
        starting_bankroll: startingBankroll,
        min_bet: minBet,
        num_decks: numDecks,
        penetration: penetration
      });

      setResults(response.data);
    } catch (error) {
      console.error('Simulation error:', error);
      alert('Error running simulation: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsSimulating(false);
    }
  };

  const saveConfiguration = () => {
    if (!configName) {
      alert('Please enter a name for this configuration');
      return;
    }

    const config = {
      name: configName,
      cardValues,
      aceAdjustment,
      betThreshold,
      betIncrement,
      maxBetUnits,
      timestamp: new Date().toISOString()
    };

    const configs = JSON.parse(localStorage.getItem('savedStrategies') || '[]');
    configs.push(config);
    localStorage.setItem('savedStrategies', JSON.stringify(configs));
    setSavedConfigs(configs);
    setConfigName('');
    alert('Configuration saved!');
  };

  const loadConfiguration = (config) => {
    setCardValues(config.cardValues);
    setAceAdjustment(config.aceAdjustment);
    setBetThreshold(config.betThreshold);
    setBetIncrement(config.betIncrement);
    setMaxBetUnits(config.maxBetUnits);
  };

  const deleteConfiguration = (index) => {
    const configs = [...savedConfigs];
    configs.splice(index, 1);
    localStorage.setItem('savedStrategies', JSON.stringify(configs));
    setSavedConfigs(configs);
  };

  // Load saved configurations on mount
  useEffect(() => {
    const configs = JSON.parse(localStorage.getItem('savedStrategies') || '[]');
    setSavedConfigs(configs);
  }, []);

  return (
    <div className="strategy-tester">
      <h1>Blackjack Strategy Tester</h1>
      
      <div className="config-section">
        <h2>Card Counting Values</h2>
        <div className="card-values-grid">
          {['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'].map(card => (
            <div key={card} className="card-value-input">
              <label>{card}</label>
              <input
                type="number"
                value={cardValues[card] || 0}
                onChange={(e) => handleCardValueChange(card, e.target.value)}
                disabled={isSimulating}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="config-section">
        <h2>Betting Strategy</h2>
        <div className="betting-inputs">
          <div className="input-group">
            <label>Ace Adjustment</label>
            <input
              type="number"
              value={aceAdjustment}
              onChange={(e) => setAceAdjustment(parseInt(e.target.value) || 0)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Bet Threshold (True Count)</label>
            <input
              type="number"
              value={betThreshold}
              onChange={(e) => setBetThreshold(parseInt(e.target.value) || 0)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Bet Increment</label>
            <input
              type="number"
              value={betIncrement}
              onChange={(e) => setBetIncrement(parseInt(e.target.value) || 1)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Max Bet Units</label>
            <input
              type="number"
              value={maxBetUnits}
              onChange={(e) => setMaxBetUnits(parseInt(e.target.value) || 1)}
              disabled={isSimulating}
            />
          </div>
        </div>
      </div>

      <div className="config-section">
        <h2>Simulation Parameters</h2>
        <div className="simulation-inputs">
          <div className="input-group">
            <label>Number of Hands</label>
            <input
              type="number"
              value={numHands}
              onChange={(e) => setNumHands(parseInt(e.target.value) || 1000)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Starting Bankroll ($)</label>
            <input
              type="number"
              value={startingBankroll}
              onChange={(e) => setStartingBankroll(parseInt(e.target.value) || 1000)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Minimum Bet ($)</label>
            <input
              type="number"
              value={minBet}
              onChange={(e) => setMinBet(parseInt(e.target.value) || 10)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Number of Decks</label>
            <input
              type="number"
              value={numDecks}
              onChange={(e) => setNumDecks(parseInt(e.target.value) || 6)}
              disabled={isSimulating}
            />
          </div>
          <div className="input-group">
            <label>Penetration (%)</label>
            <input
              type="number"
              value={penetration}
              onChange={(e) => setPenetration(parseInt(e.target.value) || 72)}
              disabled={isSimulating}
            />
          </div>
        </div>
      </div>

      <div className="actions">
        <button onClick={loadDefaultConfig} disabled={isSimulating}>
          Load Dad's Original
        </button>
        <button onClick={loadOptimizedConfig} disabled={isSimulating}>
          Load Optimized
        </button>
        <button 
          onClick={runSimulation} 
          disabled={isSimulating}
          className="primary"
        >
          {isSimulating ? 'Running Simulation...' : 'Run Simulation'}
        </button>
      </div>

      <div className="save-config">
        <input
          type="text"
          placeholder="Configuration name"
          value={configName}
          onChange={(e) => setConfigName(e.target.value)}
        />
        <button onClick={saveConfiguration} disabled={!configName}>
          Save Configuration
        </button>
      </div>

      {savedConfigs.length > 0 && (
        <div className="saved-configs">
          <h3>Saved Configurations</h3>
          {savedConfigs.map((config, index) => (
            <div key={index} className="saved-config-item">
              <span>{config.name}</span>
              <span className="timestamp">
                {new Date(config.timestamp).toLocaleDateString()}
              </span>
              <button onClick={() => loadConfiguration(config)}>Load</button>
              <button onClick={() => deleteConfiguration(index)}>Delete</button>
            </div>
          ))}
        </div>
      )}

      {results && (
        <div className="results">
          <h2>Simulation Results</h2>
          <div className="results-grid">
            <div className="result-item">
              <label>ROI</label>
              <span className={results.roi >= 0 ? 'positive' : 'negative'}>
                {(results.roi * 100).toFixed(2)}%
              </span>
            </div>
            <div className="result-item">
              <label>Win Rate</label>
              <span>{(results.win_rate * 100).toFixed(2)}%</span>
            </div>
            <div className="result-item">
              <label>Final Bankroll</label>
              <span>${results.final_bankroll.toFixed(2)}</span>
            </div>
            <div className="result-item">
              <label>Total Hands</label>
              <span>{results.total_hands.toLocaleString()}</span>
            </div>
            <div className="result-item">
              <label>Average Bet</label>
              <span>${results.avg_bet.toFixed(2)}</span>
            </div>
            <div className="result-item">
              <label>Total Wagered</label>
              <span>${results.total_wagered.toFixed(2)}</span>
            </div>
            <div className="result-item">
              <label>Net Win/Loss</label>
              <span className={results.total_won_lost >= 0 ? 'positive' : 'negative'}>
                ${results.total_won_lost.toFixed(2)}
              </span>
            </div>
            <div className="result-item">
              <label>Blackjacks</label>
              <span>{results.blackjacks}</span>
            </div>
          </div>

          {results.bet_distribution && (
            <div className="bet-distribution">
              <h3>Bet Distribution</h3>
              <div className="distribution-grid">
                {Object.entries(results.bet_distribution).map(([units, count]) => (
                  <div key={units} className="distribution-item">
                    <span>{units}x min bet:</span>
                    <span>{count} hands</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StrategyTester;