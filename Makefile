# Makefile for SmileAdventure Development
# Provides convenient commands for development, testing, and deployment

# Default shell
SHELL := /bin/bash

# Project settings
PROJECT_NAME := smileadventure
COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Help target - shows available commands
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)SmileAdventure Development Commands$(NC)"
	@echo "=================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# =============================================================================
# SETUP COMMANDS
# =============================================================================

.PHONY: setup
setup: ## Initial setup for development environment
	@echo "$(BLUE)Setting up SmileAdventure development environment...$(NC)"
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(YELLOW)Creating .env file from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env file created. Please edit it with your actual values.$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists.$(NC)"; \
	fi
	@echo "$(GREEN)✓ Setup complete!$(NC)"

.PHONY: install-deps
install-deps: ## Install all dependencies for microservices
	@echo "$(BLUE)Installing dependencies for all microservices...$(NC)"
	@for service in microservices/*/; do \
		if [ -f "$$service/requirements.txt" ]; then \
			echo "$(YELLOW)Installing dependencies for $$service...$(NC)"; \
			cd "$$service" && pip install -r requirements.txt && cd ../..; \
		fi; \
	done
	@echo "$(GREEN)✓ All dependencies installed!$(NC)"

# =============================================================================
# DOCKER COMMANDS
# =============================================================================

.PHONY: build
build: ## Build all Docker containers
	@echo "$(BLUE)Building Docker containers...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

.PHONY: up
up: ## Start all services in detached mode
	@echo "$(BLUE)Starting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

.PHONY: down
down: ## Stop all services and remove containers
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: rebuild
rebuild: down build up ## Rebuild and restart all services

.PHONY: logs
logs: ## Show logs for all services
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-auth
logs-auth: ## Show logs for Auth service
	docker-compose -f $(COMPOSE_FILE) logs -f auth

.PHONY: logs-users
logs-users: ## Show logs for Users service
	docker-compose -f $(COMPOSE_FILE) logs -f users

.PHONY: logs-reports
logs-reports: ## Show logs for Reports service
	docker-compose -f $(COMPOSE_FILE) logs -f reports

.PHONY: logs-gateway
logs-gateway: ## Show logs for API Gateway
	docker-compose -f $(COMPOSE_FILE) logs -f api-gateway

.PHONY: logs-db
logs-db: ## Show logs for PostgreSQL database
	docker-compose -f $(COMPOSE_FILE) logs -f postgres-db

# =============================================================================
# DATABASE COMMANDS
# =============================================================================

.PHONY: db-init
db-init: ## Initialize database with schemas and seed data
	@echo "$(BLUE)Initializing database...$(NC)"
	docker-compose -f $(COMPOSE_FILE) run --rm db-init

.PHONY: db-connect
db-connect: ## Connect to PostgreSQL database
	@echo "$(BLUE)Connecting to PostgreSQL database...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec postgres-db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2)

.PHONY: db-backup
db-backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec postgres-db pg_dump -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2) > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backup created in backups/ directory$(NC)"

.PHONY: db-restore
db-restore: ## Restore database from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Error: Please specify BACKUP_FILE variable$(NC)"; \
		echo "Example: make db-restore BACKUP_FILE=backups/backup_20250527_120000.sql"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(BACKUP_FILE)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec -T postgres-db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2) < $(BACKUP_FILE)
	@echo "$(GREEN)✓ Database restored from $(BACKUP_FILE)$(NC)"

# =============================================================================
# HEALTH CHECK COMMANDS
# =============================================================================

.PHONY: health
health: ## Run health checks for all services
	@echo "$(BLUE)Running health checks...$(NC)"
	@if command -v bash >/dev/null 2>&1; then \
		chmod +x scripts/healthchecks.sh && ./scripts/healthchecks.sh; \
	else \
		powershell -ExecutionPolicy Bypass -File scripts/healthchecks.ps1; \
	fi

.PHONY: status
status: ## Show status of all Docker containers
	@echo "$(BLUE)Docker Container Status:$(NC)"
	@echo "======================="
	docker-compose -f $(COMPOSE_FILE) ps

# =============================================================================
# TESTING COMMANDS
# =============================================================================

.PHONY: test
test: test-unit test-integration ## Run all tests

.PHONY: test-unit
test-unit: ## Run unit tests for all services
	@echo "$(BLUE)Running unit tests...$(NC)"
	@for service in microservices/*/; do \
		if [ -d "$$service/tests" ] || [ -f "$$service/pytest.ini" ]; then \
			echo "$(YELLOW)Running tests for $$service...$(NC)"; \
			cd "$$service" && python -m pytest tests/ -v && cd ../..; \
		fi; \
	done

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@if [ -d "tests/integration" ]; then \
		python -m pytest tests/integration/ -v; \
	else \
		echo "$(YELLOW)No integration tests found$(NC)"; \
	fi

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	@if [ -d "tests/e2e" ]; then \
		python -m pytest tests/e2e/ -v; \
	else \
		echo "$(YELLOW)No e2e tests found$(NC)"; \
	fi

.PHONY: test-performance
test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	@if [ -d "tests/performance" ]; then \
		python -m pytest tests/performance/ -v; \
	else \
		echo "$(YELLOW)No performance tests found$(NC)"; \
	fi

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

.PHONY: dev
dev: up ## Start development environment with live reload
	@echo "$(BLUE)Starting development environment...$(NC)"
	@echo "$(GREEN)Services available at:$(NC)"
	@echo "  API Gateway: http://localhost:8000"
	@echo "  Auth Service: http://localhost:8001"
	@echo "  Users Service: http://localhost:8006"
	@echo "  Reports Service: http://localhost:8007"
	@echo "  Web Frontend: http://localhost:3000"
	@echo "  PostgreSQL: localhost:5432"

.PHONY: shell-auth
shell-auth: ## Open shell in Auth service container
	docker-compose -f $(COMPOSE_FILE) exec auth /bin/bash

.PHONY: shell-users
shell-users: ## Open shell in Users service container
	docker-compose -f $(COMPOSE_FILE) exec users /bin/bash

.PHONY: shell-reports
shell-reports: ## Open shell in Reports service container
	docker-compose -f $(COMPOSE_FILE) exec reports /bin/bash

.PHONY: shell-gateway
shell-gateway: ## Open shell in API Gateway container
	docker-compose -f $(COMPOSE_FILE) exec api-gateway /bin/bash

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

.PHONY: clean
clean: ## Remove containers, networks, and volumes
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -f

.PHONY: clean-all
clean-all: ## Remove everything including images
	@echo "$(BLUE)Removing all Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all --remove-orphans
	docker system prune -a -f

.PHONY: reset
reset: clean setup build up db-init ## Complete reset and setup

# =============================================================================
# DOCUMENTATION COMMANDS
# =============================================================================

.PHONY: docs
docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(NC)"
	@if [ -d "docs/api_contracts" ]; then \
		echo "$(GREEN)✓ API contracts found in docs/api_contracts/$(NC)"; \
	else \
		echo "$(YELLOW)Warning: No API contracts found$(NC)"; \
	fi

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server...$(NC)"
	@if command -v python3 >/dev/null 2>&1; then \
		cd docs && python3 -m http.server 8080; \
	else \
		echo "$(RED)Error: Python 3 is required to serve documentation$(NC)"; \
	fi

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

.PHONY: format
format: ## Format code in all microservices
	@echo "$(BLUE)Formatting code...$(NC)"
	@for service in microservices/*/src; do \
		if [ -d "$$service" ]; then \
			echo "$(YELLOW)Formatting $$service...$(NC)"; \
			black "$$service" --line-length 88; \
			isort "$$service"; \
		fi; \
	done

.PHONY: lint
lint: ## Lint code in all microservices
	@echo "$(BLUE)Linting code...$(NC)"
	@for service in microservices/*/src; do \
		if [ -d "$$service" ]; then \
			echo "$(YELLOW)Linting $$service...$(NC)"; \
			flake8 "$$service" --max-line-length 88; \
			pylint "$$service"; \
		fi; \
	done

.PHONY: security-check
security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@for service in microservices/*/; do \
		if [ -f "$$service/requirements.txt" ]; then \
			echo "$(YELLOW)Checking $$service for vulnerabilities...$(NC)"; \
			cd "$$service" && safety check -r requirements.txt && cd ../..; \
		fi; \
	done

# =============================================================================
# MONITORING COMMANDS
# =============================================================================

.PHONY: monitor
monitor: ## Show real-time resource usage
	@echo "$(BLUE)Monitoring container resources...$(NC)"
	docker stats $$(docker-compose -f $(COMPOSE_FILE) ps -q)

.PHONY: top
top: ## Show top processes in containers
	@echo "$(BLUE)Container processes:$(NC)"
	@for container in $$(docker-compose -f $(COMPOSE_FILE) ps -q); do \
		echo "$(YELLOW)Container: $$container$(NC)"; \
		docker top $$container; \
		echo ""; \
	done

# Make help the default target
.DEFAULT_GOAL := help
