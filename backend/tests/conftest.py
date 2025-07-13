import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def game_session(client):
    """Create a new game session and return session_id"""
    response = client.post("/api/game/new")
    assert response.status_code == 200
    return response.json()["session_id"]