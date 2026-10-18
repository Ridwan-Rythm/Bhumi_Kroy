.PHONY: setup seed backend frontend dev test lint check schema mocks reset

PY ?= python3

setup:
	$(PY) -m pip install -r backend/requirements-dev.txt
	cd frontend && npm ci

seed:
	cd backend && $(PY) -m seed.load

backend:
	cd backend && DEMO_MODE=$${DEMO_MODE:-1} $(PY) -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Run these in two terminals:"
	@echo "  1) make backend"
	@echo "  2) make frontend     (VITE_USE_MOCK=1 make frontend  serves saved fixtures instead of the API)"

test:
	cd backend && $(PY) -m pytest -q
	cd frontend && npm test

lint:
	$(PY) -m ruff check backend
	cd frontend && npm run lint

# Everything CI runs, in one command.
check: lint test
	cd backend && $(PY) -m scripts.export_schema --check
	cd frontend && npm run build && npm run check:contract

# Regenerate contracts/report.schema.json and the frontend mock fixtures from the real backend.
schema:
	cd backend && $(PY) -m scripts.export_schema

mocks:
	cd backend && $(PY) -m scripts.export_mocks
	$(MAKE) schema

reset:
	rm -f backend/data/landcheck.db backend/data/landcheck.db-wal backend/data/landcheck.db-shm
	$(MAKE) seed
