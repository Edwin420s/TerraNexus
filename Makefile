.PHONY: up down logs test build-frontend test-all dev-api dev-frontend

up:
	docker compose -f infrastructure/compose.yaml up --build

down:
	docker compose -f infrastructure/compose.yaml down

logs:
	docker compose -f infrastructure/compose.yaml logs -f

test:
	cd backend && python3 -m pytest tests -v

build-frontend:
	cd frontend && npm run build

dev-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test-all: test build-frontend
	@echo "All TerraNexus test suites and frontend builds passed successfully!"
