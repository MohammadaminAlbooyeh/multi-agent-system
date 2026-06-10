# =============================================================================
# MARES — Makefile
# Common developer commands.
# =============================================================================

.PHONY: help install lint format test test-unit test-integration test-cov \
        run-api run-example run-notebooks clean docker-build docker-up \
        docker-down docker-logs pre-commit

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	    awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
install:  ## Install dependencies
	$(PIP) install -r requirements.txt

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------
lint:  ## Run linters (ruff + mypy)
	ruff check mares api tests
	mypy mares

format:  ## Auto-format code
	black mares api tests examples
	isort mares api tests examples
	ruff check --fix mares api tests

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
test:  ## Run all tests
	$(PYTHON) -m pytest tests/ -v

test-unit:  ## Run unit tests
	$(PYTHON) -m pytest tests/unit -v

test-integration:  ## Run integration tests
	$(PYTHON) -m pytest tests/integration -v

test-cov:  ## Run tests with coverage
	$(PYTHON) -m pytest tests/ --cov=mares --cov-report=html --cov-report=term

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
run-api:  ## Start FastAPI server
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-example:  ## Run basic example
	$(PYTHON) -m examples.run_basic_task

run-notebooks:  ## Launch Jupyter
	jupyter notebook notebooks/

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
docker-build:  ## Build Docker image
	docker build -t mares:latest .

docker-up:  ## Start all services
	docker compose up -d

docker-down:  ## Stop all services
	docker compose down

docker-logs:  ## Tail logs
	docker compose logs -f

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
clean:  ## Remove build/cache artifacts
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage
