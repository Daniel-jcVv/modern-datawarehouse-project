#!/usr/bin/env python3
"""
Bronze Layer Data Validator - Enterprise Quality Assurance
Validates successful data loading with comprehensive checks
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger
from typing import Dict, List, Any
import pandas as pd


class QualityCheckBronze:
    """Enterprise data validation for Bronze layer tables"""
    
    def __init__(self):
        self.validation_queries = {
            "bronze.crm_cust_info": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.crm_cust_info",
                "sample_query": "SELECT TOP 3 * FROM bronze.crm_cust_info",
                "expected_columns": ["cst_id", "cst_key", "cst_firstname", "cst_lastname", 
                                   "cst_marital_status", "cst_gndr", "cst_create_date"],
                "source_file": "source_crm/cust_info.csv"
            },
            "bronze.crm_prd_info": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.crm_prd_info",
                "sample_query": "SELECT TOP 3 * FROM bronze.crm_prd_info",
                "expected_columns": ["prd_id", "prd_key", "prd_nm", "prd_cost", 
                                   "prd_line", "prd_start_dt", "prd_end_dt"],
                "source_file": "source_crm/prd_info.csv"
            },
            "bronze.crm_sales_details": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.crm_sales_details",
                "sample_query": "SELECT TOP 3 * FROM bronze.crm_sales_details",
                "expected_columns": ["sls_ord_num", "sls_prd_key", "sls_cust_id", "sls_order_dt",
                                   "sls_ship_dt", "sls_due_dt", "sls_sales", "sls_quantity", "sls_price"],
                "source_file": "source_crm/sales_details.csv"
            },
            "bronze.erp_cust_az12": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.erp_cust_az12",
                "sample_query": "SELECT TOP 3 * FROM bronze.erp_cust_az12",
                "expected_columns": ["cid", "bdate", "gen"],
                "source_file": "source_erp/CUST_AZ12.csv"
            },
            "bronze.erp_loc_a101": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.erp_loc_a101",
                "sample_query": "SELECT TOP 3 * FROM bronze.erp_loc_a101",
                "expected_columns": ["cid", "cntry"],
                "source_file": "source_erp/LOC_A101.csv"
            },
            "bronze.erp_px_cat_g1v2": {
                "count_query": "SELECT COUNT(*) as record_count FROM bronze.erp_px_cat_g1v2",
                "sample_query": "SELECT TOP 3 * FROM bronze.erp_px_cat_g1v2",
                "expected_columns": ["id", "cat", "subcat", "maintenance"],
                "source_file": "source_erp/PX_CAT_G1V2.csv"
            }
        }
    
    def validate_table_count(self, table_name: str) -> Dict[str, Any]:
        """Validate record count matches source file"""
        try:
            config = self.validation_queries[table_name]
            
            # Get database count
            db_result = db_connector.execute_query(config["count_query"])
            db_count = db_result[0][0]
            
            # Get source file count
            source_file_path = project_root / "data_sets" / config["source_file"]
            source_df = pd.read_csv(source_file_path)
            source_count = len(source_df)
            
            # Validation result
            is_valid = db_count == source_count
            
            return {
                "table": table_name,
                "db_count": db_count,
                "source_count": source_count,
                "match": is_valid,
                "status": "PASS" if is_valid else "FAIL"
            }
            
        except Exception as e:
            logger.error(f"Count validation failed for {table_name}: {str(e)}")
            return {
                "table": table_name,
                "error": str(e),
                "status": "ERROR"
            }
    
    def validate_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Validate table exists and has expected columns
        
        Note: Ignores system metadata columns (dwh_*, etl_*, etc.) as these are
        added by the Bronze layer for tracking and auditing purposes.
        """
        try:
            # Get table columns
            schema_query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'bronze' 
            AND TABLE_NAME = '{table_name.split('.')[1]}'
            ORDER BY ORDINAL_POSITION
            """
            
            db_result = db_connector.execute_query(schema_query)
            all_db_columns = [row[0] for row in db_result]
            
            # Filter out system metadata columns (dwh_*, etl_*, batch_*, etc.)
            # These are added by the Bronze layer for tracking purposes
            system_column_prefixes = ('dwh_', 'etl_', 'batch_', 'load_', 'audit_')
            db_columns = [
                col for col in all_db_columns 
                if not col.lower().startswith(system_column_prefixes)
            ]
            
            config = self.validation_queries[table_name]
            expected_columns = config["expected_columns"]
            
            # Check if all expected columns exist (ignoring metadata columns)
            missing_columns = set(expected_columns) - set(db_columns)
            
            # Extra columns are only a problem if they're NOT metadata columns
            extra_columns = set(db_columns) - set(expected_columns)
            
            # Schema is valid if all expected columns are present
            # Extra metadata columns are acceptable (and expected)
            is_valid = len(missing_columns) == 0
            
            # Identify metadata columns for reporting
            metadata_columns = [
                col for col in all_db_columns 
                if col.lower().startswith(system_column_prefixes)
            ]
            
            return {
                "table": table_name,
                "expected_columns": expected_columns,
                "actual_columns": db_columns,
                "metadata_columns": metadata_columns,
                "missing_columns": list(missing_columns),
                "extra_columns": list(extra_columns),
                "match": is_valid,
                "status": "PASS" if is_valid else "FAIL"
            }
            
        except Exception as e:
            logger.error(f"Schema validation failed for {table_name}: {str(e)}")
            return {
                "table": table_name,
                "error": str(e),
                "status": "ERROR"
            }
    
    def validate_data_sample(self, table_name: str) -> Dict[str, Any]:
        """Validate sample data from table"""
        try:
            config = self.validation_queries[table_name]
            
            # Get sample data
            db_result = db_connector.execute_query(config["sample_query"])
            
            return {
                "table": table_name,
                "sample_count": len(db_result),
                "has_data": len(db_result) > 0,
                "sample_data": db_result[:3] if db_result else [],
                "status": "HAS DATA" if db_result else "NO DATA"
            }
            
        except Exception as e:
            logger.error(f"Sample validation failed for {table_name}: {str(e)}")
            return {
                "table": table_name,
                "error": str(e),
                "status": "ERROR"
            }
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Execute comprehensive validation of all Bronze tables"""
        logger.info("Starting Bronze Layer Data Validation")
        logger.info("=" * 60)
        
        validation_results = {
            "count_validations": [],
            "schema_validations": [],
            "sample_validations": [],
            "summary": {}
        }
        
        total_tables = len(self.validation_queries)
        passed_count = 0
        
        for table_name in self.validation_queries.keys():
            logger.info(f"Validating: {table_name}")
            
            # Count validation
            count_result = self.validate_table_count(table_name)
            validation_results["count_validations"].append(count_result)
            
            # Schema validation  
            schema_result = self.validate_table_schema(table_name)
            validation_results["schema_validations"].append(schema_result)
            
            # Sample data validation
            sample_result = self.validate_data_sample(table_name)
            validation_results["sample_validations"].append(sample_result)
            
            # Check if table passed all validations
            table_passed = (
                count_result.get("match", False) and 
                schema_result.get("match", False) and 
                sample_result.get("has_data", False)
            )
            
            if table_passed:
                passed_count += 1
                logger.success(f"{table_name}: ALL VALIDATIONS PASSED")
            else:
                logger.error(f"{table_name}: VALIDATION ISSUES DETECTED")
            
            logger.info(f"   Count: {count_result.get('db_count', 0)} records")
            logger.info(f"   Schema: {schema_result.get('status', 'ERROR')}")
            logger.info(f"   Data: {sample_result.get('status', 'ERROR')}")
            logger.info("-" * 40)
        
        # Summary
        validation_results["summary"] = {
            "total_tables": total_tables,
            "passed_tables": passed_count,
            "failed_tables": total_tables - passed_count,
            "success_rate": round((passed_count / total_tables) * 100, 2),
            "overall_status": "ALL PASSED" if passed_count == total_tables else f"{total_tables - passed_count} FAILED"
        }
        
        logger.info("=" * 60)
        logger.info("BRONZE LAYER VALIDATION SUMMARY:")
        logger.info(f"   Tables Validated: {total_tables}")
        logger.info(f"   Passed: {passed_count}")
        logger.info(f"   Failed: {total_tables - passed_count}")
        logger.info(f"   Success Rate: {validation_results['summary']['success_rate']}%")
        logger.info(f"   Overall Status: {validation_results['summary']['overall_status']}")
        
        return validation_results


def main():
    """Execute Bronze layer validation"""
    logger.info("Bronze Layer Data Validation - Enterprise Quality Assurance")
    
    # Test database connectivity
    if not db_connector.test_connection():
        logger.error("Database connection failed - cannot proceed with validation")
        sys.exit(1)
    
    # Run validation
    validator = QualityCheckBronze()
    results = validator.run_full_validation()
    
    # Exit with appropriate code
    if results["summary"]["failed_tables"] == 0:
        logger.success("🎉 All Bronze layer validations passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some Bronze layer validations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
