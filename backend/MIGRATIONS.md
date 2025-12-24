# Database Migrations Guide

## Overview

PromiseThread uses **Alembic** for database migrations with **PostgreSQL**. This document explains how to set up, run, and manage database migrations.

## Database Credentials

**Local Development:**
```
Host:     localhost
Port:     5432
Database: promisethread
Username: promisethread
Password: hackfest2025
```

**Connection URL:**
```
postgresql://promisethread:hackfest2025@localhost:5432/promisethread
```

## Prerequisites

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# Create user
CREATE USER promisethread WITH PASSWORD 'hackfest2025' CREATEDB;

# Create database
CREATE DATABASE promisethread OWNER promisethread;

# Exit psql
\q
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Migration Commands

### Initialize Database (First Time Setup)

Run this command to create all tables from scratch:

```bash
cd backend
python migrate.py init
```

This will:
1. Create the database if it doesn't exist
2. Run all pending migrations
3. Import voter data from CSV
4. Seed sample politicians and manifestos

### Check Migration Status

```bash
cd backend
python migrate.py status
```

Shows:
- Current database revision
- Pending migrations
- Applied migrations

### Apply Migrations

```bash
cd backend
python migrate.py upgrade
```

Applies all pending migrations to bring the database up to date.

### Rollback Migrations

```bash
# Rollback one migration
cd backend
python migrate.py downgrade

# Rollback to specific revision
cd backend
alembic downgrade <revision_id>
```

### Reset Database (⚠️ DESTRUCTIVE)

```bash
cd backend
python migrate.py reset
```

This will:
1. Drop all tables
2. Recreate tables
3. Re-import voter data
4. Re-seed sample data

**WARNING:** This deletes ALL data!

### Create New Migration

After modifying models in `models.py`:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

This generates a new migration file in `migrations/versions/`.

## Migration Files

### Structure

```
backend/
├── alembic.ini              # Alembic configuration
├── migrations/
│   ├── env.py              # Migration environment setup
│   ├── script.py.mako      # Template for new migrations
│   ├── README              # Alembic README
│   └── versions/
│       └── 51ee1b7bf96e_initial_migration_create_all_tables.py
```

### Initial Migration

**File:** `51ee1b7bf96e_initial_migration_create_all_tables.py`

**Creates:**
1. **voters** - Voter registry (25,924 records from CSV)
2. **zk_credentials** - Anonymous ZK credentials
3. **politicians** - Political figures
4. **manifestos** - Political promises
5. **manifesto_votes** - Individual votes (anonymous)
6. **comments** - Discussion threads
7. **comment_votes** - Upvote/downvote tracking
8. **audit_logs** - Blockchain simulation
9. **merkle_roots** - Merkle tree roots

## Database Schema

### Tables Overview

```
voters (25,924 records)
  ├── id, voter_id (unique), name, age, gender
  ├── province, district, vdc, ward
  └── merkle_leaf (for ZK proofs)

zk_credentials (anonymous auth)
  ├── id, nullifier_hash (unique)
  └── credential_hash, is_valid

politicians
  ├── id, name, party, position
  └── image_url, bio

manifestos (promises)
  ├── id, politician_id (FK)
  ├── title, description, category, status
  ├── promise_hash (blockchain)
  ├── grace_period_end (voting lock)
  └── vote_kept, vote_broken (aggregates)

manifesto_votes (anonymous voting)
  ├── id, manifesto_id (FK)
  ├── nullifier (anonymous voter ID)
  ├── vote_type (kept/broken)
  └── UNIQUE(manifesto_id, nullifier) ← prevents double voting

comments (discussions)
  ├── id, manifesto_id (FK)
  ├── parent_id (threading)
  ├── nullifier_display (truncated)
  └── content, upvotes, downvotes

comment_votes
  ├── id, comment_id (FK)
  ├── nullifier (anonymous)
  └── UNIQUE(comment_id, nullifier) ← one vote per comment

audit_logs (blockchain)
  ├── id (block number)
  ├── block_hash, prev_hash
  └── data (JSONB)

merkle_roots
  ├── id, root_hash (unique)
  └── leaf_count, tree_type
```

### Key Constraints

**Privacy Protection:**
- No foreign key from `zk_credentials` to `voters` (true anonymity)
- Nullifiers are anonymous identifiers

**Vote Integrity:**
- `UNIQUE(manifesto_id, nullifier)` prevents double voting on promises
- `UNIQUE(comment_id, nullifier)` prevents double voting on comments

**Status Validation:**
- `CHECK (status IN ('pending', 'kept', 'broken'))`
- `CHECK (vote_type IN ('kept', 'broken'))`
- `CHECK (vote_type IN ('up', 'down'))`

## Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if stopped
brew services start postgresql@15

# Test connection
psql -U promisethread -d promisethread -c "SELECT 1;"
```

### Migration Already Exists Error

If you see "Target database is not up to date":

```bash
# Check current revision
cd backend
alembic current

# Stamp database to current head (if tables exist)
alembic stamp head
```

### Reset to Clean State

```bash
cd backend

# Drop all tables
python -c "from database import reset_db; reset_db()"

# Re-run migrations
alembic upgrade head

# Import data
python import_csv.py
python seed_data.py
```

## Production Deployment

### Environment Variables

Set these in production:

```bash
export DB_HOST=your-db-host.com
export DB_PORT=5432
export DB_NAME=promisethread
export DB_USER=promisethread
export DB_PASSWORD=your-secure-password
```

### Migration Workflow

1. **Test migrations locally first**
2. **Backup production database**
   ```bash
   pg_dump -U promisethread promisethread > backup.sql
   ```
3. **Run migrations on production**
   ```bash
   alembic upgrade head
   ```
4. **Verify data integrity**
   ```bash
   psql -U promisethread -d promisethread -c "SELECT COUNT(*) FROM voters;"
   ```

### Docker Deployment

When adding PostgreSQL to `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: promisethread
      POSTGRES_PASSWORD: hackfest2025
      POSTGRES_DB: promisethread
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Further Reading

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
