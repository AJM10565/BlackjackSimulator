#!/bin/bash

echo "🎰 Starting Blackjack Simulator..."
echo ""
echo "Starting backend server..."
cd backend/src
python3 api.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting frontend server..."
cd ../../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Blackjack Simulator is running!"
echo "🌐 Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait