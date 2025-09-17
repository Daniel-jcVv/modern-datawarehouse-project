#!/usr/bin/env python3
"""
Gold Layer Pipeline Orchestrator
Manages the complete Silver to Gold ETL transformation process
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger


class GoldPipeline:
    """Orchestrates the complete Gold layer ETL process"""
    
    def __init__(self):
        """Initialize pipeline components"""
        self.connector = db_connector
        self.start_time = None
    
    def create_gold_views(self) -> bool:
        """Create Gold layer views (Star Schema)"""
        try:
            logger.info("Verifying Gold layer views...")
            
            # First check if views already exist
            views_query = """
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = 'gold'
            ORDER BY TABLE_NAME
            """
            
            existing_views = self.connector.execute_query(views_query)
            
            if existing_views and len(existing_views) >= 3:
                logger.info(f"Gold views already exist ({len(existing_views)} views found):")
                for schema, view in existing_views:
                    logger.info(f"  - {schema}.{view}")
                return True
            
            # If views don't exist, create them
            logger.info("Creating Gold layer views...")
            views_script_path = project_root / "sql" / "views" / "gold_views.sql"
            
            if not views_script_path.exists():
                logger.error(f"Gold views script not found at: {views_script_path}")
                return False
            
            # Execute views script
            logger.info(f"Executing Gold views from: {views_script_path}")
            success = self.connector.execute_script(str(views_script_path))
            
            if success:
                logger.success("Gold layer views created successfully!")
                
                # Verify views were created
                views = self.connector.execute_query(views_query)
                logger.info(f"Created {len(views)} Gold views:")
                for schema, view in views:
                    logger.info(f"  - {schema}.{view}")
                    
                return True
            else:
                logger.error("Failed to create Gold views")
                return False
                
        except Exception as e:
            logger.error(f"Error with Gold views: {str(e)}")
            return False
    
    def validate_gold_data(self) -> bool:
        """Validate Gold layer data"""
        try:
            logger.info("Validating Gold layer data...")
            
            validation_queries = {
                "dim_customers": "SELECT COUNT(*) FROM gold.dim_customers",
                "dim_products": "SELECT COUNT(*) FROM gold.dim_products",
                "fact_sales": "SELECT COUNT(*) FROM gold.fact_sales"
            }
            
            all_valid = True
            total_records = 0
            
            for view_name, query in validation_queries.items():
                result = self.connector.execute_query(query)
                if result:
                    count = result[0][0]
                    total_records += count
                    if count > 0:
                        logger.success(f"  {view_name}: {count:,} records")
                    else:
                        logger.error(f"  {view_name}: No records found")
                        all_valid = False
                else:
                    logger.error(f"  {view_name}: Query failed")
                    all_valid = False
            
            logger.info(f"Total Gold layer records: {total_records:,}")
            return all_valid
            
        except Exception as e:
            logger.error(f"Error validating Gold data: {str(e)}")
            return False
    
    def run_pipeline(self) -> bool:
        """Execute complete Gold layer pipeline"""
        logger.info("=" * 60)
        logger.info("GOLD LAYER ETL PIPELINE (STAR SCHEMA)")
        logger.info("=" * 60)
        self.start_time = time.time()
        
        try:
            # Step 1: Verify Silver layer has data
            if not self._verify_silver_layer():
                logger.error("Silver layer verification failed")
                return False
            
            # Step 2: Create Gold views
            if not self.create_gold_views():
                logger.error("Gold view creation failed")
                return False
            
            # Step 3: Validate Gold data
            if not self.validate_gold_data():
                logger.error("Gold data validation failed")
                return False
            
            # Step 4: Run comprehensive quality checks
            logger.info("Running comprehensive Gold layer quality checks...")
            if not self._run_quality_checks():
                logger.warning("Some quality checks failed, but pipeline continues")
                # Don't fail pipeline for quality check warnings
            
            # Step 5: Print summary
            elapsed = time.time() - self.start_time
            logger.info("=" * 60)
            logger.info("GOLD PIPELINE SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Status: SUCCESS")
            logger.info(f"Duration: {elapsed:.2f} seconds")
            logger.info("Star Schema Components Created:")
            logger.info("  - dim_customers (Customer Dimension)")
            logger.info("  - dim_products (Product Dimension)")
            logger.info("  - fact_sales (Sales Fact Table)")
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return False
    
    def _verify_silver_layer(self) -> bool:
        """Verify Silver layer has data"""
        try:
            query = """
                SELECT COUNT(*) FROM silver.crm_sales_details
                UNION ALL
                SELECT COUNT(*) FROM silver.crm_cust_info
                UNION ALL
                SELECT COUNT(*) FROM silver.crm_prd_info
            """
            
            results = self.connector.execute_query(query)
            total_rows = sum(row[0] for row in results)
            
            if total_rows == 0:
                logger.error("No data found in Silver layer!")
                return False
            
            logger.info(f"Silver layer verified: {total_rows:,} total records")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Silver layer: {str(e)}")
            return False
    
    def _run_quality_checks(self) -> bool:
        """Run comprehensive Gold layer quality checks"""
        try:
            from src.quality_checks.quality_check_gold import QualityCheckGold
            
            # Run Python quality checks
            checker = QualityCheckGold()
            results = checker.run_full_validation()
            
            # Run SQL quality checks
            logger.info("Running SQL-based quality checks...")
            self._run_sql_quality_checks()
            
            # Return True if validation passed
            return results.get("summary", {}).get("validation_passed", False)
            
        except Exception as e:
            logger.error(f"Error running quality checks: {str(e)}")
            return False
    
    def _run_sql_quality_checks(self) -> bool:
        """Execute SQL quality checks and display results"""
        try:
            sql_checks_path = project_root / "sql" / "quality_checks" / "quality_checks_gold.sql"
            
            if not sql_checks_path.exists():
                logger.warning(f"SQL quality checks file not found: {sql_checks_path}")
                return True
            
            logger.info("Executing SQL Quality Checks:")
            logger.info("-" * 50)
            
            # Check 1: Customer key uniqueness
            logger.info("Check 1: Customer Key Uniqueness")
            duplicates_customers = self.connector.execute_query("""
                SELECT customer_key, COUNT(*) AS duplicate_count
                FROM gold.dim_customers
                GROUP BY customer_key
                HAVING COUNT(*) > 1
            """)
            
            if duplicates_customers:
                logger.error(f"Found {len(duplicates_customers)} duplicate customer keys!")
                for row in duplicates_customers:
                    logger.error(f"  Customer Key {row[0]}: {row[1]} duplicates")
            else:
                logger.success("✓ No duplicate customer keys found")
            
            # Check 2: Product key uniqueness  
            logger.info("Check 2: Product Key Uniqueness")
            duplicates_products = self.connector.execute_query("""
                SELECT product_key, COUNT(*) AS duplicate_count
                FROM gold.dim_products
                GROUP BY product_key
                HAVING COUNT(*) > 1
            """)
            
            if duplicates_products:
                logger.error(f"Found {len(duplicates_products)} duplicate product keys!")
                for row in duplicates_products:
                    logger.error(f"  Product Key {row[0]}: {row[1]} duplicates")
            else:
                logger.success("✓ No duplicate product keys found")
            
            # Check 3: Referential integrity
            logger.info("Check 3: Referential Integrity (Orphaned Records)")
            orphaned_records = self.connector.execute_query("""
                SELECT COUNT(*) as orphaned_count
                FROM gold.fact_sales f
                LEFT JOIN gold.dim_customers c ON c.customer_key = f.customer_key
                LEFT JOIN gold.dim_products p ON p.product_key = f.product_key
                WHERE p.product_key IS NULL OR c.customer_key IS NULL
            """)
            
            if orphaned_records and orphaned_records[0][0] > 0:
                orphaned_count = orphaned_records[0][0]
                logger.error(f"Found {orphaned_count} orphaned records in fact_sales!")
            else:
                logger.success("✓ No orphaned records found - referential integrity maintained")
            
            logger.info("-" * 50)
            logger.success("SQL Quality Checks completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running SQL quality checks: {str(e)}")
            return False


def main():
    """Main execution function"""
    pipeline = GoldPipeline()
    
    # Run pipeline
    success = pipeline.run_pipeline()
    
    if success:
        logger.success("Gold pipeline completed successfully!")
        logger.info("\n⭐ Star Schema is ready for analytics and reporting!")
    else:
        logger.error("💥 Gold pipeline failed!")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
