.PHONY: help setup up down dev seed test lint benchmark clean

PYTHON ?= python3
UV ?= uv
PNPM ?= pnpm

help:
	@echo "NETRAVA — Open Government Video Intelligence Fabric"
	@echo "=================================================="
	@echo "make setup     - Install Python & Node.js dependencies"
	@echo "make up        - Start container infrastructure (Postgres, Redis, MinIO, MediaMTX)"
	@echo "make down      - Stop container infrastructure"
	@echo "make seed      - Populate Gujarat reference dataset (cameras, watchlists, sightings)"
	@echo "make dev       - Run local development servers (API, Web, Simulator)"
	@echo "make test      - Run full test suite"
	@echo "make benchmark - Run throughput and latency benchmarks"
	@echo "make clean     - Clean temporary artifacts and cache"

setup:
	@echo "Setting up Python virtual environment with uv..."
	$(UV) venv .venv
	@echo "Installing backend dependencies..."
	.venv/bin/pip install -e ./apps/api
	@echo "Installing frontend dependencies..."
	cd apps/web && $(PNPM) install

up:
	docker compose -f infra/compose/docker-compose.yml up -d

down:
	docker compose -f infra/compose/docker-compose.yml down

seed:
	.venv/bin/python scripts/seed_db.py

dev-api:
	.venv/bin/uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd apps/web && $(PNPM) dev

dev:
	@echo "Launching Netrava API & Web in parallel..."
	@make up
	@sleep 2
	@make seed
	@(trap 'kill 0' SIGINT; make dev-api & make dev-web & wait)

test:
	.venv/bin/pytest tests/

benchmark:
	.venv/bin/python scripts/run_benchmarks.py

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ apps/web/.next
