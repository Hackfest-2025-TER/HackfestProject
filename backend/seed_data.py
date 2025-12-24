"""
Seed Data Script for PromiseThread
===================================
Seeds initial data for politicians and sample manifestos.
"""

from datetime import datetime, timedelta
import hashlib
from sqlalchemy.orm import Session

from database import get_db_context, init_db
from models import Politician, Manifesto, AuditLog


def generate_promise_hash(title: str, description: str, politician_id: int) -> str:
    """Generate a hash for a promise (simulating blockchain hash)."""
    data = f"{title}:{description}:{politician_id}".encode('utf-8')
    return '0x' + hashlib.sha256(data).hexdigest()


def generate_block_hash(data: str, prev_hash: str) -> str:
    """Generate a block hash for audit trail."""
    combined = f"{data}:{prev_hash}".encode('utf-8')
    return '0x' + hashlib.sha256(combined).hexdigest()


# =============================================================================
# SAMPLE POLITICIANS DATA
# =============================================================================

POLITICIANS = [
    {
        "name": "कृष्ण प्रसाद सिटौला",
        "party": "नेपाली कांग्रेस",
        "position": "पूर्व प्रधानमन्त्री",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Krishna_Prasad_Sitaula.jpg/220px-Krishna_Prasad_Sitaula.jpg",
        "bio": "नेपाली कांग्रेसका वरिष्ठ नेता र पूर्व गृहमन्त्री"
    },
    {
        "name": "पुष्प कमल दाहाल",
        "party": "नेकपा माओवादी केन्द्र",
        "position": "प्रधानमन्त्री",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Pushpa_Kamal_Dahal.jpg/220px-Pushpa_Kamal_Dahal.jpg",
        "bio": "नेपाल कम्युनिस्ट पार्टी (माओवादी केन्द्र) का अध्यक्ष"
    },
    {
        "name": "केपी शर्मा ओली",
        "party": "नेकपा एमाले",
        "position": "पूर्व प्रधानमन्त्री",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Khadga_Prasad_Sharma_Oli.jpg/220px-Khadga_Prasad_Sharma_Oli.jpg",
        "bio": "नेपाल कम्युनिस्ट पार्टी (एकीकृत मार्क्सवादी–लेनिनवादी) का अध्यक्ष"
    },
    {
        "name": "शेर बहादुर देउवा",
        "party": "नेपाली कांग्रेस",
        "position": "पूर्व प्रधानमन्त्री",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Sher_Bahadur_Deuba.jpg/220px-Sher_Bahadur_Deuba.jpg",
        "bio": "नेपाली कांग्रेसका सभापति"
    },
    {
        "name": "राजेन्द्र लिङ्देन",
        "party": "राष्ट्रिय प्रजातन्त्र पार्टी",
        "position": "सांसद",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Rajendra_Lingden.jpg/220px-Rajendra_Lingden.jpg",
        "bio": "राष्ट्रिय प्रजातन्त्र पार्टीका अध्यक्ष"
    }
]


# =============================================================================
# SAMPLE MANIFESTOS DATA
# =============================================================================

def get_manifestos_data() -> list:
    """Get manifestos with dynamic dates based on current time."""
    now = datetime.utcnow()
    
    return [
        # =====================================================================
        # PENDING - Grace period NOT ended (cannot vote yet)
        # =====================================================================
        {
            "politician_id": 1,
            "title": "धुलिखेल-काभ्रे सडक विस्तार",
            "description": "धुलिखेलदेखि काभ्रेसम्मको सडकलाई चार लेन बनाउने। यो परियोजनाले यातायात सुधार गर्नेछ र आर्थिक विकासमा योगदान पुर्याउनेछ।",
            "category": "infrastructure",
            "status": "pending",
            "grace_period_end": now + timedelta(days=180),  # 6 months from now
            "vote_kept": 0,
            "vote_broken": 0
        },
        {
            "politician_id": 2,
            "title": "प्रत्येक गाउँमा स्वास्थ्य चौकी",
            "description": "हरेक गाउँमा कम्तीमा एक स्वास्थ्य चौकी स्थापना गर्ने र आधारभूत स्वास्थ्य सेवा सुनिश्चित गर्ने।",
            "category": "healthcare",
            "status": "pending",
            "grace_period_end": now + timedelta(days=365),  # 1 year from now
            "vote_kept": 0,
            "vote_broken": 0
        },
        {
            "politician_id": 3,
            "title": "युवा रोजगारी कार्यक्रम",
            "description": "५ वर्षभित्र ५ लाख युवालाई रोजगारी दिने कार्यक्रम। सीप विकास र उद्यमशीलता प्रवर्द्धनमा जोड दिइनेछ।",
            "category": "economy",
            "status": "pending",
            "grace_period_end": now + timedelta(days=90),  # 3 months from now
            "vote_kept": 0,
            "vote_broken": 0
        },
        
        # =====================================================================
        # PENDING - Grace period ENDED (can vote now)
        # =====================================================================
        {
            "politician_id": 4,
            "title": "सबै विद्यालयमा इन्टरनेट",
            "description": "देशका सबै सरकारी विद्यालयहरूमा निःशुल्क इन्टरनेट सेवा उपलब्ध गराउने।",
            "category": "education",
            "status": "pending",
            "grace_period_end": now - timedelta(days=30),  # 1 month ago (voting open)
            "vote_kept": 245,
            "vote_broken": 89
        },
        {
            "politician_id": 5,
            "title": "किसान ऋण माफी",
            "description": "साना किसानहरूको १ लाखसम्मको ऋण माफी गर्ने।",
            "category": "agriculture",
            "status": "pending",
            "grace_period_end": now - timedelta(days=60),  # 2 months ago (voting open)
            "vote_kept": 567,
            "vote_broken": 234
        },
        {
            "politician_id": 1,
            "title": "भ्रष्टाचार नियन्त्रण",
            "description": "भ्रष्टाचार विरुद्ध कडा कानून बनाउने र दोषीलाई कठोर सजाय दिने।",
            "category": "governance",
            "status": "pending",
            "grace_period_end": now - timedelta(days=120),  # 4 months ago (voting open)
            "vote_kept": 1234,
            "vote_broken": 890
        },
        
        # =====================================================================
        # KEPT - Promise fulfilled
        # =====================================================================
        {
            "politician_id": 2,
            "title": "नयाँ संविधान जारी",
            "description": "नेपालको नयाँ संविधान जारी गर्ने - २०७२ सालमा पूरा भयो।",
            "category": "governance",
            "status": "kept",
            "grace_period_end": now - timedelta(days=365 * 3),  # 3 years ago
            "vote_kept": 5678,
            "vote_broken": 1234
        },
        {
            "politician_id": 3,
            "title": "लोकतान्त्रिक गणतन्त्र घोषणा",
            "description": "नेपाललाई संघीय लोकतान्त्रिक गणतन्त्र घोषणा गर्ने।",
            "category": "governance",
            "status": "kept",
            "grace_period_end": now - timedelta(days=365 * 5),  # 5 years ago
            "vote_kept": 8901,
            "vote_broken": 2345
        },
        
        # =====================================================================
        # BROKEN - Promise not fulfilled
        # =====================================================================
        {
            "politician_id": 4,
            "title": "५ वर्षमा समृद्ध नेपाल",
            "description": "५ वर्षभित्र नेपाललाई समृद्ध देश बनाउने - पूरा भएन।",
            "category": "economy",
            "status": "broken",
            "grace_period_end": now - timedelta(days=365 * 2),  # 2 years ago
            "vote_kept": 890,
            "vote_broken": 4567
        },
        {
            "politician_id": 5,
            "title": "बेरोजगारी शून्य",
            "description": "३ वर्षभित्र बेरोजगारी शून्य गर्ने - असफल।",
            "category": "economy",
            "status": "broken",
            "grace_period_end": now - timedelta(days=365 * 4),  # 4 years ago
            "vote_kept": 456,
            "vote_broken": 7890
        }
    ]


# =============================================================================
# SEED FUNCTIONS
# =============================================================================

def seed_politicians(db: Session) -> list[Politician]:
    """Seed politicians into database."""
    print("\n📥 Seeding politicians...")
    
    politicians = []
    for data in POLITICIANS:
        politician = Politician(**data)
        db.add(politician)
        politicians.append(politician)
    
    db.flush()  # Get IDs
    print(f"  ✓ Created {len(politicians)} politicians")
    return politicians


def seed_manifestos(db: Session) -> list[Manifesto]:
    """Seed manifestos into database."""
    print("\n📥 Seeding manifestos...")
    
    manifestos = []
    for data in get_manifestos_data():
        manifesto = Manifesto(**data)
        # Generate promise hash
        manifesto.promise_hash = generate_promise_hash(
            manifesto.title,
            manifesto.description,
            manifesto.politician_id
        )
        db.add(manifesto)
        manifestos.append(manifesto)
    
    db.flush()
    print(f"  ✓ Created {len(manifestos)} manifestos")
    return manifestos


def seed_audit_logs(db: Session, manifestos: list[Manifesto]):
    """Create initial audit logs (genesis block + promise blocks)."""
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
    
    # Create blocks for each manifesto
    for manifesto in manifestos:
        block_data = {
            "manifesto_id": manifesto.id,
            "title": manifesto.title,
            "politician_id": manifesto.politician_id,
            "promise_hash": manifesto.promise_hash,
            "action": "PROMISE_CREATED",
            "timestamp": manifesto.created_at.isoformat() if manifesto.created_at else datetime.utcnow().isoformat()
        }
        
        audit = AuditLog(
            manifesto_id=manifesto.id,
            action="PROMISE_CREATED",
            block_hash=generate_block_hash(str(block_data), prev_hash),
            prev_hash=prev_hash,
            data=block_data
        )
        db.add(audit)
        db.flush()
        prev_hash = audit.block_hash
    
    print(f"  ✓ Created {len(manifestos) + 1} audit log entries (including genesis)")


def clear_seed_data(db: Session):
    """Clear all seeded data."""
    db.query(AuditLog).delete()
    db.query(Manifesto).delete()
    db.query(Politician).delete()
    db.commit()
    print("  ✓ Cleared existing seed data")


def main():
    """Main entry point for seeding."""
    print("=" * 60)
    print("  SEED DATA")
    print("=" * 60)
    
    init_db()
    
    with get_db_context() as db:
        # Check existing data
        existing_politicians = db.query(Politician).count()
        existing_manifestos = db.query(Manifesto).count()
        
        if existing_politicians > 0 or existing_manifestos > 0:
            print(f"\n⚠️  Found existing data:")
            print(f"   Politicians: {existing_politicians}")
            print(f"   Manifestos:  {existing_manifestos}")
            response = input("  Clear and reseed? (y/N): ").strip().lower()
            if response != 'y':
                print("  Aborted.")
                return
            clear_seed_data(db)
        
        # Seed data
        politicians = seed_politicians(db)
        manifestos = seed_manifestos(db)
        seed_audit_logs(db, manifestos)
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("  SEEDING COMPLETE")
        print("=" * 60)
        print(f"  Politicians: {len(politicians)}")
        print(f"  Manifestos:  {len(manifestos)}")
        print(f"  Audit logs:  {len(manifestos) + 1}")
        print("=" * 60)


if __name__ == "__main__":
    main()
