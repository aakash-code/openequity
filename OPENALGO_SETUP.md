# OpenAlgo Integration Setup Guide

This guide explains how to integrate OpenAlgo with OpenEquity for real-time Indian broker data.

## Overview

**OpenAlgo** is a self-hosted platform that connects to 24+ Indian brokers (Zerodha, Upstox, Angel One, Fyers, etc.) and provides:
- Real-time market quotes
- Historical OHLC data
- Market depth (order book)
- Live positions and holdings
- Order execution
- Account funds and margins

## Architecture

```
┌─────────────────┐
│   OpenEquity    │
│   (FastAPI)     │
└────────┬────────┘
         │
         │ HTTP REST API
         │
┌────────▼────────┐
│   OpenAlgo      │
│   (Flask)       │
│   Port: 5000    │
└────────┬────────┘
         │
         │ Broker APIs
         │
┌────────▼─────────────────────┐
│  Indian Brokers              │
│  - Zerodha                   │
│  - Upstox                    │
│  - Angel One                 │
│  - Fyers                     │
│  - Dhan                      │
│  - Shoonya (Finvasia)        │
│  - 20+ more...               │
└──────────────────────────────┘
```

## Step 1: Install OpenAlgo

### Prerequisites
- Python 3.10+
- 2GB RAM minimum
- 1GB disk space
- Linux/Windows/Mac

### Installation Methods

#### Option A: Using Docker (Recommended)

```bash
# Clone OpenAlgo repository
git clone https://github.com/marketcalls/openalgo.git
cd openalgo

# Run with Docker
docker-compose up -d
```

#### Option B: Manual Installation

```bash
# Clone repository
git clone https://github.com/marketcalls/openalgo.git
cd openalgo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

OpenAlgo will start on `http://localhost:5000`

## Step 2: Configure OpenAlgo

1. **Access Dashboard**: Open `http://localhost:5000` in browser

2. **Login**: Use default credentials (will be prompted to change)

3. **Add Broker Connection**:
   - Go to Settings → Broker
   - Select your broker (Zerodha, Upstox, etc.)
   - Enter API credentials (from broker's developer portal)
   - Complete authentication flow

4. **Generate API Key**:
   - Go to Settings → API Keys
   - Click "Generate New API Key"
   - Save the key securely - you'll need it for OpenEquity

## Step 3: Configure OpenEquity

Add these environment variables to your OpenEquity backend:

```bash
# OpenAlgo Configuration
OPENALGO_URL=http://localhost:5000
OPENALGO_API_KEY=your_api_key_here
```

### File: `.env`

```bash
# Add to backend/.env
OPENALGO_URL=http://localhost:5000
OPENALGO_API_KEY=your_openalgo_api_key_from_dashboard
```

## Step 4: Test the Connection

### Using FastAPI Swagger UI

1. Start OpenEquity backend: `uvicorn app.main:app --reload`
2. Open: `http://localhost:8000/docs`
3. Navigate to `/realtime/ping` endpoint
4. Click "Try it out" → "Execute"
5. Should return: `{"status": "connected", "openalgo_status": {...}}`

### Using curl

```bash
curl -X GET "http://localhost:8000/api/v1/realtime/ping" \
  -H "Authorization: Bearer your_openequity_token"
```

## Step 5: Available API Endpoints

### Market Data

```python
# Get real-time quotes
POST /api/v1/realtime/quotes
{
  "symbols": ["RELIANCE", "TCS", "INFY"],
  "exchange": "NSE"
}

# Get historical data
POST /api/v1/realtime/history
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}

# Get market depth
GET /api/v1/realtime/depth/RELIANCE?exchange=NSE

# Search symbols
GET /api/v1/realtime/search?query=reliance&exchange=NSE
```

### Account & Portfolio

```python
# Get current positions
GET /api/v1/realtime/positions

# Get demat holdings
GET /api/v1/realtime/holdings

# Get account funds
GET /api/v1/realtime/funds

# Get order book
GET /api/v1/realtime/orders
```

### Trading (Use with caution!)

```python
# Place order
POST /api/v1/realtime/place-order
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "action": "BUY",
  "quantity": 10,
  "order_type": "LIMIT",
  "price": 2500.00,
  "product": "CNC"
}

# Cancel order
DELETE /api/v1/realtime/cancel-order/{order_id}
```

## Step 6: Frontend Integration

Update your frontend API client to use real-time data:

```typescript
// frontend/src/lib/api.ts

async getRealTimeQuotes(symbols: string[], exchange: string = 'NSE'): Promise<any> {
  return this.request<any>('/api/v1/realtime/quotes', {
    method: 'POST',
    body: JSON.stringify({ symbols, exchange }),
  });
}

async getHistoricalData(
  symbol: string,
  exchange: string = 'NSE',
  interval: string = '1d',
  startDate?: string,
  endDate?: string
): Promise<any> {
  return this.request<any>('/api/v1/realtime/history', {
    method: 'POST',
    body: JSON.stringify({
      symbol,
      exchange,
      interval,
      start_date: startDate,
      end_date: endDate
    }),
  });
}

async getBrokerPositions(): Promise<any> {
  return this.request<any>('/api/v1/realtime/positions');
}

async getBrokerHoldings(): Promise<any> {
  return this.request<any>('/api/v1/realtime/holdings');
}
```

## Supported Exchanges

- **NSE**: National Stock Exchange (Equity)
- **BSE**: Bombay Stock Exchange (Equity)
- **NFO**: NSE Futures & Options
- **BFO**: BSE Futures & Options
- **CDS**: Currency Derivatives
- **MCX**: Multi Commodity Exchange
- **NCDEX**: National Commodity Exchange

## Supported Brokers

OpenAlgo supports 24+ brokers:
- Zerodha
- Upstox
- Angel One
- Fyers
- Dhan
- Shoonya (Finvasia)
- 5Paisa
- Aliceblue
- Kotak Securities
- ICICI Direct
- And many more...

## Data Intervals

For historical data, supported intervals:
- `1m`, `3m`, `5m`, `15m`, `30m` - Intraday
- `1h`, `2h`, `4h` - Hourly
- `1d` - Daily
- `1w` - Weekly
- `1M` - Monthly

## Security Notes

1. **API Keys**: Store securely, never commit to git
2. **HTTPS**: Use HTTPS in production
3. **Rate Limiting**: Implement rate limiting on endpoints
4. **Broker Credentials**: Never log or expose broker credentials
5. **Testing**: Use OpenAlgo's "Analyze Mode" for testing before live trading

## Troubleshooting

### Connection Failed

```python
# Check if OpenAlgo is running
curl http://localhost:5000/api/v1/ping

# Check environment variables
echo $OPENALGO_URL
echo $OPENALGO_API_KEY
```

### Authentication Errors

- Verify API key is correct
- Check if API key has expired
- Regenerate API key from OpenAlgo dashboard

### Broker Connection Issues

- Verify broker credentials in OpenAlgo dashboard
- Check if broker API is active
- Some brokers require daily re-authentication

## Production Deployment

### Using Ngrok (Quick Setup)

```bash
# In OpenAlgo directory
ngrok http 5000
```

Use the ngrok URL in `OPENALGO_URL` environment variable.

### Using Reverse Proxy (Recommended)

```nginx
# nginx configuration
location /openalgo/ {
    proxy_pass http://localhost:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Next Steps

1. **Replace Sample Data**: Update existing services to use OpenAlgo data
2. **Add WebSocket Support**: For real-time streaming quotes
3. **Implement Caching**: Cache quotes for 1-5 seconds to reduce API calls
4. **Add Error Handling**: Graceful fallback when OpenAlgo is unavailable
5. **Live Portfolio Sync**: Auto-sync positions with broker

## Resources

- OpenAlgo GitHub: https://github.com/marketcalls/openalgo
- OpenAlgo Docs: https://docs.openalgo.in
- Discord Community: https://discord.gg/marketcalls
- Broker API Docs: Check individual broker developer portals

## Support

For OpenAlgo specific issues:
- GitHub Issues: https://github.com/marketcalls/openalgo/issues
- Discord: https://discord.gg/marketcalls

For OpenEquity integration issues:
- Check logs in `backend/logs/`
- Verify environment variables
- Test connection with `/realtime/ping` endpoint
