# PromiseThread Backend

**FastAPI-based REST API server with PostgreSQL database and blockchain integration.**

## Technology Stack

- **Framework:** FastAPI 0.115.6
- **ORM:** SQLAlchemy 2.0.36
- **Database:** PostgreSQL 15
- **Migration:** Alembic 1.14.0
- **Blockchain:** web3.py 7.5.0, eth-account 0.13.1
- **Testing:** pytest 8.3.4

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 15+

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

# Seed sample data
python seed_data.py

# Verify setup
python verify_db.py

# Start server
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

## API Endpoints

### Authentication & ZK Proof

#### POST `/api/registry/lookup`
Look up voter by ID and return Merkle proof.

**Request:**
```json
{
  "voter_id": "1234567890"
}
```

**Response:**
```json
{
  "found": true,
  "voter_id_hash": "0xabc...",
  "name_masked": "Ram***",
  "ward": "1",
  "merkle_proof": [
    {"hash": "0x...", "position": "left"},
    {"hash": "0x...", "position": "right"}
  ],
  "message": "Voter found. Use this data to generate your ZK proof client-side."
}
```

#### POST `/api/zk/verify-proof`
Verify real zk-SNARK proof and issue anonymous credential.

**Request:**
```json
{
  "proof": {
    "pi_a": [...],
    "pi_b": [...],
    "pi_c": [...],
    "protocol": "groth16",
    "curve": "bn128"
  },
  "publicSignals": [
    "0xnullifier...",
    "0xvoterIdHash...",
    "0xcommitment..."
  ],
  "merkle_root": "123456..."
}
```

**Response:**
```json
{
  "valid": true,
  "credential": "anonymous_token",
  "nullifier": "0xfull_hash...",
  "nullifier_short": "0xabc...def",
  "merkle_root": "0x123...",
  "used_votes": [1, 3, 5]
}
```

### Manifestos

#### GET `/api/manifestos`
List manifestos with optional filters.

**Query Parameters:**
- `status` - pending|kept|broken
- `politician_id` - Filter by politician
- `category` - infrastructure|economy|education|health

**Response:**
```json
{
  "manifestos": [
    {
      "id": 1,
      "politician_id": 1,
      "politician_name": "Ram Bahadur",
      "title": "Build new bridge",
      "description": "...",
      "category": "infrastructure",
      "status": "pending",
      "grace_period_end": "2025-06-01T00:00:00Z",
      "vote_kept": 45,
      "vote_broken": 12,
      "created_at": "2024-12-01T00:00:00Z"
    }
  ],
  "total": 12
}
```

#### GET `/api/manifestos/{id}`
Get single manifesto with full details and comments.

### Voting

#### POST `/api/votes`
Submit or change vote on manifesto.

**Request:**
```json
{
  "manifesto_id": 1,
  "vote_type": "kept",
  "nullifier": "0xfull_nullifier...",
  "evidence_url": "https://example.com/proof" // optional
}
```

**Logic:**
1. Verify nullifier exists (user authenticated)
2. Check grace period has passed
3. Check if already voted (allow vote changes)
4. Update aggregates in database
5. Return vote hash for verification

**Response:**
```json
{
  "success": true,
  "message": "Vote recorded successfully",
  "vote_hash": "0xabc...",
  "block_height": 12345,
  "changed": false
}
```

#### GET `/api/votes/verify/{vote_hash}`
Verify a vote was recorded and get Merkle proof.

### Comments

#### GET `/api/manifestos/{id}/comments`
Get threaded comments for a manifesto.

#### POST `/api/comments`
Add a comment (anonymous via nullifier).

**Request:**
```json
{
  "manifesto_id": 1,
  "content": "Evidence shows this was completed",
  "nullifier": "0x...",
  "parent_id": 5  // optional, for replies
}
```

#### POST `/api/comments/{id}/vote`
Upvote or downvote a comment.

### Network & Audit

#### GET `/api/network/stats`
Get network statistics (total voters, votes, etc.)

#### GET `/api/blockchain/blocks`
Get recent blockchain blocks.

#### GET `/api/audit/logs`
Get audit trail of important events

## Database Schema

### Voter Table
```python
class Voter(Base):
    __tablename__ = 'voters'
    
    id = Column(Integer, primary_key=True)
    voter_id = Column(String(50), unique=True, index=True)
    name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))
    province = Column(String(50))
    district = Column(String(100))
    vdc = Column(String(100))  # Municipality
    ward = Column(Integer)
    merkle_leaf = Column(String(66))  # Hash of voter_id
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Note:** Demo uses 1,048 voters (subset of 26,193 total collected).

### ZKCredential Table
```python
class ZKCredential(Base):
    __tablename__ = 'zk_credentials'
    
    id = Column(Integer, primary_key=True)
    nullifier_hash = Column(String(128), unique=True, index=True)
    credential_hash = Column(String(128))
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # NO foreign key to voters (privacy by design)
```

### Manifesto Table
```python
class Manifesto(Base):
    __tablename__ = 'manifestos'
    
    id = Column(Integer, primary_key=True)
    politician_id = Column(Integer, ForeignKey('politicians.id'))
    title = Column(String(500))
    description = Column(Text)
    category = Column(String(50))
    status = Column(String(20))  # pending, kept, broken
    promise_hash = Column(String(66))  # SHA256 for blockchain
    grace_period_end = Column(DateTime)
    vote_kept = Column(Integer, default=0)  # Aggregate
    vote_broken = Column(Integer, default=0)  # Aggregate
    signature = Column(Text)  # ECDSA signature
    signed_by_address = Column(String(42))
```

### ManifestoVote Table
```python
class ManifestoVote(Base):
    __tablename__ = 'manifesto_votes'
    
    id = Column(Integer, primary_key=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'))
    nullifier = Column(String(128), index=True)  # Anonymous
    vote_type = Column(String(10))  # kept | broken
    vote_hash = Column(String(66), unique=True)
    created_at = Column(DateTime)
    
    # One vote per nullifier per manifesto
    __table_args__ = (
        UniqueConstraint('manifesto_id', 'nullifier'),
    )
```

### Comment Table
```python
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'))
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    nullifier = Column(String(128))  # Anonymous
    content = Column(Text)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime)
    
    # Self-referential for threading
    replies = relationship("Comment", backref="parent", remote_side=[id])
```

## Cryptographic Functions

### `crypto_utils.py`

**generate_key_pair()** - Generate Ethereum-compatible wallet
```python
def generate_key_pair() -> Tuple[str, str, str]:
    """Returns: (private_key, public_key, address)"""
    account = Account.create()
    return (account.key.hex(), account.public_key.hex(), account.address)
```

**compute_manifesto_hash()** - Deterministic hash for blockchain
```python
def compute_manifesto_hash(title: str, description: str, politician_id: int) -> str:
    """Hash(title || description || politician_id)"""
    data = f"{title}:{description}:{politician_id}".encode()
    return "0x" + hashlib.sha256(data).hexdigest()
```

**verify_signature()** - ECDSA signature verification
```python
def verify_signature(message_hash: str, signature: str, address: str) -> bool:
    """Verify politician signed their manifesto"""
    recovered = Account.recover_message(
        encode_defunct(hexstr=message_hash),
        signature=signature
    )
    return recovered.lower() == address.lower()
```

## Merkle Tree Implementation

The system builds a binary Merkle tree from voter commitments using Poseidon hashing:

```python
class MerkleTree:
    def __init__(self, leaves: List[str], use_poseidon=True):
        # Uses circomlibjs Poseidon implementation via Node.js
        # to ensure compatibility with ZK circuits
        self.leaves = leaves
        self.root = self._build_tree()
```

**For 1,048 voters:**
- Tree depth: 15 levels (2^15 = 32,768 capacity)
- Hashing: Poseidon (ZK-friendly)
- Verification: snarkjs compatible

## Database Management

See [DATABASE_QUICK_REF.md](DATABASE_QUICK_REF.md) for schema details.
See [MIGRATIONS.md](MIGRATIONS.md) for migration guide.

**Quick commands:**
```bash
# Check migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Import voter data
python import_csv.py --file ../data/file.csv --limit 1048

# Seed sample data
python seed_data.py

# Verify database
python verify_db.py
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_api.py

# Run specific test
pytest test_api.py::test_voter_lookup
```

## Production Considerations

### Environment Variables
```env
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=$(openssl rand -base64 32)
BLOCKCHAIN_RPC_URL=https://polygon-rpc.com
ALLOWED_ORIGINS=https://promisethread.com
```

### Security Checklist
- [ ] Unique voter secrets (not shared demo secret)
- [ ] Rate limiting on API endpoints
- [ ] Input validation and SQL injection prevention
- [ ] HTTPS enforcement with HSTS headers
- [ ] Audit logging for all auth events

### Performance Optimization
- Database indexing on frequently queried columns
- Connection pooling (SQLAlchemy default)
- Caching for Merkle tree (in-memory)
- Background jobs for blockchain sync

## Architecture Notes

**Hybrid Storage Model:**
- **Database**: Individual votes, full manifesto text, comments
- **Blockchain**: Vote aggregates, Merkle roots, promise hashes

**Privacy Design:**
- No foreign key between `zk_credentials` and `voters`
- Votes linked to nullifiers (anonymous)
- Nullifiers prevent double-voting without revealing identity
- Merkle proofs enable verification without exposing vote details

**Scalability:**
- Current: 1,048 voters (11-level tree)
- Production: Up to 32,768 voters (15-level tree)
- Beyond: Batched Merkle trees for 100K+ voters

---

For frontend integration, see [../frontend/README.md](../frontend/README.md)
For blockchain contracts, see [../blockchain/README.md](../blockchain/README.md)
For data collection, see [../data/README.md](../data/README.md)
