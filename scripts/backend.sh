#!/bin/bash
# 🐍 Backend script only

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🐍 Starting Backend Only${NC}"

cd backend

# Check venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate and start
source venv/bin/activate

echo -e "${BLUE}🔥 Starting FastAPI server...${NC}"
echo -e "   API: http://localhost:8000"
echo -e "   Docs: http://localhost:8000/docs"
echo -e "   Press Ctrl+C to stop"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload