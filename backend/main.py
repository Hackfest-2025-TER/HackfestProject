from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import secrets
import json

app = FastAPI(
    title="PromiseThread API",
    description="Decentralized Political Accountability Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Models =============

class ZKProofRequest(BaseModel):
    commitment: str
    proof: str

class ZKProofResponse(BaseModel):
    valid: bool
    credential: Optional[str] = None
    nullifier: Optional[str] = None
    message: str

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

# ============= ZK Proof Endpoints =============

@app.post("/api/zk/verify", response_model=ZKProofResponse)
async def verify_zk_proof(request: ZKProofRequest):
    """
    Verify a zero-knowledge proof and issue anonymous credential.
    In production, this would verify actual zk-SNARK proofs.
    """
    # Simulated ZK verification
    if len(request.commitment) < 10 or len(request.proof) < 10:
        return ZKProofResponse(
            valid=False,
            message="Invalid proof format"
        )
    
    # Generate anonymous credential
    credential = generate_credential()
    nullifier = generate_nullifier()
    
    # Store credential mapping (in production, only nullifier hash would be stored)
    credentials_db[nullifier] = {
        "credential": credential,
        "created_at": datetime.now().isoformat(),
        "used_votes": []
    }
    
    return ZKProofResponse(
        valid=True,
        credential=credential,
        nullifier=nullifier,
        message="ZK proof verified. Anonymous credential issued."
    )

@app.get("/api/zk/credential/{nullifier}")
async def check_credential(nullifier: str):
    """Check if a credential/nullifier is valid and unused for a specific manifesto."""
    if nullifier in credentials_db:
        return {
            "valid": True,
            "used_votes": credentials_db[nullifier]["used_votes"]
        }
    return {"valid": False, "used_votes": []}

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
