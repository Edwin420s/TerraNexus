.PHONY: up down logs test build-frontend test-all dev-api dev-frontend test-qa qa-load verify qa-all

up:
	docker compose -f infrastructure/compose.yaml up --build

down:
	docker compose -f infrastructure/compose.yaml down

logs:
	docker compose -f infrastructure/compose.yaml logs -f

test:
	cd backend && python3 -m pytest tests -v

test-qa:
	cd backend && python3 -m pytest tests -v --cov=app --cov-report=term-missing

qa-load:
	python3 scripts/qa_load_test.py

verify:
	python3 scripts/verify_e2e.py

build-frontend:
	cd frontend && npm run build

dev-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test-all: test build-frontend
	@echo "All TerraNexus test suites and frontend builds passed successfully!"

qa-all: test-qa qa-load build-frontend verify
	@echo "======================================================================"
	@echo "TERRANEXUS QA SUITE: ALL TESTS, BENCHMARKS & BUILDS 100% VERIFIED!"
	@echo "======================================================================"
