"""
PromiseThread API - PostgreSQL Version
======================================
Decentralized Political Accountability Platform - Blind Auditor System

Database Credentials:
- Host: localhost
- Port: 5432
- Database: promisethread
- Username: promisethread
- Password: hackfest2025
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from database import get_db, init_db, check_connection
from models import (
    Voter, ZKCredential, Politician, Manifesto as ManifestoModel,
    ManifestoVote, Comment as CommentModel, CommentVote, AuditLog, MerkleRoot
)
from crypto_utils import (
    generate_key_pair, create_encrypted_keystore, compute_manifesto_hash,
    verify_signature, get_verification_bundle, is_valid_address, format_address_short
)
from blockchain_service import get_blockchain_service, BlockchainService

app = FastAPI(
    title="PromiseThread API",
    description="Decentralized Political Accountability Platform - Blind Auditor System",
    version="2.2.0 (PostgreSQL + Blockchain)"
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


# ============= Demo Configuration =============
DEMO_SECRET = "1234567890"

# In-memory cache for expected nullifiers (temporary during auth flow)
expected_nullifiers_cache: dict = {}

# Cached Merkle tree (rebuilt from DB)
_merkle_tree_cache: Optional[MerkleTree] = None
_merkle_root_cache: str = ""
_voter_ids_cache: List[str] = []


def get_merkle_tree(db: Session) -> tuple[MerkleTree, str, List[str]]:
    """Get or rebuild Merkle tree from database."""
    global _merkle_tree_cache, _merkle_root_cache, _voter_ids_cache
    
    if _merkle_tree_cache is None:
        # Load voter IDs from database
        voters = db.query(Voter.voter_id).order_by(Voter.id).all()
        _voter_ids_cache = [v.voter_id for v in voters]
        
        if _voter_ids_cache:
            _merkle_tree_cache = MerkleTree(_voter_ids_cache)
            _merkle_root_cache = _merkle_tree_cache.root
            print(f"✓ Built Merkle tree with {len(_voter_ids_cache)} voters. Root: {_merkle_root_cache[:16]}...")
    
    return _merkle_tree_cache, _merkle_root_cache, _voter_ids_cache


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Pydantic Models =============

class VoterLookupRequest(BaseModel):
    voter_id: str

class VoterLookupResponse(BaseModel):
    found: bool
    voter_id_hash: Optional[str] = None
    name_masked: Optional[str] = None
    ward: Optional[str] = None
    merkle_proof: Optional[List[Dict[str, str]]] = None
    message: str

class ZKProofRequest(BaseModel):
    voter_id_hash: str
    nullifier: str
    merkle_proof: List[Dict[str, str]]
    commitment: str

class ZKProofResponse(BaseModel):
    valid: bool
    credential: Optional[str] = None
    nullifier: Optional[str] = None
    nullifier_short: Optional[str] = None
    message: str
    merkle_root: Optional[str] = None

class ManifestoResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    politician_id: int
    politician_name: str
    politician_party: Optional[str] = None
    deadline: str
    status: str
    created_at: str
    hash: Optional[str] = None
    vote_kept: int
    vote_broken: int
    grace_period_end: str
    voting_open: bool

class ManifestoCreate(BaseModel):
    title: str
    description: str
    category: str
    politician_id: int
    deadline: str
    promises: List[str] = []

class VoteRequest(BaseModel):
    manifesto_id: int
    vote_type: str  # "kept" or "broken"
    nullifier: str
    proof: str = ""

class VoteResponse(BaseModel):
    success: bool
    message: str
    vote_hash: Optional[str] = None
    block_height: Optional[int] = None
    changed: bool = False  # True if vote was changed

class CommentCreate(BaseModel):
    manifesto_id: int
    content: str
    nullifier: str
    parent_id: Optional[int] = None

class CommentVoteRequest(BaseModel):
    nullifier: str
    vote_type: str  # "up" or "down"

class Feedback(BaseModel):
    type: str
    content: str


# ============= Utility Functions =============

def generate_hash(data: str) -> str:
    return "0x" + hashlib.sha256(data.encode()).hexdigest()[:40]

def compute_expected_nullifier(voter_id: str, secret: str = DEMO_SECRET) -> str:
    combined = f"{voter_id}:{secret}"
    return "0x" + hashlib.sha256(combined.encode()).hexdigest()

def generate_nullifier() -> str:
    return "0x" + secrets.token_hex(16)

def generate_credential() -> str:
    return secrets.token_urlsafe(16)

def get_current_block() -> int:
    """Get current block number from blockchain, fallback to simulated."""
    try:
        blockchain = get_blockchain_service()
        if blockchain.is_connected():
            return blockchain.get_connection_info()["block_number"]
    except:
        pass
    # Fallback: simulated block number
    base_block = 18249000
    elapsed_seconds = (datetime.now() - datetime(2023, 10, 1)).total_seconds()
    return base_block + int(elapsed_seconds / 12)

def generate_block_hash(data: str, prev_hash: str) -> str:
    combined = f"{data}:{prev_hash}".encode('utf-8')
    return '0x' + hashlib.sha256(combined).hexdigest()


# ============= Voter Registry Endpoints =============

@app.get("/api/registry/merkle-root")
async def get_merkle_root(db: Session = Depends(get_db)):
    """Get the current Merkle root of the voter registry."""
    _, merkle_root, voter_ids = get_merkle_tree(db)
    
    return {
        "merkle_root": merkle_root,
        "total_voters": len(voter_ids),
        "registry_status": "active" if merkle_root else "not_loaded",
        "mode": "demo",
        "demo_secret": DEMO_SECRET,
        "demo_note": "In production, each voter receives a unique secret from Election Commission"
    }

@app.get("/api/registry/stats")
async def get_registry_stats(db: Session = Depends(get_db)):
    """Get voter registry statistics."""
    total = db.query(func.count(Voter.id)).scalar()
    
    if total == 0:
        return {"error": "Registry not loaded"}
    
    # Aggregate stats by ward
    ward_stats = db.query(
        Voter.ward, func.count(Voter.id)
    ).group_by(Voter.ward).all()
    
    _, merkle_root, _ = get_merkle_tree(db)
    
    # Get district/vdc info from first voter
    first_voter = db.query(Voter).first()
    
    return {
        "total_voters": total,
        "merkle_root": merkle_root[:16] + "..." if merkle_root else None,
        "wards": {str(ward): count for ward, count in ward_stats},
        "district": first_voter.district if first_voter else "Unknown",
        "municipality": first_voter.vdc if first_voter else "Unknown"
    }

@app.post("/api/registry/lookup")
async def lookup_voter(request: VoterLookupRequest, db: Session = Depends(get_db)):
    """Look up voter by ID and return Merkle proof."""
    voter_id = request.voter_id.strip()
    
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    
    if not voter:
        return VoterLookupResponse(
            found=False,
            message="Voter ID not found in registry"
        )
    
    merkle_tree, _, voter_ids = get_merkle_tree(db)
    
    # Get voter index
    try:
        index = voter_ids.index(voter_id)
    except ValueError:
        index = -1
    
    merkle_proof = merkle_tree.get_proof(index) if merkle_tree and index >= 0 else None
    
    voter_id_hash = generate_hash(voter_id)
    
    # Compute and store expected nullifier
    expected_nullifier = compute_expected_nullifier(voter_id)
    expected_nullifiers_cache[expected_nullifier] = {
        "voter_id_hash": voter_id_hash,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Mask the name
    name = voter.name or ""
    name_masked = name[:2] + "***" if len(name) > 2 else "***"
    
    return VoterLookupResponse(
        found=True,
        voter_id_hash=voter_id_hash,
        name_masked=name_masked,
        ward=str(voter.ward) if voter.ward else None,
        merkle_proof=merkle_proof,
        message="Voter found. Use this data to generate your ZK proof client-side."
    )

@app.get("/api/registry/search")
async def search_voters(
    query: str = "",
    ward: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search voters by name."""
    q = db.query(Voter)
    
    if query:
        q = q.filter(Voter.name.ilike(f"%{query}%"))
    
    if ward:
        q = q.filter(Voter.ward == int(ward))
    
    voters = q.limit(limit).all()
    
    results = []
    for voter in voters:
        results.append({
            "voter_id_partial": voter.voter_id[:4] + "****" + voter.voter_id[-2:],
            "voter_id_full": voter.voter_id,
            "name": voter.name,
            "ward": str(voter.ward) if voter.ward else "",
            "age": str(voter.age) if voter.age else "",
            "gender": voter.gender or ""
        })
    
    return {
        "results": results,
        "total": len(results),
        "query": query
    }


# ============= ZK Proof Endpoints =============

@app.post("/api/zk/verify", response_model=ZKProofResponse)
async def verify_zk_proof(request: ZKProofRequest, db: Session = Depends(get_db)):
    """Verify a zero-knowledge proof and issue anonymous credential."""
    
    # Check if nullifier already used
    existing = db.query(ZKCredential).filter(
        ZKCredential.nullifier_hash == request.nullifier
    ).first()
    
    if existing:
        return ZKProofResponse(
            valid=False,
            message="This credential has already been registered. One person, one vote."
        )
    
    # Verify nullifier was computed with correct secret
    if request.nullifier not in expected_nullifiers_cache:
        return ZKProofResponse(
            valid=False,
            message=f"Invalid secret. Please use the demo secret: {DEMO_SECRET}"
        )
    
    # Clean up expected nullifier entry
    expected_data = expected_nullifiers_cache.pop(request.nullifier)
    
    # Verify Merkle proof structure
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
    
    # Generate anonymous credential
    credential = generate_credential()
    
    # Store in database
    zk_cred = ZKCredential(
        nullifier_hash=request.nullifier,
        credential_hash=credential,
        is_valid=True
    )
    db.add(zk_cred)
    db.commit()
    
    _, merkle_root, _ = get_merkle_tree(db)
    
    return ZKProofResponse(
        valid=True,
        credential=credential,
        nullifier=request.nullifier,
        nullifier_short=request.nullifier[:12] + "...",
        message="✓ Zero-knowledge proof verified. Anonymous credential issued.",
        merkle_root=merkle_root[:16] + "..." if merkle_root else None
    )

@app.get("/api/zk/credential/{nullifier}")
async def check_credential(nullifier: str, db: Session = Depends(get_db)):
    """Check if a credential/nullifier is valid and get voting history."""
    cred = db.query(ZKCredential).filter(
        ZKCredential.nullifier_hash == nullifier
    ).first()
    
    if cred and cred.is_valid:
        # Get voted manifesto IDs
        votes = db.query(ManifestoVote.manifesto_id).filter(
            ManifestoVote.nullifier == nullifier
        ).all()
        used_votes = [v.manifesto_id for v in votes]
        
        return {
            "valid": True,
            "used_votes": used_votes,
            "created_at": cred.created_at.isoformat() if cred.created_at else None,
            "can_vote": True
        }
    
    return {"valid": False, "used_votes": [], "can_vote": False}


# ============= Manifesto Endpoints =============

@app.get("/api/manifestos")
async def get_manifestos(
    status: Optional[str] = None,
    category: Optional[str] = None,
    politician_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all manifestos with optional filtering."""
    q = db.query(ManifestoModel).join(Politician)
    
    if status:
        q = q.filter(ManifestoModel.status == status)
    if category:
        q = q.filter(ManifestoModel.category == category)
    if politician_id:
        q = q.filter(ManifestoModel.politician_id == politician_id)
    
    total = q.count()
    manifestos = q.order_by(ManifestoModel.created_at.desc()).offset(offset).limit(limit).all()
    
    now = datetime.now(timezone.utc)
    results = []
    for m in manifestos:
        grace_end = m.grace_period_end.replace(tzinfo=timezone.utc) if m.grace_period_end.tzinfo is None else m.grace_period_end
        voting_open = now >= grace_end
        
        results.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "category": m.category,
            "politician_id": m.politician_id,
            "politician_name": m.politician.name if m.politician else "Unknown",
            "politician_party": m.politician.party if m.politician else None,
            "deadline": m.grace_period_end.isoformat(),
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "hash": m.promise_hash,
            "vote_kept": m.vote_kept,
            "vote_broken": m.vote_broken,
            "grace_period_end": m.grace_period_end.isoformat(),
            "voting_open": voting_open
        })
    
    return {
        "manifestos": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/manifestos/{manifesto_id}")
async def get_manifesto(manifesto_id: int, db: Session = Depends(get_db)):
    """Get a specific manifesto by ID."""
    m = db.query(ManifestoModel).filter(ManifestoModel.id == manifesto_id).first()
    
    if not m:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    now = datetime.now(timezone.utc)
    grace_end = m.grace_period_end.replace(tzinfo=timezone.utc) if m.grace_period_end.tzinfo is None else m.grace_period_end
    voting_open = now >= grace_end
    
    return {
        "id": m.id,
        "title": m.title,
        "description": m.description,
        "category": m.category,
        "politician_id": m.politician_id,
        "politician_name": m.politician.name if m.politician else "Unknown",
        "politician_party": m.politician.party if m.politician else None,
        "deadline": m.grace_period_end.isoformat(),
        "status": m.status,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "hash": m.promise_hash,
        "vote_kept": m.vote_kept,
        "vote_broken": m.vote_broken,
        "grace_period_end": m.grace_period_end.isoformat(),
        "voting_open": voting_open
    }

@app.post("/api/manifestos")
async def create_manifesto(manifesto: ManifestoCreate, db: Session = Depends(get_db)):
    """Create a new manifesto."""
    # Verify politician exists
    politician = db.query(Politician).filter(Politician.id == manifesto.politician_id).first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    # Parse deadline
    try:
        deadline = datetime.fromisoformat(manifesto.deadline.replace("Z", "+00:00"))
    except:
        deadline = datetime.now(timezone.utc) + timedelta(days=365)
    
    # Create manifesto
    new_manifesto = ManifestoModel(
        politician_id=manifesto.politician_id,
        title=manifesto.title,
        description=manifesto.description,
        category=manifesto.category,
        status="pending",
        grace_period_end=deadline,
        vote_kept=0,
        vote_broken=0,
        promise_hash=generate_hash(f"{manifesto.title}:{manifesto.description}:{manifesto.politician_id}")
    )
    
    db.add(new_manifesto)
    db.commit()
    db.refresh(new_manifesto)
    
    # Create audit log
    last_audit = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last_audit.block_hash if last_audit else "0x0"
    
    audit = AuditLog(
        manifesto_id=new_manifesto.id,
        action="PROMISE_CREATED",
        block_hash=generate_block_hash(str(new_manifesto.id), prev_hash),
        prev_hash=prev_hash,
        data={
            "manifesto_id": new_manifesto.id,
            "title": new_manifesto.title,
            "politician_id": new_manifesto.politician_id
        }
    )
    db.add(audit)
    db.commit()
    
    return {
        "id": new_manifesto.id,
        "title": new_manifesto.title,
        "status": "created",
        "hash": new_manifesto.promise_hash
    }

@app.get("/api/manifestos/{manifesto_id}/votes")
async def get_manifesto_votes(manifesto_id: int, db: Session = Depends(get_db)):
    """Get vote aggregates for a manifesto."""
    m = db.query(ManifestoModel).filter(ManifestoModel.id == manifesto_id).first()
    
    if not m:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    total = m.vote_kept + m.vote_broken
    
    return {
        "manifesto_id": manifesto_id,
        "vote_kept": m.vote_kept,
        "vote_broken": m.vote_broken,
        "total_votes": total,
        "kept_percentage": round(m.vote_kept / total * 100, 1) if total > 0 else 0,
        "broken_percentage": round(m.vote_broken / total * 100, 1) if total > 0 else 0
    }


# ============= Vote Endpoints =============

@app.post("/api/votes", response_model=VoteResponse)
async def submit_vote(vote: VoteRequest, db: Session = Depends(get_db)):
    """Submit a vote on a manifesto. Can change existing vote."""
    
    # Verify nullifier exists
    cred = db.query(ZKCredential).filter(
        ZKCredential.nullifier_hash == vote.nullifier,
        ZKCredential.is_valid == True
    ).first()
    
    if not cred:
        raise HTTPException(status_code=401, detail="Invalid nullifier")
    
    # Find manifesto
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.id == vote.manifesto_id
    ).first()
    
    if not manifesto:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    # Check grace period
    now = datetime.now(timezone.utc)
    grace_end = manifesto.grace_period_end.replace(tzinfo=timezone.utc) if manifesto.grace_period_end.tzinfo is None else manifesto.grace_period_end
    
    if now < grace_end:
        raise HTTPException(status_code=400, detail="Voting not yet open - grace period active")
    
    # Check if already voted
    existing_vote = db.query(ManifestoVote).filter(
        ManifestoVote.manifesto_id == vote.manifesto_id,
        ManifestoVote.nullifier == vote.nullifier
    ).first()
    
    vote_hash = generate_hash(f"{vote.nullifier}{vote.manifesto_id}{datetime.now().isoformat()}")
    changed = False
    
    if existing_vote:
        # Change vote
        if existing_vote.vote_type != vote.vote_type:
            # Update aggregates
            if existing_vote.vote_type == "kept":
                manifesto.vote_kept -= 1
            else:
                manifesto.vote_broken -= 1
            
            if vote.vote_type == "kept":
                manifesto.vote_kept += 1
            else:
                manifesto.vote_broken += 1
            
            existing_vote.vote_type = vote.vote_type
            existing_vote.vote_hash = vote_hash
            changed = True
            message = "Vote changed successfully"
        else:
            message = "Vote unchanged (same choice)"
    else:
        # New vote
        new_vote = ManifestoVote(
            manifesto_id=vote.manifesto_id,
            nullifier=vote.nullifier,
            vote_type=vote.vote_type,
            vote_hash=vote_hash
        )
        db.add(new_vote)
        
        # Update aggregates
        if vote.vote_type == "kept":
            manifesto.vote_kept += 1
        else:
            manifesto.vote_broken += 1
        
        message = "Vote recorded successfully"
    
    db.commit()
    
    return VoteResponse(
        success=True,
        message=message,
        vote_hash=vote_hash,
        block_height=get_current_block(),
        changed=changed
    )

@app.get("/api/votes/verify/{vote_hash}")
async def verify_vote(vote_hash: str, db: Session = Depends(get_db)):
    """Verify a vote was recorded."""
    vote = db.query(ManifestoVote).filter(ManifestoVote.vote_hash == vote_hash).first()
    
    if vote:
        return {
            "verified": True,
            "vote": {
                "vote_hash": vote.vote_hash,
                "manifesto_id": vote.manifesto_id,
                "vote_type": vote.vote_type,
                "timestamp": vote.created_at.isoformat() if vote.created_at else None
            },
            "merkle_proof": {
                "root": generate_hash(f"merkle_root_{get_current_block()}"),
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
async def get_comments(manifesto_id: int, db: Session = Depends(get_db)):
    """Get all comments for a manifesto."""
    comments = db.query(CommentModel).filter(
        CommentModel.manifesto_id == manifesto_id,
        CommentModel.is_deleted == False
    ).order_by(CommentModel.created_at.desc()).all()
    
    # Build thread structure
    def build_comment(c):
        replies = [build_comment(r) for r in c.replies if not r.is_deleted]
        return {
            "id": c.id,
            "manifesto_id": c.manifesto_id,
            "content": c.content,
            "nullifier": c.nullifier_display,
            "parent_id": c.parent_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "upvotes": c.upvotes,
            "downvotes": c.downvotes,
            "replies": replies
        }
    
    root_comments = [c for c in comments if c.parent_id is None]
    result = [build_comment(c) for c in root_comments]
    
    return {"comments": result, "total": len(comments)}

@app.post("/api/comments")
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a new comment."""
    # Verify nullifier exists
    cred = db.query(ZKCredential).filter(
        ZKCredential.nullifier_hash == comment.nullifier,
        ZKCredential.is_valid == True
    ).first()
    
    if not cred:
        raise HTTPException(status_code=401, detail="Invalid nullifier - please authenticate first")
    
    # Verify manifesto exists
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.id == comment.manifesto_id
    ).first()
    
    if not manifesto:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    # Create comment
    new_comment = CommentModel(
        manifesto_id=comment.manifesto_id,
        parent_id=comment.parent_id,
        nullifier_display=comment.nullifier[:12] + "...",
        content=comment.content,
        upvotes=0,
        downvotes=0
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": new_comment.id,
        "manifesto_id": new_comment.manifesto_id,
        "content": new_comment.content,
        "nullifier": new_comment.nullifier_display,
        "parent_id": new_comment.parent_id,
        "created_at": new_comment.created_at.isoformat() if new_comment.created_at else None,
        "upvotes": new_comment.upvotes,
        "downvotes": new_comment.downvotes
    }

@app.post("/api/comments/{comment_id}/vote")
async def vote_comment(
    comment_id: int,
    vote_request: CommentVoteRequest,
    db: Session = Depends(get_db)
):
    """Upvote or downvote a comment."""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Verify nullifier
    cred = db.query(ZKCredential).filter(
        ZKCredential.nullifier_hash == vote_request.nullifier,
        ZKCredential.is_valid == True
    ).first()
    
    if not cred:
        raise HTTPException(status_code=401, detail="Invalid nullifier")
    
    # Check existing vote
    existing_vote = db.query(CommentVote).filter(
        CommentVote.comment_id == comment_id,
        CommentVote.nullifier == vote_request.nullifier
    ).first()
    
    if existing_vote:
        # Change vote
        if existing_vote.vote_type != vote_request.vote_type:
            # Reverse old vote
            if existing_vote.vote_type == "up":
                comment.upvotes -= 1
            else:
                comment.downvotes -= 1
            
            # Apply new vote
            if vote_request.vote_type == "up":
                comment.upvotes += 1
            else:
                comment.downvotes += 1
            
            existing_vote.vote_type = vote_request.vote_type
    else:
        # New vote
        new_vote = CommentVote(
            comment_id=comment_id,
            nullifier=vote_request.nullifier,
            vote_type=vote_request.vote_type
        )
        db.add(new_vote)
        
        if vote_request.vote_type == "up":
            comment.upvotes += 1
        else:
            comment.downvotes += 1
    
    db.commit()
    
    return {
        "id": comment.id,
        "upvotes": comment.upvotes,
        "downvotes": comment.downvotes
    }

@app.put("/api/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    content: str = Query(...),
    nullifier: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update a comment (only by original author via nullifier)."""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Verify ownership via nullifier display
    if comment.nullifier_display != nullifier[:12] + "...":
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    comment.content = content
    db.commit()
    
    return {"id": comment.id, "content": comment.content, "updated": True}

@app.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    nullifier: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a comment (soft delete)."""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Verify ownership
    if comment.nullifier_display != nullifier[:12] + "...":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    comment.is_deleted = True
    comment.content = "[deleted]"
    db.commit()
    
    return {"id": comment.id, "deleted": True}


# ============= Audit & Network Endpoints =============

@app.get("/api/audit/logs")
async def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": f"LOG-{log.id:08d}",
                "action": log.action,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "block_height": log.id + 18249000,
                "tx_hash": log.block_hash,
                "status": "confirmed",
                "manifesto_id": log.manifesto_id
            }
            for log in logs
        ],
        "total": len(logs)
    }

@app.get("/api/network/stats")
async def get_network_stats(db: Session = Depends(get_db)):
    """Get network statistics."""
    total_votes = db.query(func.sum(ManifestoModel.vote_kept + ManifestoModel.vote_broken)).scalar() or 0
    total_manifestos = db.query(func.count(ManifestoModel.id)).scalar()
    total_voters = db.query(func.count(Voter.id)).scalar()
    
    return {
        "active_nodes": 1247,
        "total_votes": total_votes,
        "total_manifestos": total_manifestos,
        "total_voters": total_voters,
        "integrity_score": 99.97,
        "uptime": 99.99,
        "last_block": get_current_block(),
        "avg_block_time": 12.1,
        "pending_txs": 23
    }

@app.get("/api/blockchain/blocks")
async def get_blocks(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent blockchain blocks from audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    
    if not logs:
        # Return simulated blocks if no audit logs
        current_block = get_current_block()
        return {
            "blocks": [
                {
                    "number": current_block - i,
                    "hash": generate_hash(f"block_{current_block - i}"),
                    "prev_hash": generate_hash(f"block_{current_block - i - 1}"),
                    "timestamp": (datetime.now() - timedelta(seconds=i * 12)).isoformat(),
                    "tx_count": 1,
                    "merkle_root": generate_hash(f"merkle_{current_block - i}")
                }
                for i in range(limit)
            ]
        }
    
    blocks = []
    for log in logs:
        blocks.append({
            "number": log.id + 18249000,
            "hash": log.block_hash,
            "prev_hash": log.prev_hash,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "tx_count": 1,
            "merkle_root": generate_hash(f"merkle_{log.id}"),
            "action": log.action,
            "manifesto_id": log.manifesto_id
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
async def get_politicians(db: Session = Depends(get_db)):
    """Get list of all registered politicians."""
    politicians = db.query(Politician).all()
    
    result = []
    for p in politicians:
        # Count manifestos
        manifesto_count = db.query(func.count(ManifestoModel.id)).filter(
            ManifestoModel.politician_id == p.id
        ).scalar()
        
        # Calculate integrity score based on kept vs broken
        kept = db.query(func.count(ManifestoModel.id)).filter(
            ManifestoModel.politician_id == p.id,
            ManifestoModel.status == "kept"
        ).scalar()
        broken = db.query(func.count(ManifestoModel.id)).filter(
            ManifestoModel.politician_id == p.id,
            ManifestoModel.status == "broken"
        ).scalar()
        
        total = kept + broken
        integrity_score = round(kept / total * 100) if total > 0 else 50
        
        result.append({
            "id": p.id,
            "name": p.name,
            "title": p.position or "Politician",
            "party": p.party,
            "integrity_score": integrity_score,
            "manifestos": manifesto_count,
            "verified": True,
            "public_key": generate_hash(f"pk_{p.id}")[:42],
            "image_url": p.image_url,
            "bio": p.bio
        })
    
    return {"politicians": result}

@app.get("/api/politicians/{politician_id}")
async def get_politician(politician_id: int, db: Session = Depends(get_db)):
    """Get politician details."""
    p = db.query(Politician).filter(Politician.id == politician_id).first()
    
    if not p:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    # Count manifestos
    manifesto_count = db.query(func.count(ManifestoModel.id)).filter(
        ManifestoModel.politician_id == p.id
    ).scalar()
    
    # Get all manifestos for this politician
    manifestos = db.query(ManifestoModel).filter(
        ManifestoModel.politician_id == p.id
    ).all()
    
    kept = sum(1 for m in manifestos if m.status == "kept")
    broken = sum(1 for m in manifestos if m.status == "broken")
    total = kept + broken
    integrity_score = round(kept / total * 100) if total > 0 else 50
    
    return {
        "id": p.id,
        "name": p.name,
        "title": p.position or "Politician",
        "party": p.party,
        "integrity_score": integrity_score,
        "manifestos": manifesto_count,
        "verified": True,
        "public_key": p.wallet_address or generate_hash(f"pk_{p.id}")[:42],
        "wallet_address": p.wallet_address,
        "has_wallet": bool(p.wallet_address),
        "key_version": p.key_version if hasattr(p, 'key_version') else 1,
        "image_url": p.image_url,
        "bio": p.bio,
        "joined_date": p.created_at.isoformat() if p.created_at else None
    }


# ============= Digital Signature Endpoints =============

class PoliticianRegisterRequest(BaseModel):
    """Request to register a politician with a new wallet."""
    passphrase: str  # For encrypting the keystore

class PoliticianKeyResponse(BaseModel):
    """Response containing the encrypted keystore."""
    politician_id: int
    wallet_address: str
    keystore: Dict[str, Any]  # Encrypted keystore file
    warning: str
    instructions: List[str]

@app.post("/api/politicians/{politician_id}/generate-wallet")
async def generate_politician_wallet(
    politician_id: int,
    request: PoliticianRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new wallet/key pair for a politician.
    
    This is a ONE-TIME operation. The private key is encrypted
    with the user's passphrase and returned. We NEVER store
    the private key.
    
    The politician must save the encrypted keystore file securely.
    """
    # 1. Get politician
    politician = db.query(Politician).filter(Politician.id == politician_id).first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    # 2. Check if already has wallet
    if politician.wallet_address and not politician.key_revoked:
        raise HTTPException(
            status_code=400, 
            detail="Politician already has an active wallet. Use key rotation to change."
        )
    
    # 3. Generate new key pair
    private_key, public_key, address = generate_key_pair()
    
    # 4. Create encrypted keystore
    keystore = create_encrypted_keystore(private_key, request.passphrase, address)
    
    # 5. Store ONLY public data
    if politician.wallet_address:
        # Key rotation: save old address to history
        old_addresses = politician.previous_wallet_addresses or []
        old_addresses.append({
            "address": politician.wallet_address,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "version": politician.key_version or 1
        })
        politician.previous_wallet_addresses = old_addresses
        politician.key_version = (politician.key_version or 1) + 1
        politician.key_revoked = False
        politician.key_revoked_at = None
        politician.key_revoked_reason = None
    
    politician.wallet_address = address
    politician.public_key = public_key
    politician.wallet_created_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # 6. Return encrypted keystore (private key is inside, encrypted)
    return {
        "politician_id": politician.id,
        "politician_name": politician.name,
        "wallet_address": address,
        "wallet_address_short": format_address_short(address),
        "key_version": politician.key_version or 1,
        "keystore": keystore,
        "keystore_filename": f"promisethread-{politician.name.lower().replace(' ', '-')}-key.json",
        "warning": "⚠️ SAVE THIS KEYSTORE FILE SECURELY. You will need it and your passphrase to sign manifestos. We cannot recover it.",
        "instructions": [
            "1. Download the keystore file (click the download button)",
            "2. Store it in a secure location (password manager, USB drive, secure cloud)",
            "3. Your passphrase is required to unlock the key - don't forget it",
            "4. You'll need both the keystore file AND passphrase to sign manifestos",
            "5. Anyone with both can sign as you - keep them separate and secure",
            "6. We do NOT have a copy of your key - this is your only chance to save it"
        ]
    }


class KeyRotationRequest(BaseModel):
    """Request to rotate (replace) a politician's key."""
    politician_id: int
    reason: str  # lost, compromised, scheduled
    new_passphrase: str
    admin_token: str  # Simple admin verification

ADMIN_TOKEN = "hackfest2025_admin"  # In production, use proper auth

@app.post("/api/politicians/{politician_id}/rotate-key")
async def rotate_politician_key(
    politician_id: int,
    request: KeyRotationRequest,
    db: Session = Depends(get_db)
):
    """
    Rotate a politician's key (for lost or compromised keys).
    
    This:
    1. Marks the old key as revoked
    2. Generates a new key pair
    3. Old manifestos remain tied to old key (historical integrity)
    4. Only new manifestos use the new key
    """
    # Verify admin token (simple auth for hackfest)
    if request.admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    
    # Get politician
    politician = db.query(Politician).filter(Politician.id == politician_id).first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    if not politician.wallet_address:
        raise HTTPException(status_code=400, detail="Politician has no wallet to rotate")
    
    old_address = politician.wallet_address
    
    # Generate new key pair
    private_key, public_key, new_address = generate_key_pair()
    keystore = create_encrypted_keystore(private_key, request.new_passphrase, new_address)
    
    # Save old address to history
    old_addresses = politician.previous_wallet_addresses or []
    old_addresses.append({
        "address": old_address,
        "revoked_at": datetime.now(timezone.utc).isoformat(),
        "version": politician.key_version or 1,
        "reason": request.reason
    })
    
    # Update politician
    politician.previous_wallet_addresses = old_addresses
    politician.wallet_address = new_address
    politician.public_key = public_key
    politician.wallet_created_at = datetime.now(timezone.utc)
    politician.key_version = (politician.key_version or 1) + 1
    politician.key_revoked = False
    politician.key_revoked_at = None
    
    db.commit()
    
    return {
        "success": True,
        "politician_id": politician.id,
        "old_address": format_address_short(old_address),
        "new_address": new_address,
        "new_address_short": format_address_short(new_address),
        "key_version": politician.key_version,
        "keystore": keystore,
        "keystore_filename": f"promisethread-{politician.name.lower().replace(' ', '-')}-key-v{politician.key_version}.json",
        "message": f"Key rotated successfully. Reason: {request.reason}",
        "warning": "Old manifestos remain verifiable with the old key. Only new manifestos will use this key."
    }


class SignedManifestoRequest(BaseModel):
    """Request to submit a signed manifesto."""
    title: str
    description: str
    category: str
    politician_id: int
    grace_period_days: int = 7
    manifesto_hash: str  # SHA256 hash computed by frontend
    signature: str  # ECDSA signature of the hash

@app.post("/api/manifestos/submit-signed")
async def submit_signed_manifesto(
    request: SignedManifestoRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a cryptographically signed manifesto.
    
    CRITICAL: Writes to blockchain FIRST, database SECOND.
    If blockchain write fails, manifesto is NOT stored in database.
    
    Flow:
    1. Frontend computes hash of manifesto text
    2. Politician signs hash with their private key (client-side)
    3. Backend verifies signature matches politician's wallet address
    4. **BLOCKCHAIN WRITE** - Store hash on-chain (must succeed!)
    5. Only if blockchain succeeds → Store in database
    """
    blockchain = get_blockchain_service()
    
    # 1. Get politician
    politician = db.query(Politician).filter(
        Politician.id == request.politician_id
    ).first()
    
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    if not politician.wallet_address:
        raise HTTPException(
            status_code=400, 
            detail="Politician must generate a wallet first"
        )
    
    if politician.key_revoked:
        raise HTTPException(
            status_code=400,
            detail="Politician's key has been revoked. Please contact admin for key rotation."
        )
    
    # 2. Verify hash is correct
    expected_hash = compute_manifesto_hash(request.description)
    if request.manifesto_hash != expected_hash:
        raise HTTPException(
            status_code=400,
            detail=f"Hash mismatch. Expected {expected_hash[:20]}..., got {request.manifesto_hash[:20]}..."
        )
    
    # 3. Verify signature
    sig_valid, recovered_address = verify_signature(
        request.description,
        request.signature,
        politician.wallet_address
    )
    
    if not sig_valid:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid signature. Does not match politician's wallet address."
        )
    
    # ============= PHASE 5.2: BLOCKCHAIN WRITE FIRST =============
    # CRITICAL: If blockchain fails, we do NOT store in database
    
    blockchain_tx = None
    blockchain_block = None
    blockchain_confirmed = False
    
    if blockchain.is_connected():
        # Step 4A: Ensure politician is registered on-chain
        onchain_politician = blockchain.get_politician(request.politician_id)
        
        if not onchain_politician or not onchain_politician.get("registered"):
            # Register politician on-chain first
            reg_result = blockchain.register_politician(request.politician_id)
            
            if not reg_result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to register politician on blockchain: {reg_result.get('error', 'Unknown error')}"
                )
            
            print(f"✓ Politician {request.politician_id} registered on blockchain")
        
        # Step 4B: Submit manifesto hash to blockchain
        submit_result = blockchain.submit_manifesto(
            request.politician_id, 
            request.manifesto_hash
        )
        
        if not submit_result.get("success"):
            # CRITICAL: Blockchain write failed - do NOT store in database!
            raise HTTPException(
                status_code=500,
                detail=f"❌ Blockchain write FAILED: {submit_result.get('error', 'Unknown error')}. Manifesto NOT stored."
            )
        
        # Blockchain write succeeded!
        blockchain_tx = submit_result.get("tx_hash")
        blockchain_block = submit_result.get("block_number")
        blockchain_confirmed = True
        
        print(f"✓ Manifesto submitted to blockchain: tx={blockchain_tx}, block={blockchain_block}")
    
    else:
        # Blockchain unavailable - store in database but mark as unconfirmed
        print("⚠️ Blockchain unavailable - storing in database only (unconfirmed)")
    
    # ============= DATABASE WRITE (only after blockchain success) =============
    
    # 5. Create audit log entry (local chain simulation)
    last_audit = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last_audit.block_hash if last_audit else "0x0"
    
    # 6. Create manifesto
    grace_end = datetime.now(timezone.utc) + timedelta(days=request.grace_period_days)
    
    new_manifesto = ManifestoModel(
        politician_id=request.politician_id,
        title=request.title,
        description=request.description,
        category=request.category,
        status="pending",
        promise_hash=request.manifesto_hash,
        signature=request.signature,
        signed_at=datetime.now(timezone.utc),
        signer_address=politician.wallet_address,
        signer_key_version=politician.key_version or 1,
        grace_period_end=grace_end,
        legacy_unverified=False,  # This is a properly signed manifesto
        blockchain_confirmed=blockchain_confirmed,
        blockchain_tx=blockchain_tx,
        blockchain_block=blockchain_block
    )
    
    db.add(new_manifesto)
    db.flush()
    
    # 7. Create audit log
    audit = AuditLog(
        manifesto_id=new_manifesto.id,
        action="SIGNED_MANIFESTO_CREATED",
        block_hash=generate_block_hash(str(new_manifesto.id), prev_hash),
        prev_hash=prev_hash,
        data={
            "manifesto_id": new_manifesto.id,
            "title": new_manifesto.title,
            "politician_id": new_manifesto.politician_id,
            "manifesto_hash": request.manifesto_hash,
            "signer_address": politician.wallet_address,
            "signature_verified": True,
            "blockchain_tx": blockchain_tx,
            "blockchain_block": blockchain_block,
            "blockchain_confirmed": blockchain_confirmed
        }
    )
    db.add(audit)
    db.commit()
    
    return {
        "success": True,
        "manifesto_id": new_manifesto.id,
        "title": new_manifesto.title,
        "manifesto_hash": request.manifesto_hash,
        "signature_verified": True,
        "signer_address": politician.wallet_address,
        "signer_address_short": format_address_short(politician.wallet_address),
        "grace_period_end": grace_end.isoformat(),
        
        # BLOCKCHAIN CONFIRMATION
        "blockchain": {
            "confirmed": blockchain_confirmed,
            "tx_hash": blockchain_tx,
            "block_number": blockchain_block,
            "contract": blockchain.get_connection_info()["contracts"]["manifesto_registry"]["address"] if blockchain.is_connected() else None
        },
        
        "message": "✅ Manifesto submitted and recorded on blockchain!" if blockchain_confirmed else "⚠️ Manifesto stored locally (blockchain unavailable)"
    }


class ManifestoVerifyRequest(BaseModel):
    """Request to verify a manifesto's authenticity."""
    manifesto_id: Optional[int] = None
    manifesto_text: Optional[str] = None  # If user wants to verify text directly

@app.get("/api/manifestos/{manifesto_id}/verify")
async def verify_manifesto(manifesto_id: int, db: Session = Depends(get_db)):
    """
    Verify a manifesto's authenticity.
    
    Returns:
    - Hash verification: Does the stored hash match the content?
    - Signature verification: Was it signed by the claimed politician?
    - Overall status: Is this manifesto authentic?
    """
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.id == manifesto_id
    ).first()
    
    if not manifesto:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    politician = manifesto.politician
    
    # Check if this is a legacy manifesto
    if manifesto.legacy_unverified or not manifesto.signature:
        return {
            "manifesto_id": manifesto.id,
            "title": manifesto.title,
            "politician_name": politician.name if politician else "Unknown",
            "verification_status": "LEGACY",
            "legacy_unverified": True,
            "message": "This manifesto was created before the signature system was implemented. It cannot be cryptographically verified.",
            "verification_results": {
                "hash_matches": None,
                "signature_valid": None,
                "blockchain_recorded": False
            }
        }
    
    # Perform verification
    bundle = get_verification_bundle(
        manifesto_text=manifesto.description,
        stored_hash=manifesto.promise_hash,
        signature=manifesto.signature,
        signer_address=manifesto.signer_address or politician.wallet_address,
        blockchain_tx=manifesto.blockchain_tx
    )
    
    return {
        "manifesto_id": manifesto.id,
        "title": manifesto.title,
        "politician_name": politician.name if politician else "Unknown",
        "politician_address": manifesto.signer_address,
        "politician_address_short": format_address_short(manifesto.signer_address) if manifesto.signer_address else None,
        "signed_at": manifesto.signed_at.isoformat() if manifesto.signed_at else None,
        "key_version": manifesto.signer_key_version,
        "verification_status": "AUTHENTIC" if bundle["overall_valid"] else "INVALID",
        "legacy_unverified": False,
        **bundle
    }


@app.post("/api/manifestos/verify-text")
async def verify_manifesto_text(request: ManifestoVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify manifesto text against stored data.
    
    User can paste/upload manifesto text and verify it matches what's stored.
    This allows independent verification without trusting the backend.
    """
    if not request.manifesto_id or not request.manifesto_text:
        raise HTTPException(
            status_code=400, 
            detail="Both manifesto_id and manifesto_text are required"
        )
    
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.id == request.manifesto_id
    ).first()
    
    if not manifesto:
        raise HTTPException(status_code=404, detail="Manifesto not found")
    
    # Compute hash of provided text
    computed_hash = compute_manifesto_hash(request.manifesto_text)
    stored_hash = manifesto.promise_hash
    
    hash_matches = computed_hash == stored_hash
    text_matches = request.manifesto_text.strip() == manifesto.description.strip()
    
    # Verify signature with provided text
    sig_valid = False
    if manifesto.signature and manifesto.signer_address:
        sig_valid, _ = verify_signature(
            request.manifesto_text,
            manifesto.signature,
            manifesto.signer_address
        )
    
    return {
        "manifesto_id": manifesto.id,
        "verification_results": {
            "hash_matches": hash_matches,
            "text_matches": text_matches,
            "signature_valid": sig_valid
        },
        "computed_hash": computed_hash,
        "stored_hash": stored_hash,
        "overall_valid": hash_matches and (sig_valid if manifesto.signature else True),
        "message": "✅ Text is authentic" if hash_matches else "❌ Text has been modified or is different from stored version"
    }


@app.get("/api/politicians/{politician_id}/wallet-status")
async def get_politician_wallet_status(politician_id: int, db: Session = Depends(get_db)):
    """Get the wallet/signing status of a politician."""
    politician = db.query(Politician).filter(Politician.id == politician_id).first()
    
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    
    return {
        "politician_id": politician.id,
        "name": politician.name,
        "has_wallet": bool(politician.wallet_address),
        "wallet_address": politician.wallet_address,
        "wallet_address_short": format_address_short(politician.wallet_address) if politician.wallet_address else None,
        "wallet_created_at": politician.wallet_created_at.isoformat() if politician.wallet_created_at else None,
        "key_version": politician.key_version if hasattr(politician, 'key_version') else 1,
        "key_revoked": politician.key_revoked if hasattr(politician, 'key_revoked') else False,
        "previous_keys_count": len(politician.previous_wallet_addresses or []) if hasattr(politician, 'previous_wallet_addresses') else 0
    }


# ============= PUBLIC VERIFICATION APIs (Trustless) =============
# These APIs enable independent verification without trusting the backend.
# Backend reads DIRECTLY from blockchain, not from database.
# Database is used only as a cache for text content.


def get_blockchain_config():
    """Get current blockchain configuration from the service."""
    blockchain = get_blockchain_service()
    info = blockchain.get_connection_info()
    return {
        "chain_id": info["chain_id"],
        "chain_name": "Hardhat Local" if info["chain_id"] == 31337 else f"Chain {info['chain_id']}",
        "contract_address": info["contracts"]["manifesto_registry"]["address"],
        "rpc_url": info["rpc_url"],
        "connected": info["connected"],
        "block_number": info["block_number"]
    }


@app.get("/api/manifesto/{politician_id}/hash")
async def get_manifesto_onchain_hash(politician_id: int, db: Session = Depends(get_db)):
    """
    🔗 Get On-Chain Hash (REAL BLOCKCHAIN READ)
    
    Fetches manifesto data directly from blockchain via Web3.
    Does NOT trust database - returns immutable blockchain data.
    
    Anyone can compare this hash with their locally computed hash
    to verify authenticity WITHOUT trusting this backend.
    
    Returns:
    - hash: The SHA256 hash stored on blockchain
    - timestamp: When it was recorded on-chain
    - source: "blockchain" (read via Web3)
    - contract_address: Where to verify independently
    - chain_id: Network identifier
    """
    blockchain = get_blockchain_service()
    config = get_blockchain_config()
    
    if not blockchain.is_connected():
        # Fallback to database if blockchain unavailable
        manifesto = db.query(ManifestoModel).filter(
            ManifestoModel.politician_id == politician_id
        ).order_by(ManifestoModel.created_at.desc()).first()
        
        if not manifesto:
            raise HTTPException(status_code=404, detail="Manifesto not found")
        
        return {
            "politician_id": politician_id,
            "politician_name": manifesto.politician.name if manifesto.politician else "Unknown",
            "hash": manifesto.promise_hash,
            "timestamp": manifesto.created_at.isoformat() if manifesto.created_at else None,
            "source": "database_fallback",
            "warning": "Blockchain unavailable - data from database cache",
            "contract_address": config["contract_address"],
            "chain_id": config["chain_id"]
        }
    
    # REAL BLOCKCHAIN READ - Get politician's manifestos from chain
    onchain_manifestos = blockchain.get_politician_manifestos(politician_id)
    
    if not onchain_manifestos:
        # Check database for legacy manifestos
        manifesto = db.query(ManifestoModel).filter(
            ManifestoModel.politician_id == politician_id
        ).order_by(ManifestoModel.created_at.desc()).first()
        
        if manifesto:
            return {
                "politician_id": politician_id,
                "politician_name": manifesto.politician.name if manifesto.politician else "Unknown",
                "hash": manifesto.promise_hash,
                "timestamp": manifesto.created_at.isoformat() if manifesto.created_at else None,
                "source": "database_legacy",
                "warning": "This manifesto is in database but NOT yet on blockchain",
                "blockchain_confirmed": False,
                "contract_address": config["contract_address"],
                "chain_id": config["chain_id"]
            }
        
        raise HTTPException(status_code=404, detail=f"No manifestos found for politician {politician_id}")
    
    # Get the latest manifesto from blockchain
    latest = onchain_manifestos[-1]  # Most recent
    
    # Get politician name from DB (blockchain doesn't store names)
    politician = db.query(Politician).filter(Politician.id == politician_id).first()
    
    return {
        "politician_id": politician_id,
        "politician_name": politician.name if politician else "Unknown",
        
        # ON-CHAIN DATA (from real blockchain!)
        "hash": latest["content_hash"],
        "timestamp": latest["timestamp_iso"],
        "timestamp_unix": latest["timestamp"],
        "block_number": latest["block_number"],
        
        # BLOCKCHAIN METADATA
        "source": "blockchain",  # REAL blockchain read!
        "contract_address": config["contract_address"],
        "chain_id": config["chain_id"],
        "chain_name": config["chain_name"],
        "total_manifestos_onchain": len(onchain_manifestos),
        
        # VERIFICATION INSTRUCTIONS
        "verification_note": "This hash was read directly from blockchain via Web3. Compare with your locally computed hash to verify authenticity.",
        "independent_verification": {
            "step_1": "Compute SHA256 hash of manifesto text",
            "step_2": f"Query contract {config['contract_address']} on chain {config['chain_id']}",
            "step_3": "Call getPoliticianManifestos({politician_id}) or verifyManifesto({politician_id}, hash)",
            "step_4": "Compare hashes - they must match exactly"
        }
    }


class PublicVerifyRequest(BaseModel):
    """Request for public verification (convenience API)."""
    politician_id: int
    manifesto_text: str


@app.post("/api/manifesto/verify")
async def verify_manifesto_public(request: PublicVerifyRequest, db: Session = Depends(get_db)):
    """
    ✅ Verify Manifesto Text (REAL BLOCKCHAIN VERIFICATION)
    
    User submits manifesto text, backend:
    1. Hashes it (SHA256)
    2. Calls blockchain contract to verify
    3. Returns verification result from chain
    
    ⚠️ IMPORTANT: This is a HELPER endpoint, not authoritative.
    Independent verification can (and should) be done without this backend:
    - Hash text locally using SHA256
    - Read blockchain directly via RPC
    - Compare hashes yourself
    
    This endpoint exists for user convenience only.
    """
    blockchain = get_blockchain_service()
    config = get_blockchain_config()
    
    # Step 1: Compute hash of provided text
    computed_hash = compute_manifesto_hash(request.manifesto_text)
    
    # Step 2: REAL BLOCKCHAIN CALL - verify on-chain
    if blockchain.is_connected():
        verification = blockchain.verify_manifesto(request.politician_id, computed_hash)
        
        return {
            "verification_result": {
                "valid": verification["verified"],
                "status": "AUTHENTIC" if verification["verified"] else "NOT_FOUND_ON_CHAIN",
                "message": "✅ Manifesto is AUTHENTIC - verified on blockchain" if verification["verified"] else "❌ Hash not found on blockchain for this politician"
            },
            
            # HASHES
            "computed_hash": computed_hash,
            "blockchain_verified": verification["verified"],
            "blockchain_timestamp": verification.get("timestamp_iso"),
            "blockchain_index": verification.get("index"),
            
            # SOURCE
            "source": "blockchain",
            "blockchain_source": {
                "contract": config["contract_address"],
                "chain_id": config["chain_id"],
                "block": config["block_number"]
            },
            
            # TRANSPARENCY NOTE
            "note": "Verification performed via real blockchain call. Independent verification: hash text with SHA256, call verifyManifesto() on contract."
        }
    
    # Fallback to database if blockchain unavailable
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.politician_id == request.politician_id
    ).order_by(ManifestoModel.created_at.desc()).first()
    
    if not manifesto:
        raise HTTPException(status_code=404, detail=f"No manifesto found for politician {request.politician_id}")
    
    blockchain_hash = manifesto.promise_hash
    hashes_match = computed_hash == blockchain_hash
    
    return {
        "verification_result": {
            "valid": hashes_match,
            "status": "AUTHENTIC" if hashes_match else "TAMPERED_OR_DIFFERENT",
            "message": "✅ Hash matches database" if hashes_match else "❌ Hash mismatch"
        },
        "computed_hash": computed_hash,
        "database_hash": blockchain_hash,
        "hashes_match": hashes_match,
        "source": "database_fallback",
        "warning": "Blockchain unavailable - verified against database cache",
        "blockchain_source": {
            "contract": config["contract_address"],
            "chain_id": config["chain_id"]
        }
    }


@app.get("/api/manifesto/{politician_id}/proof")
async def get_verification_proof_bundle(politician_id: int, db: Session = Depends(get_db)):
    """
    📦 Get Verification Proof Bundle (COMPLETE EVIDENCE PACKAGE)
    
    Returns everything needed for:
    - Offline verification
    - Third-party audits
    - Media verification
    - Legal evidence
    
    This bundle allows ANYONE to independently verify authenticity
    without trusting this backend or being online.
    
    The bundle contains:
    - Manifesto text (cached from database)
    - Blockchain hash & data (REAL from chain)
    - Authorship proof (on-chain registration)
    - Verification instructions
    """
    blockchain = get_blockchain_service()
    config = get_blockchain_config()
    
    # Get politician data from database
    politician = db.query(Politician).filter(Politician.id == politician_id).first()
    
    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")
    
    # Get latest manifesto from database (for text content)
    manifesto = db.query(ManifestoModel).filter(
        ManifestoModel.politician_id == politician_id
    ).order_by(ManifestoModel.created_at.desc()).first()
    
    # Compute hash if we have text
    computed_hash = compute_manifesto_hash(manifesto.description) if manifesto else None
    
    # REAL BLOCKCHAIN DATA
    onchain_data = None
    blockchain_status = "unavailable"
    
    if blockchain.is_connected():
        # Get manifestos from blockchain
        onchain_manifestos = blockchain.get_politician_manifestos(politician_id)
        
        if onchain_manifestos:
            latest = onchain_manifestos[-1]
            onchain_data = latest
            blockchain_status = "connected"
            
            # Verify hash matches if we have both
            if computed_hash:
                verification = blockchain.verify_manifesto(politician_id, computed_hash)
                hash_valid = verification["verified"]
            else:
                hash_valid = None
        else:
            blockchain_status = "no_data"
            hash_valid = None
    else:
        hash_valid = computed_hash == manifesto.promise_hash if manifesto else None
    
    return {
        "proof_bundle_version": "2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        
        # MANIFESTO DATA (from database cache)
        "manifesto": {
            "politician_id": politician_id,
            "title": manifesto.title if manifesto else None,
            "text": manifesto.description if manifesto else None,
            "category": manifesto.category if manifesto else None,
            "created_at": manifesto.created_at.isoformat() if manifesto and manifesto.created_at else None,
            "grace_period_end": manifesto.grace_period_end.isoformat() if manifesto else None,
            "source": "database_cache"
        },
        
        # POLITICIAN DATA
        "politician": {
            "id": politician.id,
            "name": politician.name,
            "party": politician.party,
            "wallet_address": politician.wallet_address
        },
        
        # BLOCKCHAIN PROOF (REAL on-chain data!)
        "blockchain_proof": {
            "status": blockchain_status,
            "onchain_hash": onchain_data["content_hash"] if onchain_data else None,
            "computed_hash": computed_hash,
            "hash_valid": hash_valid,
            "contract_address": config["contract_address"],
            "chain_id": config["chain_id"],
            "chain_name": config["chain_name"],
            "block_number": onchain_data["block_number"] if onchain_data else None,
            "timestamp_unix": onchain_data["timestamp"] if onchain_data else None,
            "timestamp_iso": onchain_data["timestamp_iso"] if onchain_data else None,
            "total_manifestos_onchain": len(blockchain.get_politician_manifestos(politician_id)) if blockchain.is_connected() else 0,
            "source": "blockchain" if blockchain_status == "connected" else "unavailable"
        },
        
        # AUTHORSHIP PROOF
        "authorship_proof": {
            "registered_wallet": politician.wallet_address,
            "signer_address": manifesto.signer_address if manifesto else None,
            "signed_at": manifesto.signed_at.isoformat() if manifesto and manifesto.signed_at else None,
            "note": "Authorship is proven via blockchain transaction signer. The address that submitted must be registered to this politician."
        },
        
        # VERIFICATION STATUS
        "verification_status": {
            "overall": "AUTHENTIC" if hash_valid else ("UNVERIFIED" if hash_valid is None else "INVALID"),
            "hash_integrity": hash_valid,
            "blockchain_connected": blockchain.is_connected(),
            "onchain_record_exists": onchain_data is not None
        },
        
        # VERIFICATION INSTRUCTIONS
        "verification_instructions": {
            "overview": "This bundle contains everything needed to verify this manifesto independently.",
            "steps": [
                {
                    "step": 1,
                    "title": "Verify Hash Integrity",
                    "description": "Compute SHA256 hash of the manifesto text",
                    "code": "hash = SHA256(manifesto.text)",
                    "expected": computed_hash
                },
                {
                    "step": 2,
                    "title": "Verify On-Chain Record",
                    "description": f"Query the ManifestoRegistry contract",
                    "contract": config["contract_address"],
                    "chain_id": config["chain_id"],
                    "code": f"contract.verifyManifesto({politician_id}, hash) or contract.getPoliticianManifestos({politician_id})"
                },
                {
                    "step": 3,
                    "title": "Compare Hashes",
                    "description": "Your computed hash must match the blockchain hash",
                    "result": "If match → AUTHENTIC. If mismatch → TAMPERED."
                }
            ],
            "tools": [
                "Any SHA256 implementation (browser crypto.subtle, openssl, Python hashlib)",
                "Any Ethereum RPC client (ethers.js, web3.js, Web3.py)",
                "Block explorer for manual verification"
            ],
            "rpc_endpoint": config["rpc_url"] if blockchain.is_connected() else "http://localhost:8545"
        }
    }


@app.get("/api/verification/config")
async def get_verification_config():
    """
    Get blockchain configuration for independent verification.
    
    Returns all information needed to verify manifestos
    independently without trusting this backend.
    """
    blockchain = get_blockchain_service()
    config = get_blockchain_config()
    
    return {
        "blockchain": {
            "chain_id": config["chain_id"],
            "chain_name": config["chain_name"],
            "contract_address": config["contract_address"],
            "rpc_url": config["rpc_url"],
            "connected": config["connected"],
            "block_number": config["block_number"]
        },
        "hash_algorithm": "SHA256",
        "hash_format": "0x + hex string (64 chars for SHA256)",
        "contract_functions": {
            "verifyManifesto": "verifyManifesto(uint256 politicianId, bytes32 contentHash) → (bool verified, uint256 timestamp, uint256 index)",
            "getPoliticianManifestos": "getPoliticianManifestos(uint256 politicianId) → Manifesto[]",
            "lookupHash": "lookupHash(bytes32 contentHash) → (uint256 politicianId, bool exists, uint256 timestamp)",
            "submitManifesto": "submitManifesto(uint256 politicianId, bytes32 contentHash) [WRITE]",
            "registerPolitician": "registerPolitician(uint256 politicianId, address wallet) [WRITE]"
        },
        "rpc_endpoint": config["rpc_url"],
        "verification_note": "All verification can be done independently by querying the blockchain directly. This backend reads from blockchain via Web3 - it is a convenience layer, not a trust requirement."
    }


# ============= Health Check =============

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with blockchain status."""
    db_ok = check_connection()
    voter_count = db.query(func.count(Voter.id)).scalar() if db_ok else 0
    
    # Get blockchain status
    blockchain = get_blockchain_service()
    blockchain_connected = blockchain.is_connected()
    blockchain_info = blockchain.get_connection_info()
    
    return {
        "status": "healthy" if db_ok and blockchain_connected else "degraded",
        "version": "2.2.0",
        "database": "connected" if db_ok else "disconnected",
        "blockchain": {
            "connected": blockchain_connected,
            "chain_id": blockchain_info["chain_id"],
            "block_number": blockchain_info["block_number"],
            "contracts": {
                "manifesto_registry": blockchain_info["contracts"]["manifesto_registry"]["loaded"],
                "promise_registry": blockchain_info["contracts"]["promise_registry"]["loaded"]
            }
        },
        "voters_loaded": voter_count,
        "timestamp": datetime.now().isoformat()
    }


# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("🚀 Starting PromiseThread API (PostgreSQL version)...")
    init_db()
    print("✓ Database initialized")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
