#!/bin/bash
# 🔧 Fix missing imports and validate backend structure

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing Backend Import Issues${NC}"

# Ensure we're in project root
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo -e "${RED}❌ Please run from project root directory${NC}"
    exit 1
fi

cd backend

# Check if virtual environment exists and activate it
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install missing dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q fastapi uvicorn python-multipart pydantic-settings PyPDF2 ebooklib beautifulsoup4 lxml

# Create missing directories
echo -e "${YELLOW}📁 Creating missing directories...${NC}"
mkdir -p app/api/routes
mkdir -p app/services
mkdir -p app/models  
mkdir -p app/core
mkdir -p app/utils
mkdir -p storage/uploads
mkdir -p storage/outputs
mkdir -p tests/unit
mkdir -p tests/integration

# Create missing __init__.py files
echo -e "${YELLOW}📝 Creating __init__.py files...${NC}"
touch app/__init__.py
touch app/api/__init__.py
touch app/api/routes/__init__.py
touch app/services/__init__.py
touch app/models/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# Validate imports
echo -e "${BLUE}🔍 Validating imports...${NC}"
python -c "
try:
    from app.main import app
    print('✅ Main app imports successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test FastAPI app creation
echo -e "${BLUE}🧪 Testing FastAPI app creation...${NC}"
python -c "
try:
    from app.main import create_app
    app = create_app()
    print('✅ FastAPI app created successfully')
    print(f'   App title: {app.title}')
    print(f'   Routes: {len(app.routes)}')
except Exception as e:
    print(f'❌ App creation failed: {e}')
    exit(1)
"

# Check directory structure
echo -e "\n${BLUE}📁 Current directory structure:${NC}"
find app -name "*.py" | head -20

echo -e "\n${GREEN}✅ Backend import issues fixed!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Try running: ${YELLOW}make backend${NC}"
echo -e "  2. Check API docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "  3. Run tests: ${YELLOW}python -m pytest tests/${NC}"