# OpenEquity Database

PostgreSQL database schema and migrations for the OpenEquity Research Platform.

## Database Stack

- **Primary DB:** PostgreSQL 15+
- **Time-series:** TimescaleDB extension
- **Search:** pg_trgm extension for full-text search
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic

## Schema Overview

### Core Tables

1. **companies** - Master table for company data
2. **financial_statements** - Income statements, balance sheets, cash flows
3. **stock_prices** - Historical price data (TimescaleDB hypertable)
4. **users** - Platform users
5. **financial_models** - User-created valuation models
6. **model_versions** - Version control for models
7. **workspaces** - Collaborative workspaces
8. **workspace_members** - Workspace membership
9. **watchlists** - User watchlists
10. **watchlist_items** - Items in watchlists
11. **audit_logs** - Security and compliance audit trail

### Enum Types

- `statement_type`: income, balance, cashflow
- `period_type`: annual, quarterly
- `user_role`: user, admin, moderator
- `model_type`: dcf, comp, precedent, ddm, residual, custom

## Setup

### 1. Install PostgreSQL and Extensions

```bash
# Install PostgreSQL 15+
sudo apt-get install postgresql-15 postgresql-contrib

# Install TimescaleDB
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-postgresql-15
```

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE openequity;
CREATE USER openequity WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE openequity TO openequity;
```

### 3. Apply Schema

```bash
# Run initial schema
psql -U openequity -d openequity -f schemas/001_initial_schema.sql

# Enable TimescaleDB
psql -U openequity -d openequity -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# Convert stock_prices to hypertable
psql -U openequity -d openequity -c "SELECT create_hypertable('stock_prices', 'timestamp');"
```

### 4. Run Migrations (via Alembic)

```bash
# From backend directory
cd ../backend

# Initialize alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

## Sample Data

```bash
# Load seed data
psql -U openequity -d openequity -f seeds/001_sample_companies.sql
```

## Backup and Restore

### Backup

```bash
# Full database backup
pg_dump -U openequity openequity > backup_$(date +%Y%m%d).sql

# Schema only
pg_dump -U openequity -s openequity > schema_backup.sql

# Data only
pg_dump -U openequity -a openequity > data_backup.sql
```

### Restore

```bash
# Restore full backup
psql -U openequity openequity < backup_20241116.sql
```

## Performance Tuning

### Indexes

All tables have appropriate indexes for common queries:
- Primary keys and foreign keys
- Timestamp columns for time-based queries
- JSONB columns with GIN indexes
- Text columns with trigram indexes for search

### Query Optimization

```sql
-- Analyze tables for query optimization
ANALYZE companies;
ANALYZE financial_statements;
ANALYZE stock_prices;

-- View table statistics
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';
```

## Maintenance

### Vacuum

```sql
-- Regular vacuum
VACUUM ANALYZE;

-- Full vacuum (requires exclusive lock)
VACUUM FULL;
```

### Monitor Size

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('openequity'));

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Data Retention Policy

As per PDR requirements:

- **Real-time quotes:** 30 days
- **Daily prices:** 20 years
- **Financial statements:** Indefinite
- **User models:** 5 years (unless deleted)
- **Audit logs:** 7 years
- **Temporary calculations:** 24 hours

```sql
-- Clean up old data (run periodically via cron)
DELETE FROM stock_prices WHERE timestamp < NOW() - INTERVAL '20 years';
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '7 years';
```

## Security

### Row-Level Security (Future Enhancement)

```sql
-- Enable RLS
ALTER TABLE financial_models ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY user_models ON financial_models
    FOR ALL
    USING (created_by = current_user_id() OR is_public = true);
```

## Learn More

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
