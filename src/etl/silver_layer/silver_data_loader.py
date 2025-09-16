#!/usr/bin/env python3
"""
Silver Layer Data Loader - Transform Bronze to Silver
Executes stored procedures to transform and cleanse data from Bronze to Silver layer

This module follows the medallion architecture pattern where:
- Bronze = Raw data (as-is from source)
- Silver = Cleansed and standardized data
- Gold = Business-ready aggregated data
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger


class SilverDataLoader:
    """
    Handles Silver layer data loading through stored procedure execution
    
    This class manages the transformation of Bronze data to Silver,
    applying business rules, data cleansing, and standardization.
    """
    
    def __init__(self):
        """Initialize Silver loader with configuration"""
        self.stored_procedure = "silver.load_silver"
        self._ensure_stored_procedure_exists()
        self.silver_tables = [
            "silver.crm_cust_info",
            "silver.crm_prd_info", 
            "silver.crm_sales_details",
            "silver.erp_cust_az12",
            "silver.erp_loc_a101",
            "silver.erp_px_cat_g1v2"
        ]
    
    def _ensure_stored_procedure_exists(self) -> bool:
        """
        Verify that the Silver stored procedure exists, create if missing
        
        This method ensures the silver.load_silver procedure is available
        before attempting to execute the ETL process.
        """
        try:
            # Check if stored procedure exists
            check_query = """
            SELECT COUNT(*) 
            FROM sys.procedures 
            WHERE name = 'load_silver' 
            AND schema_id = SCHEMA_ID('silver')
            """
            result = db_connector.execute_query(check_query)
            
            if result and result[0][0] > 0:
                logger.debug("Stored procedure silver.load_silver already exists")
                return True
            
            # If not exists, create it
            logger.info("Creating silver.load_silver stored procedure...")
            
            # Import and execute the procedure creation
            from .silver_procedure import create_silver_procedure
            
            if create_silver_procedure():
                logger.success("Stored procedure created successfully")
                return True
            else:
                logger.error("Failed to create stored procedure")
                return False
                
        except Exception as e:
            logger.error(f"Error checking/creating stored procedure: {e}")
            return False
        
    def execute_stored_procedure(self) -> bool:
        """
        Execute the Silver layer stored procedure with detailed timing
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Executing stored procedure: {self.stored_procedure}")
            
            # Execute the stored procedure
            cursor = db_connector.execute_procedure(self.stored_procedure)
            
            # Capture and log any output messages from the procedure
            messages = []
            while cursor.nextset():
                pass  # Process all result sets
            
            logger.success(f"Stored procedure {self.stored_procedure} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute stored procedure: {str(e)}")
            return False
    
    def execute_transformation_with_timing(self) -> bool:
        """
        Execute Silver transformations with individual table timing
        
        Returns:
            bool: True if successful, False otherwise
        """
        import time
        
        try:
            logger.info("SILVER LAYER ETL - Data Transformation Pipeline")
            logger.info(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            batch_start_time = time.time()
            total_records = 0
            
            # Process each table with individual timing
            table_configs = [
                {"name": "silver.crm_cust_info", "order": "[1/6]", "description": "Customer information standardization"},
                {"name": "silver.crm_prd_info", "order": "[2/6]", "description": "Product information transformation"},
                {"name": "silver.crm_sales_details", "order": "[3/6]", "description": "Sales data validation and cleaning"},
                {"name": "silver.erp_cust_az12", "order": "[4/6]", "description": "ERP customer data normalization"},
                {"name": "silver.erp_loc_a101", "order": "[5/6]", "description": "Location data standardization"},
                {"name": "silver.erp_px_cat_g1v2", "order": "[6/6]", "description": "Product category data migration"}
            ]
            
            for config in table_configs:
                table_start_time = time.time()
                logger.info(f"{config['order']} Processing: {config['name']}")
                logger.info(f"    Task: {config['description']}")
                
                # Here we would call individual transformation logic
                # For now, we'll execute the full stored procedure once
                if config['order'] == '[1/6]':  # Only execute SP once
                    cursor = db_connector.execute_procedure(self.stored_procedure)
                
                table_end_time = time.time()
                
                # Get record count for this table
                count_query = f"SELECT COUNT(*) FROM {config['name']}"
                result = db_connector.execute_query(count_query)
                record_count = result[0][0] if result else 0
                total_records += record_count
                
                duration_ms = round((table_end_time - table_start_time) * 1000, 1)
                logger.info(f"    Records loaded: {record_count:,} | Duration: {duration_ms}ms")
            
            batch_end_time = time.time()
            total_duration_ms = round((batch_end_time - batch_start_time) * 1000, 1)
            
            logger.info("=" * 60)
            logger.info("SILVER LAYER ETL COMPLETED SUCCESSFULLY")
            logger.info(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Total Duration: {total_duration_ms}ms")
            logger.info(f"Total Records Processed: {total_records:,}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Silver transformation failed: {str(e)}")
            return False
    
    def validate_table_loads(self) -> Dict[str, Any]:
        """
        Validate that Silver tables were loaded correctly
        
        Returns:
            Dict containing validation results
        """
        validation_results = {
            "tables": {},
            "total_records": 0,
            "all_valid": True
        }
        
        for table in self.silver_tables:
            try:
                # Get record count
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                result = db_connector.execute_query(count_query)
                record_count = result[0][0] if result else 0
                
                # Check if table has data
                has_data = record_count > 0
                
                validation_results["tables"][table] = {
                    "record_count": record_count,
                    "has_data": has_data,
                    "status": "✅ LOADED" if has_data else "⚠️ EMPTY"
                }
                
                validation_results["total_records"] += record_count
                
                if not has_data:
                    validation_results["all_valid"] = False
                    logger.warning(f"Table {table} is empty after load")
                else:
                    logger.info(f"Table {table}: {record_count:,} records loaded")
                    
            except Exception as e:
                logger.error(f"Failed to validate table {table}: {str(e)}")
                validation_results["tables"][table] = {
                    "record_count": 0,
                    "has_data": False,
                    "status": "❌ ERROR",
                    "error": str(e)
                }
                validation_results["all_valid"] = False
        
        return validation_results
    
    def get_transformation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the transformations applied
        
        Returns:
            Dict containing transformation statistics
        """
        stats = {}
        
        try:
            # Check data quality improvements
            quality_checks = [
                {
                    "name": "Standardized Gender Values",
                    "query": """
                        SELECT COUNT(DISTINCT cst_gndr) as unique_values
                        FROM silver.crm_cust_info
                        WHERE cst_gndr IN ('Male', 'Female', 'n/a')
                    """
                },
                {
                    "name": "Standardized Marital Status",
                    "query": """
                        SELECT COUNT(DISTINCT cst_marital_status) as unique_values
                        FROM silver.crm_cust_info
                        WHERE cst_marital_status IN ('Single', 'Married', 'n/a')
                    """
                },
                {
                    "name": "Cleaned Customer IDs",
                    "query": """
                        SELECT COUNT(*) as cleaned_ids
                        FROM silver.erp_cust_az12
                        WHERE cid NOT LIKE 'NAS%'
                    """
                },
                {
                    "name": "Valid Dates",
                    "query": """
                        SELECT COUNT(*) as valid_dates
                        FROM silver.crm_sales_details
                        WHERE sls_order_dt IS NOT NULL
                        AND sls_order_dt <= GETDATE()
                    """
                }
            ]
            
            for check in quality_checks:
                result = db_connector.execute_query(check["query"])
                if result:
                    stats[check["name"]] = result[0][0]
                    
        except Exception as e:
            logger.warning(f"Could not get all transformation statistics: {str(e)}")
        
        return stats
    
    def run_silver_etl(self) -> bool:
        """
        Main method to run the complete Silver ETL process
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting Silver Layer ETL Process")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Step 1: Execute Silver transformation with detailed timing
        logger.info("Step 1: Executing Silver transformation with detailed timing")
        if not self.execute_transformation_with_timing():
            logger.error("Silver transformation failed")
            return False
        logger.success("Silver transformation completed successfully")
        
        # Step 2: Validate loads
        logger.info("Step 2: Validating Silver table loads")
        validation_results = self.validate_table_loads()
        
        if not validation_results["all_valid"]:
            logger.warning("WARNING: Some tables may have issues - review validation results")
        else:
            logger.success("All Silver tables loaded successfully")
        
        # Step 3: Get transformation statistics
        logger.info("Step 3: Analyzing transformation results")
        stats = self.get_transformation_statistics()
        
        # Report results
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        logger.info("=" * 60)
        logger.info("SILVER LAYER ETL SUMMARY")
        logger.info(f"Duration: {duration} seconds")
        logger.info(f"Total Records: {validation_results['total_records']:,}")
        logger.info(f"Tables Processed: {len(self.silver_tables)}")
        
        if stats:
            logger.info("Data Quality Improvements:")
            for metric, value in stats.items():
                logger.info(f"  - {metric}: {value:,}")
        
        logger.info("=" * 60)
        
        return validation_results["all_valid"]


def main():
    """Execute Silver ETL pipeline"""
    logger.info("SILVER LAYER ETL PIPELINE")
    logger.info("Transforming Bronze data to Silver standard")
    
    # Check database connectivity
    if not db_connector.test_connection():
        logger.error("❌ Database connection failed")
        sys.exit(1)
    
    # Run Silver ETL
    loader = SilverDataLoader()
    success = loader.run_silver_etl()
    
    if success:
        logger.success("Silver Layer ETL completed successfully!")
        sys.exit(0)
    else:
        logger.error("Silver Layer ETL completed with issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
