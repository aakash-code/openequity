# OpenEquity Backend

FastAPI-based backend for the OpenEquity Research Platform.

## Tech Stack

- **Framework:** FastAPI 0.110+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+ with SQLAlchemy
- **Cache:** Redis 7.0+
- **Testing:** pytest
- **Code Quality:** black, flake8, mypy

## Getting Started

### Prerequisites

- Python >= 3.11
- PostgreSQL >= 15
- Redis >= 7.0

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Create initial data (if any)
python -m app.db.init_db
```

### Development

```bash
# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Project Structure

```
app/
├── api/              # API routes
├── core/            # Core configuration
├── db/              # Database connection and session
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── ml/              # Machine learning models
```

## API Documentation

### Core Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/docs` - Swagger documentation

### Company Endpoints (Planned)

- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{ticker}` - Get company details
- `GET /api/v1/companies/{ticker}/financials` - Get financial statements
- `GET /api/v1/companies/{ticker}/ratios` - Get financial ratios

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenEquity Documentation](../docs/)
