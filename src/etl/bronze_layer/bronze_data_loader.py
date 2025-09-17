#!/usr/bin/env python3
"""
Bronze Data Loader - Enterprise ETL Engine
Type-safe data loading with comprehensive validation and logging
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

import pandas as pd
import pyodbc
import numpy as np
from src.connectors.sql_server import db_connector
from loguru import logger
import time

class BronzeETLTypeSafe:
    """Type-safe ETL engine that preserves data integrity while ensuring SQL Server compatibility"""
    
    def __init__(self):
        # Use absolute path from project root
        project_root = Path(__file__).parent.parent.parent.parent
        self.data_path = project_root / "data_sets"
        self.batch_size = 5000  # Optimized batch size for performance
        
        # Table mappings with explicit column definitions
        self.table_configs = {
            "source_crm/cust_info.csv": {
                "table": "bronze.crm_cust_info",
                "columns": ["cst_id", "cst_key", "cst_firstname", "cst_lastname", 
                           "cst_marital_status", "cst_gndr", "cst_create_date"]
            },
            "source_crm/prd_info.csv": {
                "table": "bronze.crm_prd_info",
                "columns": ["prd_id", "prd_key", "prd_nm", "prd_cost", 
                           "prd_line", "prd_start_dt", "prd_end_dt"]
            },
            "source_crm/sales_details.csv": {
                "table": "bronze.crm_sales_details",
                "columns": ["sls_ord_num", "sls_prd_key", "sls_cust_id", "sls_order_dt",
                           "sls_ship_dt", "sls_due_dt", "sls_sales", "sls_quantity", "sls_price"]
            },
            "source_erp/CUST_AZ12.csv": {
                "table": "bronze.erp_cust_az12",
                "columns": ["cid", "bdate", "gen"]
            },
            "source_erp/LOC_A101.csv": {
                "table": "bronze.erp_loc_a101",
                "columns": ["cid", "cntry"]
            },
            "source_erp/PX_CAT_G1V2.csv": {
                "table": "bronze.erp_px_cat_g1v2",
                "columns": ["id", "cat", "subcat", "maintenance"]
            }
        }
    
    def clean_value_for_sql_server(self, value):
        """
        Convert Python values to SQL Server compatible types while preserving original data.
        This function handles the type mapping without transforming the actual values.
        """
        # Handle pandas NA values and numpy NaN
        if pd.isna(value) or value is None:
            return None
        
        # Handle empty strings - convert to NULL for SQL Server compatibility
        # This is critical for numeric columns that can't accept empty strings
        if isinstance(value, str) and value.strip() == '':
            return None  # Convert empty strings to NULL for SQL Server
        
        # Handle numpy types that PyODBC doesn't recognize
        if isinstance(value, (np.integer, np.int64, np.int32)):
            return int(value)
        
        if isinstance(value, (np.floating, np.float64, np.float32)):
            # Only convert to float if it's actually a number, not NaN
            if pd.isna(value):
                return None
            return float(value)
        
        # Handle string types - ensure they're proper Python strings
        if isinstance(value, (str, np.str_)):
            return str(value)
        
        # For any other type, convert to string to preserve the original value
        return str(value)
    
    def prepare_dataframe_for_sql_server(self, df):
        """
        Prepare DataFrame by cleaning values while preserving original data integrity.
        This ensures PyODBC can handle the data types without transforming the actual values.
        """
        # Create a copy to avoid modifying the original DataFrame
        df_cleaned = df.copy()
        
        # Apply type cleaning to each value in the DataFrame
        for column in df_cleaned.columns:
            df_cleaned[column] = df_cleaned[column].apply(self.clean_value_for_sql_server)
        
        return df_cleaned
    
    def get_bulk_insert_sql(self, table_name: str, columns: list) -> str:
        """Generate optimized bulk insert SQL with parameterized queries"""
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        
        return f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    def truncate_table(self, cursor, table_name: str) -> bool:
        """Execute TRUNCATE using native SQL for maximum performance"""
        try:
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            logger.info(f"   Table truncated: {table_name}")
            return True
        except pyodbc.Error as e:
            logger.error(f"Failed to truncate {table_name}: {str(e)}")
            return False
    
    def bulk_insert_batch(self, cursor, insert_sql: str, batch_data: list) -> bool:
        """High-performance bulk insert using executemany with proper error handling"""
        try:
            cursor.executemany(insert_sql, batch_data)
            return True
        except pyodbc.Error as e:
            logger.error(f"Batch insert failed: {str(e)}")
            # Log details about the problematic data for debugging
            logger.debug(f"Problematic batch size: {len(batch_data)}")
            if batch_data:
                logger.debug(f"Sample row: {batch_data[0]}")
            return False
    
    def load_file_with_type_safety(self, file_path: str, config: dict) -> bool:
        """Load CSV using type-safe PyODBC operations that preserve original data"""
        try:
            full_path = os.path.join(self.data_path, file_path)
            table_name = config["table"]
            columns = config["columns"]
            
            logger.info(f"Processing: {file_path} -> {table_name}")
            
            # Read CSV data with explicit string type to preserve original values
            df = pd.read_csv(full_path, dtype=str, keep_default_na=False)
            total_rows = len(df)
            logger.info(f"   Total rows: {total_rows}")
            
            # Clean the DataFrame for SQL Server compatibility while preserving values
            df_cleaned = self.prepare_dataframe_for_sql_server(df)
            
            # Convert to list of tuples for bulk insert
            data_tuples = [tuple(row) for row in df_cleaned.values]
            
            # Establish PyODBC connection for bulk operations
            driver = "ODBC Driver 18 for SQL Server"
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={db_connector.host},{db_connector.port};"
                f"DATABASE={db_connector.database};"
                f"UID={db_connector.user};"
                f"PWD={db_connector.password};"
                "TrustServerCertificate=yes;"
                "Encrypt=no;"
                "MARS_Connection=yes;"
            )
            
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                
                # Clear existing data using TRUNCATE for optimal performance
                if not self.truncate_table(cursor, table_name):
                    return False
                
                # Prepare the bulk insert SQL statement
                insert_sql = self.get_bulk_insert_sql(table_name, columns)
                
                # Process data in optimized batches to manage memory and performance
                rows_processed = 0
                batch_count = 0
                
                for i in range(0, total_rows, self.batch_size):
                    batch_data = data_tuples[i:i + self.batch_size]
                    batch_count += 1
                    
                    if self.bulk_insert_batch(cursor, insert_sql, batch_data):
                        rows_processed += len(batch_data)
                        logger.info(f"   Batch {batch_count}: {len(batch_data)} rows processed")
                    else:
                        # Rollback on failure to maintain data consistency
                        conn.rollback()
                        logger.error(f"   Failed on batch {batch_count}")
                        return False
                
                # Commit all successful batches
                conn.commit()
                
                logger.success(f"SUCCESS: {table_name} -> {rows_processed} rows loaded")
                return True
                
        except Exception as e:
            logger.error(f"FAILED: {file_path} -> {str(e)}")
            return False
    
    def run_bronze_etl_with_procedure(self) -> bool:
        """Execute Bronze ETL using stored procedure (enterprise pattern)"""
        try:
            logger.info("Starting Bronze ETL using stored procedure...")
            
            # Import and use the procedure pattern
            from .bronze_procedure import execute_bronze_procedure, get_execution_log_summary
            
            # Execute the stored procedure
            success = execute_bronze_procedure()
            
            if success:
                logger.success("BRONZE LAYER ETL COMPLETED SUCCESSFULLY (Procedure)")
                
                # Show execution summary
                get_execution_log_summary()
                return True
            else:
                logger.error("BRONZE LAYER ETL FAILED (Procedure)")
                return False
                
        except ImportError:
            logger.warning("Bronze procedure not available, falling back to Python ETL")
            return self.run_bronze_etl_python()
        except Exception as e:
            logger.error(f"Procedure execution failed: {e}")
            logger.info("Falling back to Python ETL...")
            return self.run_bronze_etl_python()

    def run_bronze_etl_python(self) -> bool:
        """Execute Bronze ETL using Python (original implementation)"""
        logger.info("Starting Type-Safe Bronze Layer ETL Pipeline (Python)")
        logger.info("=" * 70)
        
        start_time = time.time()
        success_count = 0
        total_files = len(self.table_configs)
        
        for file_path, config in self.table_configs.items():
            if self.load_file_with_type_safety(file_path, config):
                success_count += 1
            else:
                logger.error(f"PIPELINE FAILURE: {file_path}")
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        logger.info("=" * 70)
        logger.info(f"BRONZE ETL PIPELINE RESULTS:")
        logger.info(f"   Successfully processed: {success_count}/{total_files} files")
        logger.info(f"   Total execution time: {duration} seconds")
        logger.info(f"   Average time per file: {round(duration/total_files, 2)} seconds")
        
        if success_count == total_files:
            logger.success("BRONZE LAYER ETL COMPLETED SUCCESSFULLY (Python)")
            return True
        else:
            failed_count = total_files - success_count
            logger.error(f"BRONZE LAYER ETL FAILED: {failed_count} files could not be processed")
            return False

    def run_bronze_etl(self, use_procedure: bool = True) -> bool:
        """
        Execute Bronze ETL pipeline with choice of implementation method
        
        Args:
            use_procedure: If True, use stored procedure (enterprise pattern)
                          If False, use Python implementation (original)
        """
        if use_procedure:
            return self.run_bronze_etl_with_procedure()
        else:
            return self.run_bronze_etl_python()

def main():
    """Execute the type-safe Bronze ETL pipeline"""
    etl = BronzeETLTypeSafe()
    
    # Verify database connectivity before starting ETL operations
    if not db_connector.test_connection():
        logger.error("Database connection test failed - cannot proceed with ETL")
        sys.exit(1)
    
    # Execute the ETL pipeline
    success = etl.run_bronze_etl()
    
    if not success:
        logger.error("ETL pipeline failed - check logs for details")
        sys.exit(1)
    else:
        logger.info("ETL pipeline completed successfully - ready for Silver layer processing")

if __name__ == "__main__":
    main()
