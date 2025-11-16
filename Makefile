.PHONY: help build up down logs clean test

# Default target
help:
	@echo "OpenEquity Research Platform - Development Commands"
	@echo ""
	@echo "make build          - Build all Docker containers"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make logs           - View logs from all services"
	@echo "make clean          - Remove all containers and volumes"
	@echo "make test           - Run tests"
	@echo "make db-migrate     - Run database migrations"
	@echo "make db-seed        - Seed database with sample data"
	@echo "make backend-shell  - Open shell in backend container"
	@echo "make frontend-shell - Open shell in frontend container"
	@echo "make db-shell       - Open PostgreSQL shell"

# Build containers
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/docs"

# Start with full profile (including Elasticsearch, Celery)
up-full:
	docker-compose --profile full up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	docker-compose down -v
	docker system prune -f

# Run tests
test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

# Database migrations
db-migrate:
	docker-compose exec backend alembic upgrade head

# Seed database
db-seed:
	docker-compose exec -T postgres psql -U openequity -d openequity < database/seeds/001_sample_companies.sql

# Backend shell
backend-shell:
	docker-compose exec backend /bin/bash

# Frontend shell
frontend-shell:
	docker-compose exec frontend /bin/sh

# Database shell
db-shell:
	docker-compose exec postgres psql -U openequity -d openequity

# Install dependencies
install:
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

# Development setup
dev-setup: build up db-migrate
	@echo "Development environment ready!"

# Production build
prod-build:
	docker-compose --profile production build

# Restart specific service
restart-%:
	docker-compose restart $*
