# PromiseThread

**Decentralized Political Accountability Platform**

A transparent platform where citizens anonymously track and evaluate political promises through community discussion and voting. Built with Svelte, Zero-Knowledge Proofs, and Blockchain technology.

![PromiseThread](./design/banner.png)

## 🌟 Vision

PromiseThread solves the fundamental problem of political accountability: **How do you have transparent, tamper-proof political accountability while protecting citizen privacy?**

Our solution combines **Zero-Knowledge Proofs** with a **Hybrid Storage Architecture** to create a platform where:
- Citizens can vote anonymously while preventing Sybil attacks
- Vote results are transparent and immutable
- No personal data is ever stored or tracked

## 🚀 Features

### Core Functionality
- **Anonymous Voting** - ZK-SNARK proofs ensure one-person-one-vote without revealing identity
- **Promise Tracking** - Track political promises from creation to completion
- **Community Discussion** - Reddit-style threaded comments with evidence links
- **Grace Periods** - Fair timing prevents premature judgment
- **Blockchain Immutability** - Final results are permanently recorded on-chain

### Technical Highlights
- **Zero-Knowledge Proofs** - SnarkJS/Circom for cryptographic privacy
- **Hybrid Storage** - Aggregates on-chain, details off-chain for scalability
- **Merkle Proof Verification** - Citizens can verify their vote was counted
- **Real-time Network Dashboard** - Monitor blockchain integrity

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                    (SvelteKit + Vite)                        │
├─────────────────────────────────────────────────────────────┤
│  Landing │ Auth │ Manifestos │ Voting │ Audit │ Politician  │
│   Page   │ Page │   List     │  Box   │ Trail │   Portal    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│                    (FastAPI + Python)                        │
├─────────────────────────────────────────────────────────────┤
│  ZK Proof  │  Manifesto  │   Vote   │  Comment  │   Audit   │
│ Verification│   CRUD     │ Aggregate│   Thread  │    Logs   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       BLOCKCHAIN                             │
│                  (Hardhat + Solidity)                        │
├─────────────────────────────────────────────────────────────┤
│     PromiseRegistry.sol     │       ZKVerifier.sol          │
│   - Promise hashes          │   - Proof verification        │
│   - Vote aggregates         │   - Credential issuance       │
│   - Merkle roots            │   - Nullifier tracking        │
└─────────────────────────────────────────────────────────────┘
```

### Hybrid Storage Model

| On-Chain (Immutable) | Off-Chain (Database) |
|---------------------|---------------------|
| Promise hash + metadata | Full promise text |
| Vote AGGREGATES only | Individual vote records |
| Status changes + timestamps | Discussion threads |
| Merkle root of all votes | Evidence links |

## 📦 Project Structure

```
HackfestProject/
├── frontend/               # SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/  # Reusable UI components
│   │   │   ├── stores.ts    # Svelte stores
│   │   │   ├── api.ts       # API client
│   │   │   └── types.ts     # TypeScript interfaces
│   │   └── routes/          # SvelteKit pages
│   └── package.json
├── backend/                # FastAPI backend
│   ├── main.py             # API endpoints
│   └── requirements.txt
├── blockchain/             # Smart contracts
│   ├── contracts/
│   │   ├── PromiseRegistry.sol
│   │   └── ZKVerifier.sol
│   ├── scripts/deploy.js
│   └── hardhat.config.js
├── design/                 # Design assets
└── docker-compose.yml
```

## 🛠️ Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose (optional)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/promisethread.git
cd promisethread

# Start all services
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Blockchain RPC: http://localhost:8545

### Manual Setup

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Blockchain:**
```bash
cd blockchain
npm install
npx hardhat node  # In one terminal
npx hardhat run scripts/deploy.js --network localhost  # In another
```

## 📱 Pages & Features

| Page | Description |
|------|-------------|
| `/` | Landing page with platform overview |
| `/auth` | Login/Register with ZK authentication |
| `/manifestos` | Browse all political promises |
| `/manifestos/[id]` | Promise detail with discussion |
| `/citizen/attestation` | Vote on promises anonymously |
| `/politicians` | Directory of all politicians |
| `/politicians/[id]` | Politician profile & track record |
| `/audit-trail` | Network integrity dashboard |
| `/politician/dashboard` | Politician portal |
| `/politician/new-manifesto` | Create new promise |
| `/feedback` | Submit bug reports/suggestions |
| `/settings` | User preferences |

## 🔐 Zero-Knowledge Flow

```
1. Citizen generates ZK proof  →  Proves "I am eligible" without revealing identity
2. System issues credential   →  Anonymous credential (e.g., ABC123)
3. Citizen votes             →  Vote linked to credential, not identity
4. Nullifier check           →  Prevents double-voting
5. Votes batched             →  Merkle tree created every N votes
6. Merkle root on-chain      →  Immutable proof of all votes
7. Verification              →  Any citizen can verify their vote was counted
```

## 📊 API Endpoints

### ZK Proof
- `POST /api/zk/verify` - Verify ZK proof and issue credential
- `GET /api/zk/credential/{nullifier}` - Check credential status

### Manifestos
- `GET /api/manifestos` - List all manifestos
- `GET /api/manifestos/{id}` - Get manifesto details
- `POST /api/manifestos` - Create new manifesto
- `GET /api/manifestos/{id}/votes` - Get vote aggregates

### Voting
- `POST /api/votes` - Submit a vote
- `GET /api/votes/verify/{hash}` - Verify vote with Merkle proof

### Comments
- `GET /api/manifestos/{id}/comments` - Get discussion thread
- `POST /api/comments` - Add comment

### Network
- `GET /api/network/stats` - Network statistics
- `GET /api/audit/logs` - Audit trail
- `GET /api/blockchain/blocks` - Recent blocks

## 🎯 Demo Flow

1. **Generate ZK Credential** - Visit Auth page, generate anonymous credential
2. **Browse Promises** - See locked (grace period) vs open for voting
3. **Join Discussion** - Add anonymous comment with evidence
4. **Cast Vote** - Vote on promise (kept/broken)
5. **View Blockchain** - See vote aggregate update
6. **Verify Vote** - Use Merkle proof to verify inclusion

## 🧪 Testing

```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && pytest

# Smart contract tests
cd blockchain && npx hardhat test
```

## 🚀 Deployment

### Testnet Deployment

```bash
cd blockchain

# Polygon Mumbai
npx hardhat run scripts/deploy.js --network mumbai

# Avalanche Fuji
npx hardhat run scripts/deploy.js --network fuji

# Sepolia
npx hardhat run scripts/deploy.js --network sepolia
```

### Environment Variables

Create `.env` files from examples:
- `blockchain/.env` - Private keys, RPC URLs
- `backend/.env` - Database URL, secrets
- `frontend/.env` - API URLs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [SnarkJS](https://github.com/iden3/snarkjs) - Zero-knowledge proof library
- [Circom](https://github.com/iden3/circom) - ZK circuit compiler
- [SvelteKit](https://kit.svelte.dev/) - Frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Hardhat](https://hardhat.org/) - Ethereum development environment

---

**Built with ❤️ for Hackfest 2024**

*Democracy can be transparent AND protect citizen privacy.*
