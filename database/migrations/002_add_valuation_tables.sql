-- OpenEquity Research Platform - Valuation Tables Migration
-- Version: 2.0
-- Date: November 2024
-- Description: Add DCF valuation and peer group tables for Phase 1B/1C

-- ============================================
-- DCF VALUATIONS TABLE
-- ============================================
CREATE TABLE dcf_valuations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Model metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,

    -- WACC assumptions
    risk_free_rate DECIMAL(6,5) NOT NULL,
    equity_risk_premium DECIMAL(6,5) NOT NULL,
    beta DECIMAL(6,4) NOT NULL,
    cost_of_debt DECIMAL(6,5) NOT NULL,
    tax_rate DECIMAL(6,5) NOT NULL,
    debt_weight DECIMAL(6,5) NOT NULL,
    equity_weight DECIMAL(6,5) NOT NULL,
    wacc DECIMAL(6,5) NOT NULL,

    -- Projection assumptions
    projection_years INTEGER DEFAULT 5,
    revenue_growth_rates JSONB NOT NULL,
    ebitda_margin DECIMAL(6,5),
    depreciation_pct_revenue DECIMAL(6,5),
    capex_pct_revenue DECIMAL(6,5),
    nwc_pct_revenue DECIMAL(6,5),

    -- Terminal value assumptions
    terminal_growth_rate DECIMAL(6,5),
    terminal_ebitda_multiple DECIMAL(6,2),

    -- Results
    enterprise_value DECIMAL(20,2),
    equity_value DECIMAL(20,2),
    shares_outstanding DECIMAL(15,2),
    value_per_share DECIMAL(12,4),
    current_price DECIMAL(12,4),
    upside_downside DECIMAL(8,4),

    -- Detailed projections and calculations
    projections JSONB,
    fcf_projections JSONB,
    terminal_value DECIMAL(20,2),
    pv_terminal_value DECIMAL(20,2),
    pv_fcf DECIMAL(20,2),

    -- Sensitivity analysis
    sensitivity_analysis JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes for DCF valuations
CREATE INDEX idx_dcf_ticker ON dcf_valuations(ticker);
CREATE INDEX idx_dcf_user_id ON dcf_valuations(user_id);
CREATE INDEX idx_dcf_created_at ON dcf_valuations(created_at DESC);
CREATE INDEX idx_dcf_is_public ON dcf_valuations(is_public) WHERE is_public = TRUE;

-- ============================================
-- PEER GROUPS TABLE
-- ============================================
CREATE TABLE peer_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Group metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,

    -- Peer tickers
    peer_tickers JSONB NOT NULL,

    -- Analysis results (cached)
    analysis_results JSONB,
    last_analyzed TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes for peer groups
CREATE INDEX idx_peer_groups_ticker ON peer_groups(ticker);
CREATE INDEX idx_peer_groups_user_id ON peer_groups(user_id);
CREATE INDEX idx_peer_groups_created_at ON peer_groups(created_at DESC);
CREATE INDEX idx_peer_groups_is_public ON peer_groups(is_public) WHERE is_public = TRUE;

-- ============================================
-- COMPARABLE ANALYSES TABLE
-- ============================================
CREATE TABLE comparable_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    peer_group_id UUID NOT NULL REFERENCES peer_groups(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,

    -- Company data
    company_data JSONB NOT NULL,

    -- Valuation multiples
    pe_ratio DECIMAL(8,2),
    forward_pe DECIMAL(8,2),
    peg_ratio DECIMAL(8,4),
    price_to_book DECIMAL(8,4),
    price_to_sales DECIMAL(8,4),
    ev_to_revenue DECIMAL(8,4),
    ev_to_ebitda DECIMAL(8,4),
    ev_to_ebit DECIMAL(8,4),
    ev_to_fcf DECIMAL(8,4),

    -- Profitability metrics
    gross_margin DECIMAL(6,4),
    operating_margin DECIMAL(6,4),
    net_margin DECIMAL(6,4),
    roe DECIMAL(6,4),
    roa DECIMAL(6,4),
    roic DECIMAL(6,4),

    -- Growth metrics
    revenue_growth DECIMAL(6,4),
    earnings_growth DECIMAL(6,4),

    -- Other metrics
    market_cap DECIMAL(20,2),
    enterprise_value DECIMAL(20,2),

    -- Timestamp
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for comparable analyses
CREATE INDEX idx_comps_peer_group_id ON comparable_analyses(peer_group_id);
CREATE INDEX idx_comps_ticker ON comparable_analyses(ticker);
CREATE INDEX idx_comps_calculated_at ON comparable_analyses(calculated_at DESC);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for DCF valuations
CREATE TRIGGER update_dcf_valuations_updated_at
    BEFORE UPDATE ON dcf_valuations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add triggers for peer groups
CREATE TRIGGER update_peer_groups_updated_at
    BEFORE UPDATE ON peer_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE dcf_valuations IS 'Stores DCF (Discounted Cash Flow) valuation models created by users';
COMMENT ON TABLE peer_groups IS 'Stores peer groups for comparable company analysis';
COMMENT ON TABLE comparable_analyses IS 'Stores calculated comparable company analysis results for peer groups';

COMMENT ON COLUMN dcf_valuations.wacc IS 'Weighted Average Cost of Capital (calculated)';
COMMENT ON COLUMN dcf_valuations.revenue_growth_rates IS 'Array of revenue growth rates for each projection year';
COMMENT ON COLUMN dcf_valuations.projections IS 'Detailed year-by-year financial projections';
COMMENT ON COLUMN dcf_valuations.fcf_projections IS 'Free cash flow projections for each year';
COMMENT ON COLUMN dcf_valuations.sensitivity_analysis IS 'Sensitivity analysis grid varying WACC and terminal growth';
COMMENT ON COLUMN dcf_valuations.upside_downside IS 'Percentage upside/downside vs current price';

COMMENT ON COLUMN peer_groups.peer_tickers IS 'Array of peer company ticker symbols';
COMMENT ON COLUMN peer_groups.analysis_results IS 'Cached comparable company analysis results';
