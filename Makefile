# Makefile for AudioBook Converter
# Commands for development, testing, and deployment

.PHONY: help install dev backend frontend test clean docker deploy

# Variables
PYTHON := python3
PIP := pip
NPM := npm
DOCKER := docker
BACKEND_PORT := 8001
FRONTEND_PORT := 3001

# Default target
help:
	@echo "📚 AudioBook Converter - Available Commands"
	@echo "==========================================="
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development servers"
	@echo "  make backend    - Start backend only"
	@echo "  make frontend   - Start frontend only"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean temporary files"
	@echo "  make docker     - Build Docker image"
	@echo "  make deploy     - Deploy to CapRover"
	@echo ""

# Install all dependencies
install:
	@echo "📦 Installing dependencies..."
	# Backend
	cd backend && \
		$(PYTHON) -m venv venv && \
		. venv/bin/activate && \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r requirements.txt && \
		$(PIP) install -r requirements-dev.txt
	# Frontend
	cd frontend && $(NPM) install
	@echo "✅ Dependencies installed"

# Start development environment
dev:
	@echo "🚀 Starting development servers..."
	@bash development.sh

# Start backend server only
backend:
	@echo "🐍 Starting backend server..."
	cd backend && \
		. venv/bin/activate && \
		$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

# Start frontend server only
frontend:
	@echo "⚛️  Starting frontend server..."
	cd frontend && $(NPM) run dev -- --port $(FRONTEND_PORT)

# Run all tests
test: test-backend test-frontend

# Run backend tests
test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && \
		. venv/bin/activate && \
		pytest -v --cov=app tests/

# Run frontend tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && $(NPM) test

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	# Python
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	# Node
	rm -rf frontend/.next
	rm -rf frontend/out
	# Storage
	rm -rf backend/storage/temp/*
	@echo "✅ Cleaned"

# Build Docker image
docker:
	@echo "🐳 Building Docker image..."
	$(DOCKER) build -t audiobook-converter:latest .
	@echo "✅ Docker image built"

# Deploy to CapRover
deploy:
	@echo "🚢 Deploying to CapRover..."
	tar -czf deploy.tar.gz \
		captain-definition \
		Dockerfile \
		backend/ \
		frontend/ \
		deployment/
	@echo "📦 Deployment package created: deploy.tar.gz"
	@echo "Upload this file to CapRover to deploy"

# Development with live reload
watch:
	@echo "👀 Starting development with live reload..."
	# Start both servers in parallel with live reload
	make -j2 watch-backend watch-frontend

watch-backend:
	cd backend && \
		. venv/bin/activate && \
		watchmedo auto-restart \
			--directory=./app \
			--pattern="*.py" \
			--recursive \
			-- python -m uvicorn app.main:app --host 0.0.0.0 --port $(BACKEND_PORT)

watch-frontend:
	cd frontend && $(NPM) run dev -- --port $(FRONTEND_PORT)

# Format code
format:
	@echo "✨ Formatting code..."
	# Python
	cd backend && \
		. venv/bin/activate && \
		black app/ && \
		isort app/
	# JavaScript/TypeScript
	cd frontend && $(NPM) run format
	@echo "✅ Code formatted"

# Lint code
lint:
	@echo "🔍 Linting code..."
	# Python
	cd backend && \
		. venv/bin/activate && \
		flake8 app/ && \
		mypy app/
	# JavaScript/TypeScript
	cd frontend && $(NPM) run lint
	@echo "✅ Code linted"

# Check voice models
check-voices:
	@echo "🎤 Checking voice models..."
	@ls -la backend/voices/ 2>/dev/null || echo "No voices directory found"
	@find backend/voices -name "*.onnx" 2>/dev/null | wc -l | xargs echo "Voice models found:"

# Download recommended voices
download-voices:
	@echo "📥 Downloading recommended French voices..."
	@bash scripts/download-voices.sh

# Initialize project
init: install download-voices
	@echo "🎉 Project initialized and ready!"
	@echo "Run 'make dev' to start development servers"