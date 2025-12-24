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
    nullifier_hash = Column(String(66), unique=True, nullable=False, index=True)
    credential_hash = Column(String(66), nullable=False)
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
    - Full text stored here (off-chain)
    - promise_hash stored on blockchain (on-chain)
    - vote_kept/vote_broken are cached aggregates
    """
    __tablename__ = 'manifestos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    politician_id = Column(Integer, ForeignKey('politicians.id'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # infrastructure, economy, education, etc.
    status = Column(String(20), default='pending')  # pending, kept, broken
    promise_hash = Column(String(66), nullable=True)  # Keccak256 hash for blockchain
    grace_period_end = Column(DateTime, nullable=False)  # When voting opens
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
    - Anonymous via nullifier_display (truncated)
    - upvotes/downvotes are cached aggregates
    """
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    manifesto_id = Column(Integer, ForeignKey('manifestos.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)  # NULL = top-level
    nullifier_display = Column(String(20), nullable=False)  # Truncated: "abc123..."
    content = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)  # Cached aggregate
    downvotes = Column(Integer, default=0)  # Cached aggregate
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manifesto = relationship("Manifesto", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    comment_votes = relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Comment {self.id} by {self.nullifier_display}>"


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
