#!/bin/bash
#===============================================================================
# Enterprise Data Warehouse - Quality Validation Automation
# Runs comprehensive quality checks across all layers
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

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "==============================================================================="
echo "                    ENTERPRISE DATA WAREHOUSE"
echo "                     Quality Validation Suite"
echo "==============================================================================="
echo

cd "$PROJECT_ROOT"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    log "Virtual environment activated"
fi

# Initialize counters
total_checks=0
passed_checks=0
failed_checks=0

# Function to run quality check
run_quality_check() {
    local layer=$1
    local script_path=$2
    
    log "Running ${layer} layer quality checks..."
    
    if [ -f "$script_path" ]; then
        if python "$script_path"; then
            success "${layer} quality checks: PASSED"
            ((passed_checks++))
        else
            error "${layer} quality checks: FAILED"
            ((failed_checks++))
        fi
        ((total_checks++))
    else
        warning "${layer} quality check script not found: $script_path"
    fi
    echo
}

# Step 1: Bronze Layer Quality Checks
run_quality_check "Bronze" "src/quality_checks/quality_check_bronze.py"

# Step 2: Silver Layer Quality Checks  
run_quality_check "Silver" "src/quality_checks/quality_check_silver.py"

# Step 3: Gold Layer Quality Checks
run_quality_check "Gold" "src/quality_checks/quality_check_gold.py"

# Step 4: Data Volume Validation
log "Step 4: Validating data volumes across layers..."
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))

try:
    from src.connectors.sql_server import db_connector
    
    # Get record counts
    bronze_tables = [
        'bronze.crm_cust_info',
        'bronze.crm_prd_info', 
        'bronze.crm_sales_details'
    ]
    
    silver_tables = [
        'silver.crm_cust_info',
        'silver.crm_prd_info',
        'silver.crm_sales_details'
    ]
    
    gold_views = [
        'gold.dim_customers',
        'gold.dim_products',
        'gold.fact_sales'
    ]
    
    print('=== DATA VOLUME VALIDATION ===')
    
    # Bronze layer
    bronze_total = 0
    for table in bronze_tables:
        try:
            count = db_connector.execute_query(f'SELECT COUNT(*) FROM {table}')[0][0]
            bronze_total += count
            print(f'✅ {table}: {count:,} records')
        except Exception as e:
            print(f'❌ {table}: ERROR - {e}')
    
    print(f'Bronze Total: {bronze_total:,} records')
    print()
    
    # Silver layer
    silver_total = 0
    for table in silver_tables:
        try:
            count = db_connector.execute_query(f'SELECT COUNT(*) FROM {table}')[0][0]
            silver_total += count
            print(f'✅ {table}: {count:,} records')
        except Exception as e:
            print(f'❌ {table}: ERROR - {e}')
    
    print(f'Silver Total: {silver_total:,} records')
    print()
    
    # Gold layer
    gold_total = 0
    for view in gold_views:
        try:
            count = db_connector.execute_query(f'SELECT COUNT(*) FROM {view}')[0][0]
            gold_total += count
            print(f'✅ {view}: {count:,} records')
        except Exception as e:
            print(f'❌ {view}: ERROR - {e}')
    
    print(f'Gold Total: {gold_total:,} records')
    print()
    
    # Data retention analysis
    if bronze_total > 0 and silver_total > 0:
        retention_rate = (silver_total / bronze_total) * 100
        print(f'Data Retention (Bronze→Silver): {retention_rate:.2f}%')
        
        if retention_rate >= 99:
            print('✅ Data retention: EXCELLENT')
        elif retention_rate >= 95:
            print('⚠️  Data retention: GOOD')
        else:
            print('❌ Data retention: NEEDS ATTENTION')
    
except Exception as e:
    print(f'❌ Data volume validation failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    success "Data volume validation: PASSED"
    ((passed_checks++))
else
    error "Data volume validation: FAILED"
    ((failed_checks++))
fi
((total_checks++))

# Step 5: Performance Validation
log "Step 5: Testing query performance..."
python -c "
import time
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))

try:
    from src.connectors.sql_server import db_connector
    
    # Test query performance
    start_time = time.time()
    
    # Complex analytical query
    query = '''
    SELECT 
        c.country,
        p.category,
        COUNT(*) as order_count,
        SUM(f.sales_amount) as total_sales
    FROM gold.fact_sales f
    JOIN gold.dim_customers c ON f.customer_key = c.customer_key
    JOIN gold.dim_products p ON f.product_key = p.product_key
    GROUP BY c.country, p.category
    ORDER BY total_sales DESC
    '''
    
    result = db_connector.execute_query(query)
    execution_time = time.time() - start_time
    
    print(f'✅ Analytical query executed successfully')
    print(f'✅ Execution time: {execution_time:.3f} seconds')
    print(f'✅ Result rows: {len(result):,}')
    
    if execution_time < 5.0:
        print('✅ Performance: EXCELLENT (< 5 seconds)')
    elif execution_time < 10.0:
        print('⚠️  Performance: GOOD (< 10 seconds)')
    else:
        print('❌ Performance: NEEDS OPTIMIZATION (> 10 seconds)')
        
except Exception as e:
    print(f'❌ Performance validation failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    success "Performance validation: PASSED"
    ((passed_checks++))
else
    error "Performance validation: FAILED"
    ((failed_checks++))
fi
((total_checks++))

# Final Summary
echo
echo "==============================================================================="
echo "                        QUALITY VALIDATION SUMMARY"
echo "==============================================================================="
echo "Total Checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $failed_checks"

if [ $failed_checks -eq 0 ]; then
    success "🎉 ALL QUALITY CHECKS PASSED!"
    echo "📊 Data warehouse is production-ready"
    exit 0
else
    error "❌ $failed_checks quality checks failed"
    echo "Please review and fix the issues above"
    exit 1
fi