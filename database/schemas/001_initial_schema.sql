-- OpenEquity Research Platform - Initial Database Schema
-- Version: 1.0
-- Date: November 2024

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom enum types
CREATE TYPE statement_type AS ENUM ('income', 'balance', 'cashflow');
CREATE TYPE period_type AS ENUM ('annual', 'quarterly');
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
CREATE TYPE model_type AS ENUM ('dcf', 'comp', 'precedent', 'ddm', 'residual', 'custom');

-- ============================================
-- COMPANIES TABLE
-- ============================================
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    employees INTEGER,
    founded_year INTEGER,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    description TEXT,
    sic_code VARCHAR(10),
    cik VARCHAR(10) UNIQUE,
    exchange VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for companies
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_cik ON companies(cik);
CREATE INDEX idx_companies_name_trgm ON companies USING gin(name gin_trgm_ops);

-- ============================================
-- FINANCIAL STATEMENTS TABLE
-- ============================================
CREATE TABLE financial_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    statement_type statement_type NOT NULL,
    period_type period_type NOT NULL,
    period_end DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period VARCHAR(10),
    data JSONB NOT NULL,
    source VARCHAR(50),
    filing_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, statement_type, period_type, period_end)
);

-- Create indexes for financial statements
CREATE INDEX idx_fs_ticker ON financial_statements(ticker);
CREATE INDEX idx_fs_period_end ON financial_statements(period_end DESC);
CREATE INDEX idx_fs_statement_type ON financial_statements(statement_type);
CREATE INDEX idx_fs_data ON financial_statements USING gin(data);

-- ============================================
-- STOCK PRICES TABLE (TimescaleDB hypertable)
-- ============================================
CREATE TABLE stock_prices (
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    adjusted_close DECIMAL(12,4),
    volume BIGINT,
    PRIMARY KEY (ticker, timestamp)
);

-- Create indexes for stock prices
CREATE INDEX idx_prices_ticker_time ON stock_prices(ticker, timestamp DESC);

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(500),
    bio TEXT,
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Create indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- FINANCIAL MODELS TABLE
-- ============================================
CREATE TABLE financial_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ticker VARCHAR(10) REFERENCES companies(ticker) ON DELETE SET NULL,
    model_type model_type NOT NULL,
    data JSONB NOT NULL,
    assumptions JSONB,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    fork_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for financial models
CREATE INDEX idx_models_created_by ON financial_models(created_by);
CREATE INDEX idx_models_ticker ON financial_models(ticker);
CREATE INDEX idx_models_type ON financial_models(model_type);
CREATE INDEX idx_models_public ON financial_models(is_public);
CREATE INDEX idx_models_rating ON financial_models(rating DESC);

-- ============================================
-- MODEL VERSIONS TABLE (Version Control)
-- ============================================
CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES financial_models(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data JSONB NOT NULL,
    assumptions JSONB,
    change_description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(model_id, version_number)
);

-- Create indexes for model versions
CREATE INDEX idx_model_versions_model_id ON model_versions(model_id);

-- ============================================
-- WORKSPACES TABLE (Collaboration)
-- ============================================
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for workspaces
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);

-- ============================================
-- WORKSPACE MEMBERS TABLE
-- ============================================
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'viewer', -- owner, editor, viewer
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- Create indexes for workspace members
CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);

-- ============================================
-- WATCHLISTS TABLE
-- ============================================
CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for watchlists
CREATE INDEX idx_watchlists_user ON watchlists(user_id);

-- ============================================
-- WATCHLIST ITEMS TABLE
-- ============================================
CREATE TABLE watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    notes TEXT,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(watchlist_id, ticker)
);

-- Create indexes for watchlist items
CREATE INDEX idx_watchlist_items_watchlist ON watchlist_items(watchlist_id);
CREATE INDEX idx_watchlist_items_ticker ON watchlist_items(ticker);

-- ============================================
-- AUDIT LOGS TABLE
-- ============================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for audit logs
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to tables
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_statements_updated_at BEFORE UPDATE ON financial_statements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_models_updated_at BEFORE UPDATE ON financial_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlists_updated_at BEFORE UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE companies IS 'Master table for publicly traded companies';
COMMENT ON TABLE financial_statements IS 'Financial statements (income, balance sheet, cash flow)';
COMMENT ON TABLE stock_prices IS 'Historical stock price data';
COMMENT ON TABLE users IS 'Platform users';
COMMENT ON TABLE financial_models IS 'User-created valuation models';
COMMENT ON TABLE model_versions IS 'Version control for financial models';
COMMENT ON TABLE workspaces IS 'Collaborative workspaces';
COMMENT ON TABLE workspace_members IS 'Workspace membership';
COMMENT ON TABLE watchlists IS 'User watchlists';
COMMENT ON TABLE audit_logs IS 'Audit trail for security and compliance';
