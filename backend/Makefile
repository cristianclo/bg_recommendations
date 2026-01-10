# Makefile for CJEI Recommendations System

.PHONY: help install migrate seed run test clean

help:  ## Show this help message
	@echo "CJEI Board Game Recommendation System - Commands"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

migrate:  ## Run database migrations
	alembic upgrade head

migrate-create:  ## Create new migration
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

seed:  ## Seed database with sample data
	python -m scripts.seed_data

run:  ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest -v

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

format:  ## Format code with black and isort
	black app/ tests/ scripts/
	isort app/ tests/ scripts/

lint:  ## Lint code with flake8
	flake8 app/ tests/ scripts/

clean:  ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	rm -rf .pytest_cache htmlcov .coverage

db-create:  ## Create PostgreSQL database
	createdb cjei_recommendations

db-drop:  ## Drop PostgreSQL database (WARNING: destructive)
	dropdb cjei_recommendations

setup: install migrate seed  ## Complete setup (install + migrate + seed)

dev: migrate seed run  ## Start development environment
