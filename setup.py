"""
Master Setup Script for DataWarehouse
Creates database, schemas, and tables for Bronze and Silver layers
Orchestrates individual setup scripts
"""

import sys
import os

# Adjust path to find src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


def run_database_setup():
    """Run database setup"""
    logger.info("Step 1: Database and Schema Creation")
    
    # Import and run database setup
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            'scripts/database/setup_database.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            logger.info("Database setup completed")
            return True
        else:
            logger.error(f"Database setup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
        return False


def run_bronze_tables():
    """Create bronze tables"""
    logger.info("Step 2: Bronze Layer Table Creation")
    
    try:
        # Import and run bronze table creation directly
        sys.path.append('scripts/database')
        from create_bronze_tables import create_bronze_tables
        
        success = create_bronze_tables()
        if success:
            logger.info("Bronze tables creation completed")
        else:
            logger.error("Bronze tables creation failed")
        return success
            
    except Exception as e:
        logger.error(f"Bronze tables error: {str(e)}")
        return False


def run_silver_tables():
    """Create silver tables"""
    logger.info("Step 3: Silver Layer Table Creation")
    
    try:
        # Import and run silver table creation directly
        from create_silver_tables import create_silver_tables
        
        success = create_silver_tables()
        if success:
            logger.info("Silver tables creation completed")
        else:
            logger.error("Silver tables creation failed")
        return success
            
    except Exception as e:
        logger.error(f"Silver tables error: {str(e)}")
        return False


def main():
    """Main setup orchestration"""
    logger.info("Starting Complete DataWarehouse Setup...")
    logger.info("=" * 50)
    
    # Step 1: Database and schemas
    if not run_database_setup():
        logger.error("Setup failed at database creation")
        return False
    
    # Step 2: Bronze tables
    if not run_bronze_tables():
        logger.error("Setup failed at bronze tables creation")
        return False
    
    # Step 3: Silver tables
    if not run_silver_tables():
        logger.error("Setup failed at silver tables creation")
        return False
    
    logger.info("=" * 50)
    logger.info("Complete DataWarehouse Setup Successful!")
    logger.info("Ready for data ingestion and transformation")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
