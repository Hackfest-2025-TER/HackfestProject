# Database Quick Reference

## Connection Details

```
Host:     localhost
Port:     5432
Database: promisethread
Username: promisethread
Password: hackfest2025
URL:      postgresql://promisethread:hackfest2025@localhost:5432/promisethread
```

## Quick Commands

```bash
# Initialize database (first time only)
python migrate.py init

# Check status
python migrate.py status

# Apply migrations
python migrate.py upgrade

# Import voter CSV
python migrate.py import

# Seed sample data
python migrate.py seed

# Reset everything (⚠️ DESTRUCTIVE)
python migrate.py reset
```

## Direct SQL Access

```bash
# Connect to database
psql -U promisethread -d promisethread

# List tables
\dt

# Count records
SELECT 'voters' as table, COUNT(*) FROM voters
UNION ALL SELECT 'politicians', COUNT(*) FROM politicians
UNION ALL SELECT 'manifestos', COUNT(*) FROM manifestos;

# Check recent votes
SELECT m.title, mv.vote_type, COUNT(*) as votes
FROM manifesto_votes mv
JOIN manifestos m ON mv.manifesto_id = m.id
GROUP BY m.title, mv.vote_type
ORDER BY COUNT(*) DESC;

# Exit
\q
```

## Alembic Commands

```bash
# Generate new migration (after model changes)
alembic revision --autogenerate -m "Description"

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history

# Stamp database (mark as migrated without running)
alembic stamp head
```

## Troubleshooting

**Can't connect to database:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start it
brew services start postgresql@15

# Test connection
psql -U promisethread -d promisethread -c "SELECT 1;"
```

**Tables already exist:**
```bash
# Stamp database with current version
cd backend
alembic stamp head
```

**Need to reset:**
```bash
# Complete reset
python migrate.py reset

# Or manually:
python -c "from database import reset_db; reset_db()"
alembic upgrade head
python import_csv.py
python seed_data.py
```

## Data Verification

```sql
-- Check voter count
SELECT COUNT(*) FROM voters;  -- Should be 25,924

-- Check politicians
SELECT id, name, party FROM politicians;  -- Should be 5

-- Check manifestos
SELECT COUNT(*), status FROM manifestos GROUP BY status;

-- Check votes
SELECT COUNT(*) as total_votes FROM manifesto_votes;

-- Check integrity
SELECT 
    m.title,
    m.vote_kept,
    m.vote_broken,
    COUNT(mv.id) as actual_votes
FROM manifestos m
LEFT JOIN manifesto_votes mv ON m.id = mv.manifesto_id
GROUP BY m.id, m.title, m.vote_kept, m.vote_broken;
```
