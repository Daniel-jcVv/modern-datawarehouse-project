USE [master]
GO

-- Create DataWarehouse database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'DataWarehouse')
BEGIN
    CREATE DATABASE [DataWarehouse]
    PRINT 'Database DataWarehouse created successfully'
END
ELSE
BEGIN
    PRINT 'Database DataWarehouse already exists'
END
GO

USE [DataWarehouse]
GO

-- Verify database is ready
SELECT
    'Database Ready' as Status,
    DB_NAME() as DatabaseName,
    GETDATE() as CurrentTime
GO
