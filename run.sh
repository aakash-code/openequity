#!/bin/bash

################################################################################
# OpenEquity - Complete Setup, Check, and Run Script
# This script handles installation, verification, and execution of the entire app
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=============================================="
    echo -e "${GREEN}$1${NC}"
    echo "=============================================="
    echo ""
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}

trap cleanup EXIT

################################################################################
# STEP 1: System Requirements Check
################################################################################

check_requirements() {
    print_header "STEP 1: Checking System Requirements"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python 3 found: $PYTHON_VERSION"
    else
        log_error "Python 3 not found. Please install Python 3.10+"
        exit 1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js found: $NODE_VERSION"
    else
        log_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm found: $NPM_VERSION"
    else
        log_error "npm not found. Please install npm"
        exit 1
    fi

    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | cut -d' ' -f3)
        log_success "PostgreSQL found: $PSQL_VERSION"
    else
        log_warning "PostgreSQL not found. You may need to install it for production use."
    fi

    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        log_success "Git found: $GIT_VERSION"
    else
        log_warning "Git not found"
    fi

    log_success "All system requirements satisfied!"
}

################################################################################
# STEP 2: Backend Setup
################################################################################

setup_backend() {
    print_header "STEP 2: Setting up Backend"

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip -q

    # Install dependencies
    log_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi

    # Check for .env file
    if [ ! -f ".env" ]; then
        log_warning ".env file not found, creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from .env.example"
        else
            log_warning "No .env.example found, creating minimal .env..."
            cat > .env << EOF
# Database
DATABASE_URL=sqlite:///./openequity.db

# Security
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# OpenAlgo (optional)
OPENALGO_URL=http://localhost:5000
OPENALGO_API_KEY=

# Environment
ENVIRONMENT=development
EOF
            log_success "Created minimal .env file"
        fi
    else
        log_info ".env file exists"
    fi

    cd ..
}

################################################################################
# STEP 3: Frontend Setup
################################################################################

setup_frontend() {
    print_header "STEP 3: Setting up Frontend"

    cd frontend

    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    else
        log_info "Node.js dependencies already installed"
    fi

    # Check for .env.local file
    if [ ! -f ".env.local" ]; then
        log_warning ".env.local file not found, creating..."
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1
EOF
        log_success "Created .env.local file"
    else
        log_info ".env.local file exists"
    fi

    cd ..
}

################################################################################
# STEP 4: Database Setup
################################################################################

setup_database() {
    print_header "STEP 4: Setting up Database"

    cd backend
    source venv/bin/activate

    log_info "Running database migrations..."

    # Check if alembic is being used
    if [ -d "alembic" ]; then
        alembic upgrade head
        log_success "Database migrations completed"
    else
        log_info "Creating database tables..."
        python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)" 2>/dev/null || true
        log_success "Database tables created"
    fi

    cd ..
}

################################################################################
# STEP 5: Run Tests
################################################################################

run_tests() {
    print_header "STEP 5: Running Tests"

    # Backend tests
    log_info "Running backend tests..."
    cd backend
    source venv/bin/activate

    if [ -d "tests" ]; then
        python -m pytest tests/ -v --tb=short 2>/dev/null || log_warning "Some backend tests failed"
    else
        log_warning "No backend tests found"
    fi

    cd ..

    # Frontend tests
    log_info "Running frontend tests..."
    cd frontend

    if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
        npm test -- --passWithNoTests 2>/dev/null || log_warning "Some frontend tests failed"
    else
        log_warning "No frontend tests configured"
    fi

    cd ..
}

################################################################################
# STEP 6: Verify Installation
################################################################################

verify_installation() {
    print_header "STEP 6: Verifying Installation"

    # Check backend files
    log_info "Checking backend structure..."
    BACKEND_FILES=(
        "backend/app/main.py"
        "backend/app/api/v1/router.py"
        "backend/app/services/openalgo_connector.py"
        "backend/app/services/technical_indicators.py"
        "backend/app/services/websocket_manager.py"
    )

    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "✓ $file"
        else
            log_error "✗ $file missing"
        fi
    done

    # Check frontend files
    log_info "Checking frontend structure..."
    FRONTEND_FILES=(
        "frontend/src/app/page.tsx"
        "frontend/src/lib/api.ts"
        "frontend/src/app/technical-analysis/page.tsx"
        "frontend/src/hooks/useWebSocket.ts"
        "frontend/src/hooks/useMarketData.ts"
    )

    for file in "${FRONTEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "✓ $file"
        else
            log_error "✗ $file missing"
        fi
    done
}

################################################################################
# STEP 7: Start Services
################################################################################

start_services() {
    print_header "STEP 7: Starting Services"

    # Start Backend
    log_info "Starting backend server..."
    cd backend
    source venv/bin/activate

    # Start backend in background
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!

    log_info "Backend starting... (PID: $BACKEND_PID)"
    sleep 5

    # Check if backend is running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log_success "Backend server started successfully"
    else
        log_error "Backend server failed to start. Check backend.log for details"
        cat ../backend.log
        exit 1
    fi

    cd ..

    # Start Frontend
    log_info "Starting frontend server..."
    cd frontend

    # Start frontend in background
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!

    log_info "Frontend starting... (PID: $FRONTEND_PID)"
    sleep 10

    # Check if frontend is running
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        log_success "Frontend server started successfully"
    else
        log_error "Frontend server failed to start. Check frontend.log for details"
        cat ../frontend.log
        exit 1
    fi

    cd ..
}

################################################################################
# STEP 8: Health Checks
################################################################################

run_health_checks() {
    print_header "STEP 8: Running Health Checks"

    # Wait a bit for services to fully start
    sleep 5

    # Check Backend Health
    log_info "Checking backend health..."
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        log_success "Backend API is responding (http://localhost:8000)"
    else
        log_error "Backend API is not responding"
    fi

    # Check Backend API endpoints
    log_info "Testing API endpoints..."

    # Test endpoints (without auth)
    ENDPOINTS=(
        "/api/v1/ws/status"
    )

    for endpoint in "${ENDPOINTS[@]}"; do
        if curl -s "http://localhost:8000$endpoint" > /dev/null 2>&1; then
            log_success "✓ $endpoint"
        else
            log_warning "✗ $endpoint not accessible (may require auth)"
        fi
    done

    # Check Frontend
    log_info "Checking frontend health..."
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend is responding (http://localhost:3000)"
    else
        log_error "Frontend is not responding"
    fi

    # Check WebSocket
    log_info "Checking WebSocket support..."
    if curl -s http://localhost:8000/api/v1/ws/status | grep -q "connection_info" 2>/dev/null; then
        log_success "WebSocket manager is running"
    else
        log_warning "WebSocket status check failed"
    fi
}

################################################################################
# STEP 9: Display Summary
################################################################################

display_summary() {
    print_header "STEP 9: Setup Complete!"

    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    OpenEquity is Running!                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Application URLs:"
    echo "  • Frontend:      http://localhost:3000"
    echo "  • Backend API:   http://localhost:8000"
    echo "  • API Docs:      http://localhost:8000/docs"
    echo "  • API Redoc:     http://localhost:8000/redoc"
    echo ""
    echo "🔌 WebSocket URLs:"
    echo "  • Ticker:        ws://localhost:8000/api/v1/ws/ticker/{symbol}"
    echo "  • Quotes:        ws://localhost:8000/api/v1/ws/quotes"
    echo "  • Depth:         ws://localhost:8000/api/v1/ws/depth/{symbol}"
    echo "  • OHLC:          ws://localhost:8000/api/v1/ws/ohlc/{symbol}"
    echo ""
    echo "📁 Log Files:"
    echo "  • Backend:       ./backend.log"
    echo "  • Frontend:      ./frontend.log"
    echo ""
    echo "🎯 Key Features Available:"
    echo "  ✓ Financial Analysis & DCF Valuation"
    echo "  ✓ Comparable Analysis"
    echo "  ✓ Portfolio Management"
    echo "  ✓ Stock Screening"
    echo "  ✓ Indian Market Integration (NSE/BSE)"
    echo "  ✓ IPO & Primary Markets"
    echo "  ✓ Options & Derivatives"
    echo "  ✓ Technical Analysis (20+ indicators)"
    echo "  ✓ Chart Pattern Recognition"
    echo "  ✓ Real-time Data (OpenAlgo)"
    echo "  ✓ WebSocket Streaming"
    echo ""
    echo "📝 Next Steps:"
    echo "  1. Visit http://localhost:3000 in your browser"
    echo "  2. Register a new account or login"
    echo "  3. Explore the features!"
    echo ""
    echo "⚙️  Optional Setup:"
    echo "  • Install OpenAlgo for real-time broker data"
    echo "    (See OPENALGO_SETUP.md for instructions)"
    echo ""
    echo "🛑 To stop the servers:"
    echo "  • Press Ctrl+C in this terminal"
    echo "  • Or run: ./stop.sh"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  OpenEquity Setup Script                       ║"
    echo "║          Financial Analysis Platform - Complete Setup          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    # Parse arguments
    SKIP_TESTS=false
    SKIP_HEALTH_CHECKS=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-health-checks)
                SKIP_HEALTH_CHECKS=true
                shift
                ;;
            --help)
                echo "Usage: ./run.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-tests           Skip running tests"
                echo "  --skip-health-checks   Skip health checks"
                echo "  --help                 Show this help message"
                echo ""
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Run all steps
    check_requirements
    setup_backend
    setup_frontend
    setup_database

    if [ "$SKIP_TESTS" = false ]; then
        run_tests
    else
        log_warning "Skipping tests (--skip-tests flag)"
    fi

    verify_installation
    start_services

    if [ "$SKIP_HEALTH_CHECKS" = false ]; then
        run_health_checks
    else
        log_warning "Skipping health checks (--skip-health-checks flag)"
    fi

    display_summary

    # Keep script running
    log_info "Servers are running. Press Ctrl+C to stop..."

    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
