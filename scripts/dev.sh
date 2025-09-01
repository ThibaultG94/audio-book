#!/bin/bash
# 🚀 Development script - Start backend + frontend (Enhanced Voice Edition)

set -e

echo "🚀 Starting AudioBook Converter Development Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}🐍 Starting Backend Server...${NC}"
    cd backend
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Create necessary directories
    mkdir -p storage/{uploads,outputs,temp}
    mkdir -p voices
    
    # Start FastAPI server
    echo -e "${GREEN}✅ Backend starting on http://localhost:8001${NC}"
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting Frontend Server...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    # Create .env.local if not exists
    if [ ! -f ".env.local" ]; then
        echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
    fi
    
    # Start Next.js server
    echo -e "${GREEN}✅ Frontend starting on http://localhost:3001${NC}"
    npm run dev -- --port 3001 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend.pid
    
    cd ..
}

# Function to stop servers
stop_servers() {
    echo -e "${YELLOW}Stopping servers...${NC}"
    
    # Stop backend
    if [ -f "backend/.backend.pid" ]; then
        kill $(cat backend/.backend.pid) 2>/dev/null || true
        rm backend/.backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend/.frontend.pid" ]; then
        kill $(cat frontend/.frontend.pid) 2>/dev/null || true
        rm frontend/.frontend.pid
    fi
    
    echo -e "${GREEN}✅ Servers stopped${NC}"
}

# Trap for cleanup on exit
trap stop_servers EXIT

# Start servers
start_backend
sleep 5 # Wait for backend to initialize

start_frontend
sleep 3 # Wait for frontend to initialize

echo -e "${GREEN}🎉 Development environment ready!${NC}"
echo -e "${BLUE}📚 Backend API: http://localhost:8001${NC}"
echo -e "${BLUE}🎨 Frontend App: http://localhost:3001${NC}"
echo -e "${BLUE}📖 API Docs: http://localhost:8001/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for user interrupt
while true; do
    sleep 1
done