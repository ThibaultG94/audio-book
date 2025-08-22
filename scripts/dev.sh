#!/bin/bash
# 🚀 Development script - Start backend + frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Audio Book App Development Environment${NC}"

# Check if we're in project root
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Please run from project root directory${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping development servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Trap interrupt signals
trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "${GREEN}🐍 Starting Python backend...${NC}"
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    touch .deps_installed
fi

# Create storage directories
mkdir -p storage/uploads storage/outputs

# Check if Piper is available
if ! command -v piper &> /dev/null; then
    echo -e "${YELLOW}⚠️  Piper TTS not found in PATH${NC}"
    echo -e "${YELLOW}   You may need to install it manually${NC}"
fi

# Start backend server
echo -e "${GREEN}🔥 Starting FastAPI server on http://localhost:8000${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ..

# Start Frontend
echo -e "${GREEN}⚛️  Starting Next.js frontend...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Start frontend server
echo -e "${GREEN}🔥 Starting Next.js server on http://localhost:3000${NC}"
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev &
FRONTEND_PID=$!

cd ..

# Show status
echo -e "\n${GREEN}✅ Development servers started successfully!${NC}"
echo -e "${BLUE}📍 Services:${NC}"
echo -e "   Backend API:  http://localhost:8000"
echo -e "   Frontend:     http://localhost:3000"
echo -e "   API Docs:     http://localhost:8000/docs"
echo -e "\n${YELLOW}💡 Press Ctrl+C to stop all servers${NC}"

# Wait for interrupt
wait