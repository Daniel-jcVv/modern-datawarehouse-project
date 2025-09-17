#!/usr/bin/env python3
"""
Create Silver Tables - Enterprise Data Transformation Layer
This script creates Silver layer tables in the Data Warehouse
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger


def create_silver_tables():
    """Create Silver layer tables by executing DDL script with quality checks"""
    
    # Expected Silver tables that should be created
    expected_tables = [
        'crm_cust_info',
        'crm_prd_info',
        'crm_sales_details', 
        'erp_cust_az12',
        'erp_loc_a101',
        'erp_px_cat_g1v2'
    ]
    
    logger.info("Creating Silver layer tables...")
    logger.info(f"Expected to create {len(expected_tables)} tables: {', '.join(expected_tables)}")
    
    try:
        # Path to Silver DDL script
        ddl_script_path = project_root / "sql" / "ddl" / "tables" / "ddl_silver.sql"
        
        if not ddl_script_path.exists():
            logger.error(f"Silver DDL script not found at: {ddl_script_path}")
            return False
        
        # Execute DDL script
        logger.info(f"Executing Silver DDL from: {ddl_script_path}")
        success = db_connector.execute_script(str(ddl_script_path))
        
        if success:
            logger.info("Silver DDL script executed successfully!")
            
            # Verify tables were created with detailed checks
            tables_query = """
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'silver' 
            ORDER BY TABLE_NAME
            """
            
            tables = db_connector.execute_query(tables_query)
            created_table_names = [table[1] for table in tables]
            
            logger.info(f"Created {len(tables)} Silver tables:")
            for schema, table in tables:
                logger.info(f"   ✓ {schema}.{table}")
            
            # Quality Check: Verify all expected tables were created
            missing_tables = set(expected_tables) - set(created_table_names)
            unexpected_tables = set(created_table_names) - set(expected_tables)
            
            if missing_tables:
                logger.error(f"MISSING TABLES: {', '.join(missing_tables)}")
                logger.error("Some expected Silver tables were not created!")
                return False
                
            if unexpected_tables:
                logger.warning(f"UNEXPECTED TABLES: {', '.join(unexpected_tables)}")
                
            if len(created_table_names) == len(expected_tables) and not missing_tables:
                logger.info("✓ All expected Silver tables created successfully!")
                logger.info(f"Silver tables: {', '.join(sorted(created_table_names))}")
                return True
            else:
                logger.error(f"Expected {len(expected_tables)} tables, got {len(created_table_names)}")
                return False
        else:
            logger.error("Failed to create Silver tables")
            return False
        
    except Exception as e:
        logger.error(f"Error creating Silver tables: {str(e)}")
        return False


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Silver Table Creation - Data Warehouse Setup")
    logger.info("=" * 60)
    
    # Test database connection
    if not db_connector.test_connection():
        logger.error("Database connection failed - cannot proceed")
        sys.exit(1)
    
    # Create Silver tables
    if create_silver_tables():
        logger.success("Silver table creation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Silver table creation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
