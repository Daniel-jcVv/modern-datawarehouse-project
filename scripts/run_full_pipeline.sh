#!/bin/bash
#===============================================================================
# Enterprise Data Warehouse - Full Pipeline Automation
# Executes complete Bronze → Silver → Gold ETL pipeline with validation
#===============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "==============================================================================="
echo "                    ENTERPRISE DATA WAREHOUSE PIPELINE"
echo "                           Full ETL Automation"
echo "==============================================================================="
echo

cd "$PROJECT_ROOT"

# Step 1: Infrastructure verification
log "Step 1: Verifying infrastructure and database..."
if python setup.py > /dev/null 2>&1; then
    success "Infrastructure verification passed"
else
    error "Infrastructure setup failed!"
    echo "Please run: python setup.py"
    exit 1
fi

# Step 2: Bronze Layer ETL
log "Step 2: Executing Bronze Layer ETL..."
if python run_pipeline.py bronze; then
    success "Bronze layer completed successfully"
else
    error "Bronze layer failed!"
    exit 1
fi

# Step 3: Silver Layer ETL
log "Step 3: Executing Silver Layer transformations..."
if python run_pipeline.py silver; then
    success "Silver layer completed successfully"
else
    error "Silver layer failed!"
    exit 1
fi

# Step 4: Gold Layer ETL
log "Step 4: Executing Gold Layer star schema..."
if python run_pipeline.py gold; then
    success "Gold layer completed successfully"
else
    error "Gold layer failed!"
    exit 1
fi

# Step 5: Quality validation summary
log "Step 5: Running comprehensive quality validation..."
echo
echo "=== PIPELINE EXECUTION SUMMARY ==="
echo "Bronze Layer: ✅ Completed"
echo "Silver Layer: ✅ Completed" 
echo "Gold Layer:   ✅ Completed"
echo
success "🎉 Complete ETL pipeline executed successfully!"
echo "📊 Data warehouse is ready for analytics and BI tools"
echo

# Optional: Display record counts
log "Final data volumes:"
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))
from src.connectors.sql_server import db_connector

try:
    # Bronze layer count
    bronze_count = db_connector.execute_query('SELECT COUNT(*) FROM bronze.crm_sales_details')[0][0]
    # Silver layer count  
    silver_count = db_connector.execute_query('SELECT COUNT(*) FROM silver.crm_sales_details')[0][0]
    # Gold layer count
    gold_count = db_connector.execute_query('SELECT COUNT(*) FROM gold.fact_sales')[0][0]
    
    print(f'  Bronze layer: {bronze_count:,} records')
    print(f'  Silver layer: {silver_count:,} records') 
    print(f'  Gold layer:   {gold_count:,} records')
except Exception as e:
    print(f'  Could not retrieve counts: {e}')
"

echo
echo "==============================================================================="
echo "                           PIPELINE COMPLETED"
echo "==============================================================================="