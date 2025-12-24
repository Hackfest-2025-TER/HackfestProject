"""
CSV Import Script for PromiseThread
====================================
Imports voter data from dhulikhel_voter_list_full.csv into PostgreSQL.
Generates Merkle leaves for each voter for ZK proof verification.
"""

import csv
import hashlib
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from database import get_db_context, init_db
from models import Voter

# CSV file path
CSV_PATH = Path(__file__).parent.parent / "data" / "dhulikhel_voter_list_full.csv"

# CSV column mapping (Nepali headers to English)
COLUMN_MAP = {
    'सि.नं.': 'serial_number',
    'मतदाता नं': 'voter_id',
    'मतदाताको नाम': 'name',
    'उमेर(वर्ष)': 'age',
    'लिङ्ग': 'gender',
    'पति/पत्नीको नाम': 'spouse_name',
    'पिता/माताको नाम': 'parent_name',
    'मतदाता विवरण': 'voter_details',  # Will be ignored
    'Province': 'province',
    'District': 'district',
    'VDC': 'vdc',
    'Ward': 'ward',
    'RegCentre': 'registration_center'
}


def generate_merkle_leaf(voter_id: str, name: str) -> str:
    """
    Generate a Merkle leaf hash for a voter.
    This is used in the Merkle tree for ZK proof verification.
    
    Format: keccak256(voter_id + name)
    """
    data = f"{voter_id}:{name}".encode('utf-8')
    return '0x' + hashlib.sha256(data).hexdigest()


def clean_value(value: str) -> str:
    """Clean a CSV value - strip whitespace and handle empty strings."""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def parse_age(age_str: str) -> int:
    """Parse age from string, return None if invalid."""
    try:
        age = int(float(str(age_str).strip()))
        return age if 0 < age < 150 else None
    except (ValueError, TypeError):
        return None


def parse_ward(ward_str: str) -> int:
    """Parse ward number from string, return None if invalid."""
    try:
        return int(float(str(ward_str).strip()))
    except (ValueError, TypeError):
        return None


def import_csv(db: Session, batch_size: int = 1000) -> tuple[int, int]:
    """
    Import voters from CSV file into database.
    Returns (success_count, error_count).
    """
    success_count = 0
    error_count = 0
    batch = []
    
    print(f"Reading CSV from: {CSV_PATH}")
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Extract values using column mapping
                voter_id = clean_value(row.get('मतदाता नं', ''))
                name = clean_value(row.get('मतदाताको नाम', ''))
                
                # Skip rows without voter_id or name
                if not voter_id or not name:
                    error_count += 1
                    continue
                
                # Create voter object
                voter = Voter(
                    voter_id=voter_id,
                    name=name,
                    age=parse_age(row.get('उमेर(वर्ष)', '')),
                    gender=clean_value(row.get('लिङ्ग', '')),
                    spouse_name=clean_value(row.get('पति/पत्नीको नाम', '')),
                    parent_name=clean_value(row.get('पिता/माताको नाम', '')),
                    province=clean_value(row.get('Province', '')),
                    district=clean_value(row.get('District', '')),
                    vdc=clean_value(row.get('VDC', '')),
                    ward=parse_ward(row.get('Ward', '')),
                    registration_center=clean_value(row.get('RegCentre', '')),
                    merkle_leaf=generate_merkle_leaf(voter_id, name)
                )
                
                batch.append(voter)
                
                # Commit in batches for performance
                if len(batch) >= batch_size:
                    db.bulk_save_objects(batch)
                    db.commit()
                    success_count += len(batch)
                    print(f"  Imported {success_count} voters...")
                    batch = []
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only print first 5 errors
                    print(f"  Error on row {row_num}: {e}")
        
        # Commit remaining batch
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            success_count += len(batch)
    
    return success_count, error_count


def clear_voters(db: Session):
    """Clear all voters from database."""
    db.query(Voter).delete()
    db.commit()
    print("  Cleared existing voters.")


def main():
    """Main entry point for CSV import."""
    print("=" * 60)
    print("  VOTER DATA IMPORT")
    print("=" * 60)
    
    # Initialize database tables if needed
    init_db()
    
    with get_db_context() as db:
        # Check if voters already exist
        existing_count = db.query(Voter).count()
        
        if existing_count > 0:
            print(f"\n⚠️  Found {existing_count} existing voters.")
            response = input("  Clear existing data and reimport? (y/N): ").strip().lower()
            if response != 'y':
                print("  Aborted.")
                return
            clear_voters(db)
        
        # Import from CSV
        print("\n📥 Importing voters from CSV...")
        start_time = datetime.now()
        
        success, errors = import_csv(db)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("  IMPORT COMPLETE")
        print("=" * 60)
        print(f"  ✓ Imported: {success:,} voters")
        print(f"  ✗ Errors:   {errors:,}")
        print(f"  ⏱ Time:     {elapsed:.2f} seconds")
        print("=" * 60)


if __name__ == "__main__":
    main()
