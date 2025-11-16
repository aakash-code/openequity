-- Sample company data for testing and development
-- Includes major companies from various sectors

INSERT INTO companies (ticker, name, sector, industry, market_cap, employees, founded_year, headquarters, website, description, sic_code, cik, exchange, is_active) VALUES
-- Technology
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 2800000000000, 164000, 1976, 'Cupertino, California', 'https://www.apple.com', 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.', '3571', '0000320193', 'NASDAQ', true),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software—Infrastructure', 2500000000000, 221000, 1975, 'Redmond, Washington', 'https://www.microsoft.com', 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.', '7372', '0000789019', 'NASDAQ', true),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information', 1700000000000, 190000, 1998, 'Mountain View, California', 'https://www.google.com', 'Alphabet Inc. offers various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.', '7370', '0001652044', 'NASDAQ', true),
('AMZN', 'Amazon.com, Inc.', 'Technology', 'Internet Retail', 1600000000000, 1540000, 1994, 'Seattle, Washington', 'https://www.amazon.com', 'Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.', '5961', '0001018724', 'NASDAQ', true),
('META', 'Meta Platforms, Inc.', 'Technology', 'Internet Content & Information', 850000000000, 86000, 2004, 'Menlo Park, California', 'https://www.meta.com', 'Meta Platforms, Inc. engages in the development of products that enable people to connect and share with friends and family through mobile devices, personal computers, virtual reality headsets, and wearables worldwide.', '7370', '0001326801', 'NASDAQ', true),

-- Finance
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks—Diversified', 450000000000, 293000, 1799, 'New York, New York', 'https://www.jpmorganchase.com', 'JPMorgan Chase & Co. operates as a financial services company worldwide.', '6021', '0000019617', 'NYSE', true),
('BAC', 'Bank of America Corporation', 'Financial Services', 'Banks—Diversified', 280000000000, 213000, 1784, 'Charlotte, North Carolina', 'https://www.bankofamerica.com', 'Bank of America Corporation, through its subsidiaries, provides banking and financial products and services for individual consumers, small and middle-market businesses, institutional investors, large corporations, and governments worldwide.', '6021', '0000070858', 'NYSE', true),
('GS', 'The Goldman Sachs Group, Inc.', 'Financial Services', 'Capital Markets', 120000000000, 45000, 1869, 'New York, New York', 'https://www.goldmansachs.com', 'The Goldman Sachs Group, Inc., a financial institution, provides range of financial services for corporations, financial institutions, governments, and individuals worldwide.', '6211', '0000886982', 'NYSE', true),

-- Healthcare
('JNJ', 'Johnson & Johnson', 'Healthcare', 'Drug Manufacturers—General', 380000000000, 152000, 1886, 'New Brunswick, New Jersey', 'https://www.jnj.com', 'Johnson & Johnson researches, develops, manufactures, and sells various products in the healthcare field worldwide.', '2834', '0000200406', 'NYSE', true),
('UNH', 'UnitedHealth Group Incorporated', 'Healthcare', 'Healthcare Plans', 450000000000, 440000, 1977, 'Minnetonka, Minnesota', 'https://www.unitedhealthgroup.com', 'UnitedHealth Group Incorporated operates as a diversified health care company in the United States.', '6324', '0000731766', 'NYSE', true),

-- Consumer
('PG', 'The Procter & Gamble Company', 'Consumer Defensive', 'Household & Personal Products', 360000000000, 106000, 1837, 'Cincinnati, Ohio', 'https://www.pg.com', 'The Procter & Gamble Company provides branded consumer packaged goods to consumers in North and Latin America, Europe, the Asia Pacific, Greater China, India, the Middle East, and Africa.', '2840', '0000080424', 'NYSE', true),
('KO', 'The Coca-Cola Company', 'Consumer Defensive', 'Beverages—Non-Alcoholic', 260000000000, 82500, 1892, 'Atlanta, Georgia', 'https://www.coca-colacompany.com', 'The Coca-Cola Company, a beverage company, manufactures, markets, and sells various nonalcoholic beverages worldwide.', '2080', '0000021344', 'NYSE', true),
('WMT', 'Walmart Inc.', 'Consumer Defensive', 'Discount Stores', 420000000000, 2100000, 1962, 'Bentonville, Arkansas', 'https://www.walmart.com', 'Walmart Inc. engages in the operation of retail, wholesale, and other units worldwide.', '5331', '0000104169', 'NYSE', true),

-- Energy
('XOM', 'Exxon Mobil Corporation', 'Energy', 'Oil & Gas Integrated', 450000000000, 63000, 1999, 'Irving, Texas', 'https://www.exxonmobil.com', 'Exxon Mobil Corporation engages in the exploration and production of crude oil and natural gas in the United States and internationally.', '2911', '0000034088', 'NYSE', true),
('CVX', 'Chevron Corporation', 'Energy', 'Oil & Gas Integrated', 290000000000, 43000, 1879, 'San Ramon, California', 'https://www.chevron.com', 'Chevron Corporation, through its subsidiaries, engages in integrated energy and chemicals operations worldwide.', '2911', '0000093410', 'NYSE', true),

-- Industrial
('BA', 'The Boeing Company', 'Industrials', 'Aerospace & Defense', 120000000000, 171000, 1916, 'Chicago, Illinois', 'https://www.boeing.com', 'The Boeing Company, together with its subsidiaries, designs, develops, manufactures, sells, services, and supports commercial jetliners, military aircraft, satellites, missile defense, human space flight and launch systems, and services worldwide.', '3721', '0000012927', 'NYSE', true),
('CAT', 'Caterpillar Inc.', 'Industrials', 'Farm & Heavy Construction Machinery', 140000000000, 107700, 1925, 'Deerfield, Illinois', 'https://www.caterpillar.com', 'Caterpillar Inc. manufactures and sells construction and mining equipment, diesel and natural gas engines, industrial gas turbines, and diesel-electric locomotives worldwide.', '3531', '0000018230', 'NYSE', true),

-- Communication Services
('DIS', 'The Walt Disney Company', 'Communication Services', 'Entertainment', 180000000000, 220000, 1923, 'Burbank, California', 'https://www.thewaltdisneycompany.com', 'The Walt Disney Company, together with its subsidiaries, operates as an entertainment company worldwide.', '7996', '0001001039', 'NYSE', true),
('NFLX', 'Netflix, Inc.', 'Communication Services', 'Entertainment', 190000000000, 13000, 1997, 'Los Gatos, California', 'https://www.netflix.com', 'Netflix, Inc. provides entertainment services.', '7841', '0001065280', 'NASDAQ', true),

-- Real Estate
('AMT', 'American Tower Corporation', 'Real Estate', 'REIT—Specialty', 95000000000, 6000, 1995, 'Boston, Massachusetts', 'https://www.americantower.com', 'American Tower Corporation, one of the largest global REITs, is a leading independent owner, operator and developer of multitenant communications real estate with a portfolio of approximately 225,000 communications sites.', '6798', '0001053507', 'NYSE', true),

-- Utilities
('NEE', 'NextEra Energy, Inc.', 'Utilities', 'Utilities—Regulated Electric', 145000000000, 15000, 1925, 'Juno Beach, Florida', 'https://www.nexteraenergy.com', 'NextEra Energy, Inc., through its subsidiaries, generates, transmits, distributes, and sells electric power to retail and wholesale customers in North America.', '4911', '0000753308', 'NYSE', true)
ON CONFLICT (ticker) DO NOTHING;

-- Update timestamp
UPDATE companies SET updated_at = NOW();
