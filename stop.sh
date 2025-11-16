#!/bin/bash

################################################################################
# OpenEquity - Stop Script
# Gracefully stops all running services
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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Stopping OpenEquity Services...                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Stop Backend (uvicorn)
log_info "Stopping backend server..."
if pkill -f "uvicorn app.main:app"; then
    log_success "Backend server stopped"
else
    log_warning "No backend server process found"
fi

# Stop Frontend (Next.js)
log_info "Stopping frontend server..."
if pkill -f "next dev"; then
    log_success "Frontend server stopped"
else
    log_warning "No frontend server process found"
fi

# Additional cleanup
log_info "Cleaning up processes..."

# Kill any remaining Python processes from backend
pkill -f "python.*app.main" 2>/dev/null || true

# Kill any remaining Node processes from frontend
pkill -f "node.*next" 2>/dev/null || true

echo ""
log_success "All services stopped successfully!"
echo ""
