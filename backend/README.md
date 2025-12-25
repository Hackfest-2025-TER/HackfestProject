# PromiseThread Backend

**FastAPI-based REST API server with PostgreSQL database and blockchain integration.**

## Architecture Overview

The backend serves as the bridge between the user interface, the off-chain database, and the on-chain smart contracts. It implements a **Hybrid Storage Model**:

1.  **Off-Chain (PostgreSQL)**: "Heavy" data (Text, Comments, History).
2.  **On-Chain (Blockchain)**: "Trust Anchors" (Hashes, Aggregates).

### 🔬 Deep Technical Theory: The Hybrid Model

Why not put everything on Blockchain?

#### 1. The "Gas Wall" & Scalability
Storing 26,000+ voter records and thousands of comments directly on an EVM blockchain is cost-prohibitive.
*   **Cost**: Storing 1KB of data on Ethereum can cost $5-$10 (depending on gas).
*   **Latency**: Block times (2s on Polygon, 12s on Ethereum) are too slow for instant chat/comment interactions.
*   **Solution**: We use the **Database** for speed and cost-efficiency, and the **Blockchain** only for *finality* and *dispute resolution*.

#### 2. Merkle Trees for Privacy & Scale
We use a **Merkle Tree** (Binary Hash Tree) to manage the voter registry.
*   **Structure**: 26,193 voters = ~15 levels ($2^{15} = 32,768$).
*   **Efficiency**: To prove a voter is in the set, we don't check all 26,000 records. We only need the **Merkle Root** (1 hash) and a **Merkle Proof** (15 hashes).
*   **Privacy**: The backend stores the tree. The *public* only sees the Root. A user can prove "I am in this Root" via ZK-SNARKs without revealing *which* leaf they are.
*   **Complexity**: Verification is $O(\log n)$, making it scalable to millions of voters.

#### 3. Privacy-Preserving Database Design
GDPR and privacy ethics dictate that a user's *Identity* (Voter ID) and their *Activity* (Votes) must never be linkable.
*   **Table Separation**:
    *   `Voters Table`: Stores PII (Name, ID) & `merkle_leaf`. **Read-Only**.
    *   `ZKCredentials Table`: Stores `nullifier` (derived from secret). **Write-Only**.
*   **The Air Gap**: There is **NO foreign key** linking these two tables. Even the database administrator cannot mathematically link a `nullifier` back to a `voter_id` without knowing the user's private secret.

### Blockchain Integration
The backend uses `web3.py` to interact with the smart contracts deployed on Polygon/Avalanche/Localhost.
-   **Service**: `blockchain_service.py` manages connections and transaction signing.
-   **Syncing**: The backend listens for on-chain events (`PromiseCreated`, `VotesUpdated`) to keep the Postgres database in sync with the blockchain state.
-   **Writes**: When a politician creates a manifesto or a voting period ends, the backend submits transactions to the blockchain on their behalf (or verifies their direct submission).

## Technology Stack

-   **Framework:** FastAPI 0.115.6
-   **ORM:** SQLAlchemy 2.0.36
-   **Database:** PostgreSQL 15
-   **Migration:** Alembic 1.14.0
-   **Blockchain:** web3.py 7.5.0, eth-account 0.13.1
-   **Testing:** pytest 8.3.4

## Installation

### Prerequisites
-   Python 3.10+
-   PostgreSQL 15+
-   Node (for local blockchain)

### Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
DATABASE_URL=postgresql://promisethread:hackfest2025@localhost:5432/promisethread
DB_HOST=localhost
DB_PORT=5432
DB_NAME=promisethread
DB_USER=promisethread
DB_PASSWORD=hackfest2025
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
BLOCKCHAIN_RPC_URL=http://localhost:8545
EOF

# Run database migrations
alembic upgrade head

# Import voter data (1,048 demo subset)
python import_csv.py --file ../data/dhulikhel_voter_list_full.csv --limit 1048

# Seed sample data (Politicians, Comments)
python seed_data.py

# Start server
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

## API Design Philosophy

The API is designed not just as a data gateway, but as a **Protocol Enforcer**. It ensures that no state change (Voting, Manifesto Creation) occurs without cryptographic authorization.

### Key Protocol Interactions

1.  **The "Blind" Login**:
    *   **Intention**: Authenticate a user without ever seeing their password or ID.
    *   **Technology**: `POST /api/zk/login` accepts a zero-knowledge proof. It verifies the math, issues a session token, and discards the proof.

2.  **Manifesto Anchoring**:
    *   **Intention**: Prevent "Gaslighting" (politicians editing promises).
    *   **Technology**: `POST /api/manifestos` automatically computes the `SHA256` hash of the text and anchors it to the blockchain event log.

3.  **Anonymous Voting**:
    *   **Intention**: Double-voting prevention without identity tracking.
    *   **Technology**: `POST /api/votes` checks the **Nullifier** (a deterministic hash of `Secret + Context`). If the nullifier exists in the DB, the vote is rejected. The server has no way to reverse-engineer the nullifier to find the voter.

## Core Endpoints Reference

### Authentication & ZK Proofs

#### `POST /api/zk/login`
Verifies a zero-knowledge proof and issues a session credential.
-   **Input**: `proof`, `publicSignals` (nullifier, merkle_root)
-   **Output**: Session `credential` string.

#### `POST /api/zk/verify`
Similar to login, but strictly for verifying a proof without necessarily starting a session.

#### `GET /api/zk/credential/{nullifier}`
Checks if a nullifier is valid and retrieves its voting history.

### Manifestos

#### `GET /api/manifestos`
List all manifestos.
-   **Params**: `status`, `category`, `politician_id`, `limit`, `offset`

#### `GET /api/manifestos/{id}`
Get full details of a single manifesto.

#### `POST /api/manifestos`
**Create a new manifesto.** (Requires Politician Verification)
-   **Body**: `title`, `description`, `category`, `deadline`, `politician_id`
-   **Process**: Hashes content, stores in DB, and initiates blockchain transaction.

#### `GET /api/manifestos/{id}/votes`
Get real-time vote aggregates (kept/broken) for a manifesto.

### Voting

#### `POST /api/votes`
Submit a vote on a manifesto using a ZK nullifier.
-   **Body**: `manifesto_id`, `vote_type` ('kept'|'broken'), `nullifier`
-   **Logic**: Verifies nullifier uniqueness for this manifesto, updates DB aggregates. Use blockchain service to batch-commit later.

#### `GET /api/votes/verify/{vote_hash}`
Verify a specific vote receipt against the ledger.

### Comments

#### `GET /api/manifestos/{id}/comments`
Get threaded discussion.
-   **Params**: `include_flagged` (bool)

#### `POST /api/comments`
Post a comment anonymously.
-   **Body**: `manifesto_id`, `content`, `parent_id` (optional), `session_id`

#### `POST /api/comments/{id}/vote`
Upvote/Downvote/Flag a comment.
-   **Body**: `vote_type` ('up'|'down'|'flag'), `nullifier`

### Politicians

#### `GET /api/politicians`
List all registered politicians with their trust scores.

#### `GET /api/politicians/{identifier}`
Get details by ID or slug string.

#### `GET /api/politicians/pending`
List pending politician applications (Admin only).

### System & Network

#### `GET /api/network/stats`
Global stats: Total voters, votes, active nodes, and integrity score.

#### `GET /api/blockchain/blocks`
Visualizer endpoint: Returns recent "blocks" (audit logs) representing chain state.

#### `GET /api/audit/logs`
Detailed audit trail of all system actions.

#### `POST /api/feedback`
Submit anonymous platform feedback.

## Database Schema

### `voters`
Read-only registry imported from Election Commission. Used to build Merkle Tree.
- `voter_id`, `name`, `ward`, `merkle_leaf`

### `zk_credentials`
Stores valid nullifiers. **NO LINK** to `voters` table to ensure privacy.
- `nullifier_hash`, `credential_hash`, `is_valid`

### `manifestos`
- `title`, `description`, `promise_hash` (on-chain link), `status`, `politician_id`

### `manifesto_votes`
- `manifesto_id`, `nullifier`, `vote_type`, `vote_hash`

### `politicians`
- `name`, `party`, `wallet_address`, `integrity_score` (calculated)

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html
```

## Security

-   **Zero-Knowledge**: Voter identities are never sent to the backend during voting. Only the proof and nullifier are.
-   **Nullifiers**: Prevent double-voting while maintaining anonymity.
-   **Manifesto Hashing**: Ensures politicians cannot silently edit promises after making them.
