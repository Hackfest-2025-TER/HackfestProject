"""
SQLAlchemy Models for PromiseThread
====================================
Database schema for the decentralized political accountability platform.

Privacy Architecture:
- Voters table has NO foreign key to credentials (true anonymity)
- Nullifiers are used for tracking votes without revealing identity
- ZK proofs verify eligibility without storing personal data
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()


# =============================================================================
# VOTER REGISTRY (from CSV import)
# =============================================================================

class Voter(Base):
    """
    Voter registry imported from election commission data.
    Used ONLY for Merkle tree computation and ZK proof verification.
    NO link to credentials or votes.
    """
    __tablename__ = 'voters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    voter_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    spouse_name = Column(String(255), nullable=True)
    parent_name = Column(String(255), nullable=True)
    province = Column(String(50), nullable=True)
    district = Column(String(100), nullable=True)
    vdc = Column(String(100), nullable=True)  # Village Development Committee / Municipality
    ward = Column(Integer, nullable=True)
    registration_center = Column(String(255), nullable=True)
    merkle_leaf = Column(String(66), nullable=True)  # Keccak256 hash for Merkle tree
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Voter {self.voter_id}: {self.name}>"


# =============================================================================
# ZK CREDENTIALS (anonymous authentication)
# =============================================================================

class ZKCredential(Base):
    """
    Zero-knowledge credentials for anonymous authentication.
    NO foreign key to voters - this is intentional for privacy!
    """
    __tablename__ = 'zk_credentials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nullifier_hash = Column(String(128), unique=True, nullable=False, index=True)  # ZK nullifiers can be ~78 chars
    credential_hash = Column(String(128), nullable=False)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ZKCredential {self.nullifier_hash[:12]}...>"


# =============================================================================
# POLITICIANS
# =============================================================================

class Politician(Base):
    """
    Politicians who make promises. Will be seeded with sample data.
    
    Digital Signature Architecture:
    - wallet_address: Public Ethereum address (stored)
    - private key: NEVER stored - given to politician once
    - Signatures prove authorship without backend involvement
    """
    __tablename__ = 'politicians'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(300), nullable=True, unique=True, index=True)  # URL-friendly version of name
    party = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)  # PM, Minister, MP, etc.
    image_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ========= Digital Identity (Wallet) =========
    wallet_address = Column(String(42), unique=True, nullable=True)  # Ethereum address (0x...)
    wallet_created_at = Column(DateTime, nullable=True)
    public_key = Column(String(130), nullable=True)  # Full public key (for advanced verification)
    
    # ========= Key Rotation Support =========
    key_version = Column(Integer, default=1)  # Increments on key rotation
    key_revoked = Column(Boolean, default=False)  # True if key has been revoked
    key_revoked_at = Column(DateTime, nullable=True)
    key_revoked_reason = Column(String(255), nullable=True)  # "lost", "compromised", etc.
    
    # Previous wallet addresses (for historical verification)
    previous_wallet_addresses = Column(JSONB, default=list)  # List of {address, revoked_at, version}
    
    # Relationships
    manifestos = relationship("Manifesto", back_populates="politician")
    
    def __repr__(self):
        return f"<Politician {self.name} ({self.party})>"


# =============================================================================
# MANIFESTOS (Promises)
# =============================================================================

class Manifesto(Base):
    """
    Political promises/manifestos.
    
    Data Architecture:
    - Full text stored here (off-chain cache)
    - promise_hash + signature stored on blockchain (on-chain)
    - vote_kept/vote_broken are cached aggregates
    
    Signature Architecture:
    - signature: ECDSA signature of promise_hash by politician
    - Proves politician authored this manifesto
    - Cannot be forged (backend never has private key)
    """
    __tablename__ = 'manifestos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    politician_id = Column(Integer, ForeignKey('politicians.id'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # infrastructure, economy, education, etc.
    status = Column(String(20), default='pending')  # pending, kept, broken
    promise_hash = Column(String(66), nullable=True)  # SHA256 hash for blockchain
    grace_period_end = Column(DateTime, nullable=False)  # When voting opens
    
    # ========= Digital Signature Fields =========
    signature = Column(Text, nullable=True)  # ECDSA signature (hex string)
    signed_at = Column(DateTime, nullable=True)  # When signature was created
    signer_address = Column(String(42), nullable=True)  # Address that signed (for key rotation)
    signer_key_version = Column(Integer, nullable=True)  # Which key version was used
    
    # ========= Blockchain Integration =========
    blockchain_tx = Column(String(66), nullable=True)  # Transaction hash on blockchain
    blockchain_confirmed = Column(Boolean, default=False)  # True if confirmed on-chain
    blockchain_block = Column(Integer, nullable=True)  # Block number where recorded
    
    # ========= Legacy Data Handling =========
    legacy_unverified = Column(Boolean, default=False)  # True for pre-signature manifestos
    
    # Existing fields
    vote_kept = Column(Integer, default=0)  # Cached aggregate
    vote_broken = Column(Integer, default=0)  # Cached aggregate
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Check constraint for status
    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'kept', 'broken']), name='valid_status'),
    )
    
    # Relationships
    politician = relationship("Politician", back_populates="manifestos")
    votes = relationship("ManifestoVote", back_populates="manifesto", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="manifesto", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="manifesto", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Manifesto {self.id}: {self.title[:50]}...>"


# =============================================================================
# MANIFESTO VOTES (individual votes - anonymous via nullifier)
# =============================================================================

class ManifestoVote(Base):
    """
    Individual votes on manifestos.
    - Linked to nullifier (anonymous)
    - One vote per nullifier per manifesto (can change vote type)
    - vote_hash for Merkle proof verification
    """
    __tablename__ = 'manifesto_votes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'), nullable=False)
    nullifier = Column(String(66), nullable=False, index=True)  # Anonymous voter ID
    vote_type = Column(String(10), nullable=False)  # 'kept' or 'broken'
    vote_hash = Column(String(66), nullable=True)  # For Merkle proof
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('manifesto_id', 'nullifier', name='unique_vote_per_manifesto'),
        CheckConstraint(vote_type.in_(['kept', 'broken']), name='valid_vote_type'),
    )
    
    # Relationships
    manifesto = relationship("Manifesto", back_populates="votes")
    
    def __repr__(self):
        return f"<ManifestoVote {self.nullifier[:12]}... -> {self.vote_type}>"


# =============================================================================
# COMMENTS (Discussion threads)
# =============================================================================

class Comment(Base):
    """
    Discussion comments on manifestos.
    - Threaded via parent_id (self-referential)
    - Anonymous via session_id (random identifier per session)
    - upvotes/downvotes are cached aggregates
    - Cosine similarity moderation for spam/relevance
    
    Moderation States:
    - active: Visible to all users
    - auto_flagged: Flagged by similarity check, needs review
    - community_flagged: Flagged by user reports
    - quarantined: Spam detected, hidden from main view
    - soft_deleted: Deleted (cooling period before hard delete)
    
    Auto-Flag Reasons:
    - off_topic: Low similarity to manifesto promises (< 0.25)
    - spam_like: High similarity to recent comments (> 0.92)
    - low_relevance: Marginal relevance (0.25-0.40)
    """
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)  # NULL = top-level
    
    # === Legacy field for backward compatibility ===
    nullifier_display = Column(String(20), nullable=False, default='anonymous')  # Kept for DB compatibility
    
    # === Identity (no nullifier required for posting) ===
    session_id = Column(String(32), nullable=False)  # Random session identifier
    author_display = Column(String(20), nullable=True)  # Display name: "Citizen-a1b2c3"
    
    # === Content ===
    content = Column(Text, nullable=False)
    
    # === Voting (cached aggregates) ===
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    flag_count = Column(Integer, default=0)  # Community flag reports
    
    # === Moderation State ===
    state = Column(String(20), default='active')  # active, auto_flagged, community_flagged, quarantined, soft_deleted
    auto_flag_reason = Column(String(20), nullable=True)  # off_topic, spam_like, low_relevance
    
    # === Cosine Similarity Scores ===
    similarity_score = Column(Integer, nullable=True)  # 0-100 (max similarity to any promise)
    matched_promise_id = Column(Integer, nullable=True)  # ID of most similar promise
    spam_similarity_score = Column(Integer, nullable=True)  # 0-100 (max similarity to recent comments)
    
    # === Timestamps ===
    is_deleted = Column(Boolean, default=False)  # Soft delete flag
    delete_scheduled_at = Column(DateTime, nullable=True)  # When deletion was scheduled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manifesto = relationship("Manifesto", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    comment_votes = relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Comment {self.id} by {self.author_display or self.session_id[:8]}>"


# =============================================================================
# COMMENT VOTES (upvote/downvote tracking)
# =============================================================================

class CommentVote(Base):
    """
    Votes on comments (upvote/downvote).
    - One vote per nullifier per comment (can change)
    """
    __tablename__ = 'comment_votes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=False)
    nullifier = Column(String(66), nullable=False, index=True)  # Anonymous voter
    vote_type = Column(String(10), nullable=False)  # 'up' or 'down'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('comment_id', 'nullifier', name='unique_vote_per_comment'),
        CheckConstraint(vote_type.in_(['up', 'down']), name='valid_comment_vote_type'),
    )
    
    # Relationships
    comment = relationship("Comment", back_populates="comment_votes")
    
    def __repr__(self):
        return f"<CommentVote {self.nullifier[:12]}... -> {self.vote_type}>"


# =============================================================================
# AUDIT LOGS (Blockchain simulation)
# =============================================================================

class AuditLog(Base):
    """
    Audit trail for blockchain visualization.
    Each entry is a "block" with hash linking to previous.
    """
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Block number
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'), nullable=True)
    action = Column(String(50), nullable=False)  # PROMISE_CREATED, VOTE_AGGREGATED, STATUS_CHANGED
    block_hash = Column(String(66), nullable=False)
    prev_hash = Column(String(66), nullable=False)
    data = Column(JSONB, nullable=True)  # Block data as JSON
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    manifesto = relationship("Manifesto", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog Block {self.id}: {self.action}>"


# =============================================================================
# MERKLE TREE NODES (Optional - for storing intermediate computation)
# =============================================================================

class MerkleRoot(Base):
    """
    Store computed Merkle roots for vote batches.
    This is what gets stored on-chain.
    """
    __tablename__ = 'merkle_roots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    root_hash = Column(String(66), nullable=False, unique=True)
    leaf_count = Column(Integer, nullable=False)
    tree_type = Column(String(50), nullable=False)  # 'voters' or 'votes'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MerkleRoot {self.root_hash[:12]}... ({self.leaf_count} leaves)>"
