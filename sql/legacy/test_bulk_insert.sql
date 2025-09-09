/*
===============================================================================
DIAGNOSTIC SCRIPT: Test BULK INSERT functionality
===============================================================================
*/
USE DataWarehouse;
GO

PRINT '============================================';
PRINT 'BULK INSERT DIAGNOSTIC TEST';
PRINT '============================================';

-- Test 1: Check SQL Server configuration
PRINT '1. Checking SQL Server configuration...';
SELECT name, value_in_use, description
FROM sys.configurations
WHERE name IN ('show advanced options', 'xp_cmdshell', 'Ad Hoc Distributed Queries');
PRINT '';

-- Test 2: Test BULK INSERT with a small file using OPENROWSET
PRINT '2. Testing BULK INSERT alternative with OPENROWSET...';
BEGIN TRY
    SELECT TOP 5 * FROM OPENROWSET(
        BULK '/data/source_crm/cust_info.csv',
        SINGLE_CLOB
    ) AS x;
    PRINT 'OPENROWSET test SUCCESSFUL!';
END TRY
BEGIN CATCH
    PRINT 'OPENROWSET test FAILED!';
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
END CATCH
PRINT '';

-- Test 3: Test basic BULK INSERT
PRINT '3. Testing basic BULK INSERT...';
BEGIN TRY
    -- Create temporary table for testing
    IF OBJECT_ID('tempdb..#test_bulk') IS NOT NULL
        DROP TABLE #test_bulk;

    CREATE TABLE #test_bulk (
        line_data NVARCHAR(MAX)
    );

    -- Attempt BULK INSERT line by line
    BULK INSERT #test_bulk
    FROM '/data/source_crm/cust_info.csv'
    WITH (
        ROWTERMINATOR = '\n',
        TABLOCK
    );

    PRINT 'Basic BULK INSERT test SUCCESSFUL!';
    PRINT 'Records loaded: ' + CAST(@@ROWCOUNT AS NVARCHAR);

    -- Show first rows
    PRINT 'First 3 lines:';
    SELECT TOP 3 line_data FROM #test_bulk;

END TRY
BEGIN CATCH
    PRINT 'Basic BULK INSERT test FAILED!';
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
    PRINT 'Error State: ' + CAST(ERROR_STATE() AS NVARCHAR);
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR);
END CATCH
PRINT '';

PRINT '============================================';
PRINT 'DIAGNOSTIC TEST COMPLETED';
PRINT '============================================';
