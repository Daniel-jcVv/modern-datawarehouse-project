#!/bin/bash
#===============================================================================
# Enterprise Data Warehouse - Environment Setup Automation
# Sets up complete development environment from scratch
#===============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "==============================================================================="
echo "                    ENTERPRISE DATA WAREHOUSE SETUP"
echo "                        Environment Automation"
echo "==============================================================================="
echo

# Step 1: Python Environment Setup
log "Step 1: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Virtual environment created"
else
    warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
success "Virtual environment activated"

# Step 2: Install Dependencies
log "Step 2: Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    success "Dependencies installed successfully"
else
    error "requirements.txt not found!"
    exit 1
fi

# Step 3: Verify Docker Container
log "Step 3: Verifying SQL Server container..."
if docker ps | grep -q sqlserver; then
    success "SQL Server container is running"
else
    warning "SQL Server container not running"
    echo "Please start SQL Server container:"
    echo "docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=MyPass123!' \\"
    echo "  -p 1434:1433 --name sqlserver-dwh \\"
    echo "  -v \$(pwd)/data_sets:/data_sets \\"
    echo "  -d mcr.microsoft.com/mssql/server:2022-latest"
    exit 1
fi

# Step 4: Database Setup
log "Step 4: Initializing database and schemas..."
if python setup.py; then
    success "Database and schemas initialized"
else
    error "Database setup failed!"
    exit 1
fi

# Step 5: Environment Verification
log "Step 5: Running environment verification..."
python -c "
import pandas as pd
import sqlalchemy
import pyodbc
from src.connectors.sql_server import db_connector

print('✅ pandas:', pd.__version__)
print('✅ sqlalchemy:', sqlalchemy.__version__)
print('✅ pyodbc:', pyodbc.version)

# Test database connection
if db_connector.test_connection():
    print('✅ Database connection: OK')
else:
    print('❌ Database connection: FAILED')
    exit(1)
"

success "Environment setup completed successfully!"
echo
echo "=== NEXT STEPS ==="
echo "1. Run full pipeline: ./scripts/run_full_pipeline.sh"
echo "2. Run individual layers:"
echo "   python run_pipeline.py bronze"
echo "   python run_pipeline.py silver" 
echo "   python run_pipeline.py gold"
echo "3. Run quality checks:"
echo "   python src/quality_checks/quality_check_gold.py"
echo
echo "==============================================================================="
echo "                        ENVIRONMENT READY"
echo "==============================================================================="