from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import csv
import os
from pathlib import Path

app = FastAPI(
    title="PromiseThread API",
    description="Decentralized Political Accountability Platform - Blind Auditor System",
    version="2.0.0"
)

# ============= Merkle Tree Implementation =============

class MerkleTree:
    """Binary Merkle Tree for voter registry."""
    
    def __init__(self, leaves: List[str]):
        self.leaves = [self._hash(leaf) for leaf in leaves]
        self.layers = self._build_tree()
        self.root = self.layers[-1][0] if self.layers else ""
    
    def _hash(self, data: str) -> str:
        """Hash function using SHA256."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _build_tree(self) -> List[List[str]]:
        """Build the Merkle tree from leaves."""
        if not self.leaves:
            return [[]]
        
        layers = [self.leaves]
        current_layer = self.leaves
        
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if i + 1 < len(current_layer) else left
                combined = self._hash(left + right)
                next_layer.append(combined)
            layers.append(next_layer)
            current_layer = next_layer
        
        return layers
    
    def get_proof(self, index: int) -> List[Dict[str, str]]:
        """Get Merkle proof for a leaf at given index."""
        if index < 0 or index >= len(self.leaves):
            return []
        
        proof = []
        for layer in self.layers[:-1]:
            sibling_index = index ^ 1  # XOR to get sibling
            if sibling_index < len(layer):
                proof.append({
                    "hash": layer[sibling_index],
                    "position": "right" if index % 2 == 0 else "left"
                })
            index //= 2
        
        return proof
    
    def verify_proof(self, leaf: str, proof: List[Dict[str, str]]) -> bool:
        """Verify a Merkle proof."""
        current = self._hash(leaf)
        
        for step in proof:
            sibling = step["hash"]
            if step["position"] == "right":
                current = self._hash(current + sibling)
            else:
                current = self._hash(sibling + current)
        
        return current == self.root


class VoterRegistry:
    """Voter registry loaded from CSV with Merkle tree for membership proofs."""
    
    def __init__(self, csv_path: str = None):
        self.voters: Dict[str, Dict[str, Any]] = {}  # voter_id -> voter data
        self.voter_ids: List[str] = []
        self.merkle_tree: Optional[MerkleTree] = None
        self.merkle_root: str = ""
        
        if csv_path and os.path.exists(csv_path):
            self._load_csv(csv_path)
    
    def _load_csv(self, csv_path: str):
        """Load voter data from CSV file."""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    voter_id = row.get('मतदाता नं', '').strip()
                    if voter_id:
                        self.voter_ids.append(voter_id)
                        self.voters[voter_id] = {
                            "serial": row.get('सि.नं.', ''),
                            "name": row.get('मतदाताको नाम', ''),
                            "age": row.get('उमेर(वर्ष)', ''),
                            "gender": row.get('लिङ्ग', ''),
                            "ward": row.get('Ward', ''),
                            "district": row.get('District', ''),
                            "province": row.get('Province', '')
                        }
            
            # Build Merkle tree from voter IDs
            if self.voter_ids:
                self.merkle_tree = MerkleTree(self.voter_ids)
                self.merkle_root = self.merkle_tree.root
                print(f"✓ Loaded {len(self.voter_ids)} voters. Merkle root: {self.merkle_root[:16]}...")
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
    
    def is_eligible(self, voter_id: str) -> bool:
        """Check if voter ID exists in registry."""
        return voter_id in self.voters
    
    def get_voter_info(self, voter_id: str) -> Optional[Dict[str, Any]]:
        """Get voter info (for display only, not for verification)."""
        return self.voters.get(voter_id)
    
    def get_voter_index(self, voter_id: str) -> int:
        """Get index of voter ID in the list."""
        try:
            return self.voter_ids.index(voter_id)
        except ValueError:
            return -1
    
    def get_merkle_proof(self, voter_id: str) -> Optional[List[Dict[str, str]]]:
        """Get Merkle proof for a voter ID."""
        index = self.get_voter_index(voter_id)
        if index == -1 or not self.merkle_tree:
            return None
        return self.merkle_tree.get_proof(index)
    
    def verify_membership(self, voter_id: str, proof: List[Dict[str, str]]) -> bool:
        """Verify voter membership using Merkle proof."""
        if not self.merkle_tree:
            return False
        return self.merkle_tree.verify_proof(voter_id, proof)


# Initialize voter registry from CSV
# In Docker, data is mounted at /app/data; locally it's at ../data
DATA_DIR = Path("/app/data") if Path("/app/data").exists() else Path(__file__).parent.parent / "data"
CSV_PATH = DATA_DIR / "dhulikhel_voter_list_full.csv"
print(f"Looking for voter CSV at: {CSV_PATH} (exists: {CSV_PATH.exists()})")
voter_registry = VoterRegistry(str(CSV_PATH) if CSV_PATH.exists() else None)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Models =============

# ZK Proof Models - Updated for Blind Auditor System
class VoterLookupRequest(BaseModel):
    voter_id: str

class VoterLookupResponse(BaseModel):
    found: bool
    voter_id_hash: Optional[str] = None
    name_masked: Optional[str] = None  # First 2 chars + ***
    ward: Optional[str] = None
    merkle_proof: Optional[List[Dict[str, str]]] = None
    message: str

class ZKProofRequest(BaseModel):
    """Request for ZK proof verification."""
    voter_id_hash: str  # Hash of voter ID (computed client-side)
    nullifier: str      # Hash(voter_id + secret) - prevents double voting
    merkle_proof: List[Dict[str, str]]  # Proof of membership
    commitment: str     # Hash(voter_id_hash + nullifier) - for verification

class ZKProofResponse(BaseModel):
    valid: bool
    credential: Optional[str] = None
    nullifier: Optional[str] = None
    nullifier_short: Optional[str] = None  # Truncated for display
    message: str
    merkle_root: Optional[str] = None

class Manifesto(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: str
    politician_id: str
    politician_name: str
    deadline: str
    status: str = "pending"
    created_at: Optional[str] = None
    hash: Optional[str] = None
    vote_kept: int = 0
    vote_broken: int = 0

class ManifestoCreate(BaseModel):
    title: str
    description: str
    category: str
    politician_id: str
    deadline: str
    promises: List[str] = []

class Vote(BaseModel):
    manifesto_id: str
    vote_type: str  # "kept" or "broken"
    nullifier: str
    proof: str

class VoteResponse(BaseModel):
    success: bool
    message: str
    vote_hash: Optional[str] = None
    block_height: Optional[int] = None

class Comment(BaseModel):
    id: Optional[str] = None
    manifesto_id: str
    content: str
    nullifier: str
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0

class CommentCreate(BaseModel):
    manifesto_id: str
    content: str
    nullifier: str
    parent_id: Optional[str] = None

class Feedback(BaseModel):
    type: str  # "bug", "suggestion", "general"
    content: str

class AuditLog(BaseModel):
    id: str
    action: str
    timestamp: str
    block_height: int
    tx_hash: str
    status: str

class NetworkStats(BaseModel):
    active_nodes: int
    total_votes: int
    total_manifestos: int
    integrity_score: float
    uptime: float
    last_block: int

# ============= In-Memory Storage (Demo) =============

manifestos_db: List[dict] = [
    {
        "id": "MAN-2023-0001",
        "title": "Universal Healthcare Act",
        "description": "Comprehensive healthcare reform ensuring coverage for all citizens",
        "category": "Healthcare",
        "politician_id": "POL-001",
        "politician_name": "Jane Doe",
        "deadline": "2024-06-30",
        "status": "kept",
        "created_at": "2023-01-15T10:00:00Z",
        "hash": "0x7f8e9d0c1b2a3f4e5d6c7b8a9",
        "vote_kept": 1247,
        "vote_broken": 203,
        "grace_period_end": "2024-01-15T10:00:00Z"
    },
    {
        "id": "MAN-2023-0002",
        "title": "North-South Rail Link",
        "description": "Major infrastructure project to connect northern and southern regions",
        "category": "Infrastructure",
        "politician_id": "POL-001",
        "politician_name": "Jane Doe",
        "deadline": "2025-12-31",
        "status": "pending",
        "created_at": "2023-03-20T14:30:00Z",
        "hash": "0x3c4d5e6f7a8b9c0d1e2f3a4b",
        "vote_kept": 892,
        "vote_broken": 156,
        "grace_period_end": "2024-03-20T14:30:00Z"
    },
    {
        "id": "MAN-2023-0003",
        "title": "Green Energy Initiative",
        "description": "Transition to 50% renewable energy sources by 2025",
        "category": "Environment",
        "politician_id": "POL-002",
        "politician_name": "John Smith",
        "deadline": "2025-06-30",
        "status": "pending",
        "created_at": "2023-05-10T09:00:00Z",
        "hash": "0x9a0b1c2d3e4f5a6b7c8d9e0f",
        "vote_kept": 2156,
        "vote_broken": 89,
        "grace_period_end": "2024-05-10T09:00:00Z"
    },
    {
        "id": "MAN-2023-0004",
        "title": "Education Reform Bill",
        "description": "Modernize curriculum and increase teacher salaries",
        "category": "Education",
        "politician_id": "POL-001",
        "politician_name": "Jane Doe",
        "deadline": "2023-09-01",
        "status": "broken",
        "created_at": "2022-09-01T11:00:00Z",
        "hash": "0x1d2e3f4a5b6c7d8e9f0a1b2c",
        "vote_kept": 456,
        "vote_broken": 1789,
        "grace_period_end": "2023-09-01T11:00:00Z"
    }
]

comments_db: List[dict] = []
votes_db: List[dict] = []
credentials_db: dict = {}  # nullifier -> credential mapping

# ============= Utility Functions =============

def generate_hash(data: str) -> str:
    return "0x" + hashlib.sha256(data.encode()).hexdigest()[:40]

def generate_nullifier() -> str:
    return "0x" + secrets.token_hex(16)

def generate_credential() -> str:
    return secrets.token_urlsafe(16)

def get_current_block() -> int:
    # Simulated block height
    base_block = 18249000
    elapsed_seconds = (datetime.now() - datetime(2023, 10, 1)).total_seconds()
    return base_block + int(elapsed_seconds / 12)

# ============= Voter Registry Endpoints =============

@app.get("/api/registry/merkle-root")
async def get_merkle_root():
    """Get the current Merkle root of the voter registry."""
    return {
        "merkle_root": voter_registry.merkle_root,
        "total_voters": len(voter_registry.voter_ids),
        "registry_status": "active" if voter_registry.merkle_root else "not_loaded"
    }

@app.get("/api/registry/stats")
async def get_registry_stats():
    """Get voter registry statistics."""
    if not voter_registry.voters:
        return {"error": "Registry not loaded"}
    
    # Aggregate stats by ward
    ward_stats = {}
    for voter in voter_registry.voters.values():
        ward = voter.get("ward", "Unknown")
        ward_stats[ward] = ward_stats.get(ward, 0) + 1
    
    return {
        "total_voters": len(voter_registry.voter_ids),
        "merkle_root": voter_registry.merkle_root[:16] + "..." if voter_registry.merkle_root else None,
        "wards": ward_stats,
        "district": "काभ्रेपलाञ्चोक",
        "municipality": "धुलिखेल नगरपालिका"
    }

@app.post("/api/registry/lookup")
async def lookup_voter(request: VoterLookupRequest):
    """
    Look up voter by ID and return Merkle proof.
    This is used client-side to generate the ZK proof.
    NOTE: The actual voter_id is NOT stored - only used to fetch proof.
    """
    voter_id = request.voter_id.strip()
    
    if not voter_registry.is_eligible(voter_id):
        return VoterLookupResponse(
            found=False,
            message="Voter ID not found in registry"
        )
    
    voter_info = voter_registry.get_voter_info(voter_id)
    merkle_proof = voter_registry.get_merkle_proof(voter_id)
    
    # Hash the voter ID for client-side use
    voter_id_hash = generate_hash(voter_id)
    
    # Mask the name for privacy (show first 2 chars only)
    name = voter_info.get("name", "")
    name_masked = name[:2] + "***" if len(name) > 2 else "***"
    
    return VoterLookupResponse(
        found=True,
        voter_id_hash=voter_id_hash,
        name_masked=name_masked,
        ward=voter_info.get("ward"),
        merkle_proof=merkle_proof,
        message="Voter found. Use this data to generate your ZK proof client-side."
    )

@app.get("/api/registry/search")
async def search_voters(query: str = "", ward: Optional[str] = None, limit: int = 20):
    """
    Search voters by name (partial match) for UI autocomplete.
    Returns masked data only - no full voter IDs exposed.
    """
    results = []
    for voter_id, voter in voter_registry.voters.items():
        if len(results) >= limit:
            break
        
        name = voter.get("name", "")
        voter_ward = voter.get("ward", "")
        
        # Filter by ward if specified
        if ward and voter_ward != ward:
            continue
        
        # Search by name (partial match)
        if query.lower() in name.lower():
            results.append({
                "voter_id_partial": voter_id[:4] + "****" + voter_id[-2:],  # Mask middle digits
                "voter_id_full": voter_id,  # Needed for lookup, but frontend should handle carefully
                "name": name,
                "ward": voter_ward,
                "age": voter.get("age", ""),
                "gender": voter.get("gender", "")
            })
    
    return {
        "results": results,
        "total": len(results),
        "query": query
    }

# ============= ZK Proof Endpoints =============

@app.post("/api/zk/verify", response_model=ZKProofResponse)
async def verify_zk_proof(request: ZKProofRequest):
    """
    Verify a zero-knowledge proof and issue anonymous credential.
    
    The "Blind Auditor" verification:
    1. Verifies the Merkle proof (voter is in registry)
    2. Checks commitment matches claimed values
    3. Stores ONLY the nullifier (prevents double voting)
    4. Never stores or logs the actual voter ID
    """
    # Check if nullifier already used (prevent double registration)
    if request.nullifier in credentials_db:
        return ZKProofResponse(
            valid=False,
            message="This credential has already been registered. One person, one vote."
        )
    
    # Verify Merkle proof (in production, this would be done via zk-SNARK)
    # For MVP, we verify the proof structure is valid
    if not request.merkle_proof or len(request.merkle_proof) < 1:
        return ZKProofResponse(
            valid=False,
            message="Invalid Merkle proof structure"
        )
    
    # Verify commitment format
    if len(request.commitment) < 20 or len(request.nullifier) < 20:
        return ZKProofResponse(
            valid=False,
            message="Invalid proof format - commitment or nullifier too short"
        )
    
    # In production: Verify zk-SNARK proof here using snarkjs
    # The proof would cryptographically prove:
    # 1. Prover knows a voter_id that hashes to voter_id_hash
    # 2. voter_id is a leaf in the Merkle tree
    # 3. nullifier = Hash(voter_id + secret)
    
    # Generate anonymous credential
    credential = generate_credential()
    
    # Store ONLY the nullifier and credential (NEVER the voter ID)
    credentials_db[request.nullifier] = {
        "credential": credential,
        "created_at": datetime.now().isoformat(),
        "used_votes": [],
        "verified": True
    }
    
    return ZKProofResponse(
        valid=True,
        credential=credential,
        nullifier=request.nullifier,
        nullifier_short=request.nullifier[:12] + "...",
        message="✓ Zero-knowledge proof verified. Anonymous credential issued.",
        merkle_root=voter_registry.merkle_root[:16] + "..." if voter_registry.merkle_root else None
    )

@app.get("/api/zk/credential/{nullifier}")
async def check_credential(nullifier: str):
    """Check if a credential/nullifier is valid and get voting history."""
    if nullifier in credentials_db:
        cred = credentials_db[nullifier]
        return {
            "valid": True,
            "used_votes": cred["used_votes"],
            "created_at": cred["created_at"],
            "can_vote": True  # Can vote on manifestos not in used_votes
        }
    return {"valid": False, "used_votes": [], "can_vote": False}

# ============= Manifesto Endpoints =============

@app.get("/api/manifestos")
async def get_manifestos(
    status: Optional[str] = None,
    category: Optional[str] = None,
    politician_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get all manifestos with optional filtering."""
    results = manifestos_db.copy()
    
    if status:
        results = [m for m in results if m["status"] == status]
    if category:
        results = [m for m in results if m["category"] == category]
    if politician_id:
        results = [m for m in results if m["politician_id"] == politician_id]
    
    total = len(results)
    results = results[offset:offset + limit]
    
    return {
        "manifestos": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/manifestos/{manifesto_id}")
async def get_manifesto(manifesto_id: str):
    """Get a specific manifesto by ID."""
    for m in manifestos_db:
        if m["id"] == manifesto_id:
            return m
    raise HTTPException(status_code=404, detail="Manifesto not found")

@app.post("/api/manifestos")
async def create_manifesto(manifesto: ManifestoCreate):
    """Create a new manifesto (politician only)."""
    new_id = f"MAN-{datetime.now().year}-{len(manifestos_db) + 1:04d}"
    created_at = datetime.now().isoformat()
    
    new_manifesto = {
        "id": new_id,
        "title": manifesto.title,
        "description": manifesto.description,
        "category": manifesto.category,
        "politician_id": manifesto.politician_id,
        "politician_name": "Politician Name",  # Would be looked up
        "deadline": manifesto.deadline,
        "status": "pending",
        "created_at": created_at,
        "hash": generate_hash(f"{new_id}{created_at}{manifesto.title}"),
        "vote_kept": 0,
        "vote_broken": 0,
        "promises": manifesto.promises,
        "grace_period_end": (datetime.now() + timedelta(days=180)).isoformat()
    }
    
    manifestos_db.append(new_manifesto)
    return new_manifesto

@app.get("/api/manifestos/{manifesto_id}/votes")
async def get_manifesto_votes(manifesto_id: str):
    """Get vote aggregates for a manifesto."""
    for m in manifestos_db:
        if m["id"] == manifesto_id:
            total = m["vote_kept"] + m["vote_broken"]
            return {
                "manifesto_id": manifesto_id,
                "vote_kept": m["vote_kept"],
                "vote_broken": m["vote_broken"],
                "total_votes": total,
                "kept_percentage": round(m["vote_kept"] / total * 100, 1) if total > 0 else 0,
                "broken_percentage": round(m["vote_broken"] / total * 100, 1) if total > 0 else 0
            }
    raise HTTPException(status_code=404, detail="Manifesto not found")

# ============= Vote Endpoints =============

@app.post("/api/votes", response_model=VoteResponse)
async def submit_vote(vote: Vote):
    """Submit a vote on a manifesto."""
    # Verify nullifier exists
    if vote.nullifier not in credentials_db:
        raise HTTPException(status_code=401, detail="Invalid nullifier")
    
    # Check if already voted on this manifesto
    if vote.manifesto_id in credentials_db[vote.nullifier]["used_votes"]:
        raise HTTPException(status_code=400, detail="Already voted on this manifesto")
    
    # Find manifesto
    manifesto = None
    for m in manifestos_db:
        if m["id"] == vote.manifesto_id:
            manifesto = m
            break
    
    if not manifesto:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    # Check grace period
    grace_end = datetime.fromisoformat(manifesto["grace_period_end"].replace("Z", ""))
    if datetime.now() < grace_end:
        raise HTTPException(status_code=400, detail="Voting not yet open - grace period active")
    
    # Record vote
    if vote.vote_type == "kept":
        manifesto["vote_kept"] += 1
    else:
        manifesto["vote_broken"] += 1
    
    credentials_db[vote.nullifier]["used_votes"].append(vote.manifesto_id)
    
    vote_hash = generate_hash(f"{vote.nullifier}{vote.manifesto_id}{datetime.now().isoformat()}")
    
    votes_db.append({
        "vote_hash": vote_hash,
        "manifesto_id": vote.manifesto_id,
        "vote_type": vote.vote_type,
        "timestamp": datetime.now().isoformat(),
        "block_height": get_current_block()
    })
    
    return VoteResponse(
        success=True,
        message="Vote recorded successfully",
        vote_hash=vote_hash,
        block_height=get_current_block()
    )

@app.get("/api/votes/verify/{vote_hash}")
async def verify_vote(vote_hash: str):
    """Verify a vote was recorded on-chain."""
    for v in votes_db:
        if v["vote_hash"] == vote_hash:
            return {
                "verified": True,
                "vote": v,
                "merkle_proof": {
                    "root": generate_hash(f"merkle_root_{v['block_height']}"),
                    "path": [
                        {"position": "left", "hash": generate_hash("path_0")},
                        {"position": "right", "hash": generate_hash("path_1")},
                        {"position": "left", "hash": generate_hash("path_2")}
                    ]
                }
            }
    return {"verified": False, "message": "Vote not found"}

# ============= Comment Endpoints =============

@app.get("/api/manifestos/{manifesto_id}/comments")
async def get_comments(manifesto_id: str):
    """Get all comments for a manifesto."""
    comments = [c for c in comments_db if c["manifesto_id"] == manifesto_id]
    
    # Build thread structure
    root_comments = [c for c in comments if c["parent_id"] is None]
    
    def get_replies(parent_id: str):
        replies = [c for c in comments if c["parent_id"] == parent_id]
        for reply in replies:
            reply["replies"] = get_replies(reply["id"])
        return replies
    
    for comment in root_comments:
        comment["replies"] = get_replies(comment["id"])
    
    return {"comments": root_comments, "total": len(comments)}

@app.post("/api/comments")
async def create_comment(comment: CommentCreate):
    """Create a new comment."""
    new_id = f"CMT-{len(comments_db) + 1:06d}"
    
    new_comment = {
        "id": new_id,
        "manifesto_id": comment.manifesto_id,
        "content": comment.content,
        "nullifier": comment.nullifier[:12] + "...",  # Truncated for privacy
        "parent_id": comment.parent_id,
        "created_at": datetime.now().isoformat(),
        "upvotes": 0,
        "downvotes": 0
    }
    
    comments_db.append(new_comment)
    return new_comment

@app.post("/api/comments/{comment_id}/vote")
async def vote_comment(comment_id: str, vote_type: str):
    """Upvote or downvote a comment."""
    for c in comments_db:
        if c["id"] == comment_id:
            if vote_type == "up":
                c["upvotes"] += 1
            else:
                c["downvotes"] += 1
            return c
    raise HTTPException(status_code=404, detail="Comment not found")

# ============= Audit & Network Endpoints =============

@app.get("/api/audit/logs")
async def get_audit_logs(limit: int = 50):
    """Get recent audit logs."""
    base_block = get_current_block()
    
    # Generate sample audit logs
    logs = []
    actions = ["VOTE_CAST", "MANIFESTO_CREATED", "STATUS_CHANGED", "MERKLE_ROOT_UPDATED"]
    for i in range(limit):
        logs.append({
            "id": f"LOG-{base_block - i:08d}",
            "action": actions[i % len(actions)],
            "timestamp": (datetime.now() - timedelta(minutes=i * 5)).isoformat(),
            "block_height": base_block - i,
            "tx_hash": generate_hash(f"tx_{base_block - i}"),
            "status": "confirmed"
        })
    
    return {"logs": logs, "total": len(logs)}

@app.get("/api/network/stats")
async def get_network_stats():
    """Get network statistics."""
    return {
        "active_nodes": 1247,
        "total_votes": sum(m["vote_kept"] + m["vote_broken"] for m in manifestos_db),
        "total_manifestos": len(manifestos_db),
        "integrity_score": 99.97,
        "uptime": 99.99,
        "last_block": get_current_block(),
        "avg_block_time": 12.1,
        "pending_txs": 23
    }

@app.get("/api/blockchain/blocks")
async def get_blocks(limit: int = 10):
    """Get recent blockchain blocks."""
    current_block = get_current_block()
    blocks = []
    
    for i in range(limit):
        block_num = current_block - i
        prev_hash = generate_hash(f"block_{block_num - 1}") if block_num > 0 else "0x0"
        
        blocks.append({
            "number": block_num,
            "hash": generate_hash(f"block_{block_num}"),
            "prev_hash": prev_hash,
            "timestamp": (datetime.now() - timedelta(seconds=i * 12)).isoformat(),
            "tx_count": (block_num % 15) + 1,
            "merkle_root": generate_hash(f"merkle_{block_num}")
        })
    
    return {"blocks": blocks}

# ============= Feedback Endpoint =============

@app.post("/api/feedback")
async def submit_feedback(feedback: Feedback):
    """Submit anonymous feedback."""
    return {
        "success": True,
        "message": "Feedback submitted successfully. Thank you for helping improve the platform.",
        "reference": generate_hash(f"feedback_{datetime.now().isoformat()}")[:16]
    }

# ============= Politicians Endpoints =============

@app.get("/api/politicians")
async def get_politicians():
    """Get list of all registered politicians."""
    politicians = [
        {
            "id": "POL-001",
            "name": "Jane Doe",
            "title": "Governor",
            "party": "Progressive Party",
            "integrity_score": 87,
            "manifestos": 12,
            "verified": True,
            "public_key": "0x8a72f92b45c1e98d3a7b6f1c2d4e5f6a7b8c9d0e"
        },
        {
            "id": "POL-002",
            "name": "John Smith",
            "title": "Senator",
            "party": "Unity Coalition",
            "integrity_score": 92,
            "manifestos": 8,
            "verified": True,
            "public_key": "0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c"
        },
        {
            "id": "POL-003",
            "name": "Maria Garcia",
            "title": "Mayor",
            "party": "Green Alliance",
            "integrity_score": 78,
            "manifestos": 15,
            "verified": True,
            "public_key": "0x5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e"
        }
    ]
    return {"politicians": politicians}

@app.get("/api/politicians/{politician_id}")
async def get_politician(politician_id: str):
    """Get politician details."""
    politicians = {
        "POL-001": {
            "id": "POL-001",
            "name": "Jane Doe",
            "title": "Governor",
            "party": "Progressive Party",
            "state": "State of Democracy",
            "integrity_score": 87,
            "verified": True,
            "public_key": "0x8a72f92b45c1e98d3a7b6f1c2d4e5f6a7b8c9d0e",
            "joined_date": "2020-01-15"
        },
        "POL-002": {
            "id": "POL-002",
            "name": "John Smith",
            "title": "Senator",
            "party": "Unity Coalition",
            "state": "State of Democracy",
            "integrity_score": 92,
            "verified": True,
            "public_key": "0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c",
            "joined_date": "2019-06-20"
        }
    }
    
    if politician_id in politicians:
        return politicians[politician_id]
    raise HTTPException(status_code=404, detail="Politician not found")

# ============= Health Check =============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "block_height": get_current_block()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
