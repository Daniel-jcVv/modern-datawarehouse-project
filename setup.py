#!/usr/bin/env python3
"""
Master Setup Script for DataWarehouse
Complete database and bronze layer initialization
"""

import sys
import os

# Adjust path to find src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


def run_database_setup():
    """Run database setup"""
    logger.info("📋 Step 1: Database and Schema Creation")
    
    # Import and run database setup
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            'scripts/database/setup_database.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            logger.info("✅ Database setup completed")
            return True
        else:
            logger.error(f"❌ Database setup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database setup error: {str(e)}")
        return False


def run_bronze_tables():
    """Create bronze tables"""
    logger.info("📋 Step 2: Bronze Layer Table Creation")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            'scripts/database/create_bronze_tables.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            logger.info("✅ Bronze tables created")
            return True
        else:
            logger.error(f"❌ Bronze tables creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Bronze tables error: {str(e)}")
        return False


def main():
    """Main setup orchestration"""
    logger.info("🚀 Starting Complete DataWarehouse Setup...")
    logger.info("=" * 50)
    
    # Step 1: Database and schemas
    if not run_database_setup():
        logger.error("❌ Setup failed at database creation")
        return False
    
    # Step 2: Bronze tables
    if not run_bronze_tables():
        logger.error("❌ Setup failed at bronze tables creation")
        return False
    
    logger.info("=" * 50)
    logger.info("🎉 Complete DataWarehouse Setup Successful!")
    logger.info("🔗 Ready for data ingestion")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
