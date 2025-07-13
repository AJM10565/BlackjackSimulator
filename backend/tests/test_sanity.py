"""Basic sanity tests to verify test setup"""
import pytest


def test_imports():
    """Test that all main modules can be imported"""
    import api
    import game
    import deck
    import card
    import hand
    import strategy
    assert True


def test_api_root(client):
    """Test that API root endpoint works"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Blackjack Simulator API"}


def test_fastapi_client(client):
    """Test that test client is working"""
    assert client is not None