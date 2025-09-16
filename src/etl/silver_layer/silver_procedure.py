#!/usr/bin/env python3
"""
Create Silver Stored Procedure Directly
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.connectors.sql_server import db_connector
from loguru import logger

def create_silver_procedure():
    """Create the silver.load_silver stored procedure"""
    
    procedure_sql = """
CREATE OR ALTER PROCEDURE [silver].[load_silver]
AS
BEGIN
    DECLARE @start_time DATETIME, @end_time DATETIME, @batch_start_time DATETIME, @batch_end_time DATETIME;
    DECLARE @table_name NVARCHAR(50), @record_count INT;
    BEGIN TRY
        SET @batch_start_time = GETDATE();
        PRINT '================================================';
        PRINT 'SILVER LAYER ETL - Data Transformation Pipeline';
        PRINT 'Start Time: ' + CONVERT(NVARCHAR, @batch_start_time, 120);
        PRINT '================================================';

        -- Loading silver.crm_cust_info
        SET @start_time = GETDATE();
        SET @table_name = 'silver.crm_cust_info';
        PRINT '[1/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.crm_cust_info;
        INSERT INTO silver.crm_cust_info (
            cst_id, cst_key, cst_firstname, cst_lastname, cst_marital_status, cst_gndr, cst_create_date
        )
        SELECT
            cst_id, cst_key,
            TRIM(cst_firstname) AS cst_firstname,
            TRIM(cst_lastname) AS cst_lastname,
            CASE 
                WHEN UPPER(TRIM(cst_marital_status)) = 'S' THEN 'Single'
                WHEN UPPER(TRIM(cst_marital_status)) = 'M' THEN 'Married'
                ELSE 'n/a'
            END AS cst_marital_status,
            CASE 
                WHEN UPPER(TRIM(cst_gndr)) = 'F' THEN 'Female'
                WHEN UPPER(TRIM(cst_gndr)) = 'M' THEN 'Male'
                ELSE 'n/a'
            END AS cst_gndr,
            cst_create_date
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
            FROM bronze.crm_cust_info
            WHERE cst_id IS NOT NULL
        ) t
        WHERE flag_last = 1;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.crm_cust_info;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        -- Loading silver.crm_prd_info
        SET @start_time = GETDATE();
        SET @table_name = 'silver.crm_prd_info';
        PRINT '[2/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.crm_prd_info;
        INSERT INTO silver.crm_prd_info (prd_id, cat_id, prd_key, prd_nm, prd_cost, prd_line, prd_start_dt, prd_end_dt)
        SELECT
            prd_id,
            REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') AS cat_id,
            SUBSTRING(prd_key, 7, LEN(prd_key)) AS prd_key,
            prd_nm, ISNULL(prd_cost, 0) AS prd_cost,
            CASE 
                WHEN UPPER(TRIM(prd_line)) = 'M' THEN 'Mountain'
                WHEN UPPER(TRIM(prd_line)) = 'R' THEN 'Road'
                WHEN UPPER(TRIM(prd_line)) = 'S' THEN 'Other Sales'
                WHEN UPPER(TRIM(prd_line)) = 'T' THEN 'Touring'
                ELSE 'n/a'
            END AS prd_line,
            CAST(prd_start_dt AS DATE) AS prd_start_dt,
            CAST(LEAD(prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt) - 1 AS DATE) AS prd_end_dt
        FROM bronze.crm_prd_info;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.crm_prd_info;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        -- Loading silver.crm_sales_details
        SET @start_time = GETDATE();
        SET @table_name = 'silver.crm_sales_details';
        PRINT '[3/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.crm_sales_details;
        INSERT INTO silver.crm_sales_details (sls_ord_num, sls_prd_key, sls_cust_id, sls_order_dt, sls_ship_dt, sls_due_dt, sls_sales, sls_quantity, sls_price)
        SELECT 
            sls_ord_num, sls_prd_key, sls_cust_id,
            CASE WHEN sls_order_dt = 0 OR LEN(sls_order_dt) != 8 THEN NULL ELSE CAST(CAST(sls_order_dt AS VARCHAR) AS DATE) END AS sls_order_dt,
            CASE WHEN sls_ship_dt = 0 OR LEN(sls_ship_dt) != 8 THEN NULL ELSE CAST(CAST(sls_ship_dt AS VARCHAR) AS DATE) END AS sls_ship_dt,
            CASE WHEN sls_due_dt = 0 OR LEN(sls_due_dt) != 8 THEN NULL ELSE CAST(CAST(sls_due_dt AS VARCHAR) AS DATE) END AS sls_due_dt,
            CASE WHEN sls_sales IS NULL OR sls_sales <= 0 OR sls_sales != sls_quantity * ABS(sls_price) THEN sls_quantity * ABS(sls_price) ELSE sls_sales END AS sls_sales,
            sls_quantity,
            CASE WHEN sls_price IS NULL OR sls_price <= 0 THEN sls_sales / NULLIF(sls_quantity, 0) ELSE sls_price END AS sls_price
        FROM bronze.crm_sales_details;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.crm_sales_details;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        -- Loading silver.erp_cust_az12
        SET @start_time = GETDATE();
        SET @table_name = 'silver.erp_cust_az12';
        PRINT '[4/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.erp_cust_az12;
        INSERT INTO silver.erp_cust_az12 (cid, bdate, gen)
        SELECT
            CASE WHEN cid LIKE 'NAS%' THEN SUBSTRING(cid, 4, LEN(cid)) ELSE cid END AS cid,
            CASE WHEN bdate > GETDATE() THEN NULL ELSE bdate END AS bdate,
            CASE WHEN UPPER(TRIM(gen)) IN ('F', 'FEMALE') THEN 'Female' WHEN UPPER(TRIM(gen)) IN ('M', 'MALE') THEN 'Male' ELSE 'n/a' END AS gen
        FROM bronze.erp_cust_az12;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.erp_cust_az12;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        -- Loading silver.erp_loc_a101
        SET @start_time = GETDATE();
        SET @table_name = 'silver.erp_loc_a101';
        PRINT '[5/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.erp_loc_a101;
        INSERT INTO silver.erp_loc_a101 (cid, cntry)
        SELECT
            REPLACE(cid, '-', '') AS cid,
            CASE WHEN TRIM(cntry) = 'DE' THEN 'Germany' WHEN TRIM(cntry) IN ('US', 'USA') THEN 'United States' WHEN TRIM(cntry) = '' OR cntry IS NULL THEN 'n/a' ELSE TRIM(cntry) END AS cntry
        FROM bronze.erp_loc_a101;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.erp_loc_a101;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        -- Loading silver.erp_px_cat_g1v2
        SET @start_time = GETDATE();
        SET @table_name = 'silver.erp_px_cat_g1v2';
        PRINT '[6/6] Processing: ' + @table_name;
        TRUNCATE TABLE silver.erp_px_cat_g1v2;
        INSERT INTO silver.erp_px_cat_g1v2 (id, cat, subcat, maintenance)
        SELECT id, cat, subcat, maintenance FROM bronze.erp_px_cat_g1v2;
        SET @end_time = GETDATE();
        SELECT @record_count = COUNT(*) FROM silver.erp_px_cat_g1v2;
        PRINT '    Records loaded: ' + CAST(@record_count AS NVARCHAR) + ' | Duration: ' + CAST(DATEDIFF(MILLISECOND, @start_time, @end_time) AS NVARCHAR) + 'ms';

        SET @batch_end_time = GETDATE();
        PRINT '================================================';
        PRINT 'SILVER LAYER ETL COMPLETED SUCCESSFULLY';
        PRINT 'End Time: ' + CONVERT(NVARCHAR, @batch_end_time, 120);
        PRINT 'Total Duration: ' + CAST(DATEDIFF(MILLISECOND, @batch_start_time, @batch_end_time) AS NVARCHAR) + 'ms';
        PRINT '================================================';
        
    END TRY
    BEGIN CATCH
        PRINT '================================================';
        PRINT 'ERROR IN SILVER LAYER ETL PROCESS';
        PRINT 'Error Message: ' + ERROR_MESSAGE();
        PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
        PRINT 'Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
        PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
        PRINT '================================================';
    END CATCH
END
"""
    
    try:
        logger.info("Creating silver.load_silver stored procedure...")
        result = db_connector.create_stored_procedure_directly(procedure_sql)
        
        if result:
            # Verify creation
            verify = db_connector.execute_query("SELECT name FROM sys.procedures WHERE name = 'load_silver' AND schema_id = SCHEMA_ID('silver')")
            if verify:
                logger.success(f"Stored procedure created: {verify[0][0]}")
                return True
            else:
                logger.error("Procedure not found after creation")
                return False
        else:
            logger.error("Failed to create stored procedure")
            return False
            
    except Exception as e:
        logger.error(f"Error creating procedure: {e}")
        return False

if __name__ == "__main__":
    # When run directly, create the procedure and show status
    success = create_silver_procedure()
    if success:
        print("Ready to run: python run_pipeline.py silver")
    else:
        print("Failed to create stored procedure")
    sys.exit(0 if success else 1)
