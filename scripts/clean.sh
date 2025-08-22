#!/bin/bash
# 🧹 Cleanup script

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}🧹 Cleaning build artifacts...${NC}"

# Clean backend
echo "🐍 Cleaning backend..."
find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find backend -name "*.pyc" -delete 2>/dev/null || true
find backend -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf backend/.deps_installed

# Clean frontend
echo "⚛️  Cleaning frontend..."
rm -rf frontend/.next/
rm -rf frontend/out/
rm -rf frontend/node_modules/.cache/

# Clean build
echo "📦 Cleaning build..."
rm -rf build/

# Clean storage (optionally)
read -p "🗑️  Clean storage files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf backend/storage/uploads/*
    rm -rf backend/storage/outputs/*
    echo "✅ Storage cleaned"
fi

echo -e "${GREEN}✅ Cleanup completed${NC}"