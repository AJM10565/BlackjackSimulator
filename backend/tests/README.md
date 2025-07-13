# Blackjack Simulator Integration Tests

This directory contains integration tests for the Blackjack Simulator API.

## Test Structure

- `test_sanity.py` - Basic tests to verify setup is working
- `test_game_flow.py` - Tests for basic game flows (betting, hitting, standing, etc.)
- `test_strategy_api.py` - Tests for strategy simulation endpoints
- `test_end_to_end.py` - Complete user journey tests

## Running Tests

### Using Devbox (Recommended)

```bash
# Run all tests
devbox run test

# Run only game flow tests (quick)
devbox run test-quick

# Run with coverage report
devbox run test-coverage
```

### Using the test runner script

```bash
./run_tests.sh
```

### Using Docker directly

```bash
# Build test image
docker build -t blackjack-test -f backend/Dockerfile.test ./backend

# Run all tests
docker run --rm blackjack-test

# Run specific test file
docker run --rm blackjack-test python -m pytest tests/test_game_flow.py -v
```

### Running locally (requires Python environment)

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Test Coverage

The tests cover:

1. **Basic Game Flow**
   - Creating new games
   - Placing bets
   - Player actions (hit, stand, double, split)
   - Getting results
   - Starting new rounds

2. **Strategy Simulation**
   - Loading default/optimized configurations
   - Running simulations with custom parameters
   - Handling edge cases

3. **End-to-End Scenarios**
   - Casual player sessions
   - Strategy tester journey
   - Multiple concurrent sessions
   - Error recovery

## Writing New Tests

Tests use pytest and FastAPI's TestClient. Example:

```python
def test_new_feature(client):
    """Test description"""
    response = client.post("/api/endpoint", json={"data": "value"})
    assert response.status_code == 200
    assert response.json()["field"] == "expected"
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    docker build -t blackjack-test -f backend/Dockerfile.test ./backend
    docker run --rm blackjack-test
```