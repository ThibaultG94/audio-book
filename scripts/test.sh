#!/bin/bash
# 🧪 Test script

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Running Tests${NC}"

# Backend tests
echo -e "\n${GREEN}🐍 Backend tests...${NC}"
cd backend
source venv/bin/activate

if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    python -m pytest tests/ -v
else
    echo -e "${GREEN}✅ No backend tests found (yet)${NC}"
fi

cd ..

# Frontend tests (if configured)
echo -e "\n${GREEN}⚛️  Frontend tests...${NC}"
cd frontend

if [ -f "jest.config.js" ] && [ -d "src/__tests__" ]; then
    npm test -- --passWithNoTests
else
    echo -e "${GREEN}✅ No frontend tests configured${NC}"
fi

cd ..

echo -e "\n${GREEN}✅ All tests completed${NC}"