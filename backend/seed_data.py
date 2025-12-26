"""
Seed Data Script for PromiseThread
===================================
Seeds initial data for representatives and sample manifestos.
"""

from datetime import datetime, timedelta
import hashlib
import re
from sqlalchemy.orm import Session

from database import get_db_context, init_db
from models import Representative, Manifesto, AuditLog, ManifestoVote, Comment, CommentVote
# Import crypto utils
from crypto_utils import generate_key_pair, create_signature, compute_manifesto_hash

def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from representative name."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def generate_block_hash(data: str, prev_hash: str) -> str:
    """Generate a block hash for audit trail."""
    combined = f"{data}:{prev_hash}".encode('utf-8')
    return '0x' + hashlib.sha256(combined).hexdigest()

def generate_fake_tx_hash() -> str:
    """Generate a fake blockchain transaction hash."""
    return '0x' + hashlib.sha256(datetime.utcnow().isoformat().encode()).hexdigest()

# =============================================================================
# SAMPLE REPRESENTATIVES DATA (Generic Names)
# =============================================================================

REPRESENTATIVES = [
    {
        "name": "Ram Bahadur Thapa",
        "party": "Democratic Party",
        "position": "Senior Leader",
        "image_url": "https://randomuser.me/api/portraits/men/1.jpg",
        "bio": "A dedicated public servant with 20 years of experience in local governance."
    },
    {
        "name": "Priya Patel",
        "party": "Progressive Alliance",
        "position": "Representative",
        "image_url": "https://randomuser.me/api/portraits/women/2.jpg",
        "bio": "Advocate for education reform and digital literacy in rural communities."
    },
    {
        "name": "Amit Verma",
        "party": "National Development Party",
        "position": "General Secretary",
        "image_url": "https://randomuser.me/api/portraits/men/3.jpg",
        "bio": "Economist turned politician, focused on sustainable infrastructure development."
    },
    {
        "name": "Sita Devi Sharma",
        "party": "Social Justice Party",
        "position": "Chairperson",
        "image_url": "https://randomuser.me/api/portraits/women/4.jpg",
        "bio": "Champion of women's rights and healthcare access for all citizens."
    },
    {
        "name": "Hari Krishna Shrestha",
        "party": "Unified People's Party",
        "position": "Spokesperson",
        "image_url": "https://randomuser.me/api/portraits/men/5.jpg",
        "bio": "Former journalist committed to transparency and anti-corruption measures."
    }
]

# =============================================================================
# SAMPLE MANIFESTOS DATA
# =============================================================================

def get_manifestos_data() -> list:
    """Get manifestos with dynamic dates based on current time."""
    now = datetime.utcnow()
    
    return [
        # PENDING - Future
        {
            "representative_index": 0, # Ram Bahadur Thapa
            "title": "Road Expansion Project",
            "description": "Expand the main highway connecting rural districts to the capital to 4 lanes. This project aims to reduce travel time by 50% and boost local trade.",
            "category": "infrastructure",
            "status": "pending",
            "grace_period_end": now + timedelta(days=180),
            "vote_kept": 0,
            "vote_broken": 0
        },
        {
            "representative_index": 1, # Priya Patel
            "title": "Digital Classrooms Initiative",
            "description": "Equip 500 government schools with smart classrooms and high-speed internet effectively bridging the digital divide.",
            "category": "education",
            "status": "pending",
            "grace_period_end": now + timedelta(days=365),
            "vote_kept": 0,
            "vote_broken": 0
        },
        {
            "representative_index": 2, # Amit Verma
            "title": "Green Energy Subsidy",
            "description": "Provide 50% subsidy on solar panel installation for 10,000 households to promote renewable energy usage.",
            "category": "environment",
            "status": "pending",
            "grace_period_end": now + timedelta(days=90),
            "vote_kept": 0,
            "vote_broken": 0
        },
        
        # PENDING - Voting Open
        {
            "representative_index": 3, # Sita Devi Sharma
            "title": "Community Health Centers",
            "description": "Establish fully staffed 24/7 health centers in every ward of the constituency.",
            "category": "healthcare",
            "status": "pending",
            "grace_period_end": now - timedelta(days=30),
            "vote_kept": 245,
            "vote_broken": 89
        },
        {
            "representative_index": 4, # Hari Krishna Shrestha
            "title": "Zero Tolerance on Bribery",
            "description": "Implement a fully digital tracking system for all government services to eliminate bribery.",
            "category": "governance",
            "status": "pending",
            "grace_period_end": now - timedelta(days=60),
            "vote_kept": 567,
            "vote_broken": 234
        },
        
        # KEPT
        {
            "representative_index": 1, # Priya Patel
            "title": "Girls Scholarship Program",
            "description": "Provided full scholarships to 1,000 underprivileged girls for higher secondary education.",
            "category": "education",
            "status": "kept",
            "grace_period_end": now - timedelta(days=400),
            "vote_kept": 2500,
            "vote_broken": 150
        },
        
        # BROKEN
        {
            "representative_index": 2, # Amit Verma
            "title": "Free Public Wi-Fi",
            "description": "Promise to provide free Wi-Fi in all public parks was not fulfilled due to budget constraints.",
            "category": "infrastructure",
            "status": "broken",
            "grace_period_end": now - timedelta(days=500),
            "vote_kept": 400,
            "vote_broken": 3200
        }
    ]

# =============================================================================
# SEED FUNCTIONS
# =============================================================================

def seed_representatives(db: Session) -> list[dict]:
    """
    Seed representatives and generate key pairs.
    Returns list of dicts with model and private_key.
    """
    print("\n📥 Seeding representatives...")
    
    reps_with_keys = []
    
    for data in REPRESENTATIVES:
        # Generate crypto keys
        private_key, public_key, address = generate_key_pair()
        
        data_model = data.copy()
        data_model['slug'] = generate_slug(data['name'])
        data_model['wallet_address'] = address
        data_model['public_key'] = public_key
        data_model['is_verified'] = True
        
        representative = Representative(**data_model)
        db.add(representative)
        db.flush() # get ID
        
        reps_with_keys.append({
            "model": representative,
            "private_key": private_key
        })
    
    print(f"  ✓ Created {len(reps_with_keys)} representatives with wallets")
    return reps_with_keys

def seed_manifestos(db: Session, reps_with_keys: list[dict]) -> list[Manifesto]:
    """Seed manifestos and sign them."""
    print("\n📥 Seeding manifestos...")
    
    manifestos = []
    
    for data in get_manifestos_data():
        # Get representative and keys
        rep_idx = data.pop("representative_index")
        rep_info = reps_with_keys[rep_idx]
        rep_model = rep_info["model"]
        private_key = rep_info["private_key"]
        
        # Create base manifesto
        manifesto = Manifesto(**data)
        manifesto.representative_id = rep_model.id
        
        # Generate promise hash (hash of details)
        # Using simple concatenation for checking, but robust applications might use structured data
        manifesto_text = f"{manifesto.title}:{manifesto.description}:{manifesto.representative_id}"
        manifesto.promise_hash = compute_manifesto_hash(manifesto_text)
        
        # Sign the promise hash
        # We sign the hash effectively saying "I authorize this content hash"
        signature = create_signature(manifesto.promise_hash, private_key)
        
        manifesto.signature = signature
        manifesto.signer_address = rep_model.wallet_address
        manifesto.signed_at = datetime.utcnow()
        
        # Fake Blockchain confirmation
        manifesto.blockchain_tx = generate_fake_tx_hash()
        manifesto.blockchain_block = 12345 + len(manifestos)
        manifesto.blockchain_confirmed = True
        
        db.add(manifesto)
        manifestos.append(manifesto)
    
    db.flush()
    print(f"  ✓ Created {len(manifestos)} signed manifestos")
    return manifestos

def seed_audit_logs(db: Session, manifestos: list[Manifesto]):
    """Create audit logs with full verification data."""
    print("\n📥 Seeding audit trail...")
    
    # Genesis block
    genesis = AuditLog(
        manifesto_id=None,
        action="GENESIS_BLOCK",
        block_hash=generate_block_hash("GENESIS", "0x0"),
        prev_hash="0x0000000000000000000000000000000000000000000000000000000000000000",
        data={"message": "PromiseThread Genesis Block", "timestamp": datetime.utcnow().isoformat()}
    )
    db.add(genesis)
    db.flush()
    
    prev_hash = genesis.block_hash
    
    for manifesto in manifestos:
        # Full data dump matching API enhanced structure
        block_data = {
            "manifesto_id": manifesto.id,
            "title": manifesto.title,
            "description": manifesto.description,
            "representative_id": manifesto.representative_id,
            "promise_hash": manifesto.promise_hash,
            "status": manifesto.status,
            
            # Verification Data
            "signature": manifesto.signature,
            "signer_address": manifesto.signer_address,
            "signature_verified": True,
            
            "blockchain_tx": manifesto.blockchain_tx,
            "blockchain_block": manifesto.blockchain_block,
            "blockchain_confirmed": True,
            
            "timestamp": manifesto.created_at.isoformat() if manifesto.created_at else datetime.utcnow().isoformat()
        }
        
        # Action type
        action_type = "PROMISE_CREATED"
        if manifesto.signature:
            action_type = "SIGNED_MANIFESTO_CREATED"
            
        audit = AuditLog(
            manifesto_id=manifesto.id,
            action=action_type,
            block_hash=generate_block_hash(str(manifesto.id), prev_hash),
            prev_hash=prev_hash,
            data=block_data
        )
        db.add(audit)
        db.flush()
        prev_hash = audit.block_hash
        
    print(f"  ✓ Created {len(manifestos) + 1} audit logs")

def clear_seed_data(db: Session):
    """Clear all seeded data."""
    # Delete in correct order to handle Foreign Keys
    db.query(AuditLog).delete()
    db.query(CommentVote).delete()
    db.query(Comment).delete()
    db.query(ManifestoVote).delete()
    db.query(Manifesto).delete()
    db.query(Representative).delete()
    db.commit()
    print("  ✓ Cleared existing seed data")

def main():
    """Main entry point for seeding."""
    print("=" * 60)
    print("  SEED DATA (REAL CRYPTO)")
    print("=" * 60)
    
    init_db()
    
    with get_db_context() as db:
        # Always clear old data to ensure consistent crypto linkage
        clear_seed_data(db)
        
        # Seed new data
        reps_info = seed_representatives(db)
        manifestos = seed_manifestos(db, reps_info)
        seed_audit_logs(db, manifestos)
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("  SEEDING COMPLETE")
        print("=" * 60)
        print(f"  Representatives: {len(reps_info)}")
        print(f"  Manifestos:      {len(manifestos)}")
        print("=" * 60)

if __name__ == "__main__":
    main()
