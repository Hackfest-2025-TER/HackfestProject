# PromiseThread: Blind Auditor Voting System

**Decentralized Political Accountability Platform with Zero-Knowledge Privacy**

PromiseThread is a transparency and accountability framework enabling citizens to audit political promises post-election through fully anonymous interaction. The system combines Zero-Knowledge Proofs, Merkle Tree-based voter registry, and blockchain immutability to create a "Blind Auditor" mechanism where citizens can prove voting eligibility without revealing identity.

---

## Table of Contents

- [Abstract](#abstract)
- [Voter Data Source](#voter-data-source)
- [Cryptographic Protocol](#cryptographic-protocol)
- [Architecture](#architecture)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Docker Deployment](#docker-deployment)
- [Security Model](#security-model)
- [Future Roadmap](#future-roadmap)
- [References](#references)

---

## Abstract

PromiseThread addresses a fundamental challenge in democratic systems: how to enable continuous citizen feedback on political accountability while preserving voter privacy. Traditional accountability mechanisms either sacrifice privacy (identified voting) or integrity (anonymous voting without Sybil resistance).

This platform implements a **Blind Auditor System** that solves both constraints:

1. **Privacy:** Voters prove membership in a government-issued registry using zero-knowledge proofs without revealing which specific voter they are.
2. **Integrity:** The system prevents double-voting through deterministic nullifiers while maintaining unlinkability between voter identity and nullifier.
3. **Transparency:** Vote aggregates and final decisions are recorded immutably on blockchain, publicly auditable.

The core innovation is the **shuffled anonymity set** approach combined with **client-side Merkle proof generation**, ensuring the server never learns the mapping between voters and their actions.

**Production Architecture (Shuffled Purist Model):**
The intended production design eliminates server-side knowledge through:
- Cryptographic shuffling of voter commitments (destroys index-identity linkage)
- Client-side Merkle tree construction from shuffled anonymity set
- Zero-knowledge proofs generated entirely in browser (WASM)
- Server verification without learning user identity

**Current MVP Implementation:**
This demonstration validates the concept using simplified ZK authentication while maintaining the architectural foundations. See [Security Model](#security-model) for detailed analysis of MVP limitations and production requirements.

---

## Voter Data Source

### Real Government Data

PromiseThread uses **authentic voter registry data** scraped from the Nepal Election Commission (https://voterlist.election.gov.np). The data represents real citizens from:

- **Province:** बागमती प्रदेश (Bagmati Province)
- **District:** काभ्रेपलाञ्चोक (Kavrepalanchok)
- **Municipality:** धुलिखेल नगरपालिका (Dhulikhel Municipality)
- **Wards:** 1-12
- **Total Voters:** 26,193 individuals across 12 electoral wards

### Data Collection Methodology

The voter data was collected using web scraping techniques with R and Selenium WebDriver. The scraper repository: [https://github.com/Hackfest-2025-TER/ScraperElectionCommision](https://github.com/Hackfest-2025-TER/ScraperElectionCommision)

**Technical Implementation:**
```r
# Parallel scraping with 3 WebDriver instances
# Distributed across wards for performance
library(httr)
library(rvest)
library(parallel)
library(doParallel)

NUM_WORKERS <- 3
DRIVER_BASE_PORT <- 4550L  # Ports 4550, 4551, 4552
```

**Data Collection Process:**
1. **Distributed Scraping:** 3 parallel Chrome WebDriver sessions
2. **Ward Coverage:** Each worker handles 4 wards (12 total)
3. **Pagination:** Full pagination support (100 entries per page)
4. **Registration Centers:** All voting centers per ward
5. **Output:** Consolidated CSV with 26K+ voter records

**Schema:**
```csv
VoterID, Name, Age, Gender, SpouseName, ParentName, Province, District, 
VDC, Ward, RegistrationCentre
```

**Privacy Handling:**
- Voter names are masked in UI (`"Ram***"` format)
- Only voter ID is used for cryptographic operations
- No personal data transmitted during authentication
- Server stores hashed commitments only

**CSV Location:** `data/dhulikhel_voter_list_full.csv`

---

## Cryptographic Protocol

### The "Shuffled Purist" Approach

PromiseThread implements a multi-stage cryptographic protocol designed to maximize privacy while maintaining verifiability. The protocol is inspired by mixnet-based voting systems and zk-SNARK membership proofs.

#### Stage 1: Server-Side Commitment and Shuffling

**Purpose:** Destroy the linkage between voter registry order and commitment order.

**Process:**
```python
# 1. Load voter registry from CSV
voters = load_csv("dhulikhel_voter_list_full.csv")

# 2. Compute commitments for each voter
#    Commitment = Hash(VoterID || ServerSecret)
commitments = [sha256(f"{voter.id}:{SERVER_SECRET}") for voter in voters]

# 3. Cryptographically shuffle commitments
#    Uses Fisher-Yates shuffle with cryptographic RNG
shuffled_commitments = cryptographic_shuffle(commitments)

# 4. Build Merkle tree from shuffled leaves
merkle_tree = MerkleTree(shuffled_commitments)
merkle_root = merkle_tree.root

# 5. CRITICAL: Delete the shuffle mapping
#    Server must not retain: original_index -> shuffled_index
#    This ensures server cannot reverse-link commitments to voters
del shuffle_mapping  # Intentional data destruction
```

**Security Property:** After shuffling and map deletion, the server cannot determine which voter corresponds to which commitment, even though it knows all commitments.

**Trust Assumption:** This step requires trusting the Election Commission (server operator) to:
1. Perform the shuffle honestly (not store the mapping)
2. Use a cryptographically secure RNG
3. Publish the Merkle root publicly

**Future Enhancement:** Implement verifiable shuffling using multi-party computation or public randomness beacons (e.g., drand).

#### Stage 2: Client Downloads Anonymity Set

**Purpose:** Enable client-side Merkle proof generation without server involvement.

**Process:**
```typescript
// Client downloads full shuffled commitment list
const response = await fetch('/api/registry/anonymity-set');
const { shuffled_leaves, merkle_root } = await response.json();

// Client now has ~26K commitments (shuffled)
// Size: ~26K × 32 bytes = ~832 KB (acceptable for download)
```

**Performance Consideration:**
- Anonymity set size: ~1 MB for 26K voters
- Download time: < 2 seconds on typical broadband
- Trade-off: Privacy (large anonymity set) vs Performance (download size)

**Scalability Limit:**
For larger registries (>100K voters), implement:
- Batch Merkle trees (partition voters into batches)
- Client-side caching with versioning
- Progressive download with Web Workers

#### Stage 3: Client-Side Proof Generation

**Purpose:** Prove membership in registry without revealing identity.

**Process:**
```typescript
// User inputs: voterID and personal secret
const userInput = {
  voterId: "1234567890",
  secret: "citizenship_number_or_passphrase"
};

// 1. Compute user's commitment (matches server's algorithm)
const commitment = sha256(`${voterId}:${SERVER_SECRET}`);

// 2. Find commitment index in shuffled set
const index = shuffled_leaves.indexOf(commitment);
if (index === -1) throw new Error("Not in registry");

// 3. Compute Merkle proof locally (client-side)
const merkle_path = computeMerklePath(shuffled_leaves, index);

// 4. Generate nullifier (deterministic per voter+secret)
//    Nullifier = Hash(voterId || secret)
//    Different from commitment due to different salt
const nullifier = sha256(`${voterId}:${secret}`);

// 5. Generate zk-SNARK proof
const proof = await generateProof({
  // Private inputs (not revealed)
  voterId: voterId,
  voterSecret: secret,
  merklePathElements: merkle_path.elements,
  merklePathIndices: merkle_path.indices,
  
  // Public inputs (revealed)
  merkleRoot: merkle_root
});

// 6. Send only proof and public signals to server
await fetch('/api/zk/verify', {
  method: 'POST',
  body: JSON.stringify({
    proof: proof.proof,          // zk-SNARK proof
    publicSignals: {
      merkleRoot: merkle_root,
      nullifier: proof.nullifier,
      commitment: proof.commitment
    }
  })
});
```

**Critical Detail:** The Merkle path is **NEVER** transmitted to the server. Only the zk-SNARK proof is sent, which cryptographically proves the prover knows a valid path without revealing the path itself.

#### Stage 4: Server-Side Verification

**Purpose:** Verify proof validity and prevent double-voting without learning identity.

**Process:**
```python
@app.post("/api/zk/verify")
async def verify_proof(request: ProofRequest):
    # 1. Verify zk-SNARK proof against verification key
    is_valid = snarkjs.verify(
        verification_key,
        request.publicSignals,
        request.proof
    )
    
    if not is_valid:
        return {"valid": False, "error": "Invalid proof"}
    
    # 2. Verify Merkle root matches published root
    if request.publicSignals.merkleRoot != PUBLISHED_MERKLE_ROOT:
        return {"valid": False, "error": "Root mismatch"}
    
    # 3. Check nullifier hasn't been used (prevent double-voting)
    if db.query(Nullifier).filter_by(hash=request.nullifier).first():
        return {"valid": False, "error": "Already voted"}
    
    # 4. Store nullifier (prevents future reuse)
    db.add(Nullifier(hash=request.nullifier))
    db.commit()
    
    # 5. Issue anonymous credential
    credential = generate_credential()
    return {
        "valid": True,
        "credential": credential,
        "nullifier_short": request.nullifier[:12] + "..."
    }
```

**Privacy Guarantee:** At this stage, the server knows:
- A valid voter authenticated (proven by zk-SNARK)
- The nullifier (for double-vote prevention)

The server does **NOT** know:
- Which specific voter this is
- The voter's identity
- The Merkle path used
- Any linkage between nullifier and voter identity

#### Circom Circuit Logic

**File:** `blockchain/circuits/citizen_credential.circom`

The zero-knowledge circuit enforces the following constraints:

```circom
template VoterCredential(levels) {
    // Private inputs (witness)
    signal input voterId;
    signal input voterSecret;
    signal input pathElements[levels];
    signal input pathIndices[levels];
    
    // Public inputs
    signal input merkleRoot;
    
    // Outputs
    signal output nullifier;
    signal output voterIdHash;
    signal output commitment;
    
    // Constraint 1: Compute voter ID hash (leaf)
    component voterHasher = Poseidon(1);
    voterHasher.inputs[0] <== voterId;
    voterIdHash <== voterHasher.out;
    
    // Constraint 2: Verify Merkle membership
    component merkleProof = MerkleProof(levels);
    merkleProof.leaf <== voterIdHash;
    // ... path verification ...
    merkleRoot === merkleProof.root;  // ENFORCED
    
    // Constraint 3: Generate nullifier
    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== voterId;
    nullifierHasher.inputs[1] <== voterSecret;
    nullifier <== nullifierHasher.out;
    
    // Constraint 4: Commitment binding
    component commitHasher = Poseidon(2);
    commitHasher.inputs[0] <== voterIdHash;
    commitHasher.inputs[1] <== nullifier;
    commitment <== commitHasher.out;
}
```

**Circuit Parameters:**
- **levels:** 15 (supports up to 2^15 = 32,768 voters)
- **Hash function:** Poseidon (optimized for zk-SNARKs)
- **Proof system:** Groth16 (efficient verification)

**Compilation:**
```bash
circom citizen_credential.circom --r1cs --wasm --sym -o build/circuits
```

**Trusted Setup:**
```bash
# Download Powers of Tau (ceremony)
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_15.ptau

# Generate circuit-specific proving/verification keys
snarkjs groth16 setup citizen_credential.r1cs powersOfTau28_hez_final_15.ptau circuit_final.zkey

# Export verification key
snarkjs zkey export verificationkey circuit_final.zkey verification_key.json
```

---

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                            │
│                  (SvelteKit + TypeScript + WASM)                  │
├──────────────────────────────────────────────────────────────────┤
│  Landing │ Auth/ZK │ Manifesto │ Vote │ Discussion │ Audit Trail │
│   Page   │  Proof  │   List    │  UI  │   Thread   │  Visualizer │
│          │  Gen    │           │      │            │             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                    HTTP/JSON API
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                         BACKEND LAYER                             │
│                  (FastAPI + SQLAlchemy + Python)                  │
├──────────────────────────────────────────────────────────────────┤
│  Voter      │   ZK Proof   │  Manifesto  │   Vote    │  Comment  │
│  Registry   │  Verification│    CRUD     │ Aggregate │   Thread  │
│  (Merkle)   │  (snarkjs)   │             │  Storage  │   Storage │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                    PostgreSQL
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                       DATABASE LAYER                              │
│                      (PostgreSQL 15)                              │
├──────────────────────────────────────────────────────────────────┤
│  voters │ zk_credentials │ politicians │ manifestos │ votes │     │
│         │   (nullifiers) │             │            │       │     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      BLOCKCHAIN LAYER                             │
│              (Hardhat + Solidity + EVM)                           │
├──────────────────────────────────────────────────────────────────┤
│  PromiseRegistry.sol  │  ManifestoRegistry.sol │ ZKVerifier.sol  │
│  - Vote aggregates    │  - Promise hashes      │ - Proof verify  │
│  - Merkle roots       │  - Digital signatures  │ - Nullifier log │
└──────────────────────────────────────────────────────────────────┘
```


### Hybrid Storage Model

The system employs a **two-tier storage architecture** optimized for both privacy and performance:

**ON-CHAIN (Immutable Blockchain):**
- Vote aggregates only (`vote_kept`, `vote_broken` counts)
- Promise hashes (`sha256(title + description + politician)`)
- Merkle roots (batch commitments every N votes)
- Status transitions with timestamps
- Digital signatures (politician wallet proofs)

**OFF-CHAIN (PostgreSQL Database):**
- Full manifesto text and metadata
- Individual vote records (linked to nullifiers, not voters)
- Discussion threads and comments
- Evidence URLs and upvote counts
- Merkle tree leaves (shuffled commitments)

**Rationale:**
- **Scalability:** 26K voters × multiple votes = millions of transactions. Storing individual votes on-chain is prohibitively expensive.
- **Privacy:** Individual votes remain off-chain. Only nullifiers and aggregates are public.
- **Auditability:** Merkle roots enable vote verification without exposing individual votes.
- **Cost:** Database storage is ~$0.001/GB vs blockchain ~$100/GB at scale.

---

## File Structure

### Root Directory

```
HackfestProject/
├── frontend/               # SvelteKit frontend application
├── backend/                # FastAPI backend server
├── blockchain/             # Hardhat smart contracts & circuits
├── data/                   # Voter registry CSV
├── docker-compose.yml      # Orchestration configuration
├── Makefile                # Build automation
└── README.md               # This file
```

### Frontend (`frontend/`)

**Purpose:** Client-side application for voters and politicians. Handles ZK proof generation, UI/UX, and blockchain interaction.

**Technology Stack:**
- **Framework:** SvelteKit 2.0 (SSR + SPA hybrid)
- **Language:** TypeScript 5.0
- **Styling:** Tailwind CSS 3.4
- **ZK Libraries:** snarkjs 0.7.5, circomlibjs 0.1.7
- **Blockchain:** ethers.js 5.7.2
- **Build Tool:** Vite 5.0

**Key Files:**

```
frontend/
├── src/
│   ├── routes/
│   │   ├── +layout.svelte              # Global layout & navigation
│   │   ├── +page.svelte                # Landing page
│   │   ├── auth/
│   │   │   ├── +page.svelte            # ZK authentication UI
│   │   │   └── +page.ts                # Auth page data loader
│   │   ├── manifestos/
│   │   │   ├── +page.svelte            # Manifesto list view
│   │   │   ├── +page.ts                # Data fetching logic
│   │   │   └── [id]/
│   │   │       └── +page.svelte        # Single manifesto detail + discussion
│   │   ├── citizen/
│   │   │   ├── +page.svelte            # Citizen dashboard
│   │   │   └── attestation/
│   │   │       └── +page.svelte        # Voting interface
│   │   ├── politician/
│   │   │   ├── dashboard/+page.svelte  # Politician dashboard
│   │   │   ├── new-manifesto/+page.svelte  # Create promise
│   │   │   └── wallet/+page.svelte     # Digital signature wallet
│   │   ├── verify/+page.svelte         # Vote verification page
│   │   └── audit-trail/+page.svelte    # Blockchain explorer
│   │
│   ├── lib/
│   │   ├── api.ts                      # API client (fetch wrappers)
│   │   ├── stores.ts                   # Svelte stores (auth state, etc.)
│   │   ├── components/
│   │   │   ├── Header.svelte           # Navigation header
│   │   │   ├── Footer.svelte           # Footer component
│   │   │   ├── VoteBox.svelte          # Voting UI component
│   │   │   ├── CommentThread.svelte    # Threaded discussion
│   │   │   ├── BlockchainVisualizer.svelte  # Blockchain explorer
│   │   │   ├── SignatureVerifier.svelte     # Signature validation UI
│   │   │   └── ManifestoCard.svelte    # Promise card component
│   │   └── utils/
│   │       ├── zkProof.ts              # ZK proof generation logic
│   │       └── crypto.ts               # Cryptographic utilities
│   │
│   ├── app.html                        # HTML template
│   ├── app.css                         # Global styles
│   └── vite-env.d.ts                   # TypeScript declarations
│
├── static/
│   └── zk/
│       ├── citizen_credential.wasm     # Compiled circuit (WASM)
│       ├── circuit_final.zkey          # Proving key
│       └── verification_key.json       # Verification key
│
├── svelte.config.js                    # SvelteKit configuration
├── vite.config.js                      # Vite build config
├── tailwind.config.js                  # Tailwind CSS config
├── tsconfig.json                       # TypeScript config
├── package.json                        # Dependencies
└── Dockerfile                          # Frontend container
```

**Data Flow:**

1. **Authentication (`auth/+page.svelte`):**
   ```typescript
   // User enters voterID + secret
   const proof = await generateZKProof(voterId, secret, merklePath);
   const result = await verifyZKProof(proof);
   authStore.setCredential(result.credential);
   ```

2. **Voting (`citizen/attestation/+page.svelte`):**
   ```typescript
   const voteData = {
     manifesto_id: manifestoId,
     vote_type: 'kept', // or 'broken'
     nullifier: authStore.credential.nullifier
   };
   await submitVote(voteData);
   ```

3. **Discussion (`manifestos/[id]/+page.svelte`):**
   ```typescript
   const comment = {
     manifesto_id: id,
     content: userInput,
     nullifier: authStore.credential.nullifier,
     parent_id: replyToId || null
   };
   await addComment(comment);
   ```

**Environment Variables (`.env`):**
```env
VITE_API_URL=http://localhost:8000
VITE_BLOCKCHAIN_RPC=http://localhost:8545
```

### Backend (`backend/`)

**Purpose:** API server handling authentication, data persistence, and blockchain interaction.

**Technology Stack:**
- **Framework:** FastAPI 0.115.6
- **ORM:** SQLAlchemy 2.0.36
- **Database:** PostgreSQL 15
- **Migration:** Alembic 1.14.0
- **Blockchain:** web3.py 7.5.0, eth-account 0.13.1
- **Testing:** pytest 8.3.4

**Key Files:**

```
backend/
├── main.py                          # FastAPI application entry point
├── main_db.py                       # Database-backed version (production)
├── main_inmemory.py                 # In-memory version (testing)
├── models.py                        # SQLAlchemy ORM models
├── database.py                      # Database connection & session management
├── crypto_utils.py                  # Cryptographic functions (signatures, hashes)
├── blockchain_service.py            # Web3 integration (contract calls)
├── migrate.py                       # Migration runner
├── seed_data.py                     # Sample data generator
├── import_csv.py                    # Voter registry CSV importer
├── verify_db.py                     # Database integrity checker
├── test_api.py                      # API endpoint tests
│
├── migrations/                      # Alembic migration files
│   ├── env.py                       # Alembic environment
│   └── versions/
│       ├── 51ee1b7bf96e_initial_migration.py
│       └── add_politician_slug.py
│
├── alembic.ini                      # Alembic configuration
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Backend container
├── DATABASE_QUICK_REF.md            # Database schema reference
└── MIGRATIONS.md                    # Migration guide
```

**Core Modules:**

#### `main.py` - API Endpoints

**Authentication Endpoints:**
```python
@app.post("/api/registry/lookup")
async def lookup_voter(request: VoterLookupRequest, db: Session):
    """
    Look up voter by ID, return Merkle proof.
    
    Input: {"voter_id": "1234567890"}
    Output: {
        "found": true,
        "voter_id_hash": "0xabc...",
        "name_masked": "Ram***",
        "merkle_proof": [{"hash": "0x...", "position": "left"}, ...]
    }
    """
    
@app.post("/api/zk/verify")
async def verify_zk_proof(request: ZKProofRequest, db: Session):
    """
    Verify zk-SNARK proof and issue credential.
    
    Input: {
        "proof": "...",  # zk-SNARK proof
        "publicSignals": {
            "merkleRoot": "0x...",
            "nullifier": "0x...",
            "commitment": "0x..."
        }
    }
    Output: {
        "valid": true,
        "credential": "token",
        "nullifier_short": "0xabc...def"
    }
    """
```

**Manifesto Endpoints:**
```python
@app.get("/api/manifestos")
async def get_manifestos(
    status: Optional[str] = None,
    politician_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List manifestos with filters.
    
    Query params:
    - status: pending|kept|broken
    - politician_id: filter by politician
    - category: infrastructure|economy|education|health
    
    Returns: List of manifesto objects with vote counts
    """

@app.get("/api/manifestos/{id}")
async def get_manifesto(id: int, db: Session):
    """Get single manifesto with full details + comments."""
```

**Voting Endpoints:**
```python
@app.post("/api/votes")
async def submit_vote(vote: VoteRequest, db: Session):
    """
    Submit or change vote on manifesto.
    
    Input: {
        "manifesto_id": 1,
        "vote_type": "kept" | "broken",
        "nullifier": "0x...",
        "evidence_url": "https://..." (optional)
    }
    
    Logic:
    1. Verify nullifier exists (user authenticated)
    2. Check grace period passed
    3. Check if already voted (allow vote changes)
    4. Update aggregates
    5. Return vote_hash for verification
    """
```

#### `models.py` - Database Schema

**Voter Table:**
```python
class Voter(Base):
    __tablename__ = 'voters'
    
    id = Column(Integer, primary_key=True)
    voter_id = Column(String(50), unique=True, index=True)  # From CSV
    name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))
    province = Column(String(50))
    district = Column(String(100))
    vdc = Column(String(100))                # Municipality
    ward = Column(Integer)
    merkle_leaf = Column(String(66))         # Keccak256(voter_id)
```

**ZKCredential Table:**
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

**Manifesto Table:**
```python
class Manifesto(Base):
    __tablename__ = 'manifestos'
    
    id = Column(Integer, primary_key=True)
    politician_id = Column(Integer, ForeignKey('politicians.id'))
    title = Column(String(500))
    description = Column(Text)
    category = Column(String(50))            # infrastructure, economy, ...
    status = Column(String(20))              # pending, kept, broken
    promise_hash = Column(String(66))        # SHA256 for blockchain
    grace_period_end = Column(DateTime)      # Voting locked until this date
    vote_kept = Column(Integer, default=0)   # Aggregate count
    vote_broken = Column(Integer, default=0)
    signature = Column(Text)                 # ECDSA signature (hex)
    signed_by_address = Column(String(42))   # Politician's wallet
```

**ManifestoVote Table:**
```python
class ManifestoVote(Base):
    __tablename__ = 'manifesto_votes'
    
    id = Column(Integer, primary_key=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'))
    nullifier = Column(String(128), index=True)  # Anonymous voter ID
    vote_type = Column(String(10))                # kept | broken
    vote_hash = Column(String(66), unique=True)   # For verification
    created_at = Column(DateTime)
    
    # Composite unique constraint: one vote per nullifier per manifesto
    __table_args__ = (
        UniqueConstraint('manifesto_id', 'nullifier'),
    )
```

**Comment Table:**
```python
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'))
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    nullifier = Column(String(128))           # Anonymous commenter
    content = Column(Text)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime)
    
    # Self-referential relationship for threading
    replies = relationship("Comment", backref="parent", remote_side=[id])
```

#### `crypto_utils.py` - Cryptographic Operations

```python
def generate_key_pair() -> Tuple[str, str, str]:
    """
    Generate Ethereum-compatible key pair.
    
    Returns:
        (private_key, public_key, address)
    
    WARNING: private_key must be shown to user ONCE and never stored.
    """
    account = Account.create()
    return (account.key.hex(), account.public_key.hex(), account.address)

def compute_manifesto_hash(title: str, description: str, politician_id: int) -> str:
    """
    Compute deterministic hash for manifesto (for blockchain storage).
    
    Hash(title || description || politician_id || timestamp)
    """
    data = f"{title}:{description}:{politician_id}".encode()
    return "0x" + hashlib.sha256(data).hexdigest()

def verify_signature(message_hash: str, signature: str, address: str) -> bool:
    """
    Verify ECDSA signature against expected address.
    
    Used to verify politician signed their manifesto.
    """
    recovered = Account.recover_message(
        encode_defunct(hexstr=message_hash),
        signature=signature
    )
    return recovered.lower() == address.lower()
```

#### `blockchain_service.py` - Smart Contract Integration

```python
class BlockchainService:
    def __init__(self, rpc_url: str = "http://localhost:8545"):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.promise_registry = self.load_contract("PromiseRegistry")
        
    def store_vote_aggregate(self, promise_id: int, kept: int, broken: int):
        """
        Store vote aggregates on-chain.
        
        Calls: PromiseRegistry.updateVotes(promiseId, kept, broken)
        """
        tx = self.promise_registry.functions.updateVotes(
            promise_id, kept, broken
        ).transact()
        return self.web3.eth.wait_for_transaction_receipt(tx)
    
    def store_merkle_root(self, root: str, batch_id: int):
        """
        Store Merkle root for vote batch.
        
        Calls: PromiseRegistry.storeMerkleRoot(batchId, root)
        """
```

**Environment Variables (`.env`):**
```env
DATABASE_URL=postgresql://promisethread:hackfest2025@localhost:5432/promisethread
BLOCKCHAIN_RPC_URL=http://localhost:8545
SECRET_KEY=your-secret-key-change-in-production
```

**Database Setup:**
```bash
# Create database
createdb -U postgres promisethread

# Run migrations
cd backend
alembic upgrade head

# Import voter data
python import_csv.py --file ../data/dhulikhel_voter_list_full.csv

# Seed sample data
python seed_data.py

# Verify setup
python verify_db.py
```

### Blockchain (`blockchain/`)

**Purpose:** Smart contracts for on-chain data storage and zk-SNARK verification.

**Technology Stack:**
- **Framework:** Hardhat 2.19.0
- **Language:** Solidity 0.8.19
- **ZK Circuits:** Circom 2.0.0
- **Testing:** Hardhat Test Runner
- **Network:** Local node (dev), Polygon Mumbai (testnet), Avalanche Fuji (testnet)

**Key Files:**

```
blockchain/
├── contracts/
│   ├── PromiseRegistry.sol          # Vote aggregates storage
│   ├── ManifestoRegistry.sol        # Promise hash storage
│   └── ZKVerifier.sol               # ZK proof verification contract
│
├── circuits/
│   └── citizen_credential.circom    # Voter membership circuit
│
├── scripts/
│   └── deploy.js                    # Deployment script
│
├── test/
│   ├── PromiseRegistry.test.js
│   └── ManifestoRegistry.test.js
│
├── hardhat.config.js                # Network configuration
├── deployments.json                 # Deployed contract addresses
└── package.json                     # Dependencies
```

#### `contracts/PromiseRegistry.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract PromiseRegistry {
    struct Promise {
        bytes32 promiseHash;         // SHA256 of promise content
        uint256 voteKept;             // Aggregate: votes for "kept"
        uint256 voteBroken;           // Aggregate: votes for "broken"
        uint256 createdAt;
        uint256 gracePeriodEnd;
        bool finalized;
    }
    
    mapping(uint256 => Promise) public promises;
    mapping(uint256 => bytes32) public merkleBatches;  // Batch ID => Merkle root
    
    event PromiseCreated(uint256 indexed promiseId, bytes32 promiseHash);
    event VotesUpdated(uint256 indexed promiseId, uint256 kept, uint256 broken);
    event MerkleRootStored(uint256 indexed batchId, bytes32 root);
    
    function createPromise(
        uint256 promiseId,
        bytes32 promiseHash,
        uint256 gracePeriodEnd
    ) external {
        require(promises[promiseId].createdAt == 0, "Promise exists");
        
        promises[promiseId] = Promise({
            promiseHash: promiseHash,
            voteKept: 0,
            voteBroken: 0,
            createdAt: block.timestamp,
            gracePeriodEnd: gracePeriodEnd,
            finalized: false
        });
        
        emit PromiseCreated(promiseId, promiseHash);
    }
    
    function updateVotes(
        uint256 promiseId,
        uint256 kept,
        uint256 broken
    ) external {
        require(promises[promiseId].createdAt > 0, "Promise not found");
        require(block.timestamp >= promises[promiseId].gracePeriodEnd, "Grace period active");
        
        promises[promiseId].voteKept = kept;
        promises[promiseId].voteBroken = broken;
        
        emit VotesUpdated(promiseId, kept, broken);
    }
    
    function storeMerkleRoot(uint256 batchId, bytes32 root) external {
        merkleBatches[batchId] = root;
        emit MerkleRootStored(batchId, root);
    }
}
```

#### `contracts/ZKVerifier.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ZKVerifier {
    mapping(bytes32 => bool) public usedNullifiers;
    bytes32 public merkleRoot;
    
    event NullifierUsed(bytes32 indexed nullifier);
    event MerkleRootUpdated(bytes32 indexed root);
    
    function setMerkleRoot(bytes32 _root) external {
        merkleRoot = _root;
        emit MerkleRootUpdated(_root);
    }
    
    function verifyAndRegister(
        bytes32 nullifier,
        bytes32 commitment,
        uint[8] calldata proof  // Groth16 proof (simplified)
    ) external returns (bool) {
        require(!usedNullifiers[nullifier], "Nullifier already used");
        require(merkleRoot != bytes32(0), "Merkle root not set");
        
        // In production, verify the actual zk-SNARK proof here
        // bool isValid = verifyProof(proof, [merkleRoot, nullifier, commitment]);
        // For MVP, we trust the backend verification
        
        usedNullifiers[nullifier] = true;
        emit NullifierUsed(nullifier);
        
        return true;
    }
}
```

#### `circuits/citizen_credential.circom`

See [Circom Circuit Logic](#circom-circuit-logic) above for full implementation.

**Compilation Process:**
```bash
# 1. Compile circuit to R1CS + WASM
circom citizen_credential.circom --r1cs --wasm --sym -o build/circuits

# 2. Download Powers of Tau (15th power = 32K constraints)
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_15.ptau

# 3. Generate proving key and verification key
snarkjs groth16 setup build/circuits/citizen_credential.r1cs \
    powersOfTau28_hez_final_15.ptau \
    build/circuits/circuit_final.zkey

# 4. Export verification key (for server-side verification)
snarkjs zkey export verificationkey \
    build/circuits/circuit_final.zkey \
    build/circuits/verification_key.json

# 5. Copy WASM and keys to frontend
cp build/circuits/citizen_credential_js/citizen_credential.wasm frontend/static/zk/
cp build/circuits/circuit_final.zkey frontend/static/zk/
cp build/circuits/verification_key.json frontend/static/zk/
```

**Network Configuration (`hardhat.config.js`):**
```javascript
module.exports = {
  solidity: "0.8.19",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    },
    mumbai: {
      url: process.env.MUMBAI_RPC_URL,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY],
      chainId: 80001
    },
    fuji: {
      url: process.env.FUJI_RPC_URL,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY],
      chainId: 43113
    }
  }
};
```

### Data (`data/`)

```
data/
└── dhulikhel_voter_list_full.csv    # 26,193 voter records
```

**CSV Schema:**
```csv
VoterID,Name,Age,Gender,SpouseName,ParentName,Province,District,VDC,Ward,RegistrationCentre
123456789,राम बहादुर तामाङ,45,पुरुष,सिता देवी तामाङ,धन बहादुर तामाङ,बागमती प्रदेश,काभ्रेपलाञ्चोक,धुलिखेल नगरपालिका,1,प्रथमिक विद्यालय
```

---

## Installation

### Prerequisites

**System Requirements:**
- Operating System: Linux, macOS, or Windows (WSL recommended)
- RAM: Minimum 8 GB
- Disk Space: 10 GB free
- Network: Broadband internet for package downloads

**Software Dependencies:**

1. **Node.js** (v18 or higher)
   ```bash
   # Verify installation
   node --version  # Should be >= v18.0.0
   npm --version   # Should be >= 9.0.0
   
   # Install via nvm (recommended)
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 18
   nvm use 18
   ```

2. **Python** (3.10 or higher)
   ```bash
   # Verify installation
   python3 --version  # Should be >= 3.10
   pip3 --version
   
   # Install via pyenv (recommended)
   curl https://pyenv.run | bash
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```

3. **PostgreSQL** (15 or higher)
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql-15 postgresql-contrib-15
   
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Verify
   psql --version  # Should be 15.x
   ```

4. **Circom** (2.0 or higher) - For circuit compilation
   ```bash
   # Install Rust (required for Circom)
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # Install Circom
   git clone https://github.com/iden3/circom.git
   cd circom
   cargo build --release
   cargo install --path circom
   
   # Verify
   circom --version  # Should be >= 2.0.0
   ```

5. **Docker** (optional, for containerized deployment)
   ```bash
   # Install Docker Engine
   curl -fsSL https://get.docker.com | sh
   
   # Install Docker Compose
   sudo apt install docker-compose  # Linux
   # or
   brew install docker-compose      # macOS
   
   # Verify
   docker --version
   docker-compose --version
   ```

### Manual Installation

#### 1. Clone Repository

```bash
git clone https://github.com/Hackfest-2025-TER/HackfestProject.git
cd HackfestProject
```

#### 2. Database Setup

```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql@15  # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE promisethread;
CREATE USER promisethread WITH ENCRYPTED PASSWORD 'hackfest2025';
GRANT ALL PRIVILEGES ON DATABASE promisethread TO promisethread;
\q
```

```bash
# Verify connection
psql -U promisethread -d promisethread -h localhost
# Password: hackfest2025
```

#### 3. Backend Setup

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

# Import voter data
python import_csv.py --file ../data/dhulikhel_voter_list_full.csv

# Expected output:
# ✓ Loaded 26,193 voters from CSV
# ✓ Computing Merkle leaves...
# ✓ Inserted 26,193 voters into database
# ✓ Merkle root: 0xabc123...

# Seed sample politicians and manifestos
python seed_data.py

# Expected output:
# ✓ Created 5 politicians
# ✓ Created 12 manifestos
# ✓ Database ready

# Verify database integrity
python verify_db.py

# Expected output:
# Database: promisethread
# Total voters: 26,193
# Total credentials: 0
# Total politicians: 5
# Total manifestos: 12
# ✓ All checks passed
```

#### 4. Blockchain Setup

```bash
cd ../blockchain

# Install dependencies
npm install
# or
pnpm install

# Compile smart contracts
npx hardhat compile

# Expected output:
# Compiled 3 Solidity files successfully

# Start local blockchain node (separate terminal)
npx hardhat node

# Expected output:
# Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/
# 
# Accounts:
# Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
# Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
# ...

# Deploy contracts (new terminal)
npx hardhat run scripts/deploy.js --network localhost

# Expected output:
# Deploying contracts to localhost...
# PromiseRegistry deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
# ManifestoRegistry deployed to: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
# ZKVerifier deployed to: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
# ✓ Deployment complete
```

**Save Contract Addresses:**
```bash
# File: blockchain/deployments.json (auto-generated)
{
  "localhost": {
    "PromiseRegistry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ManifestoRegistry": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "ZKVerifier": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
  }
}
```

#### 5. Circuit Compilation (Optional - For Production ZK)

**Note:** This step is required only if implementing actual zk-SNARK verification. The MVP uses simplified authentication.

```bash
cd blockchain

# Compile Circom circuit
mkdir -p build/circuits
circom circuits/citizen_credential.circom \
    --r1cs --wasm --sym \
    -o build/circuits

# Expected output:
# template instances: 33
# non-linear constraints: 1024
# linear constraints: 0
# public inputs: 1
# private inputs: 33
# public outputs: 3
# wires: 1058
# labels: 2116

# Download Powers of Tau file (265 MB)
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_15.ptau

# Generate proving key (this takes ~5-10 minutes)
snarkjs groth16 setup \
    build/circuits/citizen_credential.r1cs \
    powersOfTau28_hez_final_15.ptau \
    build/circuits/circuit_final.zkey

# Expected output:
# [INFO]  snarkJS: Groth16 Zkey Generator started
# [INFO]  snarkJS: Circuit loaded successfully
# [INFO]  snarkJS: Generating proving key...
# [INFO]  snarkJS: Proving key generated successfully

# Export verification key
snarkjs zkey export verificationkey \
    build/circuits/circuit_final.zkey \
    build/circuits/verification_key.json

# Copy artifacts to frontend
cp build/circuits/citizen_credential_js/citizen_credential.wasm \
   ../frontend/static/zk/
cp build/circuits/circuit_final.zkey \
   ../frontend/static/zk/
cp build/circuits/verification_key.json \
   ../frontend/static/zk/

# Verify artifacts copied
ls -lh ../frontend/static/zk/
# Expected:
# citizen_credential.wasm   (~45 KB)
# circuit_final.zkey        (~1.2 MB)
# verification_key.json     (~2 KB)
```

#### 6. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
# or
pnpm install

# Configure environment
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_BLOCKCHAIN_RPC=http://localhost:8545
VITE_PROMISE_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
EOF

# Build frontend (optional - dev mode doesn't require build)
npm run build

# Expected output:
# vite v5.0.0 building for production...
# ✓ 245 modules transformed.
# build/client complete in 12.3s
# build/server complete in 8.7s
```

#### 7. Start Development Servers

**Terminal 1 - Blockchain:**
```bash
cd blockchain
npx hardhat node
# Runs on http://localhost:8545
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Expected output:
# INFO:     Will watch for changes in these directories: ['d:\\hackfest\\HackfestProject\\backend']
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# ✓ Database connection established
# ✓ Built Merkle tree with 26193 voters. Root: 0xabc123...
# INFO:     Application startup complete.
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev

# Expected output:
# 
#   VITE v5.0.0  ready in 1234 ms
# 
#   ➜  Local:   http://localhost:3000/
#   ➜  Network: http://192.168.1.100:3000/
#   ➜  press h + enter to show help
```

**Access Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Blockchain RPC: http://localhost:8545

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/Hackfest-2025-TER/HackfestProject.git
cd HackfestProject

# Start all services
docker-compose up --build

# Expected output:
# Creating network "promisethread-network"
# Creating volume "postgres_data"
# Creating promisethread-db ... done
# Creating promisethread-blockchain ... done
# Creating promisethread-backend ... done
# Creating promisethread-frontend ... done
```

**Service Health Checks:**
```bash
# Check all containers running
docker-compose ps

# Expected:
# NAME                      STATUS              PORTS
# promisethread-db          Up (healthy)        0.0.0.0:5432->5432/tcp
# promisethread-blockchain  Up (healthy)        0.0.0.0:8545->8545/tcp
# promisethread-backend     Up                  0.0.0.0:8000->8000/tcp
# promisethread-frontend    Up                  0.0.0.0:3000->3000/tcp
```

### Docker Compose Configuration

**File:** `docker-compose.yml`

```yaml
services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: promisethread-db
    environment:
      POSTGRES_USER: promisethread
      POSTGRES_PASSWORD: hackfest2025
      POSTGRES_DB: promisethread
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U promisethread -d promisethread"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - promisethread-network

  # Blockchain Node
  blockchain:
    build: ./blockchain
    container_name: promisethread-blockchain
    ports:
      - "8545:8545"
    healthcheck:
      test: ["CMD", "curl", "-sf", "-X", "POST", 
             "-H", "Content-Type: application/json",
             "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}',
             "http://localhost:8545"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks:
      - promisethread-network

  # Backend API
  backend:
    build: ./backend
    container_name: promisethread-backend
    depends_on:
      postgres:
        condition: service_healthy
      blockchain:
        condition: service_healthy
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://promisethread:hackfest2025@postgres:5432/promisethread
      - BLOCKCHAIN_RPC_URL=http://blockchain:8545
      - SECRET_KEY=change-this-in-production
    volumes:
      - ./data:/app/data:ro        # Mount CSV data as read-only
    networks:
      - promisethread-network

  # Frontend Application
  frontend:
    build: ./frontend
    container_name: promisethread-frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_BLOCKCHAIN_RPC=http://localhost:8545
    networks:
      - promisethread-network

volumes:
  postgres_data:
    driver: local

networks:
  promisethread-network:
    driver: bridge
```

### Individual Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run database migrations and start server
CMD ["sh", "-c", "\
    until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do \
      echo 'Waiting for PostgreSQL...'; \
      sleep 2; \
    done && \
    alembic upgrade head && \
    python import_csv.py --file /app/data/dhulikhel_voter_list_full.csv && \
    python seed_data.py && \
    uvicorn main:app --host 0.0.0.0 --port 8000 \
"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm
RUN pnpm install

# Copy application code
COPY . .

# Build application
RUN pnpm run build

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "build"]
```

**Blockchain Dockerfile** (`blockchain/Dockerfile`):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy contracts and scripts
COPY . .

# Compile contracts
RUN npx hardhat compile

# Expose RPC port
EXPOSE 8545

# Start Hardhat node and deploy contracts
CMD ["sh", "-c", "\
    npx hardhat node & \
    sleep 5 && \
    npx hardhat run scripts/deploy.js --network localhost && \
    wait \
"]
```

### Docker Commands Reference

```bash
# Build and start all services
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v

# View logs
docker-compose logs -f                    # All services
docker-compose logs -f backend            # Specific service

# Execute command in running container
docker-compose exec backend bash          # Open shell
docker-compose exec postgres psql -U promisethread -d promisethread

# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose up -d --build backend

# View resource usage
docker stats
```

### Production Deployment Considerations

**1. Environment Variables (`.env.production`):**
```env
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/promisethread
DB_PASSWORD=$(openssl rand -base64 32)

# Backend
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_ORIGINS=https://promisethread.example.com

# Blockchain
BLOCKCHAIN_RPC_URL=https://polygon-rpc.com  # Use public RPC or Infura

# Frontend
VITE_API_URL=https://api.promisethread.example.com
```

**2. HTTPS/TLS Termination:**
Use Nginx or Traefik as reverse proxy:

```yaml
# docker-compose.prod.yml (partial)
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
```

**3. Resource Limits:**
```yaml
# Add to each service in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

**4. Persistent Storage:**
```bash
# Backup database
docker-compose exec postgres pg_dump -U promisethread promisethread > backup.sql

# Restore database
docker-compose exec -T postgres psql -U promisethread promisethread < backup.sql
```

---

## Security Model

### Trust Assumptions

This system operates under specific trust assumptions that must be clearly understood:

**1. Honest Dealer (Election Commission):**
- **Assumption:** The server operator (Election Commission) performs the cryptographic shuffle honestly and deletes the shuffle mapping.
- **Impact:** If violated, the server could link voters to their commitments (but NOT to their votes/nullifiers).
- **Mitigation:** Future implementations should use verifiable shuffling (multi-party computation) or public randomness beacons.

**2. Secure Secret Distribution:**
- **Assumption:** Each voter receives a unique secret through a secure channel (e.g., citizenship number, biometric-verified distribution).
- **Current MVP:** ALL voters share the demo secret `"1234567890"` (for demonstration only).
- **Impact:** Anyone knowing the shared secret can impersonate any voter.
- **Production Requirement:** Unique secrets per voter, distributed via SMS/email/physical card from Election Commission.

**3. Client-Side Security:**
- **Assumption:** Users run the proof generation in a trusted environment (their own browser).
- **Attack:** Malicious browser extensions or compromised devices could steal voterId/secret.
- **Mitigation:** Use hardware security modules (HSM) or secure enclaves for secret storage in production.

**4. Blockchain Integrity:**
- **Assumption:** The blockchain network is secure and immutable (51% attack resistance).
- **Current:** Local Hardhat node (development only).
- **Production:** Deploy to established networks (Polygon, Avalanche, Ethereum L2).

### Current MVP Limitations

**The demonstration system uses simplified cryptography and has known limitations:**

**1. Shared Demo Secret:**
```python
# backend/main.py
DEMO_SECRET = "1234567890"  # ⚠️ SHARED BY ALL VOTERS
```
- **Risk:** Complete authentication bypass
- **Fix:** Unique secrets per voter from Election Commission

**2. Simulated ZK Proofs:**
```typescript
// frontend/src/lib/utils/zkProof.ts
const proof = await sha256(`proof:${voterId}:${Date.now()}`);
// ⚠️ This is NOT a zk-SNARK, just a hash
```
- **Risk:** No cryptographic proof that user knows valid voterId+secret
- **Fix:** Implement actual snarkjs proof generation with compiled circuits

**3. Weak Merkle Validation:**
```python
# backend/main.py
if not request.merkle_proof or len(request.merkle_proof) < 1:
    return {"valid": False}
# ⚠️ Only checks array length, not cryptographic validity
```
- **Risk:** Fake proofs accepted
- **Fix:** Compute and verify Merkle root from proof path

**4. LocalStorage Credential Storage:**
```typescript
// frontend/src/lib/stores.ts
localStorage.setItem('auth', JSON.stringify(credential));
// ⚠️ Vulnerable to XSS attacks
```
- **Risk:** Credential theft via malicious scripts
- **Fix:** Use sessionStorage + encryption, or HTTP-only cookies

**5. No Rate Limiting:**
- **Risk:** Voter ID enumeration, brute force attacks
- **Fix:** Implement rate limiting (10 requests/minute per IP)

**6. No HTTPS Enforcement:**
- **Risk:** Man-in-the-middle attacks, credential interception
- **Fix:** Enforce HTTPS in production with HSTS headers

### Production Security Checklist

Before deploying to production, implement:

- [ ] **Unique voter secrets** (distributed by Election Commission)
- [ ] **Actual zk-SNARK proof generation** (snarkjs + compiled circuits)
- [ ] **Server-side proof verification** (verification key checking)
- [ ] **Encrypted credential storage** (HTTP-only cookies or encrypted sessionStorage)
- [ ] **HTTPS enforcement** (TLS 1.3, HSTS headers)
- [ ] **Rate limiting** (API throttling, CAPTCHA for voter lookup)
- [ ] **Input validation** (regex on voterID, SQL injection prevention)
- [ ] **CSP headers** (Content Security Policy to prevent XSS)
- [ ] **Device fingerprinting** (bind credentials to device)
- [ ] **Audit logging** (log all authentication attempts)
- [ ] **Penetration testing** (third-party security audit)
- [ ] **Bug bounty program** (incentivize responsible disclosure)

**Cryptographic Improvements:**

- [ ] **Verifiable shuffling** (multi-party computation for shuffle)
- [ ] **Distributed key generation** (no single point of trust)
- [ ] **Hardware security modules** (HSM for secret storage)
- [ ] **Threshold signatures** (require M-of-N for sensitive operations)
- [ ] **Zero-knowledge proof batching** (aggregate proofs for efficiency)

---

## Future Roadmap

### Phase 1: Production-Ready ZK (Q1 2026)

**Objective:** Implement full zk-SNARK verification pipeline.

**Tasks:**
1. Compile Circom circuits with production parameters
2. Perform trusted setup ceremony (multi-party computation)
3. Implement client-side proof generation (snarkjs in Web Workers)
4. Add server-side proof verification (py_ecc or verification contract)
5. Optimize circuit constraints (reduce proving time to <5 seconds)

**Deliverables:**
- Working zk-SNARK authentication
- Browser-based proof generation (WASM)
- Sub-10-second authentication flow

### Phase 2: Verifiable Shuffling (Q2 2026)

**Objective:** Eliminate "Honest Dealer" assumption.

**Approach:**
- Multi-party computation for shuffle
- Public randomness beacon (drand.love)
- Zero-knowledge shuffle proofs

**Technology:**
- `mixnet` library for verifiable shuffling
- Distributed key generation (DKG)
- Publicly auditable shuffle transcript

### Phase 3: Scalability Enhancements (Q3 2026)

**Objective:** Support 1M+ voters efficiently.

**Optimizations:**
1. **Batched Merkle Trees:**
   - Partition voters into batches of 10K
   - Parallel proof generation
   - Reduce client download to ~100 KB

2. **Recursive zk-SNARKs:**
   - Prove "I know a proof of membership"
   - Constant-size proofs regardless of anonymity set

3. **Layer 2 Deployment:**
   - Deploy to zkSync, StarkNet, or Polygon zkEVM
   - Sub-$0.01 transaction costs
   - 1000+ TPS throughput

### Phase 4: Mobile Application (Q4 2026)

**Objective:** Native mobile apps for iOS/Android.

**Features:**
- Biometric authentication (fingerprint/Face ID)
- Push notifications for vote deadlines
- Offline proof generation (sync later)
- QR code voter secret distribution

**Technology:**
- React Native or Flutter
- react-native-zkp for mobile proving
- Secure Enclave for secret storage (iOS)
- TrustZone for secret storage (Android)

### Phase 5: Advanced Features (2027)

**Governance Mechanisms:**
- Quadratic voting (prevent vote buying)
- Conviction voting (time-weighted votes)
- Delegated voting (liquid democracy)

**Evidence Verification:**
- IPFS integration for evidence storage
- Content addressing for tamper-proof links
- Automatic fact-checking API integration

**Analytics & Visualization:**
- Real-time vote dashboards
- Geographic heat maps
- Promise fulfillment trends over time

**AI-Powered Moderation:**
- Toxicity detection in comments
- Misinformation flagging
- Sentiment analysis

### Research Directions

**1. Post-Quantum Cryptography:**
- Transition to lattice-based zk-SNARKs
- Quantum-resistant signature schemes

**2. Privacy-Preserving Aggregation:**
- Homomorphic encryption for vote tallying
- Secure multi-party computation for statistics

**3. Blockchain Interoperability:**
- Cross-chain vote verification
- Multi-chain deployment (Ethereum, Polygon, Avalanche)

**4. Decentralized Storage:**
- IPFS for manifesto content
- Arweave for permanent archiving
- Filecoin for incentivized storage

---

## References

### Academic Papers

1. **Groth16:** Jens Groth. "On the Size of Pairing-Based Non-interactive Arguments." EUROCRYPT 2016.
2. **Merkle Trees:** Ralph C. Merkle. "A Digital Signature Based on a Conventional Encryption Function." CRYPTO 1987.
3. **Mix Networks:** David Chaum. "Untraceable Electronic Mail, Return Addresses, and Digital Pseudonyms." Communications of the ACM, 1981.
4. **zk-SNARKs:** Nir Bitansky, Ran Canetti, Alessandro Chiesa, Eran Tromer. "From Extractable Collision Resistance to Succinct Non-Interactive Arguments of Knowledge." ITCS 2012.

### Technical Documentation

- **Circom Documentation:** https://docs.circom.io/
- **snarkjs Guide:** https://github.com/iden3/snarkjs
- **Poseidon Hash:** https://www.poseidon-hash.info/
- **SvelteKit:** https://kit.svelte.dev/docs
- **FastAPI:** https://fastapi.tiangolo.com/
- **Hardhat:** https://hardhat.org/docs
- **SQLAlchemy:** https://docs.sqlalchemy.org/

### Security Resources

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Web3 Security:** https://consensys.github.io/smart-contract-best-practices/
- **ZK Security:** https://0xparc.org/blog/zk-security
- **Ethereum Security:** https://ethereum.org/en/developers/docs/security/

### Related Projects

- **Semaphore:** Privacy-preserving signaling (similar ZK approach)
- **MACI:** Minimal Anti-Collusion Infrastructure (for voting)
- **Zcash:** Privacy cryptocurrency (zk-SNARK pioneer)
- **Tornado Cash:** Privacy mixer (Merkle tree + nullifiers)

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

**Priority Areas:**
1. Production zk-SNARK implementation
2. Security enhancements
3. Scalability optimizations
4. Documentation improvements

---

## Support

- **GitHub Issues:** https://github.com/Hackfest-2025-TER/HackfestProject/issues
- **Documentation:** https://promisethread.docs.example.com
- **Discord:** https://discord.gg/promisethread

---

**Built with ❤️ for democracy and transparency.**

*Hackfest 2025 - Team TER*

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
- **PostgreSQL 15+** (for database)
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

**1. Database (PostgreSQL):**
```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or
sudo apt install postgresql postgresql-contrib  # Ubuntu

# Start PostgreSQL service
brew services start postgresql@15  # macOS
# or
sudo systemctl start postgresql  # Ubuntu

# Create database and user
psql postgres -c "CREATE USER promisethread WITH PASSWORD 'hackfest2025' CREATEDB;"
psql postgres -c "CREATE DATABASE promisethread OWNER promisethread;"

# Initialize database with migrations
cd backend
pip install -r requirements.txt
python migrate.py init
```

**2. Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**3. Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**4. Blockchain:**
```bash
cd blockchain
npm install
npx hardhat node  # In one terminal
npx hardhat run scripts/deploy.js --network localhost  # In another
```

## 🗄️ Database Management

PromiseThread uses **PostgreSQL** with **Alembic** for migrations.

**Quick Commands:**
```bash
cd backend

# Initialize database (first time)
python migrate.py init

# Check migration status
python migrate.py status

# Apply migrations
python migrate.py upgrade

# Import voter data
python migrate.py import

# Seed sample data
python migrate.py seed

# Reset database (⚠️ deletes all data)
python migrate.py reset
```

**Database Schema:**
- `voters` - 25,924 voter records from Dhulikhel election commission
- `zk_credentials` - Anonymous authentication credentials
- `politicians` - Political figures
- `manifestos` - Political promises
- `manifesto_votes` - Individual votes (anonymous via nullifier)
- `comments` - Discussion threads
- `comment_votes` - Upvote/downvote tracking
- `audit_logs` - Blockchain simulation
- `merkle_roots` - Merkle tree roots

See [`backend/MIGRATIONS.md`](backend/MIGRATIONS.md) for detailed documentation.

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
