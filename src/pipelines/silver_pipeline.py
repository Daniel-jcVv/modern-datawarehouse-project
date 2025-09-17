#!/usr/bin/env python3
"""
Silver Layer ETL Pipeline - Main Execution Script
Orchestrates data transformation from Bronze to Silver with quality checks

Location: src/pipelines/silver_pipeline.py
Purpose: Production pipeline for Silver layer data transformation
Author: Data Engineering Team
"""


import sys
from pathlib import Path
import time
from loguru import logger
from src.etl.silver_layer.silver_data_loader import SilverDataLoader
from src.quality_checks.quality_check_silver import QualityCheckSilver
from src.connectors.sql_server import db_connector

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def main():
    """Execute Silver ETL pipeline with validation"""
    logger.info("SILVER LAYER ETL PIPELINE - ENTERPRISE EXECUTION")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Database connectivity check
    logger.info("Step 1: Database Connectivity Verification")
    if not db_connector.test_connection():
        logger.error("Database connection failed - pipeline cannot proceed")
        sys.exit(1)
    logger.success("Database connection verified")
    logger.info("-" * 50)
    
    # Step 2: Verify Bronze data exists
    logger.info("Step 2: Verifying Bronze Layer Data")
    bronze_tables = [
        "bronze.crm_cust_info",
        "bronze.crm_prd_info",
        "bronze.crm_sales_details",
        "bronze.erp_cust_az12",
        "bronze.erp_loc_a101",
        "bronze.erp_px_cat_g1v2"
    ]
    
    bronze_ready = True
    for table in bronze_tables:
        query = f"SELECT COUNT(*) FROM {table}"
        result = db_connector.execute_query(query)
        count = result[0][0] if result else 0
        if count == 0:
            logger.error(f"Bronze table {table} is empty")
            bronze_ready = False
        else:
            logger.info(f"{table}: {count:,} records available")
    
    if not bronze_ready:
        logger.error("Bronze layer not ready - run Bronze pipeline first")
        sys.exit(1)
    
    logger.success("Bronze layer data verified")
    logger.info("-" * 50)
    
    # Step 3: Execute Silver ETL
    logger.info("Step 3: Silver Data Transformation")
    loader = SilverDataLoader()
    
    if not loader.run_silver_etl():
        logger.error("Silver ETL pipeline failed")
        sys.exit(1)
    
    logger.success("Silver data transformation completed")
    logger.info("-" * 50)
    
    # Step 4: Silver Data Quality Validation
    logger.info("Step 4: Silver Data Quality Validation")
    validator = QualityCheckSilver()
    validation_results = validator.run_full_validation()
    
    if not validation_results["summary"]["validation_passed"]:
        logger.warning(
            "WARNING: Some validation checks failed - review results"
        )
        for issue in validation_results["summary"]["issues_found"]:
            logger.warning(f"  - {issue}")
    else:
        logger.success("All Silver validations passed")
    
    logger.info("-" * 50)
    
    # Pipeline summary
    end_time = time.time()
    total_duration = round(end_time - start_time, 2)
    
    logger.info("SILVER LAYER PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Total Execution Time: {total_duration} seconds")
    logger.info("Data Quality Improvements Applied:")
    logger.info("Gender and marital status standardized")
    logger.info("Invalid dates corrected")
    logger.info("Customer IDs cleaned")
    logger.info("Country codes normalized")
    logger.info("Duplicate records removed")
    logger.info("Ready for Gold Layer processing!")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
