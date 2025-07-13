"""Integration tests for basic game flows"""
import pytest


class TestBasicGameFlow:
    """Test the basic flow of playing a game"""
    
    def test_new_game_creation(self, client):
        """Test creating a new game session"""
        response = client.post("/api/game/new")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "game_state" in data
        
        game_state = data["game_state"]
        assert game_state["state"] == "betting"
        assert game_state["player_bankroll"] == 1000
        assert len(game_state["player_hands"]) == 0
    
    def test_place_bet_and_deal(self, client, game_session):
        """Test placing a bet and getting initial cards"""
        # Place a bet
        response = client.post(
            f"/api/game/{game_session}/bet",
            json={"amount": 25}
        )
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["state"] == "player_turn"
        assert len(game_state["player_hands"]) == 1
        assert game_state["player_hands"][0]["bet"] == 25
        assert len(game_state["player_hands"][0]["cards"]) == 2
        assert len(game_state["dealer_hand"]["cards"]) == 2
    
    def test_invalid_bet_amount(self, client, game_session):
        """Test placing an invalid bet amount"""
        # Try to bet more than bankroll
        response = client.post(
            f"/api/game/{game_session}/bet",
            json={"amount": 2000}
        )
        assert response.status_code == 400
    
    def test_hit_action(self, client, game_session):
        """Test hitting during player turn"""
        # Place bet first
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        # Hit
        response = client.post(
            f"/api/game/{game_session}/action",
            json={"action": "hit"}
        )
        assert response.status_code == 200
        
        game_state = response.json()
        # Player should have at least 3 cards after hitting
        assert len(game_state["player_hands"][0]["cards"]) >= 3
    
    def test_stand_action(self, client, game_session):
        """Test standing during player turn"""
        # Place bet first
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        # Stand
        response = client.post(
            f"/api/game/{game_session}/action",
            json={"action": "stand"}
        )
        assert response.status_code == 200
        
        game_state = response.json()
        # Game should move to dealer turn or round over
        assert game_state["state"] in ["dealer_turn", "round_over"]
    
    def test_double_down(self, client, game_session):
        """Test doubling down"""
        # Place bet first
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        # Get current state to check if double is valid
        state_response = client.get(f"/api/game/{game_session}/state")
        valid_actions = state_response.json()["valid_actions"]
        
        if "double" in valid_actions:
            # Double down
            response = client.post(
                f"/api/game/{game_session}/action",
                json={"action": "double"}
            )
            assert response.status_code == 200
            
            game_state = response.json()
            # Player should have exactly 3 cards after double
            assert len(game_state["player_hands"][0]["cards"]) == 3
            # Bet should be doubled
            assert game_state["player_hands"][0]["bet"] == 50
    
    def test_complete_round(self, client, game_session):
        """Test playing a complete round"""
        # Place bet
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        # Stand
        client.post(f"/api/game/{game_session}/action", json={"action": "stand"})
        
        # Get results
        response = client.get(f"/api/game/{game_session}/results")
        assert response.status_code == 200
        
        results = response.json()["results"]
        assert len(results) > 0
        assert "result" in results[0]
        assert "net" in results[0]
        assert results[0]["result"] in ["win", "lose", "push", "blackjack", "bust"]
    
    def test_start_new_round(self, client, game_session):
        """Test starting a new round after completing one"""
        # Play a round
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        client.post(f"/api/game/{game_session}/action", json={"action": "stand"})
        
        # Start new round
        response = client.post(f"/api/game/{game_session}/new-round")
        assert response.status_code == 200
        
        data = response.json()
        assert "previous_results" in data
        assert data["game_state"]["state"] == "betting"


class TestSplitFlow:
    """Test splitting pairs"""
    
    def test_split_not_allowed_for_non_pair(self, client, game_session):
        """Test that split is not allowed for non-pairs"""
        # This is hard to test without controlling the deck
        # In a real test, we'd mock the deck to ensure we get a non-pair
        pass


class TestInvalidActions:
    """Test invalid action sequences"""
    
    def test_action_before_bet(self, client, game_session):
        """Test that actions are not allowed before betting"""
        response = client.post(
            f"/api/game/{game_session}/action",
            json={"action": "hit"}
        )
        assert response.status_code == 400
    
    def test_bet_during_player_turn(self, client, game_session):
        """Test that betting is not allowed during player turn"""
        # Place initial bet
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        # Try to bet again
        response = client.post(
            f"/api/game/{game_session}/bet",
            json={"amount": 25}
        )
        assert response.status_code == 400
    
    def test_invalid_action_type(self, client, game_session):
        """Test sending an invalid action type"""
        client.post(f"/api/game/{game_session}/bet", json={"amount": 25})
        
        response = client.post(
            f"/api/game/{game_session}/action",
            json={"action": "invalid_action"}
        )
        assert response.status_code == 400