# PromiseThread - Makefile
# =========================

.PHONY: help install server frontend backend blockchain stop deploy clean test compile

# Default target
help:
	@echo ""
	@echo "  PromiseThread - Commands"
	@echo "  ════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Development:"
	@echo "    make install     - Install all dependencies"
	@echo "    make server      - Start backend + blockchain"
	@echo "    make frontend    - Start frontend (port 3000)"
	@echo "    make stop        - Stop all services"
	@echo ""
	@echo "  Production:"
	@echo "    make deploy      - Build & run with Docker"
	@echo ""

# =============================================================================
# Installation
# =============================================================================

install:
	@echo "→ Installing frontend..."
	cd frontend && pnpm install
	@echo "→ Installing backend..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt -q
	@echo "→ Installing blockchain..."
	cd blockchain && pnpm install
	@echo "✓ All dependencies installed"

# =============================================================================
# Development (Local)
# =============================================================================

# Start backend + blockchain together (run frontend separately in another terminal)
server:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Starting PromiseThread Development Server"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "→ Stopping any existing services..."
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8545 | xargs kill -9 2>/dev/null || true
	@echo "→ Starting blockchain (port 8545)..."
	@cd blockchain && pnpm run node > /dev/null 2>&1 &
	@sleep 3
	@echo "→ Starting backend (port 8000)..."
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "  ✓ Services Running"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Backend API:      http://localhost:8000"
	@echo "  API Docs:         http://localhost:8000/docs"
	@echo "  Blockchain RPC:   http://localhost:8545"
	@echo ""
	@echo "  Run in another terminal:"
	@echo "  → make frontend   (http://localhost:3000)"
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	cd backend && . venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Individual services
frontend:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Starting Frontend"
	@echo "════════════════════════════════════════════════════════════"
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo ""
	@echo "  Frontend:  http://localhost:3000"
	@echo ""
	cd frontend && pnpm run dev

backend:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Starting Backend"
	@echo "════════════════════════════════════════════════════════════"
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@echo ""
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo ""
	cd backend && . venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

blockchain:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Starting Blockchain"
	@echo "════════════════════════════════════════════════════════════"
	@-lsof -ti:8545 | xargs kill -9 2>/dev/null || true
	@echo ""
	@echo "  Blockchain:  http://localhost:8545"
	@echo ""
	cd blockchain && pnpm run node

stop:
	@echo "Stopping all services..."
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8545 | xargs kill -9 2>/dev/null || true
	@echo "✓ All services stopped"

# =============================================================================
# Production (Docker)
# =============================================================================

deploy:
	docker-compose up --build -d

deploy-down:
	docker-compose down

deploy-logs:
	docker-compose logs -f

# =============================================================================
# Blockchain
# =============================================================================

compile:
	cd blockchain && pnpm run compile

test:
	cd blockchain && pnpm run test

# =============================================================================
# Cleanup
# =============================================================================

clean:
	rm -rf .logs
	rm -rf frontend/.svelte-kit
	rm -rf backend/__pycache__
	rm -rf blockchain/cache blockchain/artifacts
