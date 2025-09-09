#!/usr/bin/env python3
"""
Test SQL Server connectivity
Run this to verify your connection is working before proceeding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors.sql_server import db_connector
from loguru import logger


def main():
    """Test database connectivity"""
    logger.info("🧪 Testing SQL Server Connection...")
    
    # Test basic connectivity
    if db_connector.test_connection():
        logger.info("✅ Connection test passed!")
        
        # Test query execution
        try:
            result = db_connector.execute_query("SELECT @@VERSION as version")
            version = result[0][0] if result else "Unknown"
            logger.info(f"📋 SQL Server Version: {version[:50]}...")
            
            # Test database creation capability
            db_name = db_connector.database
            check_db_query = f"SELECT name FROM sys.databases WHERE name = '{db_name}'"
            result = db_connector.execute_query(check_db_query)
            
            if result:
                logger.info(f"✅ Database '{db_name}' exists and is accessible")
            else:
                logger.warning(f"⚠️ Database '{db_name}' not found - will need to create it")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Query test failed: {str(e)}")
            return False
    else:
        logger.error("❌ Connection test failed!")
        logger.info("💡 Check your Docker container: docker ps | grep sqlserver")
        logger.info("💡 Verify credentials in .env file")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
