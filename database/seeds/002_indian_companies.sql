-- Sample Indian company data for NSE and BSE
-- Major companies from various sectors

INSERT INTO companies (ticker, name, sector, industry, market_cap, employees, founded_year, headquarters, website, description, sic_code, cik, exchange, is_active) VALUES
-- Technology & IT Services
('TCS', 'Tata Consultancy Services Limited', 'Technology', 'IT Services & Consulting', 13500000000000, 614795, 1968, 'Mumbai, Maharashtra', 'https://www.tcs.com', 'Tata Consultancy Services Limited is an IT services, consulting and business solutions organization that has been partnering with many of the worlds largest businesses in their transformation journeys for over 50 years.', '7373', NULL, 'NSE', true),
('INFY', 'Infosys Limited', 'Technology', 'IT Services & Consulting', 6800000000000, 345000, 1981, 'Bangalore, Karnataka', 'https://www.infosys.com', 'Infosys Limited is a global leader in next-generation digital services and consulting.', '7373', NULL, 'NSE', true),
('WIPRO', 'Wipro Limited', 'Technology', 'IT Services & Consulting', 2800000000000, 250000, 1945, 'Bangalore, Karnataka', 'https://www.wipro.com', 'Wipro Limited is a leading technology services and consulting company focused on building innovative solutions that address clients most complex digital transformation needs.', '7373', NULL, 'NSE', true),
('HCLTECH', 'HCL Technologies Limited', 'Technology', 'IT Services & Consulting', 3600000000000, 219000, 1976, 'Noida, Uttar Pradesh', 'https://www.hcltech.com', 'HCL Technologies is a next-generation global technology company that helps enterprises reimagine their businesses for the digital age.', '7373', NULL, 'NSE', true),

-- Financial Services & Banking
('HDFCBANK', 'HDFC Bank Limited', 'Financial Services', 'Banks—Diversified', 11500000000000, 177000, 1994, 'Mumbai, Maharashtra', 'https://www.hdfcbank.com', 'HDFC Bank Limited is an Indian banking and financial services company headquartered in Mumbai.', '6029', NULL, 'NSE', true),
('ICICIBANK', 'ICICI Bank Limited', 'Financial Services', 'Banks—Diversified', 7200000000000, 124000, 1994, 'Mumbai, Maharashtra', 'https://www.icicibank.com', 'ICICI Bank Limited is an Indian multinational bank and financial services company.', '6029', NULL, 'NSE', true),
('SBIN', 'State Bank of India', 'Financial Services', 'Banks—Diversified', 5800000000000, 245000, 1806, 'Mumbai, Maharashtra', 'https://www.sbi.co.in', 'State Bank of India (SBI) is an Indian multinational public sector bank and financial services statutory body.', '6021', NULL, 'NSE', true),
('KOTAKBANK', 'Kotak Mahindra Bank Limited', 'Financial Services', 'Banks—Diversified', 3400000000000, 75000, 1985, 'Mumbai, Maharashtra', 'https://www.kotak.com', 'Kotak Mahindra Bank Limited is an Indian banking and financial services company.', '6029', NULL, 'NSE', true),

-- Consumer Goods & FMCG
('HINDUNILVR', 'Hindustan Unilever Limited', 'Consumer Defensive', 'Household & Personal Products', 6200000000000, 20000, 1933, 'Mumbai, Maharashtra', 'https://www.hul.co.in', 'Hindustan Unilever Limited is an Indian consumer goods company headquartered in Mumbai. It is a subsidiary of the British company Unilever.', '2841', NULL, 'NSE', true),
('ITC', 'ITC Limited', 'Consumer Defensive', 'Tobacco', 5100000000000, 26000, 1910, 'Kolkata, West Bengal', 'https://www.itcportal.com', 'ITC Limited is an Indian conglomerate company headquartered in Kolkata. Its business includes five segments: FMCG, hotels, paperboards & specialty papers, packaging and agri-business.', '2111', NULL, 'NSE', true),
('NESTLEIND', 'Nestle India Limited', 'Consumer Defensive', 'Packaged Foods', 2100000000000, 8000, 1959, 'Gurgaon, Haryana', 'https://www.nestle.in', 'Nestle India Limited is a subsidiary of Nestle S.A. of Switzerland. The Company is engaged in the business of manufacturing and selling of prepared dishes and cooking aids, milk products, beverages, chocolates, confectionery and other products.', '2024', NULL, 'NSE', true),

-- Energy & Oil
('RELIANCE', 'Reliance Industries Limited', 'Energy', 'Oil & Gas Integrated', 17500000000000, 347000, 1966, 'Mumbai, Maharashtra', 'https://www.ril.com', 'Reliance Industries Limited is an Indian multinational conglomerate company, engaged in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles.', '2911', NULL, 'NSE', true),
('ONGC', 'Oil and Natural Gas Corporation Limited', 'Energy', 'Oil & Gas Exploration', 2200000000000, 32000, 1956, 'New Delhi', 'https://www.ongcindia.com', 'Oil and Natural Gas Corporation Limited is an Indian multinational oil and gas company. It is Indias largest oil and gas exploration and production company.', '1311', NULL, 'NSE', true),
('IOC', 'Indian Oil Corporation Limited', 'Energy', 'Oil & Gas Refining & Marketing', 1400000000000, 33000, 1959, 'New Delhi', 'https://iocl.com', 'Indian Oil Corporation Limited is an Indian government-owned oil and gas corporation with its headquarters in New Delhi.', '2911', NULL, 'NSE', true),

-- Automotive
('TATAMOTORS', 'Tata Motors Limited', 'Consumer Cyclical', 'Auto Manufacturers', 2800000000000, 80000, 1945, 'Mumbai, Maharashtra', 'https://www.tatamotors.com', 'Tata Motors Limited is an Indian multinational automotive manufacturing company, headquartered in Mumbai and part of the Tata Group.', '3711', NULL, 'NSE', true),
('M&M', 'Mahindra & Mahindra Limited', 'Consumer Cyclical', 'Auto Manufacturers', 2100000000000, 260000, 1945, 'Mumbai, Maharashtra', 'https://www.mahindra.com', 'Mahindra & Mahindra Limited is an Indian multinational car manufacturing corporation headquartered in Mumbai.', '3711', NULL, 'NSE', true),
('MARUTI', 'Maruti Suzuki India Limited', 'Consumer Cyclical', 'Auto Manufacturers', 3400000000000, 18000, 1981, 'New Delhi', 'https://www.marutisuzuki.com', 'Maruti Suzuki India Limited is an Indian automobile manufacturer. It is a subsidiary of Japanese automaker Suzuki Motor Corporation.', '3711', NULL, 'NSE', true),

-- Pharmaceuticals
('SUNPHARMA', 'Sun Pharmaceutical Industries Limited', 'Healthcare', 'Drug Manufacturers—General', 3600000000000, 40000, 1983, 'Mumbai, Maharashtra', 'https://www.sunpharma.com', 'Sun Pharmaceutical Industries Limited is an Indian multinational pharmaceutical company headquartered in Mumbai.', '2834', NULL, 'NSE', true),
('DRREDDY', 'Dr. Reddys Laboratories Limited', 'Healthcare', 'Drug Manufacturers—General', 920000000000, 24000, 1984, 'Hyderabad, Telangana', 'https://www.drreddys.com', 'Dr. Reddys Laboratories Limited is an Indian multinational pharmaceutical company based in Hyderabad.', '2834', NULL, 'NSE', true),
('CIPLA', 'Cipla Limited', 'Healthcare', 'Drug Manufacturers—General', 1100000000000, 25000, 1935, 'Mumbai, Maharashtra', 'https://www.cipla.com', 'Cipla Limited is an Indian multinational pharmaceutical company, headquartered in Mumbai.', '2834', NULL, 'NSE', true),

-- Telecom
('BHARTIARTL', 'Bharti Airtel Limited', 'Communication Services', 'Telecom Services', 5400000000000, 19000, 1995, 'New Delhi', 'https://www.airtel.in', 'Bharti Airtel Limited is an Indian multinational telecommunications services company based in New Delhi.', '4813', NULL, 'NSE', true)

ON CONFLICT (ticker) DO NOTHING;

-- Update timestamp
UPDATE companies SET updated_at = NOW();
