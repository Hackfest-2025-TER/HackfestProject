#!/usr/bin/env python3
"""Quick database verification script."""

from database import get_db_context
from models import Voter, Politician, Manifesto, AuditLog

def main():
    with get_db_context() as db:
        voters_count = db.query(Voter).count()
        politicians_count = db.query(Politician).count()
        manifestos_count = db.query(Manifesto).count()
        audit_logs_count = db.query(AuditLog).count()
        
        print("\n" + "=" * 60)
        print("  DATABASE VERIFICATION")
        print("=" * 60)
        print(f"  ✓ Voters:      {voters_count:,}")
        print(f"  ✓ Politicians: {politicians_count}")
        print(f"  ✓ Manifestos:  {manifestos_count}")
        print(f"  ✓ Audit Logs:  {audit_logs_count}")
        print("=" * 60)
        
        if manifestos_count > 0:
            print("\nSample Manifestos:")
            manifestos = db.query(Manifesto).limit(3).all()
            for m in manifestos:
                print(f"  - {m.title} (Status: {m.status})")

if __name__ == "__main__":
    main()
