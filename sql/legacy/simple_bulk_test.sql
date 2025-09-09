/*
===============================================================================
SIMPLE BULK INSERT TEST - Step by Step
===============================================================================
*/
USE DataWarehouse;
GO

PRINT '============================================';
PRINT 'SIMPLE BULK INSERT STEP-BY-STEP TEST';
PRINT '============================================';

-- Step 1: Create a simple temporary table
PRINT 'Step 1: Creating temporary table...';
IF OBJECT_ID('tempdb..#simple_test') IS NOT NULL
    DROP TABLE #simple_test;

CREATE TABLE #simple_test (
    data_line NVARCHAR(MAX)
);
PRINT 'Temporary table created successfully.';
PRINT '';

-- Step 2: Test the most basic BULK INSERT possible
PRINT 'Step 2: Testing basic BULK INSERT...';
BEGIN TRY
    BULK INSERT #simple_test
    FROM '/data/source_crm/cust_info.csv'
    WITH (
        ROWTERMINATOR = '\n'
    );

    DECLARE @row_count INT = @@ROWCOUNT;
    PRINT 'SUCCESS! Loaded ' + CAST(@row_count AS NVARCHAR) + ' rows.';

    PRINT 'First 5 rows:';
    SELECT TOP 5 data_line FROM #simple_test;

END TRY
BEGIN CATCH
    PRINT 'FAILED! Error details:';
    PRINT '  Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
    PRINT '  Error Message: ' + ERROR_MESSAGE();
    PRINT '  Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
    PRINT '  Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
END CATCH

PRINT '';
PRINT '============================================';
PRINT 'TEST COMPLETED';
PRINT '============================================';
