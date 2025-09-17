#!/usr/bin/env python3
"""
Bronze Layer ETL Pipeline - Main Execution Script
Orchestrates data loading and validation with enterprise logging

Location: src/pipelines/bronze_pipeline.py
Purpose: Production pipeline for Bronze layer data ingestion
Author: Data Engineering Team
"""

import sys
from pathlib import Path

# Add project root to Python path
# Note: Now we go up 3 levels (pipelines -> src -> project_root)
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.etl.bronze_layer.bronze_data_loader import BronzeETLTypeSafe
from src.quality_checks import QualityCheckBronze
from src.connectors.sql_server import db_connector
from loguru import logger
import time


def main():
    """Execute Bronze ETL pipeline with validation"""
    logger.info("BRONZE LAYER ETL PIPELINE EXECUTION")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Database connectivity check
    logger.info("Step 1: Database Connectivity Verification")
    if not db_connector.test_connection():
        logger.error("Database connection failed - pipeline cannot proceed")
        sys.exit(1)
    logger.success("Database connection verified")
    logger.info("-" * 50)
    
    # Step 2: Execute Bronze ETL
    logger.info("Step 2: Bronze Data Loading")
    etl = BronzeETLTypeSafe()
    
    if not etl.run_bronze_etl():
        logger.error("Bronze ETL pipeline failed")
        sys.exit(1)
    
    logger.success("Bronze data loading completed")
    logger.info("-" * 50)
    
    # Step 3: Data validation
    logger.info("Step 3: Data Validation & Quality Assurance")
    validator = QualityCheckBronze()
    validation_results = validator.run_full_validation()

    if validation_results["summary"]["failed_tables"] > 0:
        logger.error("Data validation detected issues")
        logger.info("Check validation results above for details")
        sys.exit(1)

    logger.success("All data validations passed")
    logger.info("-" * 50)
    
    # Pipeline summary
    end_time = time.time()
    total_duration = round(end_time - start_time, 2)
    
    logger.info("BRONZE LAYER PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Total Execution Time: {total_duration} seconds")
    logger.info(f"Tables Processed: {validation_results['summary']['total_tables']}")
    logger.info(f"Validation Success Rate: {validation_results['summary']['success_rate']}%")
    logger.info("Ready for Silver Layer processing!")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
