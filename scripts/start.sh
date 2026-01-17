#!/bin/bash

echo "🚀 Starting Pesapal RDBMS Challenge..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python and Node are installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Setup virtual environment
echo -e "${BLUE}🔧 Setting up Python virtual environment...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Setup demo database
echo -e "${BLUE}📊 Setting up demo database...${NC}"
python ../scripts/setup_db.py

# Start backend in background
echo -e "${GREEN}🚀 Starting backend server...${NC}"
uvicorn src.api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}🚀 Starting frontend...${NC}"
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo -e "\n${YELLOW}✨ Pesapal RDBMS is running!${NC}"
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}🔧 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Handle Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID 2> /dev/null; echo -e "\n${RED}👋 Stopping services...${NC}"; exit' INT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID