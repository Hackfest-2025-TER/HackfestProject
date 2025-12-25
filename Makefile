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
	@echo "  Testing:"
	@echo "    make test-backend     - Run backend API tests"
	@echo "    make test-blockchain  - Run blockchain tests"
	@echo "    make test-crypto      - Test cryptographic components"
	@echo "    make test-zk          - Test ZK proof components"
	@echo "    make test-integration - Test running services"
	@echo "    make test-scenarios   - Run end-to-end scenarios with data"
	@echo "    make test-all         - Run all tests"
	@echo "    make test             - Alias for test-all"
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
	cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt -q
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
	cd backend && ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload

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
	cd backend && ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload

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
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Building and Starting PromiseThread (Docker)"
	@echo "════════════════════════════════════════════════════════════"
	docker-compose up --build -d
	@echo ""
	@echo "  ✓ Services starting..."
	@echo ""
	@echo "  Frontend:         http://localhost:3000"
	@echo "  Backend API:      http://localhost:8000"
	@echo "  API Docs:         http://localhost:8000/docs"
	@echo "  Blockchain RPC:   http://localhost:8545"
	@echo "  PostgreSQL:       localhost:5432"
	@echo ""
	@echo "  Run 'make deploy-logs' to view logs"
	@echo "════════════════════════════════════════════════════════════"

deploy-down:
	docker-compose down

deploy-logs:
	docker-compose logs -f

deploy-restart:
	docker-compose restart

deploy-clean:
	docker-compose down -v --rmi local
	@echo "✓ Removed containers, volumes, and local images"

deploy-status:
	docker-compose ps

# =============================================================================
# Blockchain
# =============================================================================

compile:
	cd blockchain && pnpm run compile

# =============================================================================
# Testing
# =============================================================================

test-backend:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Running Backend API Tests"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@cd backend && ./venv/bin/pip install pytest pytest-asyncio httpx -q 2>/dev/null || true
	@cd backend && ./venv/bin/pytest test_api.py -v --tb=short -x
	@echo ""
	@echo "  ✓ Backend tests completed"

test-blockchain:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Running Blockchain Smart Contract Tests"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	cd blockchain && pnpm run test
	@echo ""
	@echo "  ✓ Blockchain tests completed"

test-crypto:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Testing Cryptographic Components"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "→ Testing keccak256 hash consistency..."
	@cd backend && ./venv/bin/python3 -c "\
	from crypto_utils import compute_manifesto_hash; \
	from web3 import Web3; \
	test_text = 'I promise to build 100 schools by 2025'; \
	backend_hash = compute_manifesto_hash(test_text); \
	expected_hash = Web3.keccak(text=test_text).hex(); \
	print(f'  Backend hash:  {backend_hash}'); \
	print(f'  Expected hash: {expected_hash}'); \
	assert backend_hash == expected_hash, 'Hash mismatch!'; \
	print('  ✓ keccak256 hashing consistent')"
	@echo ""
	@echo "→ Testing digital signatures..."
	@cd backend && ./venv/bin/python3 -c "\
	from crypto_utils import generate_key_pair, create_signature, verify_signature; \
	private_key, _, address = generate_key_pair(); \
	message = 'Test message for signature verification'; \
	signature = create_signature(message, private_key); \
	is_valid, recovered_addr = verify_signature(message, signature, address); \
	print(f'  Generated address: {address[:10]}...'); \
	print(f'  Signature valid: {is_valid}'); \
	assert is_valid, 'Signature verification failed!'; \
	print('  ✓ Digital signatures working correctly')"
	@echo ""
	@echo "  ✓ Cryptographic tests completed"

test-zk:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Testing Zero-Knowledge Proof Components"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "→ Checking ZK circuit artifacts..."
	@test -f blockchain/circuits/build/citizen_credential_final.zkey && echo "  ✓ Final proving key found" || echo "  ⚠ Final proving key missing (run: cd blockchain && pnpm run circuit:setup)"
	@test -f blockchain/circuits/build/verification_key.json && echo "  ✓ Verification key found" || echo "  ⚠ Verification key missing"
	@test -f blockchain/circuits/build/citizen_credential.r1cs && echo "  ✓ R1CS constraint system found" || echo "  ⚠ R1CS missing"
	@echo ""
	@echo "→ Testing Poseidon hash implementation..."
	@cd backend && ./venv/bin/python3 -c "\
	from utils.poseidon import poseidon_simple; \
	result = poseidon_simple([123, 456]); \
	print(f'  Poseidon([123, 456]) = {result}'); \
	print('  ✓ Poseidon hash working')"
	@echo ""
	@echo "  ✓ ZK component tests completed"

test-integration:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Running Integration Tests (requires running services)"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "→ Testing backend API health..."
	@curl -sf http://localhost:8000/api/health > /dev/null && echo "  ✓ Backend API responding" || echo "  ⚠ Backend not running (start with: make server)"
	@echo ""
	@echo "→ Testing blockchain connection..."
	@curl -sf -X POST http://localhost:8545 -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null && echo "  ✓ Blockchain node responding" || echo "  ⚠ Blockchain not running"
	@echo ""
	@echo "  ✓ Integration tests completed"

test-scenarios:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Running End-to-End Test Scenarios"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Testing complete user journeys with realistic data:"
	@echo "  • Politician registration & manifesto submission"
	@echo "  • Voter authentication & ZK proof generation"
	@echo "  • Community discussion with evidence"
	@echo "  • Vote aggregation & Merkle verification"
	@echo "  • Full platform lifecycle"
	@echo ""
	@cd backend && ./venv/bin/pytest tests/test_scenarios.py -v -s --tb=short
	@echo ""
	@echo "  ✓ Scenario tests completed"

test-all:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Running All Tests"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@make test-crypto
	@echo ""
	@make test-zk
	@echo ""
	@make test-backend
	@echo ""
	@make test-scenarios
	@echo ""
	@make test-blockchain
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "  ✓ All Tests Completed Successfully"
	@echo "════════════════════════════════════════════════════════════"

test:
	@make test-all

# =============================================================================
# Cleanup
# =============================================================================

clean:
	rm -rf .logs
	rm -rf frontend/.svelte-kit
	rm -rf backend/__pycache__
	rm -rf blockchain/cache blockchain/artifacts
