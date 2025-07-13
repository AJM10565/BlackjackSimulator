"""End-to-end integration tests simulating real user flows"""
import pytest
import time


class TestPlayerJourney:
    """Test complete player journeys"""
    
    def test_casual_player_session(self, client):
        """Test a casual player playing a few hands"""
        # Create new game
        response = client.post("/api/game/new")
        session_id = response.json()["session_id"]
        initial_bankroll = response.json()["game_state"]["player_bankroll"]
        
        # Play 3 hands
        for i in range(3):
            # Place bet
            bet_response = client.post(
                f"/api/game/{session_id}/bet",
                json={"amount": 25}
            )
            assert bet_response.status_code == 200
            
            # Get game state to make decision
            state = bet_response.json()
            player_value = state["player_hands"][0]["value"]
            
            # Simple decision logic
            if player_value < 17:
                # Hit if under 17
                action_response = client.post(
                    f"/api/game/{session_id}/action",
                    json={"action": "hit"}
                )
                
                # Check if we busted
                new_state = action_response.json()
                if not new_state["player_hands"][0]["is_bust"]:
                    # Stand if we didn't bust
                    client.post(
                        f"/api/game/{session_id}/action",
                        json={"action": "stand"}
                    )
            else:
                # Stand if 17 or higher
                client.post(
                    f"/api/game/{session_id}/action",
                    json={"action": "stand"}
                )
            
            # Get results
            results_response = client.get(f"/api/game/{session_id}/results")
            assert results_response.status_code == 200
            
            # Start new round if not the last hand
            if i < 2:
                new_round_response = client.post(f"/api/game/{session_id}/new-round")
                assert new_round_response.status_code == 200
        
        # Verify we played 3 hands
        history_response = client.get(f"/api/game/{session_id}/history")
        history = history_response.json()["history"]
        
        # Count bet actions (one per hand)
        bet_actions = [h for h in history if h["action"] == "bet"]
        assert len(bet_actions) == 3
    
    def test_strategy_tester_journey(self, client):
        """Test a user testing their custom strategy"""
        # 1. Get default configuration
        config_response = client.get("/api/strategy/default-config")
        default_config = config_response.json()
        
        # 2. Modify some values
        custom_config = {
            "card_values": default_config["card_values"],
            "ace_adjustment": 5,  # Increase ace adjustment
            "bet_threshold": 4,   # Lower threshold
            "bet_increment": 5,
            "max_bet_units": 20,
            "num_hands": 50,  # Quick test
            "starting_bankroll": 1000,
            "min_bet": 10,
            "num_decks": 6,
            "penetration": 72
        }
        
        # 3. Run simulation
        sim_response = client.post("/api/strategy/simulate", json=custom_config)
        assert sim_response.status_code == 200
        
        result = sim_response.json()
        
        # 4. Verify results make sense
        assert result["total_hands"] > 0
        assert result["total_hands"] <= 50
        assert "roi" in result
        assert "win_rate" in result
        assert "bet_distribution" in result
        
        # 5. Compare with optimized strategy
        optimized_response = client.get("/api/strategy/optimized-config")
        optimized_config = optimized_response.json()
        
        # Run optimized simulation
        optimized_sim = {
            **custom_config,
            "card_values": optimized_config["card_values"],
            "ace_adjustment": optimized_config["ace_adjustment"],
            "bet_threshold": optimized_config["bet_threshold"]
        }
        
        opt_sim_response = client.post("/api/strategy/simulate", json=optimized_sim)
        assert opt_sim_response.status_code == 200
        
        # Both simulations should complete
        opt_result = opt_sim_response.json()
        assert opt_result["total_hands"] > 0
    
    def test_high_roller_session(self, client):
        """Test a high roller with large bets"""
        # Create game
        response = client.post("/api/game/new")
        session_id = response.json()["session_id"]
        
        # Try to place maximum bet
        bet_response = client.post(
            f"/api/game/{session_id}/bet",
            json={"amount": 500}  # Large bet
        )
        assert bet_response.status_code == 200
        
        # Play conservatively - always stand
        stand_response = client.post(
            f"/api/game/{session_id}/action",
            json={"action": "stand"}
        )
        assert stand_response.status_code == 200
        
        # Check bankroll change
        results = client.get(f"/api/game/{session_id}/results")
        result_data = results.json()["results"][0]
        
        # Verify bet amount was correct
        state = client.get(f"/api/game/{session_id}/state")
        final_bankroll = state.json()["player_bankroll"]
        
        # Bankroll should have changed by the net amount
        assert final_bankroll == 1000 + result_data["net"]


class TestConcurrentSessions:
    """Test multiple concurrent game sessions"""
    
    def test_multiple_sessions(self, client):
        """Test that multiple sessions don't interfere with each other"""
        # Create two sessions
        session1_response = client.post("/api/game/new")
        session1 = session1_response.json()["session_id"]
        
        session2_response = client.post("/api/game/new")
        session2 = session2_response.json()["session_id"]
        
        # Place different bets in each
        client.post(f"/api/game/{session1}/bet", json={"amount": 10})
        client.post(f"/api/game/{session2}/bet", json={"amount": 50})
        
        # Verify bets are independent
        state1 = client.get(f"/api/game/{session1}/state").json()
        state2 = client.get(f"/api/game/{session2}/state").json()
        
        assert state1["player_hands"][0]["bet"] == 10
        assert state2["player_hands"][0]["bet"] == 50
        
        # Play different actions
        client.post(f"/api/game/{session1}/action", json={"action": "hit"})
        client.post(f"/api/game/{session2}/action", json={"action": "stand"})
        
        # Verify states are different
        state1_after = client.get(f"/api/game/{session1}/state").json()
        state2_after = client.get(f"/api/game/{session2}/state").json()
        
        # Session 1 should have more cards (from hitting)
        assert len(state1_after["player_hands"][0]["cards"]) > 2
        # Session 2 should still have 2 cards (just stood)
        assert len(state2_after["player_hands"][0]["cards"]) == 2


class TestErrorRecovery:
    """Test error handling and recovery"""
    
    def test_invalid_session_recovery(self, client):
        """Test handling of invalid session IDs"""
        # Try to access non-existent session
        response = client.get("/api/game/invalid-session-id/state")
        assert response.status_code == 404
        
        # Create a valid session
        new_game = client.post("/api/game/new")
        assert new_game.status_code == 200
        
        # Verify we can still play normally
        session_id = new_game.json()["session_id"]
        bet_response = client.post(
            f"/api/game/{session_id}/bet",
            json={"amount": 25}
        )
        assert bet_response.status_code == 200
    
    def test_simulation_with_extreme_parameters(self, client):
        """Test simulation API with edge case parameters"""
        # Very aggressive strategy
        response = client.post("/api/strategy/simulate", json={
            "card_values": {
                "2": 10, "3": 10, "4": 10, "5": 10,
                "6": 10, "7": 0, "8": -10, "9": -10,
                "10": -10, "J": -10, "Q": -10, "K": -10, "A": -10
            },
            "ace_adjustment": 20,
            "bet_threshold": 1,
            "bet_increment": 10,
            "max_bet_units": 100,
            "num_hands": 10,
            "starting_bankroll": 100,
            "min_bet": 1,
            "num_decks": 6,
            "penetration": 90
        })
        
        # Should still work, even with extreme values
        assert response.status_code == 200
        result = response.json()
        assert "roi" in result