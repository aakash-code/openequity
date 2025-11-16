#!/bin/bash

################################################################################
# OpenEquity - Quick Health Check Script
# Verifies that all services are running correctly
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           OpenEquity Health Check                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# Check if backend is running
log_info "Checking backend server..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    log_success "Backend API running at http://localhost:8000"
else
    log_error "Backend API not responding"
    ERRORS=$((ERRORS+1))
fi

# Check if frontend is running
log_info "Checking frontend server..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    log_success "Frontend running at http://localhost:3000"
else
    log_error "Frontend not responding"
    ERRORS=$((ERRORS+1))
fi

# Check WebSocket
log_info "Checking WebSocket support..."
WS_STATUS=$(curl -s http://localhost:8000/api/v1/ws/status 2>/dev/null)
if echo "$WS_STATUS" | grep -q "connection_info"; then
    log_success "WebSocket manager operational"

    # Parse and display connection info
    TOTAL_CONNECTIONS=$(echo "$WS_STATUS" | grep -o '"total_connections":[0-9]*' | cut -d':' -f2)
    if [ ! -z "$TOTAL_CONNECTIONS" ]; then
        echo "  → Active connections: $TOTAL_CONNECTIONS"
    fi
else
    log_error "WebSocket manager not responding"
    ERRORS=$((ERRORS+1))
fi

# Check API Endpoints
echo ""
log_info "Testing key API endpoints..."

declare -a endpoints=(
    "/api/v1/ws/status|WebSocket Status"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS='|' read -r endpoint name <<< "$endpoint_info"
    if curl -s "http://localhost:8000$endpoint" > /dev/null 2>&1; then
        log_success "$name"
    else
        log_error "$name (endpoint: $endpoint)"
        ERRORS=$((ERRORS+1))
    fi
done

# Check processes
echo ""
log_info "Checking running processes..."

if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
    BACKEND_PID=$(pgrep -f "uvicorn app.main:app")
    log_success "Backend process running (PID: $BACKEND_PID)"
else
    log_error "Backend process not found"
    ERRORS=$((ERRORS+1))
fi

if pgrep -f "next dev" > /dev/null 2>&1; then
    FRONTEND_PID=$(pgrep -f "next dev")
    log_success "Frontend process running (PID: $FRONTEND_PID)"
else
    log_error "Frontend process not found"
    ERRORS=$((ERRORS+1))
fi

# Check database
echo ""
log_info "Checking database connection..."
if [ -f "backend/openequity.db" ]; then
    DB_SIZE=$(du -h backend/openequity.db | cut -f1)
    log_success "Database file exists (Size: $DB_SIZE)"
else
    log_error "Database file not found"
    ERRORS=$((ERRORS+1))
fi

# Check log files
echo ""
log_info "Checking log files..."

if [ -f "backend.log" ]; then
    BACKEND_LOG_SIZE=$(wc -l < backend.log)
    log_success "Backend log exists ($BACKEND_LOG_SIZE lines)"

    # Check for errors in backend log
    if grep -q "ERROR" backend.log 2>/dev/null; then
        log_error "Errors found in backend log (check backend.log)"
        echo "  Last error:"
        grep "ERROR" backend.log | tail -1
    fi
else
    log_error "Backend log file not found"
fi

if [ -f "frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(wc -l < frontend.log)
    log_success "Frontend log exists ($FRONTEND_LOG_SIZE lines)"

    # Check for errors in frontend log
    if grep -qi "error" frontend.log 2>/dev/null; then
        log_error "Errors found in frontend log (check frontend.log)"
    fi
else
    log_error "Frontend log file not found"
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! OpenEquity is running correctly.${NC}"
else
    echo -e "${RED}✗ Found $ERRORS issue(s). Check the logs for details.${NC}"
fi
echo "════════════════════════════════════════════════════════════════"
echo ""

# Detailed status
if [ $ERRORS -eq 0 ]; then
    echo "📊 Application Status: HEALTHY"
    echo ""
    echo "Access Points:"
    echo "  • Frontend:    http://localhost:3000"
    echo "  • Backend:     http://localhost:8000"
    echo "  • API Docs:    http://localhost:8000/docs"
    echo ""
fi

exit $ERRORS
