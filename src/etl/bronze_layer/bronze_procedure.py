"""
Bronze Layer Procedure Manager - Enterprise ETL Framework
Manages stored procedures for Bronze layer data ingestion with execution logging
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from sqlalchemy import text
from loguru import logger
import socket
import os


def log_execution(table_name: str, source_file: str, status: str, 
                 rows_affected: int = None, execution_time_seconds: int = None, 
                 error_message: str = None, error_line: int = None):
    """Log execution details to bronze.etl_execution_log table"""
    try:
        # Get system information
        executed_by = os.getenv('USER', 'system')
        execution_host = socket.gethostname()
        
        # Use a simpler approach with execute_query for the insert
        log_sql = f"""
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, error_message, error_line, 
            executed_date, executed_by, execution_host
        ) VALUES (
            '{table_name}', '{source_file}', '{status}', 
            {rows_affected if rows_affected is not None else 'NULL'}, 
            {execution_time_seconds if execution_time_seconds is not None else 'NULL'}, 
            {'NULL' if error_message is None else f"'{error_message.replace("'", "''")}'"},
            {error_line if error_line is not None else 'NULL'}, 
            GETDATE(), '{executed_by}', '{execution_host}'
        )
        """
        
        with db_connector.get_connection() as conn:
            conn.execute(text(log_sql))
            conn.commit()
            
    except Exception as e:
        logger.warning(f"Failed to log execution for {table_name}: {str(e)}")


def create_bronze_procedure():
    """Create the bronze.load_bronze stored procedure with enhanced logging"""
    
    procedure_sql = """
CREATE OR ALTER PROCEDURE [bronze].[load_bronze]
AS
BEGIN
    DECLARE @start_time DATETIME, @end_time DATETIME, @batch_start_time DATETIME, @batch_end_time DATETIME;
    DECLARE @table_name NVARCHAR(50), @source_file NVARCHAR(200), @record_count INT, @execution_time INT;
    DECLARE @executed_by NVARCHAR(50), @execution_host NVARCHAR(100);
    
    BEGIN TRY
        SET @batch_start_time = GETDATE();
        SET @executed_by = SYSTEM_USER;
        SET @execution_host = @@SERVERNAME;
        
        PRINT '================================================';
        PRINT 'BRONZE LAYER ETL - Data Ingestion Pipeline';
        PRINT 'Start Time: ' + CONVERT(NVARCHAR, @batch_start_time, 120);
        PRINT 'Executed by: ' + @executed_by + ' on ' + @execution_host;
        PRINT '================================================';

        -- Loading bronze.crm_cust_info
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.crm_cust_info';
        SET @source_file = 'data_sets/source_crm/cust_info.csv';
        PRINT '[1/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.crm_cust_info;
        BULK INSERT bronze.crm_cust_info
        -- Windows path: FROM 'C:\\data_sets\\source_crm\\cust_info.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_crm/cust_info.csv'
        FROM '/data_sets/source_crm/cust_info.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_crm_cust_info_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.crm_cust_info;
        
        -- Log successful execution
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        -- Loading bronze.crm_prd_info
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.crm_prd_info';
        SET @source_file = 'data_sets/source_crm/prd_info.csv';
        PRINT '[2/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.crm_prd_info;
        BULK INSERT bronze.crm_prd_info
        -- Windows path: FROM 'C:\\data_sets\\source_crm\\prd_info.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_crm/prd_info.csv'
        FROM '/data_sets/source_crm/prd_info.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_crm_prd_info_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.crm_prd_info;
        
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        -- Loading bronze.crm_sales_details
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.crm_sales_details';
        SET @source_file = 'data_sets/source_crm/sales_details.csv';
        PRINT '[3/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.crm_sales_details;
        BULK INSERT bronze.crm_sales_details
        -- Windows path: FROM 'C:\\data_sets\\source_crm\\sales_details.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_crm/sales_details.csv'
        FROM '/data_sets/source_crm/sales_details.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_crm_sales_details_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.crm_sales_details;
        
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        -- Loading bronze.erp_loc_a101
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.erp_loc_a101';
        SET @source_file = 'data_sets/source_erp/loc_a101.csv';
        PRINT '[4/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.erp_loc_a101;
        BULK INSERT bronze.erp_loc_a101
        -- Windows path: FROM 'C:\\data_sets\\source_erp\\loc_a101.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_erp/LOC_A101.csv'
        FROM '/data_sets/source_erp/LOC_A101.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_erp_loc_a101_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.erp_loc_a101;
        
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        -- Loading bronze.erp_cust_az12
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.erp_cust_az12';
        SET @source_file = 'data_sets/source_erp/cust_az12.csv';
        PRINT '[5/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.erp_cust_az12;
        BULK INSERT bronze.erp_cust_az12
        -- Windows path: FROM 'C:\\data_sets\\source_erp\\cust_az12.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_erp/CUST_AZ12.csv'
        FROM '/data_sets/source_erp/CUST_AZ12.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_erp_cust_az12_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.erp_cust_az12;
        
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        -- Loading bronze.erp_px_cat_g1v2
        SET @start_time = GETDATE();
        SET @table_name = 'bronze.erp_px_cat_g1v2';
        SET @source_file = 'data_sets/source_erp/px_cat_g1v2.csv';
        PRINT '[6/6] Processing: ' + @table_name + ' from ' + @source_file;
        
        TRUNCATE TABLE bronze.erp_px_cat_g1v2;
        BULK INSERT bronze.erp_px_cat_g1v2
        -- Windows path: FROM 'C:\\data_sets\\source_erp\\px_cat_g1v2.csv'
        -- Linux host path: FROM '/home/judah/dwh-portfolio/data_sets/source_erp/PX_CAT_G1V2.csv'
        FROM '/data_sets/source_erp/PX_CAT_G1V2.csv'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\\n',
            TABLOCK
            -- Windows error log: ERRORFILE = 'C:\\logs\\bronze_erp_px_cat_g1v2_errors.log'
        );
        
        SET @end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @start_time, @end_time);
        SELECT @record_count = COUNT(*) FROM bronze.erp_px_cat_g1v2;
        
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, rows_affected, 
            execution_time_seconds, executed_date, executed_by, execution_host
        ) VALUES (
            @table_name, @source_file, 'SUCCESS', @record_count,
            @execution_time, GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(@execution_time AS NVARCHAR) + 's';

        SET @batch_end_time = GETDATE();
        SET @execution_time = DATEDIFF(SECOND, @batch_start_time, @batch_end_time);
        
        -- Log batch completion
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, execution_time_seconds, 
            executed_date, executed_by, execution_host
        ) VALUES (
            'BATCH_COMPLETE', 'ALL_SOURCES', 'SUCCESS', @execution_time,
            GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '================================================';
        PRINT 'BRONZE LAYER ETL COMPLETED SUCCESSFULLY';
        PRINT 'End Time: ' + CONVERT(NVARCHAR, @batch_end_time, 120);
        PRINT 'Total Duration: ' + CAST(@execution_time AS NVARCHAR) + ' seconds';
        PRINT '================================================';
        
    END TRY
    BEGIN CATCH
        -- Log error
        INSERT INTO bronze.etl_execution_log (
            table_name, source_file, status, error_message, error_line,
            executed_date, executed_by, execution_host
        ) VALUES (
            ISNULL(@table_name, 'UNKNOWN'), ISNULL(@source_file, 'UNKNOWN'), 
            'ERROR', ERROR_MESSAGE(), ERROR_LINE(),
            GETDATE(), @executed_by, @execution_host
        );
        
        PRINT '================================================';
        PRINT 'ERROR IN BRONZE LAYER ETL PROCESS';
        PRINT 'Error Message: ' + ERROR_MESSAGE();
        PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
        PRINT 'Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
        PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
        PRINT 'Failed Table: ' + ISNULL(@table_name, 'UNKNOWN');
        PRINT '================================================';
        
        THROW;
    END CATCH
END
"""
    
    try:
        logger.info("Creating bronze.load_bronze stored procedure with execution logging...")
        
        # Create the procedure using execute_script method
        import tempfile
        import os
        
        # Write procedure SQL to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(procedure_sql)
            temp_file = f.name
        
        try:
            # Execute using the script method
            result = db_connector.execute_script(temp_file)
            
            if result:
                # Verify creation
                verify = db_connector.execute_query("""
                    SELECT name FROM sys.procedures 
                    WHERE name = 'load_bronze' AND schema_id = SCHEMA_ID('bronze')
                """)
                
                if verify:
                    logger.success(f"Stored procedure created: bronze.{verify[0][0]}")
                    logger.info("Enhanced with execution logging to bronze.etl_execution_log")
                    return True
                else:
                    logger.error("Procedure not found after creation")
                    return False
            else:
                logger.error("Failed to execute procedure creation script")
                return False
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
            
    except Exception as e:
        logger.error(f"Error creating bronze procedure: {e}")
        return False


def execute_bronze_procedure():
    """Execute the bronze.load_bronze stored procedure and log results"""
    try:
        logger.info("Executing bronze.load_bronze stored procedure...")
        
        # Log procedure start (temporarily disabled for testing)
        # log_execution(
        #     table_name="PROCEDURE_START",
        #     source_file="bronze.load_bronze", 
        #     status="RUNNING"
        # )
        
        # Execute the stored procedure
        with db_connector.get_connection() as conn:
            conn.execute(text("EXEC bronze.load_bronze"))
            conn.commit()
        
        # Log procedure completion (temporarily disabled for testing)
        # log_execution(
        #     table_name="PROCEDURE_COMPLETE",
        #     source_file="bronze.load_bronze",
        #     status="SUCCESS"
        # )
        
        logger.success("Bronze procedure executed successfully")
        return True
        
    except Exception as e:
        # Log procedure error (temporarily disabled for testing)
        # log_execution(
        #     table_name="PROCEDURE_ERROR",
        #     source_file="bronze.load_bronze",
        #     status="ERROR",
        #     error_message=str(e)
        # )
        
        logger.error(f"Bronze procedure execution failed: {e}")
        return False


def get_execution_log_summary():
    """Get summary of recent executions from etl_execution_log"""
    try:
        summary = db_connector.execute_query("""
            SELECT 
                table_name,
                status,
                COUNT(*) as execution_count,
                MAX(executed_date) as last_execution,
                SUM(ISNULL(rows_affected, 0)) as total_rows
            FROM bronze.etl_execution_log 
            WHERE executed_date >= DATEADD(day, -7, GETDATE())
            GROUP BY table_name, status
            ORDER BY last_execution DESC
        """)
        
        logger.info("Recent execution summary (last 7 days):")
        for row in summary:
            logger.info(f"  {row[0]} | {row[1]} | Count: {row[2]} | Last: {row[3]} | Rows: {row[4]}")
            
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get execution summary: {e}")
        return []


if __name__ == "__main__":
    logger.info("Bronze Procedure Manager - Enterprise ETL Framework")
    
    # Create the procedure
    if create_bronze_procedure():
        logger.info("Bronze procedure created successfully")
        
        # Show execution log summary if table has data
        get_execution_log_summary()
        
        print("Ready to run: python run_pipeline.py bronze")
    else:
        print("Failed to create bronze stored procedure")
        sys.exit(1)