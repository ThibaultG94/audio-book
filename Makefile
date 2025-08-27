# Makefile for quick commands
# Makefile
.PHONY: setup dev backend frontend build test clean help

help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup: ## Initial project setup
	@./scripts/setup.sh

dev: ## Start development servers (backend + frontend)
	@./scripts/dev.sh

backend: ## Start backend only
	@./scripts/backend.sh


frontend: ## Start frontend only  
	@./scripts/frontend.sh

build: ## Build for production
	@./scripts/build.sh

test: ## Run all tests
	@./scripts/test.sh

clean: ## Clean build artifacts
	@./scripts/clean.sh