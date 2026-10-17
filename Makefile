.PHONY: setup seed backend frontend dev test reset

PY ?= python3

setup:
	$(PY) -m pip install -r backend/requirements.txt
	@if [ -f frontend/package.json ]; then cd frontend && npm ci; else echo "frontend/package.json missing - skipping frontend setup"; fi

seed:
	cd backend && $(PY) -m seed.load

backend:
	cd backend && DEMO_MODE=$${DEMO_MODE:-1} uvicorn app.main:app --reload --port 8000

frontend:
	@if [ -f frontend/package.json ]; then cd frontend && npm run dev; else echo "frontend/package.json missing - frontend is Nazifa's folder, nothing to run yet"; fi

dev:
	@echo "Run these in two terminals:"
	@echo "  1) make backend"
	@echo "  2) make frontend"

test:
	cd backend && $(PY) -m pytest -q

reset:
	rm -f backend/data/landcheck.db
	$(MAKE) seed
