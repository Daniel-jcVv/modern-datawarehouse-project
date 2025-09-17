#!/usr/bin/env python3
"""
Create Bronze Layer Tables
Execute DDL scripts to create bronze schema tables
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.connectors.sql_server import db_connector
from loguru import logger


def create_bronze_tables():
    """Create all bronze layer tables with quality checks"""
    script_path = "./sql/ddl/tables/ddl_bronze.sql"
    
    # Expected tables that should be created
    expected_tables = [
        'crm_cust_info',
        'crm_prd_info', 
        'crm_sales_details',
        'erp_cust_az12',
        'erp_loc_a101',
        'erp_px_cat_g1v2',
        'etl_execution_log'
    ]
    
    try:
        logger.info("Creating Bronze layer tables...")
        logger.info(f"Expected to create {len(expected_tables)} tables: {', '.join(expected_tables)}")
        
        if db_connector.execute_script(script_path):
            logger.info("Bronze DDL script executed successfully!")
            
            # Verify tables were created with detailed checks
            verify_query = """
            SELECT 
                SCHEMA_NAME(schema_id) as schema_name,
                name as table_name
            FROM sys.tables 
            WHERE SCHEMA_NAME(schema_id) = 'bronze'
            ORDER BY name
            """
            
            tables = db_connector.execute_query(verify_query)
            created_table_names = [table[1] for table in tables]
            
            logger.info(f"Created {len(tables)} bronze tables:")
            for table in tables:
                logger.info(f"   ✓ {table[0]}.{table[1]}")
            
            # Quality Check: Verify all expected tables were created
            missing_tables = set(expected_tables) - set(created_table_names)
            unexpected_tables = set(created_table_names) - set(expected_tables)
            
            if missing_tables:
                logger.error(f"MISSING TABLES: {', '.join(missing_tables)}")
                logger.error("Some expected tables were not created!")
                return False
                
            if unexpected_tables:
                logger.warning(f"UNEXPECTED TABLES: {', '.join(unexpected_tables)}")
                
            if len(created_table_names) == len(expected_tables) and not missing_tables:
                logger.info("✓ All expected bronze tables created successfully!")
                logger.info(f"Bronze tables: {', '.join(sorted(created_table_names))}")
                return True
            else:
                logger.error(f"Expected {len(expected_tables)} tables, got {len(created_table_names)}")
                return False
                
        else:
            logger.error("Bronze tables creation failed!")
            return False
            
    except Exception as e:
        logger.error(f"Bronze tables creation error: {str(e)}")
        return False


def main():
    """Main execution"""
    logger.info("Creating Bronze Layer...")
    
    # Test connection first
    if not db_connector.test_connection():
        logger.error("Cannot connect to DataWarehouse")
        logger.info("Run: python create_database.py first")
        return False
    
    # Create bronze tables
    if create_bronze_tables():
        logger.info("Bronze Layer setup completed!")
        logger.info("Ready for data ingestion")
        return True
    else:
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
