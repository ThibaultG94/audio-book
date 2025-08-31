# Audio Book Converter - Makefile
# Fixed for /bin/sh compatibility (no bash-specific features)

.PHONY: help install dev backend frontend test clean docker-build docker-up fix-all

SHELL := /bin/bash

# Default target
help:
	@echo "📚 Audio Book Converter - Available Commands"
	@echo "============================================"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make backend      - Start backend only"
	@echo "  make frontend     - Start frontend only"
	@echo "  make fix-all      - Fix all known issues"
	@echo "  make test         - Run all tests"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make clean        - Clean cache and temp files"

# Complete fix for all issues
fix-all:
	@echo "🔧 Applying complete fixes..."
	@chmod +x scripts/fix-all-issues.sh
	@./scripts/fix-all-issues.sh

# Installation
install:
	@echo "📦 Installing dependencies..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "✅ Installation complete!"

# Backend with proper activation
backend:
	@echo "🐍 Starting Backend"
	@echo "🔥 Starting FastAPI server..."
	@echo "   API: http://localhost:8000"
	@echo "   Docs: http://localhost:8000/docs"
	@cd backend && . venv/bin/activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
frontend:
	@echo "⚛️  Starting Frontend"
	@cd frontend && npm run dev

# Combined dev
dev:
	@echo "🚀 Starting both servers..."
	@$(MAKE) -j2 backend frontend

# Testing
test-backend:
	@cd backend && . venv/bin/activate && pytest -v

test-frontend:
	@cd frontend && npm test

test: test-backend test-frontend

# Docker commands with latest secure images
docker-build:
	@echo "🐳 Building Docker images with secure versions..."
	@docker-compose -f docker/docker-compose.yml build

docker-up:
	@echo "🐳 Starting Docker containers..."
	@docker-compose -f docker/docker-compose.yml up -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	@docker-compose -f docker/docker-compose.yml down

# Utility commands
check-backend:
	@echo "🔍 Checking backend..."
	@cd backend && . venv/bin/activate && python -c "import fitz; print('✅ PyMuPDF OK')" 2>/dev/null || echo "❌ PyMuPDF not installed"
	@which piper > /dev/null 2>&1 && echo "✅ Piper binary found" || echo "❌ Piper binary not found"

check-deps:
	@echo "📋 Checking dependencies..."
	@cd backend && . venv/bin/activate && pip list | grep -E "fastapi|uvicorn|PyMuPDF|PyPDF2" || true

# Cleaning
clean:
	@echo "🧹 Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.coverage backend/htmlcov
	@rm -rf frontend/.next frontend/node_modules/.cache
	@echo "✅ Clean complete!"

# Quick server test
test-server:
	@curl -s http://localhost:8000/health 2>/dev/null && echo "✅ Backend is running" || echo "❌ Backend is not running"
	@curl -s http://localhost:3000 2>/dev/null && echo "✅ Frontend is running" || echo "❌ Frontend is not running"