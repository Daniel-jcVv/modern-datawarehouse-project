#!/usr/bin/env python3
"""
Docker SQL Server Connection Validation
Quick test to verify Python -> Docker SQL Server connectivity
"""

import sys
import os
sys.path.append('src')

from src.connectors.sql_server import db_connector
from loguru import logger

def main():
    """Test Docker SQL Server connection and basic operations"""
    
    logger.info("Testing Docker SQL Server connection...")
    
    # Test basic connectivity
    if not db_connector.test_connection():
        logger.error("Connection failed")
        return False
    
    # Test query execution
    try:
        result = db_connector.execute_query("SELECT @@VERSION as sql_version")
        version = result[0][0][:50] + "..." if result else "Unknown"
        logger.info(f"SQL Server Version: {version}")
        
        # Test database creation
        db_connector.execute_query("SELECT name FROM sys.databases WHERE name = 'DataWarehouse'")
        logger.info("Ready for database setup")
        
        return True
        
    except Exception as e:
        logger.error(f"Query test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.success("🎉 Docker SQL Server integration successful!")
        print("\nYour containerized Data Warehouse is ready!")
    else:
        logger.error("Integration failed - check configuration")
        sys.exit(1)
