# Blackjack Simulator

A comprehensive blackjack simulator with manual play, computer strategies, and reinforcement learning for betting optimization.

## Features

- 🎮 **Manual Play Mode**: Play blackjack with a clean web interface
- 🤖 **Computer Players**: Configurable strategies including basic strategy
- 📊 **Card Counting**: Track running and true count with Hi-Lo system
- 🧠 **Reinforcement Learning**: Train AI to find optimal betting strategies
- 📈 **Statistics Tracking**: Analyze performance over thousands of hands
- ⚙️ **Configurable Rules**: Multiple decks, shuffle thresholds, betting limits

## Quick Start with Devbox

1. Install [Devbox](https://www.jetpack.io/devbox/docs/installing_devbox/)

2. Clone the repository and enter the project:
   ```bash
   git clone <repository-url>
   cd BlackjackSimulator
   ```

3. Start the development environment:
   ```bash
   devbox shell
   ```

4. Install all dependencies:
   ```bash
   devbox run setup
   ```

5. Start both backend and frontend:
   ```bash
   devbox run start
   ```

6. Open your browser to http://localhost:3000

## Available Commands

Inside the Devbox shell:

- `devbox run setup` - Install all dependencies
- `devbox run start` - Start both backend and frontend servers
- `devbox run backend` - Start only the backend API server
- `devbox run frontend` - Start only the frontend dev server
- `devbox run test` - Run the test suite
- `devbox run lint` - Run linters
- `devbox run format` - Format code

## Manual Setup (without Devbox)

### Backend
```bash
cd backend
pip install -r requirements.txt
cd src
python api.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Architecture

- **Backend**: Python FastAPI with game logic and RL training
- **Frontend**: React with Tailwind CSS for responsive UI
- **API**: RESTful endpoints for game sessions and actions

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines and architecture notes.