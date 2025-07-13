#!/bin/bash

echo "🧪 Running Blackjack Simulator Integration Tests"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run a test suite
run_test_suite() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n📋 Running: $test_name"
    echo "-------------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name passed${NC}"
    else
        echo -e "${RED}❌ $test_name failed${NC}"
        exit 1
    fi
}

# Check if using devbox or direct
if command -v devbox &> /dev/null; then
    echo "Using devbox commands..."
    
    # Run different test suites
    run_test_suite "Basic Game Flow Tests" "devbox run test-quick"
    run_test_suite "All Integration Tests" "devbox run test"
    
    echo -e "\n📊 Generating Coverage Report..."
    devbox run test-coverage
else
    echo "Running tests directly with Docker..."
    
    # Build test image
    echo "Building test Docker image..."
    docker build -t blackjack-test -f backend/Dockerfile.test ./backend
    
    # Run tests
    run_test_suite "All Tests" "docker run --rm blackjack-test"
fi

echo -e "\n${GREEN}✅ All tests completed successfully!${NC}"
echo "=============================================="