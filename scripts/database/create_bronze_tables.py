#!/usr/bin/env python3
"""
Create Bronze Layer Tables
Execute DDL scripts to create bronze schema tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.connectors.sql_server import db_connector
from loguru import logger


def create_bronze_tables():
    """Create all bronze layer tables"""
    script_path = "./sql/ddl/tables/ddl_bronze.sql"
    
    try:
        logger.info("🏗️  Creating Bronze layer tables...")
        
        if db_connector.execute_script(script_path):
            logger.info("✅ Bronze tables created successfully!")
            
            # Verify tables were created
            verify_query = """
            SELECT 
                SCHEMA_NAME(schema_id) as schema_name,
                name as table_name
            FROM sys.tables 
            WHERE SCHEMA_NAME(schema_id) = 'bronze'
            ORDER BY name
            """
            
            tables = db_connector.execute_query(verify_query)
            logger.info(f"📋 Created {len(tables)} bronze tables:")
            for table in tables:
                logger.info(f"   ✅ {table[0]}.{table[1]}")
                
            return True
        else:
            logger.error("❌ Bronze tables creation failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Bronze tables creation error: {str(e)}")
        return False


def main():
    """Main execution"""
    logger.info("🚀 Creating Bronze Layer...")
    
    # Test connection first
    if not db_connector.test_connection():
        logger.error("❌ Cannot connect to DataWarehouse")
        logger.info("💡 Run: python create_database.py first")
        return False
    
    # Create bronze tables
    if create_bronze_tables():
        logger.info("🎉 Bronze Layer setup completed!")
        logger.info("🔗 Ready for data ingestion")
        return True
    else:
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
