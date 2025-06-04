# Temporal LLM Web App Makefile
# Provides convenient commands for development and deployment

.PHONY: help start stop restart logs build test setup health cleanup clean lint format

# Default target
.DEFAULT_GOAL := help

# Application name and version
APP_NAME := temporal-llm-web-app
VERSION := 1.0.0

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)$(APP_NAME) v$(VERSION)$(NC)"
	@echo "Available commands:"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

start: ## Start all services
	@echo "$(BLUE)Starting all services...$(NC)"
	@./scripts/start.sh start

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@./scripts/start.sh stop

restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	@./scripts/start.sh restart

logs: ## Show logs (use 'make logs SERVICE=web-app' for specific service)
	@echo "$(BLUE)Showing logs...$(NC)"
	@if [ -n "$(SERVICE)" ]; then \
		./scripts/start.sh logs $(SERVICE); \
	else \
		./scripts/start.sh logs; \
	fi

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@./scripts/start.sh build

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@./scripts/start.sh test

setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@./scripts/start.sh setup

health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@./scripts/start.sh health

cleanup: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	@./scripts/start.sh cleanup

# Development commands
dev-install: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@python -m venv .venv
	@. .venv/bin/activate && pip install -r backend/requirements.txt
	@echo "$(GREEN)✅ Development dependencies installed$(NC)"

dev-web: ## Run web app in development mode
	@echo "$(BLUE)Starting web app in development mode...$(NC)"
	@cd backend && python main.py

dev-worker: ## Run worker in development mode
	@echo "$(BLUE)Starting worker in development mode...$(NC)"
	@cd backend && python worker.py

lint: ## Run code linting
	@echo "$(BLUE)Running code linting...$(NC)"
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && \
		python -m flake8 backend/ --max-line-length=100 --ignore=E203,W503; \
	else \
		echo "$(YELLOW)Virtual environment not found. Run 'make dev-install' first.$(NC)"; \
	fi

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	@if [ -d ".venv" ]; then \
		. .venv/bin/activate && \
		python -m black backend/ --line-length=100; \
	else \
		echo "$(YELLOW)Virtual environment not found. Run 'make dev-install' first.$(NC)"; \
	fi

clean: ## Clean Python cache and temporary files
	@echo "$(YELLOW)Cleaning Python cache and temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

# Docker commands
docker-build: ## Build Docker images only
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build

docker-pull: ## Pull latest Docker images
	@echo "$(BLUE)Pulling latest Docker images...$(NC)"
	@docker-compose pull

docker-ps: ## Show running containers
	@echo "$(BLUE)Running containers:$(NC)"
	@docker-compose ps

docker-exec-web: ## Execute shell in web container
	@echo "$(BLUE)Connecting to web container...$(NC)"
	@docker-compose exec web-app bash

docker-exec-worker: ## Execute shell in worker container
	@echo "$(BLUE)Connecting to worker container...$(NC)"
	@docker-compose exec worker bash

# Testing commands
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@cd backend && python -m pytest test_workflows.py -v

test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(NC)"
	@cd backend && python -m pytest test_api.py -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@cd backend && python -m pytest --cov=. --cov-report=html --cov-report=term

# Environment commands
env-check: ## Check environment configuration
	@echo "$(BLUE)Checking environment configuration...$(NC)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ .env file exists$(NC)"; \
		if grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then \
			echo "$(YELLOW)⚠️  Please set your OpenAI API key in .env file$(NC)"; \
		else \
			echo "$(GREEN)✅ OpenAI API key is configured$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)⚠️  .env file not found. Copying from env.example...$(NC)"; \
		cp env.example .env; \
		echo "$(YELLOW)Please edit .env file with your configuration$(NC)"; \
	fi

# Database commands
db-reset: ## Reset Temporal database
	@echo "$(YELLOW)Resetting Temporal database...$(NC)"
	@docker-compose down postgresql
	@docker volume rm $$(docker volume ls -q | grep postgres) 2>/dev/null || true
	@docker-compose up -d postgresql
	@echo "$(GREEN)✅ Database reset completed$(NC)"

# Production commands
prod-deploy: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production deployment completed$(NC)"

# Monitoring commands
monitor: ## Show system resource usage
	@echo "$(BLUE)System resource usage:$(NC)"
	@docker stats --no-stream $$(docker-compose ps -q)

# Quick start command for new developers
quick-start: env-check setup start ## Quick start for new developers
	@echo "$(GREEN)🚀 Quick start completed!$(NC)"
	@echo "$(BLUE)Access the application at:$(NC)"
	@echo "  🌐 Web App: http://localhost:8001"
	@echo "  📊 Temporal UI: http://localhost:8080"
	@echo "  📚 API Docs: http://localhost:8001/docs"

# Examples in help
examples: ## Show usage examples
	@echo "$(BLUE)Usage Examples:$(NC)"
	@echo
	@echo "  $(GREEN)make quick-start$(NC)     # Complete setup for new developers"
	@echo "  $(GREEN)make start$(NC)           # Start all services"
	@echo "  $(GREEN)make logs SERVICE=web-app$(NC)  # Show web app logs"
	@echo "  $(GREEN)make test$(NC)            # Run all tests"
	@echo "  $(GREEN)make health$(NC)          # Check service health"
	@echo "  $(GREEN)make cleanup$(NC)         # Clean up all Docker resources"
	@echo

# Add any other necessary targets here
# ... 