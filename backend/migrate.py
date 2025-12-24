#!/usr/bin/env python3
"""
Database Migration Runner for PromiseThread
============================================
Easy-to-use script for managing database migrations.

Usage:
    python migrate.py init       # First time setup
    python migrate.py status     # Check migration status
    python migrate.py upgrade    # Apply pending migrations
    python migrate.py downgrade  # Rollback last migration
    python migrate.py reset      # Reset database (DESTRUCTIVE)
    python migrate.py import     # Import voter CSV data
    python migrate.py seed       # Seed sample data
"""

import sys
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, reset_db, check_connection
from import_csv import main as import_csv_main
from seed_data import main as seed_data_main

# Get the virtual environment's alembic path
VENV_PATH = Path(__file__).parent / "myenv" / "bin"
ALEMBIC_CMD = str(VENV_PATH / "alembic") if VENV_PATH.exists() else "alembic"


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_alembic_command(args: list[str]):
    """Run an alembic command"""
    try:
        subprocess.run([ALEMBIC_CMD] + args, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Alembic command failed: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Alembic not found at: {ALEMBIC_CMD}")
        print("   Please install: pip install alembic")
        return False


def cmd_init():
    """Initialize database from scratch"""
    print_header("INITIALIZING DATABASE")
    
    print("Step 1: Checking database connection...")
    if not check_connection():
        print("❌ Cannot connect to database. Please check your PostgreSQL installation.")
        print("   See MIGRATIONS.md for setup instructions.")
        return False
    print("✅ Database connection successful!\n")
    
    print("Step 2: Creating tables...")
    init_db()
    
    print("\nStep 3: Stamping database with migration version...")
    if not run_alembic_command(["stamp", "head"]):
        return False
    print("✅ Database stamped with current migration version\n")
    
    print("Step 4: Importing voter data from CSV...")
    try:
        import_csv_main()
    except Exception as e:
        print(f"⚠️  CSV import failed: {e}")
        print("   You can run 'python migrate.py import' later to retry.")
    
    print("\nStep 5: Seeding sample data...")
    try:
        seed_data_main()
    except Exception as e:
        print(f"⚠️  Data seeding failed: {e}")
        print("   You can run 'python migrate.py seed' later to retry.")
    
    print_header("INITIALIZATION COMPLETE")
    print("✅ Database is ready to use!")
    print("\nNext steps:")
    print("  1. Start backend:  cd backend && uvicorn main:app --reload")
    print("  2. Start frontend: cd frontend && pnpm run dev")
    return True


def cmd_status():
    """Show migration status"""
    print_header("MIGRATION STATUS")
    
    print("📋 Current database revision:")
    run_alembic_command(["current"])
    
    print("\n📋 Migration history:")
    run_alembic_command(["history"])
    
    print("\n📋 Pending migrations:")
    run_alembic_command(["show", "head"])
    
    return True


def cmd_upgrade():
    """Apply pending migrations"""
    print_header("APPLYING MIGRATIONS")
    
    print("Upgrading database to latest version...")
    if run_alembic_command(["upgrade", "head"]):
        print("\n✅ Database upgraded successfully!")
        return True
    return False


def cmd_downgrade():
    """Rollback last migration"""
    print_header("ROLLING BACK MIGRATION")
    
    response = input("⚠️  This will rollback the last migration. Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return False
    
    print("\nRolling back one migration...")
    if run_alembic_command(["downgrade", "-1"]):
        print("\n✅ Migration rolled back successfully!")
        return True
    return False


def cmd_reset():
    """Reset database (DESTRUCTIVE)"""
    print_header("RESET DATABASE")
    
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("    - All tables will be dropped")
    print("    - All data will be lost")
    print("    - Database will be recreated from scratch\n")
    
    response = input("Are you absolutely sure? Type 'RESET' to continue: ").strip()
    if response != 'RESET':
        print("Aborted.")
        return False
    
    print("\n1. Dropping all tables...")
    reset_db()
    
    print("\n2. Stamping database...")
    run_alembic_command(["stamp", "head"])
    
    print("\n3. Importing voter data...")
    try:
        import_csv_main()
    except Exception as e:
        print(f"⚠️  CSV import failed: {e}")
    
    print("\n4. Seeding sample data...")
    try:
        seed_data_main()
    except Exception as e:
        print(f"⚠️  Data seeding failed: {e}")
    
    print_header("RESET COMPLETE")
    print("✅ Database has been reset!")
    return True


def cmd_import():
    """Import voter CSV data"""
    print_header("IMPORTING VOTER DATA")
    try:
        import_csv_main()
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def cmd_seed():
    """Seed sample data"""
    print_header("SEEDING SAMPLE DATA")
    try:
        seed_data_main()
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False


def show_help():
    """Show help message"""
    print(__doc__)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'init': cmd_init,
        'status': cmd_status,
        'upgrade': cmd_upgrade,
        'downgrade': cmd_downgrade,
        'reset': cmd_reset,
        'import': cmd_import,
        'seed': cmd_seed,
        'help': show_help,
        '--help': show_help,
        '-h': show_help,
    }
    
    if command not in commands:
        print(f"❌ Unknown command: {command}\n")
        show_help()
        sys.exit(1)
    
    try:
        success = commands[command]()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
