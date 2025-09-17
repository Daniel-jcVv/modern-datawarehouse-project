#!/usr/bin/env python3
"""
Gold Layer Quality Checks - Enterprise Data Validation
Validates Gold layer views (Star Schema) for business intelligence readiness
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger


class QualityCheckGold:
    """Quality validation for Gold layer views and star schema"""
    
    def __init__(self):
        """Initialize Gold quality checker"""
        self.connector = db_connector
        self.gold_views = [
            "gold.dim_customers",
            "gold.dim_products", 
            "gold.fact_sales"
        ]
        
    def check_view_exists(self, view_name: str) -> Dict[str, Any]:
        """Check if Gold view exists"""
        try:
            schema, view = view_name.split('.')
            query = """
            SELECT COUNT(*) as view_count
            FROM INFORMATION_SCHEMA.VIEWS 
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            """
            
            result = self.connector.execute_query(f"""
            SELECT COUNT(*) as view_count
            FROM INFORMATION_SCHEMA.VIEWS 
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{view}'
            """)
            exists = result[0][0] > 0 if result else False
            
            return {
                "view": view_name,
                "exists": exists,
                "status": "PASS" if exists else "FAIL"
            }
            
        except Exception as e:
            return {
                "view": view_name,
                "exists": False,
                "status": "ERROR",
                "error": str(e)
            }
    
    def check_view_data_count(self, view_name: str) -> Dict[str, Any]:
        """Validate view has data"""
        try:
            query = f"SELECT COUNT(*) FROM {view_name}"
            result = self.connector.execute_query(query)
            count = result[0][0] if result else 0
            
            return {
                "view": view_name,
                "record_count": count,
                "has_data": count > 0,
                "status": "PASS" if count > 0 else "FAIL"
            }
            
        except Exception as e:
            return {
                "view": view_name,
                "record_count": 0,
                "has_data": False,
                "status": "ERROR",
                "error": str(e)
            }
    
    def check_star_schema_integrity(self) -> Dict[str, Any]:
        """Validate star schema relationships"""
        try:
            # Check that fact table can join to dimensions
            integrity_query = """
            SELECT COUNT(*) as total_sales,
                   COUNT(pr.product_key) as with_product,
                   COUNT(cu.customer_key) as with_customer
            FROM gold.fact_sales fs
            LEFT JOIN gold.dim_products pr ON fs.product_key = pr.product_key
            LEFT JOIN gold.dim_customers cu ON fs.customer_key = cu.customer_key
            """
            
            result = self.connector.execute_query(integrity_query)
            if result:
                total, with_product, with_customer = result[0]
                
                product_integrity = (with_product / total * 100) if total > 0 else 0
                customer_integrity = (with_customer / total * 100) if total > 0 else 0
                
                return {
                    "total_sales_records": total,
                    "product_match_rate": round(product_integrity, 2),
                    "customer_match_rate": round(customer_integrity, 2),
                    "integrity_passed": product_integrity >= 95 and customer_integrity >= 95,
                    "status": "PASS" if (product_integrity >= 95 and customer_integrity >= 95) else "FAIL"
                }
            else:
                return {"status": "ERROR", "error": "No results returned"}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def check_dimension_uniqueness(self) -> Dict[str, Any]:
        """Validate dimension table uniqueness"""
        results = {}
        
        dimension_checks = [
            ("gold.dim_customers", "customer_key"),
            ("gold.dim_products", "product_key")
        ]
        
        for view_name, key_column in dimension_checks:
            try:
                query = f"""
                SELECT COUNT(*) as total_records,
                       COUNT(DISTINCT {key_column}) as unique_keys
                FROM {view_name}
                """
                
                result = self.connector.execute_query(query)
                if result:
                    total, unique = result[0]
                    is_unique = total == unique
                    
                    results[view_name] = {
                        "total_records": total,
                        "unique_keys": unique,
                        "is_unique": is_unique,
                        "status": "PASS" if is_unique else "FAIL"
                    }
                else:
                    results[view_name] = {"status": "ERROR", "error": "No results"}
                    
            except Exception as e:
                results[view_name] = {"status": "ERROR", "error": str(e)}
        
        return results
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Execute comprehensive Gold layer validation"""
        logger.info("Starting Gold Layer Quality Validation")
        logger.info("=" * 60)
        
        start_time = time.time()
        validation_results = {
            "view_existence": {},
            "view_data_counts": {},
            "star_schema_integrity": {},
            "dimension_uniqueness": {},
            "summary": {}
        }
        
        # 1. Check view existence
        logger.info("Step 1: Validating view existence")
        for view in self.gold_views:
            result = self.check_view_exists(view)
            validation_results["view_existence"][view] = result
            
            if result["status"] == "PASS":
                logger.success(f"{view}: EXISTS")
            else:
                logger.error(f"{view}: MISSING or ERROR")
        
        # 2. Check view data counts
        logger.info("Step 2: Validating view data counts")
        for view in self.gold_views:
            if validation_results["view_existence"][view]["status"] == "PASS":
                result = self.check_view_data_count(view)
                validation_results["view_data_counts"][view] = result
                
                if result["status"] == "PASS":
                    logger.success(f"{view}: {result['record_count']:,} records")
                else:
                    logger.error(f"{view}: NO DATA")
            else:
                validation_results["view_data_counts"][view] = {"status": "SKIPPED", "reason": "View does not exist"}
        
        # 3. Check star schema integrity
        logger.info("Step 3: Validating star schema integrity")
        integrity_result = self.check_star_schema_integrity()
        validation_results["star_schema_integrity"] = integrity_result
        
        if integrity_result.get("status") == "PASS":
            logger.success(f"Star Schema Integrity: PASS")
            logger.info(f"  Product match rate: {integrity_result.get('product_match_rate', 0)}%")
            logger.info(f"  Customer match rate: {integrity_result.get('customer_match_rate', 0)}%")
        else:
            logger.error("Star Schema Integrity: FAIL")
        
        # 4. Check dimension uniqueness
        logger.info("Step 4: Validating dimension uniqueness")
        uniqueness_results = self.check_dimension_uniqueness()
        validation_results["dimension_uniqueness"] = uniqueness_results
        
        for view, result in uniqueness_results.items():
            if result.get("status") == "PASS":
                logger.success(f"{view}: UNIQUE KEYS")
            else:
                logger.error(f"{view}: DUPLICATE KEYS DETECTED")
        
        # Generate summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        # Count passed/failed checks
        total_checks = 0
        passed_checks = 0
        
        for category in ["view_existence", "view_data_counts", "dimension_uniqueness"]:
            for view, result in validation_results[category].items():
                if result.get("status") != "SKIPPED":
                    total_checks += 1
                    if result.get("status") == "PASS":
                        passed_checks += 1
        
        # Add star schema check
        if validation_results["star_schema_integrity"].get("status") != "SKIPPED":
            total_checks += 1
            if validation_results["star_schema_integrity"].get("status") == "PASS":
                passed_checks += 1
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        validation_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": round(success_rate, 2),
            "duration_seconds": duration,
            "validation_passed": success_rate >= 95,
            "overall_status": "ALL PASSED" if success_rate >= 95 else f"{total_checks - passed_checks} CHECKS FAILED"
        }
        
        logger.info("=" * 60)
        logger.info("GOLD LAYER VALIDATION SUMMARY:")
        logger.info(f"  Total Checks: {total_checks}")
        logger.info(f"  Passed: {passed_checks}")
        logger.info(f"  Failed: {total_checks - passed_checks}")
        logger.info(f"  Success Rate: {success_rate}%")
        logger.info(f"  Duration: {duration} seconds")
        logger.info("=" * 60)
        
        if success_rate >= 95:
            logger.success("Gold layer quality validation PASSED")
        else:
            logger.error("Gold layer quality validation FAILED")
        
        return validation_results


def main():
    """Execute Gold layer quality checks"""
    logger.info("GOLD LAYER QUALITY VALIDATION")
    logger.info("Validating Star Schema and Business Intelligence readiness")
    
    # Check database connectivity
    if not db_connector.test_connection():
        logger.error("Database connection failed - cannot proceed with validation")
        sys.exit(1)
    
    # Run Gold quality checks
    checker = QualityCheckGold()
    results = checker.run_full_validation()
    
    if results["summary"]["validation_passed"]:
        logger.success("All Gold layer quality checks passed!")
        sys.exit(0)
    else:
        logger.error("Gold layer quality validation completed with issues")
        sys.exit(1)


if __name__ == "__main__":
    main()