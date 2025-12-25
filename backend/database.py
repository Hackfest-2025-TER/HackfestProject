"""
Database Connection Module for PromiseThread
=============================================
Handles PostgreSQL connection, session management, and initialization.

Credentials:
- Host: localhost (or postgres in Docker)
- Port: 5432
- Database: promisethread
- Username: promisethread
- Password: hackfest2025
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from models import Base

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Support both DATABASE_URL (docker-compose) and individual env vars (local dev)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fall back to individual environment variables
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "promisethread")
    DB_USER = os.getenv("DB_USER", "promisethread")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "hackfest2025")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Parse from DATABASE_URL for display
    DB_HOST = "from DATABASE_URL"
    DB_PORT = "from DATABASE_URL"
    DB_NAME = "from DATABASE_URL"
    DB_USER = "from DATABASE_URL"
    DB_PASSWORD = "***"

# Print connection info for debugging (remove in production)
print(f"""
╔══════════════════════════════════════════════════════════════╗
║              DATABASE CONNECTION INFO                        ║
╠══════════════════════════════════════════════════════════════╣
║  Host:     {DB_HOST:<48} ║
║  Port:     {DB_PORT:<48} ║
║  Database: {DB_NAME:<48} ║
║  Username: {DB_USER:<48} ║
║  Password: {DB_PASSWORD:<48} ║
╚══════════════════════════════════════════════════════════════╝
""")


# =============================================================================
# ENGINE AND SESSION SETUP
# =============================================================================

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Number of connections to keep open
    max_overflow=20,        # Additional connections when pool is full
    pool_pre_ping=True,     # Check connection health before using
    echo=False              # Set True to see SQL queries (debugging)
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# DEPENDENCY INJECTION FOR FASTAPI
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Usage:
        with get_db_context() as db:
            db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.py if they don't exist.
    """
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables. USE WITH CAUTION!
    """
    print("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped.")


def reset_db():
    """
    Reset database - drop all tables and recreate.
    USE WITH CAUTION!
    """
    drop_all_tables()
    init_db()


# =============================================================================
# HEALTH CHECK
# =============================================================================

def check_connection() -> bool:
    """
    Check if database connection is healthy.
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# =============================================================================
# RUN INITIALIZATION IF EXECUTED DIRECTLY
# =============================================================================

if __name__ == "__main__":
    print("Testing database connection...")
    if check_connection():
        print("✓ Database connection successful!")
        init_db()
    else:
        print("✗ Database connection failed!")
        exit(1)
