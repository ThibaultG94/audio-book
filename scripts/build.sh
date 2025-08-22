#!/bin/bash
# 🏗️  Production build script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏗️  Building Audio Book App for Production${NC}"

# Ensure we're in project root
cd "$(dirname "$0")/.."

# Build frontend
echo -e "\n${GREEN}📦 Building frontend...${NC}"
cd frontend
npm ci --only=production
npm run build
cd ..

# Check backend
echo -e "\n${GREEN}🐍 Checking backend...${NC}"
cd backend
source venv/bin/activate
python -c "from app.main import app; print('✅ Backend imports OK')"
cd ..

# Create build directory
echo -e "\n${GREEN}📁 Creating production archive...${NC}"
mkdir -p build

# Create production tar
tar -czf build/audio-book-app.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='build' \
    --exclude='.next' \
    --exclude='storage' \
    .

echo -e "\n${GREEN}✅ Build completed: build/audio-book-app.tar.gz${NC}"