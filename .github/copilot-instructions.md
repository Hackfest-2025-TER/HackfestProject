# WaachaPatra - AI Agent Instructions

## Architecture Overview

This is a **hybrid blockchain-database platform** for anonymous political accountability. The key innovation is separating data by mutability:

- **ON-CHAIN (blockchain/)**: Vote aggregates, promise hashes, Merkle roots (immutable)
- **OFF-CHAIN (backend/)**: Full text, individual votes, discussions (queryable)
- **ZK Layer**: Anonymous credentials via SnarkJS/Circom circuits

**Critical Principle**: Individual votes NEVER go on-chain. Only aggregated tallies and Merkle roots are stored in smart contracts.

## Tech Stack

- **Frontend**: SvelteKit + Vite (port 3000)
- **Backend**: FastAPI + Python (port 8000)
- **Blockchain**: Hardhat local node (port 8545)
- **Smart Contracts**: Solidity 0.8.19
- **ZK Circuits**: Circom 2.0

## Development Workflow

### Starting the Stack

```bash
# Option 1: Docker (recommended)
docker-compose up --build

# Option 2: Manual
# Terminal 1 - Blockchain
cd blockchain && npx hardhat node

# Terminal 2 - Backend  
cd backend && uvicorn main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm run dev
```

### Smart Contract Development

```bash
cd blockchain
npx hardhat compile                # Compile contracts
npx hardhat test                   # Run tests
npx hardhat run scripts/deploy.js --network localhost  # Deploy
```

**Key Contracts**:
- `PromiseRegistry.sol`: Stores promise hashes + vote aggregates
- `ZKVerifier.sol`: Verifies zero-knowledge proofs (simplified for MVP)

### Testing

Backend uses in-memory storage (no database setup needed for MVP). Sample data is preloaded in `manifestos_db` array at [backend/main.py](backend/main.py#L108-L176).

## Core Data Flows

### 1. ZK Authentication Flow
```
User → POST /api/zk/verify → Generate nullifier + credential → Store in credentials_db
```
- **Nullifier**: Prevents double voting (unique per citizen)
- **Credential**: Anonymous identifier for this session

### 2. Vote Submission Flow
```
POST /api/votes → Check nullifier not used → Store vote in votes_db → Update manifesto aggregates
```
- Vote stored with `nullifier` (not real identity)
- **Grace period check**: Voting locked until `grace_period_end` passes
- Aggregates (`vote_kept`, `vote_broken`) increment in manifestos_db

### 3. Merkle Proof Verification
```
GET /api/votes/verify/{vote_hash} → Return Merkle path → User verifies vote included
```
Simulated in MVP; production would compute actual Merkle tree from vote batch.

## Key Conventions

### API Patterns

All endpoints return JSON. Main prefixes:
- `/api/zk/*` - Zero-knowledge proof operations
- `/api/manifestos/*` - Promise CRUD + filtering
- `/api/votes/*` - Vote submission + verification
- `/api/comments/*` - Discussion threads
- `/api/audit/*` - Blockchain audit logs
- `/api/network/*` - Network statistics

### Data Models (backend/main.py)

- **Manifesto**: Political promise with `grace_period_end`, `status` (pending/kept/broken)
- **Vote**: Links `manifesto_id` + `nullifier` + `vote_type` (kept/broken)
- **Comment**: Threaded with `parent_id`, anonymous via truncated `nullifier`

### Frontend Routing (SvelteKit)

```
routes/
  +page.svelte           # Landing page
  auth/+page.svelte      # ZK authentication
  manifestos/+page.svelte         # List all promises
  manifestos/[id]/+page.svelte    # Promise detail + discussion
  citizen/attestation/+page.svelte # Voting interface
  audit-trail/+page.svelte        # Blockchain visualizer
  politician/dashboard/+page.svelte # Politician portal
```

### Time-Locked Voting

Promises have a `grace_period_end` timestamp. UI must:
1. Show countdown timer if voting locked
2. Disable vote buttons until period ends
3. Display "Voting opens in X days" message

Check implementation pattern in existing routes.

### Blockchain Integration

**Hardhat local node** runs on port 8545. Contract deployment:
```bash
npx hardhat run scripts/deploy.js --network localhost
```

**Network configurations** in `blockchain/hardhat.config.js`:
- `localhost` (chainId: 31337) - local development
- `mumbai` (80001) - Polygon testnet
- `fuji` (43113) - Avalanche testnet

## Privacy Architecture

**Never log or store**:
- Real user identities
- Full nullifier hashes in frontend
- Personal information

**Always use**:
- Nullifiers for vote tracking (anonymous)
- Truncated nullifiers in UI (`nullifier[:12] + "..."`)
- ZK proofs for authentication (commitment + proof fields)

## Circom Circuit Structure

`circuits/citizen_credential.circom`:
- **Private inputs**: `citizenSecret`, `citizenId`, `birthYear`
- **Public inputs**: `currentYear`, `minAge`, `registrationCutoff`
- **Outputs**: `nullifierHash`, `credentialHash`

Age and registration checks enforce eligibility WITHOUT revealing actual values.

## Common Tasks

### Adding a New API Endpoint

1. Define Pydantic model in [backend/main.py](backend/main.py#L24-L106)
2. Create endpoint with FastAPI decorator
3. Update frontend API calls (components fetch from `http://localhost:8000/api/*`)

### Creating a New Route

1. Add `routes/[name]/+page.svelte` in frontend
2. Use `$app/stores` for page context (see [politicians/[id]/+page.svelte](frontend/src/routes/politicians/[id]/+page.svelte#L7))
3. Import Lucide icons: `import { Icon } from 'lucide-svelte'`

### Modifying Smart Contracts

1. Edit `.sol` files in `blockchain/contracts/`
2. Run `npx hardhat compile`
3. Update tests in `blockchain/test/`
4. Redeploy with `scripts/deploy.js`

## MVP Scope (Hackfest Demo)

**In Scope**:
- ZK credential generation (simulated)
- Promise listing with status filters
- Time-locked voting UI
- Anonymous commenting
- Vote aggregation (on-chain simulation)
- Blockchain visualizer

**Out of Scope**:
- Real zk-SNARK verification (using simplified verification)
- Persistent database (using in-memory storage)
- Actual Merkle tree computation (simulated paths)
- Production blockchain deployment

## Key Files to Reference

- [backend/main.py](backend/main.py) - All API endpoints + in-memory storage
- [blockchain/contracts/PromiseRegistry.sol](blockchain/contracts/PromiseRegistry.sol) - On-chain vote aggregation
- [blockchain/circuits/citizen_credential.circom](blockchain/circuits/citizen_credential.circom) - ZK circuit template
- [docker-compose.yml](docker-compose.yml) - Service configuration
- [README.md](README.md) - Full project documentation

## Remember

1. **Privacy first**: Never expose real identities, always use nullifiers
2. **Hybrid storage**: Aggregates on-chain, details off-chain
3. **Grace periods**: Enforce time locks on voting
4. **Merkle proofs**: Enable vote verification without revealing individual votes
5. **Demo-ready**: Focus on visual proof of concepts (blockchain visualizer, ZK flow, time locks)
