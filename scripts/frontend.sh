#!/bin/bash
# ⚛️  Frontend script only

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}⚛️  Starting Frontend Only${NC}"

cd frontend

# Install deps if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

echo -e "${BLUE}🔥 Starting Next.js server...${NC}"
echo -e "   Frontend: http://localhost:3000"
echo -e "   Press Ctrl+C to stop"

NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev