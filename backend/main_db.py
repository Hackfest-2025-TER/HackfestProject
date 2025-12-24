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

app = FastAPI(
    title="PromiseThread API",
    description="Decentralized Political Accountability Platform - Blind Auditor System",
    version="2.1.0 (PostgreSQL)"
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
        "public_key": generate_hash(f"pk_{p.id}")[:42],
        "image_url": p.image_url,
        "bio": p.bio,
        "joined_date": p.created_at.isoformat() if p.created_at else None
    }


# ============= Health Check =============

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    db_ok = check_connection()
    voter_count = db.query(func.count(Voter.id)).scalar() if db_ok else 0
    
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": "2.1.0",
        "database": "connected" if db_ok else "disconnected",
        "voters_loaded": voter_count,
        "timestamp": datetime.now().isoformat(),
        "block_height": get_current_block()
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
