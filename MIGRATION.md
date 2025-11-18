# Database Migration Guide 🔄

This document explains how database migrations work in the ICP Analysis Dashboard for both local development and Render deployment.

## Overview

Database migrations are **fully automated** and **idempotent** (safe to run multiple times). The system uses a Python migration script that reads SQL files and applies them to your PostgreSQL database.

## Automated Migration on Render

### How It Works

When you deploy to Render, migrations run automatically before each deployment:

1. **Render builds your Docker container** from `Dockerfile`
2. **`preDeployCommand` runs** the migration script: `uv run python migrate.py`
3. **Database schema is created** (if it doesn't exist)
4. **Sample data is loaded** (if not already present)
5. **Indexes are created** (if they don't exist)
6. **Application starts** with a fully initialized database

### Configuration

The automation is configured in `render.yaml`:

```yaml
services:
  - type: web
    name: icp-analysis-dashboard
    preDeployCommand: "uv run python migrate.py"
```

### What Gets Created

The migration creates:
- ✅ `user_signups` table with complete schema
- ✅ 20 sample customer records
- ✅ 5 performance indexes (industry, company_size, signup_date, revenue_range, role)
- ✅ All constraints and defaults

### Idempotency

The migration is safe to run multiple times:
- `CREATE TABLE IF NOT EXISTS` - skips if table exists
- `INSERT ... ON CONFLICT DO NOTHING` - skips duplicate records
- `CREATE INDEX IF NOT EXISTS` - skips if index exists

**Result:** You can deploy as many times as you want without errors or duplicate data.

## Local Development Migrations

### Quick Start

Run migrations locally using one of these methods:

#### Option 1: Migration Script (Recommended)

```bash
# Ensure DATABASE_URL is set in .env
uv run python migrate.py
```

#### Option 2: Helper Script

```bash
./migrate.sh
```

#### Option 3: Manual SQL

```bash
psql -U postgres -d render_data -f data/mock_signups.sql
```

### Docker Environment

If running with Docker Compose:

```bash
# Start containers first
docker-compose up -d

# Wait for PostgreSQL to be ready (3-5 seconds)
sleep 5

# Run migration inside the app container
docker-compose exec app uv run python migrate.py

# Or from your host (if you have psql)
docker-compose exec db psql -U postgres -d render_data -f /app/data/mock_signups.sql
```

## Migration Script Details

### File: `migrate.py`

The Python migration script provides:
- ✅ Database connection validation
- ✅ SQL file parsing and execution
- ✅ Error handling for existing tables/data
- ✅ Progress reporting with colored output
- ✅ Verification after migration

### Features

**Connection Test:**
```python
# Tests database connectivity before proceeding
conn.execute(text("SELECT 1"))
```

**Smart Statement Parsing:**
```python
# Splits SQL into individual statements
# Handles multi-line statements
# Skips comments and empty lines
```

**Error Handling:**
```python
# Gracefully handles "already exists" errors
# Reports duplicate key violations
# Fails fast on real errors
```

**Verification:**
```python
# Checks that table was created
# Counts rows to verify data load
# Reports final status
```

### Output Example

```
🔄 Starting database migration...
📡 Connecting to database...
✅ Database connection successful
📄 Migration file loaded
🔧 Executing 26 SQL statements...
  ✓ Created table: user_signups
  ✓ Inserted data
  ✓ Inserted data
  ...
  ✓ Created index: idx_user_signups_industry
  ✓ Created index: idx_user_signups_company_size
  ...

🔍 Verifying migration...
✅ Table 'user_signups' exists with 20 rows

✅ Migration completed successfully!
```

## SQL Schema

### File: `data/mock_signups.sql`

The SQL file contains:

#### Table Definition

```sql
CREATE TABLE IF NOT EXISTS user_signups (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    role VARCHAR(100),
    signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_case TEXT,
    revenue_range VARCHAR(50),
    location VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Sample Data

```sql
INSERT INTO user_signups (...) VALUES
(...),
(...),
...
ON CONFLICT (email) DO NOTHING;
```

**Key Points:**
- `ON CONFLICT (email) DO NOTHING` - prevents duplicate emails
- 20 realistic sample records included
- Mix of industries, company sizes, and revenue ranges

#### Performance Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_user_signups_industry ON user_signups(industry);
CREATE INDEX IF NOT EXISTS idx_user_signups_company_size ON user_signups(company_size);
CREATE INDEX IF NOT EXISTS idx_user_signups_signup_date ON user_signups(signup_date);
CREATE INDEX IF NOT EXISTS idx_user_signups_revenue_range ON user_signups(revenue_range);
CREATE INDEX IF NOT EXISTS idx_user_signups_role ON user_signups(role);
```

## Environment Variables

The migration script uses these environment variables:

### Required

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

### For Render (Auto-configured)

Render automatically provides these from the linked database:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL` (complete connection string)

### For Local Development

Set in your `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/render_data
```

Or individual components:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=render_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

## Troubleshooting

### Migration Fails: "DATABASE_URL not set"

**Solution:**
```bash
# Check your .env file
cat .env | grep DATABASE_URL

# Or set it manually
export DATABASE_URL=postgresql://postgres:password@localhost:5432/render_data
```

### Migration Fails: "Connection refused"

**Causes:**
1. PostgreSQL not running
2. Wrong host/port
3. Firewall blocking connection

**Solutions:**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (macOS)
brew services start postgresql

# Start PostgreSQL (Linux)
sudo systemctl start postgresql

# For Docker
docker-compose ps
docker-compose restart db
```

### Migration Fails: "Permission denied"

**Cause:** User lacks permissions to create tables

**Solution:**
```sql
-- Grant permissions as superuser
GRANT ALL PRIVILEGES ON DATABASE render_data TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

### "Duplicate key value violates unique constraint"

**This is normal!** The migration script handles this automatically. If you see warnings about duplicate data, it means the data already exists and is being skipped (as intended).

### Table Already Exists

**This is also normal!** The migration script uses `CREATE TABLE IF NOT EXISTS`, so it will skip creation if the table exists.

### Migration Hangs

**Possible causes:**
1. Database connection timeout
2. Long-running query
3. Lock on the table

**Solutions:**
```bash
# Check active connections
psql -U postgres -d render_data -c "SELECT * FROM pg_stat_activity;"

# Kill stuck queries (as superuser)
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';
```

## Testing Migrations

### Test Locally Before Deploying

```bash
# 1. Create a test database
createdb render_data_test

# 2. Set DATABASE_URL to test database
export DATABASE_URL=postgresql://postgres:password@localhost:5432/render_data_test

# 3. Run migration
uv run python migrate.py

# 4. Verify
psql -U postgres -d render_data_test -c "SELECT COUNT(*) FROM user_signups;"

# 5. Run again to test idempotency
uv run python migrate.py

# 6. Cleanup
dropdb render_data_test
```

### Test with Docker

```bash
# Start fresh
docker-compose down -v
docker-compose up -d

# Run migration
docker-compose exec app uv run python migrate.py

# Test idempotency
docker-compose exec app uv run python migrate.py

# Verify
docker-compose exec db psql -U postgres -d render_data -c "SELECT COUNT(*) FROM user_signups;"
```

## Best Practices

### 1. Always Test Locally First

Before deploying to Render, test migrations locally to catch issues early.

### 2. Keep Migrations Idempotent

Always use:
- `CREATE TABLE IF NOT EXISTS`
- `CREATE INDEX IF NOT EXISTS`
- `INSERT ... ON CONFLICT DO NOTHING`

### 3. Version Your SQL Files

When making schema changes:
```
data/
  migrations/
    001_initial_schema.sql
    002_add_indexes.sql
    003_add_columns.sql
```

### 4. Backup Before Major Changes

```bash
# Backup database
pg_dump -U postgres render_data > backup_$(date +%Y%m%d).sql

# Restore if needed
psql -U postgres render_data < backup_20231115.sql
```

### 5. Use Transactions for Complex Migrations

```sql
BEGIN;
  -- Your migration statements
  CREATE TABLE ...;
  INSERT INTO ...;
COMMIT;
```

## Advanced: Adding New Migrations

### Step 1: Create New SQL File

```sql
-- data/migrations/002_add_user_preferences.sql
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_signups(id),
    theme VARCHAR(50) DEFAULT 'light',
    notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 2: Update Migration Script

Modify `migrate.py` to run multiple migration files in order:

```python
migration_files = [
    'data/mock_signups.sql',
    'data/migrations/002_add_user_preferences.sql',
]

for sql_file in migration_files:
    print(f"Running migration: {sql_file}")
    # ... existing migration code
```

### Step 3: Test Locally

```bash
uv run python migrate.py
```

### Step 4: Deploy to Render

Just push to GitHub - the `preDeployCommand` will run automatically!

## FAQ

**Q: Do I need to run migrations manually on Render?**
A: No! They run automatically via `preDeployCommand` in `render.yaml`.

**Q: What if I already have data in the database?**
A: The migration is idempotent - it won't duplicate data or fail on existing tables.

**Q: Can I customize the sample data?**
A: Yes! Edit `data/mock_signups.sql` and change the INSERT statements.

**Q: How do I add a new column?**
A: Create a new migration file with `ALTER TABLE` statements, update the migration script to run it.

**Q: What happens if migration fails on Render?**
A: The deployment will fail and your old version keeps running. Check the Render logs to see the error.

**Q: Can I skip the sample data?**
A: Yes! Remove the INSERT statements from `data/mock_signups.sql`, keeping only the CREATE TABLE and indexes.

## Related Documentation

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [data/README.md](data/README.md) - Sample data documentation
- [render.yaml](render.yaml) - Render deployment configuration

---

Built with ❤️ for easy, automated database management.

