/*
===============================================================================
FILE: 02_crm_procedures_silver_improved.sql
===============================================================================
CRM table loading procedures - IMPROVED VERSION
Uses utility functions consistently and fixes architectural issues
===============================================================================
*/

CREATE OR ALTER PROCEDURE silver.load_crm_tables
    @enable_logging BIT = 1
AS
BEGIN
    DECLARE @section_start_time DATETIME, @section_end_time DATETIME;
    DECLARE @table_start_time DATETIME, @table_end_time DATETIME;
    DECLARE @row_count INT, @current_table NVARCHAR(100);

    BEGIN TRY
        SET @section_start_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '------------------------------------------------';
            PRINT 'Loading CRM Tables';
            PRINT 'Start Time: ' + CONVERT(NVARCHAR, @section_start_time, 120);
            PRINT '------------------------------------------------';
        END

        -- ===================================================================
        -- TABLE 1: CRM Customer Information Processing
        -- ===================================================================
        SET @current_table = 'crm_cust_info';
        SET @table_start_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Truncating Table: silver.crm_cust_info';
            PRINT '>> Inserting Data Into: silver.crm_cust_info';
        END

        TRUNCATE TABLE silver.crm_cust_info;
        INSERT INTO silver.crm_cust_info (cst_id, cst_key, cst_firstname, cst_lastname, cst_marital_status, cst_gndr, cst_create_date)
        SELECT
            cst_id,
            cst_key,
            dbo.clean_special_chars(cst_firstname),
            dbo.clean_special_chars(cst_lastname),
            dbo.clean_marital_status(cst_marital_status),  -- USE UTILITY FUNCTION
            dbo.clean_gender(cst_gndr),                    -- USE UTILITY FUNCTION
            cst_create_date
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC) AS rn
            FROM bronze.crm_cust_info
            WHERE cst_id IS NOT NULL
        ) t
        WHERE rn = 1;

        SELECT @row_count = COUNT(*) FROM silver.crm_cust_info;
        SET @table_end_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Rows Processed: ' + CAST(@row_count AS NVARCHAR);
            PRINT '>> Load Duration: ' + CAST(DATEDIFF(SECOND, @table_start_time, @table_end_time) AS NVARCHAR) + ' seconds';
            PRINT '>> -------------';
        END

        -- ===================================================================
        -- TABLE 2: CRM Product Information Processing (FIXED)
        -- ===================================================================
        SET @current_table = 'crm_prd_info';
        SET @table_start_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Truncating Table: silver.crm_prd_info';
            PRINT '>> Inserting Data Into: silver.crm_prd_info';
        END

        TRUNCATE TABLE silver.crm_prd_info;

        -- Improved product parsing with better validation
        INSERT INTO silver.crm_prd_info (prd_id, cat_id, prd_key, prd_nm, prd_cost, prd_line, prd_start_dt, prd_end_dt)
        SELECT
            prd_id,
            -- More robust category parsing
            CASE
                WHEN prd_key IS NULL OR LEN(TRIM(prd_key)) < 6 THEN 'UNKNOWN'
                WHEN CHARINDEX('-', prd_key) > 0 AND CHARINDEX('-', prd_key) <= 5 THEN
                    REPLACE(LEFT(prd_key, CHARINDEX('-', prd_key) - 1), '-', '_')
                ELSE REPLACE(LEFT(prd_key, 5), '-', '_')
            END AS cat_id,
            -- More robust product key extraction
            CASE
                WHEN prd_key IS NULL OR LEN(TRIM(prd_key)) < 6 THEN prd_key
                WHEN CHARINDEX('-', prd_key) > 0 THEN
                    SUBSTRING(prd_key, CHARINDEX('-', prd_key) + 1, LEN(prd_key))
                WHEN LEN(prd_key) >= 7 THEN
                    SUBSTRING(prd_key, 7, LEN(prd_key))
                ELSE prd_key
            END AS prd_key_clean,
            dbo.clean_special_chars(prd_nm) AS prd_nm,
            ISNULL(prd_cost, 0) AS prd_cost,
            dbo.clean_product_line(prd_line) AS prd_line,  -- USE UTILITY FUNCTION
            CAST(prd_start_dt AS DATE) AS prd_start_dt,
            -- Calculate end date using the cleaned product key
            DATEADD(DAY, -1, LEAD(CAST(prd_start_dt AS DATE)) OVER (
                PARTITION BY
                    CASE
                        WHEN prd_key IS NULL OR LEN(TRIM(prd_key)) < 6 THEN prd_key
                        WHEN CHARINDEX('-', prd_key) > 0 THEN
                            SUBSTRING(prd_key, CHARINDEX('-', prd_key) + 1, LEN(prd_key))
                        WHEN LEN(prd_key) >= 7 THEN
                            SUBSTRING(prd_key, 7, LEN(prd_key))
                        ELSE prd_key
                    END
                ORDER BY prd_start_dt
    )
) AS prd_end_dt
        FROM bronze.crm_prd_info
        WHERE prd_id IS NOT NULL;

        SELECT @row_count = COUNT(*) FROM silver.crm_prd_info;
        SET @table_end_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Rows Processed: ' + CAST(@row_count AS NVARCHAR);
            PRINT '>> Load Duration: ' + CAST(DATEDIFF(SECOND, @table_start_time, @table_end_time) AS NVARCHAR) + ' seconds';
            PRINT '>> -------------';
        END

        -- ===================================================================
        -- TABLE 3: CRM Sales Details Processing (IMPROVED)
        -- ===================================================================
        SET @current_table = 'crm_sales_details';
        SET @table_start_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Truncating Table: silver.crm_sales_details';
            PRINT '>> Inserting Data Into: silver.crm_sales_details';
        END

        TRUNCATE TABLE silver.crm_sales_details;
        INSERT INTO silver.crm_sales_details (sls_ord_num, sls_prd_key, sls_cust_id, sls_order_dt, sls_ship_dt, sls_due_dt, sls_sales, sls_quantity, sls_price)
        SELECT
            sls_ord_num,
            sls_prd_key,
            sls_cust_id,
            dbo.convert_int_to_date(sls_order_dt),  -- USE UTILITY FUNCTION
            dbo.convert_int_to_date(sls_ship_dt),   -- USE UTILITY FUNCTION
            dbo.convert_int_to_date(sls_due_dt),    -- USE UTILITY FUNCTION
            -- Improved sales calculation with better validation
            CASE
                WHEN sls_sales IS NULL OR sls_sales <= 0 THEN
                    CASE
                        WHEN sls_quantity IS NOT NULL AND sls_price IS NOT NULL AND sls_quantity > 0
                        THEN sls_quantity * ABS(sls_price)
                        ELSE NULL
                    END
                WHEN sls_quantity IS NOT NULL AND sls_price IS NOT NULL AND sls_quantity > 0
                     AND ABS(sls_sales - (sls_quantity * ABS(sls_price))) > 0.01 THEN
                    sls_quantity * ABS(sls_price)  -- Recalculate if inconsistent
                ELSE sls_sales
            END AS sls_sales,
            sls_quantity,
            -- Improved price calculation
            CASE
                WHEN sls_price IS NULL OR sls_price = 0 THEN
                    CASE
                        WHEN sls_sales IS NOT NULL AND sls_quantity IS NOT NULL AND sls_quantity > 0
                        THEN sls_sales / sls_quantity
                        ELSE NULL
                    END
                ELSE ABS(sls_price)
            END AS sls_price
        FROM bronze.crm_sales_details
        WHERE sls_ord_num IS NOT NULL;

        SELECT @row_count = COUNT(*) FROM silver.crm_sales_details;
        SET @table_end_time = GETDATE();

        IF @enable_logging = 1
        BEGIN
            PRINT '>> Rows Processed: ' + CAST(@row_count AS NVARCHAR);
            PRINT '>> Load Duration: ' + CAST(DATEDIFF(SECOND, @table_start_time, @table_end_time) AS NVARCHAR) + ' seconds';
            PRINT '>> -------------';
        END

        -- Section completion summary
        SET @section_end_time = GETDATE();
        IF @enable_logging = 1
        BEGIN
            PRINT 'CRM Section Completed Successfully';
            PRINT 'Section Duration: ' + CAST(DATEDIFF(SECOND, @section_start_time, @section_end_time) AS NVARCHAR) + ' seconds';
            PRINT '';
        END

    END TRY
    BEGIN CATCH
        -- Comprehensive error handling for CRM section
        PRINT '==========================================';
        PRINT 'ERROR OCCURRED DURING CRM TABLES LOADING';
        PRINT 'Error Message: ' + ERROR_MESSAGE();
        PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
        PRINT 'Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
        PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
        IF @current_table IS NOT NULL
            PRINT 'Failed on Table: silver.' + @current_table;
        PRINT 'Section Duration: ' + CAST(DATEDIFF(SECOND, @section_start_time, GETDATE()) AS NVARCHAR) + ' seconds';
        PRINT '==========================================';

        -- Re-throw error to maintain error chain
        THROW;
    END CATCH
END
GO
