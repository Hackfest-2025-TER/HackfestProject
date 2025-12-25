# PromiseThread

**Decentralized political accountability platform using zero-knowledge proofs and blockchain.**

---

## Overview

PromiseThread enables citizens to anonymously evaluate political promises through community voting and discussion. Built with real voter data from Nepal's Election Commission, the platform combines zero-knowledge cryptography with blockchain immutability to create transparent yet privacy-preserving political accountability.

**Core Innovation:** Anonymous voting with verifiable eligibility using zk-SNARKs and Merkle trees.

### Key Features

- **Zero-Knowledge Authentication** - Prove eligibility without revealing identity
- **Anonymous Voting** - Vote on promises (kept/broken) via nullifier-based system
- **Threaded Discussion** - Reddit-style comments with evidence links
- **Blockchain Immutability** - Vote aggregates stored on-chain
- **Time-Locked Evaluation** - Grace periods prevent premature judgment
- **Digital Signatures** - Politicians sign promises with crypto wallets
- **Vote Verification** - Merkle proofs enable independent verification

### System Status

**Live System** using real government data:
- **Data Source:** Nepal Election Commission voter registry
- **Location:** Dhulikhel Municipality, Kavrepalanchok District
- **Full Dataset:** 26,193 voters collected across 12 wards
- **Active Subset:** 1,048 voters (optimized for browser performance)

---

## Quick Start

### Prerequisites

- Node.js 18+, Python 3.10+, PostgreSQL 15+
- Docker & Docker Compose (optional)

### With Docker (Recommended)

```bash
git clone https://github.com/Hackfest-2025-TER/HackfestProject.git
cd HackfestProject
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Blockchain: http://localhost:8545

### Manual Setup

```bash
# 1. Database
createdb -U postgres promisethread

# 2. Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python import_csv.py --file ../data/dhulikhel_voter_list_full.csv --limit 1048
uvicorn main:app --reload --port 8000

# 3. Blockchain (separate terminal)
cd blockchain
npm install && npx hardhat node
# In another terminal: npx hardhat run scripts/deploy.js --network localhost

# 4. Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

**Full installation guide:** See [Installation](#installation) below.

---

## Architecture

### System Overview

```
┌───────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                         │
│                (SvelteKit + TypeScript)                    │
├───────────────────────────────────────────────────────────┤
│  Auth/ZK │ Manifesto │ Voting │ Discussion │ Audit Trail │
│   Proof  │   List    │   UI   │   Thread   │  Visualizer │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                     BACKEND LAYER                          │
│              (FastAPI + SQLAlchemy)                        │
├───────────────────────────────────────────────────────────┤
│  Voter   │ ZK Proof │ Manifesto │  Vote   │   Comment    │
│ Registry │  Verify  │   CRUD    │ Storage │    Thread    │
│ (Merkle) │(snarkjs) │           │         │              │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                    DATABASE LAYER                          │
│                   (PostgreSQL 15)                          │
├───────────────────────────────────────────────────────────┤
│ voters │ zk_credentials │ manifestos │ votes │ comments   │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                   BLOCKCHAIN LAYER                         │
│            (Hardhat + Solidity + EVM)                      │
├───────────────────────────────────────────────────────────┤
│ PromiseRegistry │ ManifestoRegistry │ ZKVerifier          │
│ Vote aggregates │  Promise hashes   │ Proof verification  │
└───────────────────────────────────────────────────────────┘
```

### Hybrid Storage Model

The system uses a **two-tier architecture** optimized for privacy, scalability, and cost:

| Storage | Purpose | Data Stored |
|---------|---------|-------------|
| **Blockchain (On-Chain)** | Immutable records | Vote aggregates, promise hashes, Merkle roots, signatures |
| **Database (Off-Chain)** | Queryable data | Full text, individual votes (nullifier-linked), comments |

**Why Hybrid?**
- **Scalability:** Database handles 1K+ voters efficiently (blockchain is expensive)
- **Privacy:** Individual votes remain off-chain (only aggregates public)
- **Auditability:** Merkle roots enable verification without exposing details
- **Cost:** Database ~$0.001/GB vs blockchain ~$100/GB at scale

**Component Details:**
- [backend/README.md](backend/README.md) - API endpoints, database schema
- [frontend/README.md](frontend/README.md) - UI components, routing
- [blockchain/README.md](blockchain/README.md) - Smart contracts, ZK circuits

---

## Cryptographic Protocol

### Shuffled Anonymity Approach

Four-stage protocol ensuring server cannot link voters to votes:

**1. Server Shuffle**
- Backend shuffles voter commitments (hashes)
- Deletes original mapping (honest dealer assumption)
- Builds Merkle tree from shuffled set

**2. Client Download**  
- User downloads full anonymity set (~33 KB for 1,048 voters)
- All voter hashes visible, but shuffled (no identity linkage)

**3. Client Proof Generation**
- Merkle proof computed locally in browser
- Server never sees which path was used
- Generates nullifier (anonymous voter ID)

**4. Server Verification**
- Validates Merkle proof against root
- Checks nullifier not already used (prevents double-voting)
- Issues anonymous credential

**Privacy Guarantees:**
- Server cannot link votes to voters (nullifier-based)
- Server cannot determine Merkle path (client-side computation)
- Even malicious server cannot link votes to identities (nullifiers are anonymous)

### Zero-Knowledge Proofs

**Technology:** Circom circuits with Poseidon hash and Groth16 proof system

**Proves:** "I am a registered voter" without revealing which voter

**Circuit constraints:**
1. Voter ID hash exists in Merkle tree (membership proof)
2. Nullifier = Hash(voterId, secret) (prevents double-voting)
3. Commitment binds voter hash to nullifier (prevents forgery)



**Circuit details:** See [blockchain/README.md](blockchain/README.md)

---

## Data Source

### Authentic Government Voter Registry

Scraped from Nepal Election Commission: https://voterlist.election.gov.np

**Data Specifics:**
- **Province:** बागमती प्रदेश (Bagmati)
- **District:** काभ्रेपलाञ्चोक (Kavrepalanchok)  
- **Municipality:** धुलिखेल नगरपालिका (Dhulikhel)
- **Wards:** 1-12
- **Total Collected:** 26,193 voters
- **Demo Subset:** 1,048 voters

**Why 1,048 Voters?**

Optimal balance for demonstration:
- **Merkle Tree:** 11 levels (2^11 = 2,048 capacity)
- **Proof Time:** <1 second in browser
- **Download Size:** ~33 KB (shuffled commitments)
- **Privacy:** 1K+ anonymity set provides meaningful unlinkability
- **Reliability:** Smooth performance on standard laptops

**Scalability Path:**
- Current: 1,048 voters (11-level tree)
- Full Dataset: 26,193 voters (15-level tree)
- Enterprise: 100K+ voters (batched Merkle trees )

### Scraping Methodology

**Technology:** R + Selenium WebDriver (parallel scraping)
- 3 concurrent Chrome instances
- All 12 wards × all registration centers
- Full pagination (100 entries/page)
- Output: Consolidated CSV

**Scraper Repository:** https://github.com/Hackfest-2025-TER/ScraperElectionCommision

 **Data details:** See [data/README.md](data/README.md) for schema and privacy handling

---

## Installation

### Prerequisites

**Software:**
- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.10+ ([Download](https://www.python.org/))
- PostgreSQL 15+ ([Download](https://www.postgresql.org/))
- Docker (optional) ([Download](https://www.docker.com/))


### Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql@15  # macOS

# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE promisethread;
CREATE USER promisethread WITH PASSWORD 'hackfest2025';
GRANT ALL PRIVILEGES ON DATABASE promisethread TO promisethread;
\q
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
DATABASE_URL=postgresql://promisethread:hackfest2025@localhost:5432/promisethread
BLOCKCHAIN_RPC_URL=http://localhost:8545
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
EOF

# Run migrations
alembic upgrade head

# Import voter data (1,048 demo subset)
python import_csv.py --file ../data/dhulikhel_voter_list_full.csv --limit 1048

# Seed sample data
python seed_data.py

# Start server
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
- Database connected
- Merkle tree built: 1048 voters, depth 11, root 0xabc...
```

### Blockchain Setup

```bash
cd blockchain

# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Start local node (Terminal 1)
npx hardhat node

# Deploy contracts (Terminal 2)
npx hardhat run scripts/deploy.js --network localhost
```

**Save contract addresses from deployment output.**

### Frontend Setup

```bash
cd frontend

# Install dependencies  
npm install

# Configure environment
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_BLOCKCHAIN_RPC=http://localhost:8545
EOF

# Start dev server
npm run dev
```

**Access application:** http://localhost:3000



---

## Docker Deployment

### Quick Start

```bash
docker-compose up --build
```

**Services Started:**
- `postgres` - PostgreSQL database (port 5432)
- `blockchain` - Hardhat node (port 8545)
- `backend` - FastAPI server (port 8000)
- `frontend` - SvelteKit app (port 3000)

### Docker Commands

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Reset database (deletes data)
docker-compose down -v

# Execute commands
docker-compose exec backend bash
docker-compose exec postgres psql -U promisethread
```



---

## Project Structure

```
HackfestProject/
├── frontend/              # SvelteKit web app
│   ├── src/routes/        # Pages (auth, manifestos, voting)
│   ├── src/lib/           # Components, API client, stores
│   └── static/zk/         # ZK circuit artifacts (WASM, keys)
│
├── backend/               # FastAPI server
│   ├── main.py            # API endpoints
│   ├── models.py          # Database models
│   ├── crypto_utils.py    # Cryptographic functions
│   └── migrations/        # Alembic migrations
│
├── blockchain/            # Smart contracts
│   ├── contracts/         # Solidity contracts
│   ├── circuits/          # Circom ZK circuits
│   └── scripts/           # Deployment scripts
│
├── data/                  # Voter registry CSV
│   └── dhulikhel_voter_list_full.csv
│
├── docker-compose.yml     # Development orchestration
└── README.md              # This file
```

**Component Documentation:**
- [backend/README.md](backend/README.md) - API reference, database schema
- [frontend/README.md](frontend/README.md) - UI components, routing, state management
- [blockchain/README.md](blockchain/README.md) - Smart contracts, ZK circuits, deployment
- [data/README.md](data/README.md) - Data collection, schema, privacy

---

## Security Model

### Trust Assumptions

**1. Honest Dealer (Server Shuffle)**
- Server shuffles voter commitments honestly and deletes mapping
- If violated: Server could link commitments to voters (but NOT votes to voters)
- Mitigation: Use verifiable shuffle (MPC) in production

**2. Unique Voter Secrets**
- Each voter receives unique secret from Election Commission
- Current MVP: Shared demo secret `"CITIZENSHIP_'CITIZENSHIPNO'"` (demonstration only)
- Production: SMS/physical card distribution of unique secrets

**3. Client-Side Security**
- Browser environment is trusted (no malware)
- If violated: Attacker could steal voter ID + secret
- Mitigation: Hardware security modules (HSM) for secret storage




**Security details:** See [backend/README.md](backend/README.md) and [blockchain/README.md](blockchain/README.md)

---

## Technology Stack

### Frontend
- **Framework:** SvelteKit 2.0
- **Language:** TypeScript 5.0
- **Styling:** Tailwind CSS 3.4
- **ZK Libraries:** snarkjs 0.7.5, circomlibjs 0.1.7
- **Build:** Vite 5.0

### Backend
- **Framework:** FastAPI 0.115.6
- **Database:** PostgreSQL 15, SQLAlchemy 2.0.36
- **Migration:** Alembic 1.14.0
- **Blockchain:** web3.py 7.5.0

### Blockchain
- **Framework:** Hardhat 2.19.0
- **Language:** Solidity 0.8.19
- **ZK Circuits:** Circom 2.0.0
- **Proof System:** Groth16 (snarkjs)

---








## Support & Links

- **GitHub:** https://github.com/Hackfest-2025-TER/HackfestProject
- **Scraper:** https://github.com/Hackfest-2025-TER/ScraperElectionCommision

---

## References

**Academic Papers:**
- Groth16: "On the Size of Pairing-Based Non-interactive Arguments" (EUROCRYPT 2016)
- Merkle Trees: "A Digital Signature Based on a Conventional Encryption Function" (CRYPTO 1987)
- zk-SNARKs: "From Extractable Collision Resistance to Succinct NIARKs" (ITCS 2012)

**Technical Docs:**
- Circom: https://docs.circom.io/
- snarkjs: https://github.com/iden3/snarkjs
- SvelteKit: https://kit.svelte.dev/docs
- FastAPI: https://fastapi.tiangolo.com/
- Hardhat: https://hardhat.org/docs


---


*Hackfest 2025 - Team Three Eyed Raven*
