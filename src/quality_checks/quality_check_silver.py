#!/usr/bin/env python3
"""
Silver Layer Quality Check - Enterprise Data Quality Framework
Implements comprehensive quality checks for transformed data integrity
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger
import pandas as pd
from src.config import QUALITY_THRESHOLDS, ALERT_CONFIG, DASHBOARD_CONFIG


class QualityCheckSilver:
    """Enterprise data quality validation for Silver layer tables"""
    
    def __init__(self):
        """Initialize quality check configurations for all Silver tables"""
        self.quality_checks = self._initialize_quality_checks()
        self.validation_results = []
        
    def _initialize_quality_checks(self) -> Dict[str, Dict[str, Any]]:
        """Define all quality check queries and expected values"""
        return {
            "silver.crm_cust_info": {
                "primary_key_check": """
                    SELECT cst_id, COUNT(*) as count
                    FROM silver.crm_cust_info
                    GROUP BY cst_id
                    HAVING COUNT(*) > 1 OR cst_id IS NULL
                """,
                "trimmed_data_check": """
                    SELECT cst_key 
                    FROM silver.crm_cust_info
                    WHERE cst_key != TRIM(cst_key)
                """,
                "standardization_check": """
                    SELECT DISTINCT cst_marital_status 
                    FROM silver.crm_cust_info
                """,
                "expected_values": {
                    "cst_marital_status": ["S", "M", "D", "W", None]
                }
            },
            "silver.crm_prd_info": {
                "primary_key_check": """
                    SELECT prd_id, COUNT(*) as count
                    FROM silver.crm_prd_info
                    GROUP BY prd_id
                    HAVING COUNT(*) > 1 OR prd_id IS NULL
                """,
                "trimmed_data_check": """
                    SELECT prd_nm 
                    FROM silver.crm_prd_info
                    WHERE prd_nm != TRIM(prd_nm)
                """,
                "cost_validation": """
                    SELECT prd_id, prd_cost 
                    FROM silver.crm_prd_info
                    WHERE prd_cost < 0 OR prd_cost IS NULL
                """,
                "date_order_check": """
                    SELECT prd_id, prd_start_dt, prd_end_dt 
                    FROM silver.crm_prd_info
                    WHERE prd_end_dt < prd_start_dt
                """,
                "standardization_check": """
                    SELECT DISTINCT prd_line 
                    FROM silver.crm_prd_info
                """
            },
            "silver.crm_sales_details": {
                "primary_key_check": """
                    SELECT sls_ord_num, COUNT(*) as count
                    FROM silver.crm_sales_details
                    GROUP BY sls_ord_num
                    HAVING COUNT(*) > 1 OR sls_ord_num IS NULL
                """,
                "date_order_check": """
                    SELECT sls_ord_num, sls_order_dt, sls_ship_dt, sls_due_dt
                    FROM silver.crm_sales_details
                    WHERE sls_order_dt > sls_ship_dt 
                       OR sls_order_dt > sls_due_dt
                """,
                "data_consistency_check": """
                    SELECT sls_ord_num, sls_sales, sls_quantity, sls_price 
                    FROM silver.crm_sales_details
                    WHERE ABS(sls_sales - (sls_quantity * sls_price)) > 0.01
                       OR sls_sales IS NULL 
                       OR sls_quantity IS NULL 
                       OR sls_price IS NULL
                       OR sls_sales <= 0 
                       OR sls_quantity <= 0 
                       OR sls_price <= 0
                """
            },
            "silver.erp_cust_az12": {
                "primary_key_check": """
                    SELECT cid, COUNT(*) as count
                    FROM silver.erp_cust_az12
                    GROUP BY cid
                    HAVING COUNT(*) > 1 OR cid IS NULL
                """,
                "date_range_check": """
                    SELECT cid, bdate 
                    FROM silver.erp_cust_az12
                    WHERE bdate < '1924-01-01' 
                       OR bdate > GETDATE()
                """,
                "standardization_check": """
                    SELECT DISTINCT gen 
                    FROM silver.erp_cust_az12
                """,
                "expected_values": {
                    "gen": ["M", "F", None]
                }
            },
            "silver.erp_loc_a101": {
                "primary_key_check": """
                    SELECT cid, COUNT(*) as count
                    FROM silver.erp_loc_a101
                    GROUP BY cid
                    HAVING COUNT(*) > 1 OR cid IS NULL
                """,
                "standardization_check": """
                    SELECT DISTINCT cntry 
                    FROM silver.erp_loc_a101
                    ORDER BY cntry
                """
            },
            "silver.erp_px_cat_g1v2": {
                "primary_key_check": """
                    SELECT id, COUNT(*) as count
                    FROM silver.erp_px_cat_g1v2
                    GROUP BY id
                    HAVING COUNT(*) > 1 OR id IS NULL
                """,
                "trimmed_data_check": """
                    SELECT id, cat, subcat, maintenance
                    FROM silver.erp_px_cat_g1v2
                    WHERE cat != TRIM(cat) 
                       OR subcat != TRIM(subcat) 
                       OR maintenance != TRIM(maintenance)
                """,
                "standardization_check": """
                    SELECT DISTINCT maintenance 
                    FROM silver.erp_px_cat_g1v2
                """,
                "expected_values": {
                    "maintenance": ["Low", "Medium", "High", None]
                }
            }
        }
    
    def validate_primary_keys(self, table_name: str) -> Dict[str, Any]:
        """Validate primary key integrity - no nulls or duplicates"""
        try:
            config = self.quality_checks.get(table_name)
            if not config or "primary_key_check" not in config:
                return {"status": "SKIPPED", "message": "No primary key check defined"}
            
            results = db_connector.execute_query(config["primary_key_check"])
            
            if not results:
                return {
                    "check_type": "PRIMARY_KEY",
                    "table": table_name,
                    "status": "PASS",
                    "issues_found": 0,
                    "message": "No duplicate or null primary keys found"
                }
            else:
                return {
                    "check_type": "PRIMARY_KEY",
                    "table": table_name,
                    "status": "FAIL",
                    "issues_found": len(results),
                    "message": f"Found {len(results)} primary key violations",
                    "sample_issues": results[:5]
                }
                
        except Exception as e:
            logger.error(f"Primary key validation failed for {table_name}: {str(e)}")
            return {
                "check_type": "PRIMARY_KEY",
                "table": table_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def validate_data_trimming(self, table_name: str) -> Dict[str, Any]:
        """Validate all string fields are properly trimmed"""
        try:
            config = self.quality_checks.get(table_name)
            if not config or "trimmed_data_check" not in config:
                return {"status": "SKIPPED", "message": "No trim check defined"}
            
            results = db_connector.execute_query(config["trimmed_data_check"])
            
            if not results:
                return {
                    "check_type": "DATA_TRIMMING",
                    "table": table_name,
                    "status": "PASS",
                    "issues_found": 0,
                    "message": "All string fields are properly trimmed"
                }
            else:
                return {
                    "check_type": "DATA_TRIMMING",
                    "table": table_name,
                    "status": "FAIL",
                    "issues_found": len(results),
                    "message": f"Found {len(results)} untrimmed values",
                    "sample_issues": results[:5]
                }
                
        except Exception as e:
            logger.error(f"Data trimming validation failed for {table_name}: {str(e)}")
            return {
                "check_type": "DATA_TRIMMING",
                "table": table_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def validate_data_ranges(self, table_name: str) -> Dict[str, Any]:
        """Validate numeric and date ranges are within expected bounds"""
        try:
            config = self.quality_checks.get(table_name)
            validation_results = []
            
            # Check for cost validation
            if "cost_validation" in config:
                results = db_connector.execute_query(config["cost_validation"])
                if results:
                    validation_results.append({
                        "type": "cost_validation",
                        "issues": len(results),
                        "message": f"Found {len(results)} invalid cost values"
                    })
            
            # Check for date order
            if "date_order_check" in config:
                results = db_connector.execute_query(config["date_order_check"])
                if results:
                    validation_results.append({
                        "type": "date_order",
                        "issues": len(results),
                        "message": f"Found {len(results)} invalid date orders"
                    })
            
            # Check for date ranges
            if "date_range_check" in config:
                results = db_connector.execute_query(config["date_range_check"])
                if results:
                    validation_results.append({
                        "type": "date_range",
                        "issues": len(results),
                        "message": f"Found {len(results)} dates out of range"
                    })
            
            total_issues = sum(v["issues"] for v in validation_results)
            
            return {
                "check_type": "DATA_RANGES",
                "table": table_name,
                "status": "PASS" if total_issues == 0 else "FAIL",
                "issues_found": total_issues,
                "validations": validation_results,
                "message": "All data ranges valid" if total_issues == 0 else f"Found {total_issues} range violations"
            }
            
        except Exception as e:
            logger.error(f"Data range validation failed for {table_name}: {str(e)}")
            return {
                "check_type": "DATA_RANGES",
                "table": table_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def validate_data_consistency(self, table_name: str) -> Dict[str, Any]:
        """Validate business logic consistency"""
        try:
            config = self.quality_checks.get(table_name)
            if not config or "data_consistency_check" not in config:
                return {"status": "SKIPPED", "message": "No consistency check defined"}
            
            results = db_connector.execute_query(config["data_consistency_check"])
            
            if not results:
                return {
                    "check_type": "DATA_CONSISTENCY",
                    "table": table_name,
                    "status": "PASS",
                    "issues_found": 0,
                    "message": "All data consistency checks passed"
                }
            else:
                return {
                    "check_type": "DATA_CONSISTENCY",
                    "table": table_name,
                    "status": "FAIL",
                    "issues_found": len(results),
                    "message": f"Found {len(results)} consistency violations",
                    "sample_issues": results[:5]
                }
                
        except Exception as e:
            logger.error(f"Data consistency validation failed for {table_name}: {str(e)}")
            return {
                "check_type": "DATA_CONSISTENCY",
                "table": table_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def validate_standardization(self, table_name: str) -> Dict[str, Any]:
        """Validate data standardization and expected values"""
        try:
            config = self.quality_checks.get(table_name)
            if not config or "standardization_check" not in config:
                return {"status": "SKIPPED", "message": "No standardization check defined"}
            
            results = db_connector.execute_query(config["standardization_check"])
            actual_values = [row[0] for row in results]
            
            # Check against expected values if defined
            if "expected_values" in config:
                validation_results = {}
                for field, expected in config["expected_values"].items():
                    unexpected = set(actual_values) - set(expected)
                    validation_results[field] = {
                        "expected": expected,
                        "actual": actual_values,
                        "unexpected": list(unexpected),
                        "valid": len(unexpected) == 0
                    }
                
                all_valid = all(v["valid"] for v in validation_results.values())
                
                return {
                    "check_type": "STANDARDIZATION",
                    "table": table_name,
                    "status": "PASS" if all_valid else "FAIL",
                    "validations": validation_results,
                    "message": "All values standardized" if all_valid else "Found non-standard values"
                }
            else:
                return {
                    "check_type": "STANDARDIZATION",
                    "table": table_name,
                    "status": "INFO",
                    "distinct_values": actual_values,
                    "message": f"Found {len(actual_values)} distinct values"
                }
                
        except Exception as e:
            logger.error(f"Standardization validation failed for {table_name}: {str(e)}")
            return {
                "check_type": "STANDARDIZATION",
                "table": table_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    def run_table_validation(self, table_name: str) -> Dict[str, Any]:
        """Run all quality checks for a specific table"""
        logger.info(f"Running quality checks for: {table_name}")
        
        table_results = {
            "table": table_name,
            "checks": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0}
        }
        
        # Run all validation checks
        checks = [
            ("Primary Keys", self.validate_primary_keys),
            ("Data Trimming", self.validate_data_trimming),
            ("Data Ranges", self.validate_data_ranges),
            ("Data Consistency", self.validate_data_consistency),
            ("Standardization", self.validate_standardization)
        ]
        
        for check_name, check_function in checks:
            result = check_function(table_name)
            table_results["checks"].append(result)
            
            # Update summary
            if result.get("status") == "PASS":
                table_results["summary"]["passed"] += 1
            elif result.get("status") == "FAIL":
                table_results["summary"]["failed"] += 1
            elif result.get("status") == "ERROR":
                table_results["summary"]["errors"] += 1
        
        # Overall status
        if table_results["summary"]["failed"] > 0 or table_results["summary"]["errors"] > 0:
            table_results["overall_status"] = "FAIL"
        else:
            table_results["overall_status"] = "PASS"
        
        return table_results
    
    def _send_alert(self, alert_type: str, message: str, details: Dict[str, Any]) -> None:
        """Send quality alerts based on configuration"""
        if not ALERT_CONFIG["enabled"]:
            return
        
        # Log file alert
        if ALERT_CONFIG["channels"]["log_file"]["enabled"]:
            alert_log_path = project_root / ALERT_CONFIG["channels"]["log_file"]["path"]
            alert_log_path.parent.mkdir(exist_ok=True)
            
            with open(alert_log_path, "a") as f:
                alert_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": alert_type,
                    "message": message,
                    "details": details
                }
                f.write(json.dumps(alert_entry) + "\n")
        
        # Console alert
        if ALERT_CONFIG["channels"]["console"]["enabled"]:
            if alert_type == "CRITICAL":
                logger.error(f"CRITICAL ALERT: {message}")
            elif alert_type == "HIGH":
                logger.warning(f"HIGH ALERT: {message}")
            else:
                logger.info(f"ALERT: {message}")
    
    def _save_dashboard_metrics(self, results: Dict[str, Any]) -> None:
        """Save metrics for dashboard visualization"""
        if not DASHBOARD_CONFIG["enabled"]:
            return
        
        metrics_path = project_root / DASHBOARD_CONFIG["export"]["path"]
        metrics_path.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now()
        filename = DASHBOARD_CONFIG["export"]["filename_pattern"].format(
            date=timestamp.strftime("%Y%m%d"),
            time=timestamp.strftime("%H%M%S")
        )
        
        # Prepare dashboard metrics
        dashboard_data = {
            "timestamp": timestamp.isoformat(),
            "summary": results["summary"],
            "table_health": [],
            "check_performance": [],
            "top_issues": []
        }
        
        # Extract table health metrics
        for table_result in results["tables"]:
            table_health = {
                "table": table_result["table"],
                "status": table_result["overall_status"],
                "checks_passed": table_result["summary"]["passed"],
                "checks_failed": table_result["summary"]["failed"],
                "health_score": round(
                    (table_result["summary"]["passed"] / len(table_result["checks"])) * 100, 2
                )
            }
            dashboard_data["table_health"].append(table_health)
            
            # Collect top issues
            for check in table_result["checks"]:
                if check.get("status") == "FAIL":
                    issue = {
                        "table": table_result["table"],
                        "check_type": check.get("check_type", "Unknown"),
                        "issues_found": check.get("issues_found", 0),
                        "message": check.get("message", "")
                    }
                    dashboard_data["top_issues"].append(issue)
        
        # Sort top issues by count
        dashboard_data["top_issues"] = sorted(
            dashboard_data["top_issues"], 
            key=lambda x: x["issues_found"], 
            reverse=True
        )[:DASHBOARD_CONFIG["metrics"]["table_health"]["show_top_issues"]]
        
        # Save metrics
        with open(metrics_path / filename, "w") as f:
            json.dump(dashboard_data, f, indent=2)
        
        logger.info(f"Dashboard metrics saved to: {metrics_path / filename}")
    
    def _check_thresholds(self, results: Dict[str, Any]) -> bool:
        """Check if quality thresholds are met and trigger alerts"""
        all_passed = True
        
        # Check overall thresholds
        table_success_rate = results["summary"]["table_success_rate"]
        check_success_rate = results["summary"]["check_success_rate"]
        
        if table_success_rate < QUALITY_THRESHOLDS["overall"]["min_table_success_rate"]:
            self._send_alert(
                "HIGH",
                f"Table success rate ({table_success_rate}%) below threshold ({QUALITY_THRESHOLDS['overall']['min_table_success_rate']}%)",
                {"metric": "table_success_rate", "value": table_success_rate}
            )
            all_passed = False
        
        if check_success_rate < QUALITY_THRESHOLDS["overall"]["min_check_success_rate"]:
            self._send_alert(
                "HIGH",
                f"Check success rate ({check_success_rate}%) below threshold ({QUALITY_THRESHOLDS['overall']['min_check_success_rate']}%)",
                {"metric": "check_success_rate", "value": check_success_rate}
            )
            all_passed = False
        
        # Check table-specific thresholds
        for table_result in results["tables"]:
            table_name = table_result["table"]
            table_config = QUALITY_THRESHOLDS["table_specific"].get(table_name, {})
            
            if table_config:
                # Check critical checks
                for check in table_result["checks"]:
                    check_type = check.get("check_type", "")
                    if check_type in table_config.get("critical_checks", []):
                        if check.get("status") == "FAIL":
                            self._send_alert(
                                "CRITICAL",
                                f"Critical check '{check_type}' failed for table {table_name}",
                                {
                                    "table": table_name,
                                    "check_type": check_type,
                                    "issues": check.get("issues_found", 0)
                                }
                            )
                            all_passed = False
        
        return all_passed
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Execute comprehensive quality checks for all Silver tables"""
        logger.info("Starting Silver Layer Data Quality Checks")
        logger.info("=" * 60)
        
        validation_results = {
            "tables": [],
            "summary": {
                "total_tables": len(self.quality_checks),
                "passed_tables": 0,
                "failed_tables": 0,
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "error_checks": 0
            }
        }
        
        # Validate each table
        for table_name in self.quality_checks.keys():
            table_result = self.run_table_validation(table_name)
            validation_results["tables"].append(table_result)
            
            # Update summary
            if table_result["overall_status"] == "PASS":
                validation_results["summary"]["passed_tables"] += 1
                logger.success(f"{table_name}: ALL QUALITY CHECKS PASSED")
            else:
                validation_results["summary"]["failed_tables"] += 1
                logger.error(f"{table_name}: QUALITY ISSUES DETECTED")
            
            # Aggregate check counts
            validation_results["summary"]["total_checks"] += len(table_result["checks"])
            validation_results["summary"]["passed_checks"] += table_result["summary"]["passed"]
            validation_results["summary"]["failed_checks"] += table_result["summary"]["failed"]
            validation_results["summary"]["error_checks"] += table_result["summary"]["errors"]
            
            logger.info(f"   Checks Passed: {table_result['summary']['passed']}")
            logger.info(f"   Checks Failed: {table_result['summary']['failed']}")
            logger.info(f"   Checks Errored: {table_result['summary']['errors']}")
            logger.info("-" * 40)
        
        # Calculate success rates
        validation_results["summary"]["table_success_rate"] = round(
            (validation_results["summary"]["passed_tables"] / validation_results["summary"]["total_tables"]) * 100, 2
        )
        validation_results["summary"]["check_success_rate"] = round(
            (validation_results["summary"]["passed_checks"] / validation_results["summary"]["total_checks"]) * 100, 2
        )
        
        # Overall status
        if validation_results["summary"]["failed_tables"] == 0:
            validation_results["summary"]["overall_status"] = "ALL PASSED"
        else:
            validation_results["summary"]["overall_status"] = f"{validation_results['summary']['failed_tables']} TABLES FAILED"
        
        # Print summary
        logger.info("=" * 60)
        logger.info("SILVER LAYER QUALITY CHECK SUMMARY:")
        logger.info(f"   Tables Validated: {validation_results['summary']['total_tables']}")
        logger.info(f"   Tables Passed: {validation_results['summary']['passed_tables']}")
        logger.info(f"   Tables Failed: {validation_results['summary']['failed_tables']}")
        logger.info(f"   Table Success Rate: {validation_results['summary']['table_success_rate']}%")
        logger.info(f"   Total Quality Checks: {validation_results['summary']['total_checks']}")
        logger.info(f"   Checks Passed: {validation_results['summary']['passed_checks']}")
        logger.info(f"   Checks Failed: {validation_results['summary']['failed_checks']}")
        logger.info(f"   Check Success Rate: {validation_results['summary']['check_success_rate']}%")
        logger.info(f"   Overall Status: {validation_results['summary']['overall_status']}")
        
        # Check thresholds and send alerts
        thresholds_met = self._check_thresholds(validation_results)
        
        # Save dashboard metrics
        self._save_dashboard_metrics(validation_results)
        
        # Update overall status based on thresholds
        if not thresholds_met:
            validation_results["summary"]["thresholds_met"] = False
            logger.warning("Quality thresholds not met - alerts have been triggered")
        else:
            validation_results["summary"]["thresholds_met"] = True
        
        return validation_results
    
    def generate_quality_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed quality report"""
        report_lines = [
            "Silver Layer Data Quality Report",
            "=" * 50,
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 20,
            f"Total Tables Analyzed: {results['summary']['total_tables']}",
            f"Tables Passed: {results['summary']['passed_tables']}",
            f"Tables Failed: {results['summary']['failed_tables']}",
            f"Overall Success Rate: {results['summary']['table_success_rate']}%",
            "",
            "DETAILED FINDINGS",
            "-" * 20
        ]
        
        for table_result in results["tables"]:
            report_lines.extend([
                "",
                f"Table: {table_result['table']}",
                f"Status: {table_result['overall_status']}",
                "Quality Checks:"
            ])
            
            for check in table_result["checks"]:
                if check.get("status") == "SKIPPED":
                    continue
                    
                status_icon = "✓" if check.get("status") == "PASS" else "✗"
                report_lines.append(f"  {status_icon} {check.get('check_type', 'Unknown')}: {check.get('message', 'No message')}")
                
                if check.get("status") == "FAIL" and "issues_found" in check:
                    report_lines.append(f"    Issues Found: {check['issues_found']}")
        
        report_lines.extend([
            "",
            "=" * 50,
            "End of Report"
        ])
        
        return "\n".join(report_lines)


def main():
    """Execute Silver layer quality checks"""
    logger.info("Silver Layer Data Quality Validation - Enterprise Framework")
    
    # Test database connectivity
    if not db_connector.test_connection():
        logger.error("Database connection failed - cannot proceed with quality checks")
        sys.exit(1)
    
    # Run validation
    validator = QualityCheckSilver()
    results = validator.run_full_validation()
    
    # Generate report
    report = validator.generate_quality_report(results)
    
    # Save report to file
    report_path = project_root / "logs" / f"silver_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write(report)
    
    logger.info(f"Quality report saved to: {report_path}")
    
    # Exit with appropriate code
    if results["summary"]["failed_tables"] == 0:
        logger.success("All Silver layer quality checks passed!")
        sys.exit(0)
    else:
        logger.error(f"💥 {results['summary']['failed_tables']} tables failed quality checks!")
        sys.exit(1)


if __name__ == "__main__":
    main()
