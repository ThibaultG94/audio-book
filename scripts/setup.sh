#!/bin/bash
# 🔧 Initial installation script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Audio Book App - Initial Setup${NC}"

# Check if we're in project root
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Please run from project root directory${NC}"
    exit 1
fi

# Backend setup
echo -e "\n${GREEN}🐍 Setting up Python backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create directories
mkdir -p storage/uploads storage/outputs
mkdir -p app/{api/routes,services,models,core,utils}
mkdir -p tests/{unit,integration}

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/routes/__init__.py
touch app/services/__init__.py
touch app/models/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

echo -e "${GREEN}✅ Backend setup complete${NC}"
cd ..

# Frontend setup
echo -e "\n${GREEN}⚛️  Setting up Next.js frontend...${NC}"
cd frontend

echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
npm install

# Remove test dependencies for now (avoid React 19 conflicts)
echo -e "${YELLOW}🧹 Cleaning up conflicting test dependencies...${NC}"
npm uninstall @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/jest jest jest-environment-jsdom 2>/dev/null || true

echo -e "${GREEN}✅ Frontend setup complete${NC}"
cd ..

# Create environment file
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}📝 Creating .env file...${NC}"
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# Development environment
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:8000

# TTS Configuration
VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
LENGTH_SCALE=1.0
NOISE_SCALE=0.667
SENTENCE_SILENCE=0.35
PAUSE_BETWEEN_BLOCKS=0.35

# File Processing
MAX_FILE_SIZE=52428800
MAX_CHUNK_CHARS=1500
EOF
fi

# Check Piper installation
echo -e "\n${BLUE}🔍 Checking Piper TTS installation...${NC}"
if command -v piper &> /dev/null; then
    echo -e "${GREEN}✅ Piper TTS found${NC}"
else
    echo -e "${YELLOW}⚠️  Piper TTS not found in PATH${NC}"
    echo -e "${YELLOW}   Install with:${NC}"
    echo -e "   wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
    echo -e "   tar -xzf piper_amd64.tar.gz"
    echo -e "   sudo mv piper /usr/local/bin/"
fi

echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Install Piper TTS (if not already done)"
echo -e "  2. Copy voice models to backend/voices/"
echo -e "  3. Run: ${YELLOW}./scripts/dev.sh${NC}"