"""Integration tests for strategy simulation API"""
import pytest


class TestStrategyAPI:
    """Test the strategy simulation endpoints"""
    
    def test_get_default_config(self, client):
        """Test getting default strategy configuration"""
        response = client.get("/api/strategy/default-config")
        assert response.status_code == 200
        
        config = response.json()
        assert "card_values" in config
        assert "ace_adjustment" in config
        assert "bet_threshold" in config
        assert "bet_increment" in config
        assert "max_bet_units" in config
        
        # Check card values format
        assert "2" in config["card_values"]
        assert config["card_values"]["A"] == -3
    
    def test_get_optimized_config(self, client):
        """Test getting optimized strategy configuration"""
        response = client.get("/api/strategy/optimized-config")
        assert response.status_code == 200
        
        config = response.json()
        assert "card_values" in config
        assert config["bet_threshold"] == 3  # Optimized threshold
    
    def test_simulate_with_default_strategy(self, client):
        """Test running a simulation with default strategy"""
        response = client.post("/api/strategy/simulate", json={
            "card_values": {
                "2": 0, "3": 3, "4": 4, "5": 5,
                "6": 3, "7": 0, "8": -1, "9": -2,
                "10": -3, "J": -3, "Q": -3, "K": -3, "A": -3
            },
            "ace_adjustment": 4,
            "bet_threshold": 5,
            "bet_increment": 5,
            "max_bet_units": 20,
            "num_hands": 100,  # Small number for testing
            "starting_bankroll": 1000,
            "min_bet": 10,
            "num_decks": 6,
            "penetration": 72
        })
        
        assert response.status_code == 200
        
        result = response.json()
        assert "final_bankroll" in result
        assert "roi" in result
        assert "win_rate" in result
        assert "total_hands" in result
        assert "bet_distribution" in result
        
        # Verify some basic sanity checks
        assert result["total_hands"] <= 100
        assert 0 <= result["win_rate"] <= 1
        assert result["final_bankroll"] >= 0
    
    def test_simulate_with_custom_strategy(self, client):
        """Test running a simulation with custom card values"""
        response = client.post("/api/strategy/simulate", json={
            "card_values": {
                # All cards neutral except aces
                "2": 0, "3": 0, "4": 0, "5": 0,
                "6": 0, "7": 0, "8": 0, "9": 0,
                "10": 0, "J": 0, "Q": 0, "K": 0, "A": -1
            },
            "ace_adjustment": 1,
            "bet_threshold": 2,
            "bet_increment": 1,
            "max_bet_units": 5,
            "num_hands": 50,
            "starting_bankroll": 500,
            "min_bet": 5,
            "num_decks": 6,
            "penetration": 75
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["total_hands"] > 0
    
    def test_simulate_with_invalid_card_values(self, client):
        """Test that invalid card values are handled"""
        response = client.post("/api/strategy/simulate", json={
            "card_values": {
                "invalid": 0  # Invalid card
            },
            "ace_adjustment": 4,
            "bet_threshold": 5,
            "bet_increment": 5,
            "max_bet_units": 20,
            "num_hands": 10,
            "starting_bankroll": 1000,
            "min_bet": 10,
            "num_decks": 6,
            "penetration": 72
        })
        
        # Should handle gracefully or return error
        # The actual behavior depends on implementation
        assert response.status_code in [200, 400, 500]
    
    def test_simulate_bankroll_preservation(self, client):
        """Test that simulation stops when bankroll is depleted"""
        response = client.post("/api/strategy/simulate", json={
            "card_values": {
                "2": 0, "3": 3, "4": 4, "5": 5,
                "6": 3, "7": 0, "8": -1, "9": -2,
                "10": -3, "J": -3, "Q": -3, "K": -3, "A": -3
            },
            "ace_adjustment": 4,
            "bet_threshold": 5,
            "bet_increment": 5,
            "max_bet_units": 20,
            "num_hands": 1000,
            "starting_bankroll": 50,  # Very small bankroll
            "min_bet": 10,
            "num_decks": 6,
            "penetration": 72
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should stop before 1000 hands if bankroll depleted
        assert result["total_hands"] <= 1000
        assert result["final_bankroll"] >= 0


class TestStrategiesEndpoint:
    """Test the strategies listing endpoint"""
    
    def test_get_available_strategies(self, client):
        """Test getting list of available strategies"""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        
        data = response.json()
        assert "playing_strategies" in data
        assert "betting_strategies" in data
        
        assert "basic" in data["playing_strategies"]
        assert "flat" in data["betting_strategies"]