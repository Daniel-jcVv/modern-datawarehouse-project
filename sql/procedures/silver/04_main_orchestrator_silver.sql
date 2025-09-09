/*
===============================================================================
FILE: 04_main_orchestrator.sql
===============================================================================
Main silver layer loading orchestrator
===============================================================================
*/


CREATE OR ALTER PROCEDURE silver.load_silver
    @enable_logging BIT = 1,
    @validation_mode BIT = 0
AS
BEGIN
    DECLARE @batch_start DATETIME = GETDATE(), @batch_end DATETIME;

    BEGIN TRY
        -- Start a transaction to ensure atomicity of the entire batch
        BEGIN TRANSACTION;

        IF @enable_logging = 1
        BEGIN
            PRINT '=== Silver Layer Loading Started ===';
            PRINT 'Start Time: ' + CONVERT(VARCHAR, @batch_start, 120);
        END

        -- Load CRM section
        EXEC silver.load_crm_tables @enable_logging = @enable_logging;

        -- Load ERP section
        EXEC silver.load_erp_tables @enable_logging = @enable_logging;

        -- If all procedures succeed, commit the transaction
        COMMIT TRANSACTION;

        -- Validation summary (only runs after a successful commit)
        IF @validation_mode = 1 AND @enable_logging = 1
        BEGIN
            PRINT '--- Validation Summary ---';
            SELECT 'crm_cust_info' AS table_name, COUNT(*) AS row_count FROM silver.crm_cust_info
            UNION ALL SELECT 'crm_prd_info', COUNT(*) FROM silver.crm_prd_info
            UNION ALL SELECT 'crm_sales_details', COUNT(*) FROM silver.crm_sales_details
            UNION ALL SELECT 'erp_cust_az12', COUNT(*) FROM silver.erp_cust_az12
            UNION ALL SELECT 'erp_loc_a101', COUNT(*) FROM silver.erp_loc_a101
            UNION ALL SELECT 'erp_px_cat_g1v2', COUNT(*) FROM silver.erp_px_cat_g1v2;
        END

        SET @batch_end = GETDATE();
        IF @enable_logging = 1
        BEGIN
            PRINT '=== Silver Layer Loading Completed ===';
            PRINT 'Total Duration: ' + CAST(DATEDIFF(SECOND, @batch_start, @batch_end) AS NVARCHAR) + ' seconds';
            PRINT '==========================================';
        END

    END TRY
    BEGIN CATCH
        -- If an error occurs, roll back the transaction to undo all changes
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        PRINT '==========================================';
        PRINT 'ERROR OCCURRED DURING SILVER LAYER LOADING';
        PRINT 'Error Message: ' + ERROR_MESSAGE();
        PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
        PRINT 'Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
        PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
        PRINT 'Batch Duration: ' + CAST(DATEDIFF(SECOND, @batch_start, GETDATE()) AS NVARCHAR) + ' seconds';
        PRINT '==========================================';

        -- Re-throw the error to maintain the error handling chain
        THROW;
    END CATCH
END
GO
