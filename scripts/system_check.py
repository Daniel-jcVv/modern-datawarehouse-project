#!/usr/bin/env python3
"""
System Health Check
Verifies prerequisites before running ETL pipelines
"""

import sys
from pathlib import Path
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_docker():
    """Check if Docker container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=datawarehouse-sql-server'], 
                              capture_output=True, text=True, check=True)
        if 'datawarehouse-sql-server' in result.stdout:
            print("[OK] Docker container is running")
            return True
        else:
            print("[ERROR] Docker container not found")
            print("   Run: docker-compose up -d")
            return False
    except Exception as e:
        print(f"[ERROR] Docker check failed: {e}")
        print("   Ensure Docker is installed and running")
        return False

def check_imports():
    """Check if all required modules can be imported"""
    try:
        from src.connectors.sql_server import db_connector
        print("[OK] SQL Server connector import successful")
        
        from src.etl.bronze_layer.bronze_data_loader import BronzeETLTypeSafe
        print("[OK] Bronze ETL loader import successful")
        
        from src.validators.bronze_data_validator import BronzeDataValidator
        print("[OK] Bronze validator import successful")
        
        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Check database connectivity"""
    try:
        from src.connectors.sql_server import db_connector
        if db_connector.test_connection():
            print("[OK] Database connection successful")
            return True
        else:
            print("[ERROR] Database connection failed")
            print("   Check .env configuration and SQL Server container")
            return False
    except Exception as e:
        print(f"[ERROR] Database connection error: {e}")
        return False

def check_data_files():
    """Check if all required data files exist"""
    data_files = [
        "data_sets/source_crm/cust_info.csv",
        "data_sets/source_crm/prd_info.csv", 
        "data_sets/source_crm/sales_details.csv",
        "data_sets/source_erp/CUST_AZ12.csv",
        "data_sets/source_erp/LOC_A101.csv",
        "data_sets/source_erp/PX_CAT_G1V2.csv"
    ]
    
    all_exist = True
    for file_path in data_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """Run system health checks"""
    print("SYSTEM HEALTH CHECK")
    print("=" * 50)
    print("Verifying prerequisites for ETL pipeline execution...")
    
    checks = [
        ("Docker Container Status", check_docker),
        ("Python Module Dependencies", check_imports), 
        ("Database Connectivity", check_database_connection),
        ("Source Data Files", check_data_files)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("ALL CHECKS PASSED")
        print("\nRun pipelines with:")
        print("  python run_pipeline.py bronze")
    else:
        print("SYSTEM CHECK FAILED")
        print("Resolve issues before proceeding")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
