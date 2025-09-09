/*
===============================================================================
FILE: 03_erp_procedures.sql
===============================================================================
ERP table loading procedures
===============================================================================
*/

CREATE OR ALTER PROCEDURE silver.load_erp_tables
    @enable_logging BIT = 1
AS
BEGIN
    DECLARE @start_time DATETIME, @end_time DATETIME, @row_count INT;

    BEGIN TRY
        IF @enable_logging = 1 PRINT '--- Loading ERP Tables ---';

        -- ERP Customer AZ12
        SET @start_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Loading erp_cust_az12...';

        TRUNCATE TABLE silver.erp_cust_az12;
        INSERT INTO silver.erp_cust_az12 (cid, bdate, gen)
        SELECT CASE WHEN UPPER(TRIM(cid)) LIKE 'NAS%' THEN TRIM(SUBSTRING(cid, 4, LEN(cid))) ELSE TRIM(cid) END,
               CASE WHEN bdate > GETDATE() OR bdate < '1900-01-01' THEN NULL ELSE bdate END,
               dbo.clean_gender(gen)
        FROM bronze.erp_cust_az12 WHERE cid IS NOT NULL;

        SELECT @row_count = COUNT(*) FROM silver.erp_cust_az12;
        SET @end_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Processed ' + CAST(@row_count AS VARCHAR) + ' rows in ' + CAST(DATEDIFF(SECOND, @start_time, @end_time) AS VARCHAR) + 's';

        -- ERP Location A101
        SET @start_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Loading erp_loc_a101...';

        TRUNCATE TABLE silver.erp_loc_a101;
        INSERT INTO silver.erp_loc_a101 (cid, cntry)
        SELECT REPLACE(TRIM(cid), '-', ''), dbo.clean_country(cntry)
        FROM bronze.erp_loc_a101 WHERE cid IS NOT NULL;

        SELECT @row_count = COUNT(*) FROM silver.erp_loc_a101;
        SET @end_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Processed ' + CAST(@row_count AS VARCHAR) + ' rows in ' + CAST(DATEDIFF(SECOND, @start_time, @end_time) AS VARCHAR) + 's';

        -- ERP Product Category G1V2
        SET @start_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Loading erp_px_cat_g1v2...';

        TRUNCATE TABLE silver.erp_px_cat_g1v2;
        INSERT INTO silver.erp_px_cat_g1v2 (id, cat, subcat, maintenance)
        SELECT id,
               dbo.clean_special_chars(cat),
               dbo.clean_special_chars(subcat),
               CASE WHEN UPPER(dbo.clean_special_chars(maintenance)) = 'YES' THEN 'Yes'
                    WHEN UPPER(dbo.clean_special_chars(maintenance)) = 'NO' THEN 'No'
                    WHEN dbo.clean_special_chars(maintenance) = '' THEN 'Unknown'
                    ELSE dbo.clean_special_chars(maintenance) END
        FROM bronze.erp_px_cat_g1v2 WHERE id IS NOT NULL;

        SELECT @row_count = COUNT(*) FROM silver.erp_px_cat_g1v2;
        SET @end_time = GETDATE();
        IF @enable_logging = 1 PRINT 'Processed ' + CAST(@row_count AS VARCHAR) + ' rows in ' + CAST(DATEDIFF(SECOND, @start_time, @end_time) AS VARCHAR) + 's';

    END TRY
    BEGIN CATCH
        PRINT 'ERROR in ERP loading: ' + ERROR_MESSAGE();
        THROW;
    END CATCH
END
GO

/home/judah/Documents/pj/datawarehouse/scripts/bronze/03_erp_procedures_bronze.sql
