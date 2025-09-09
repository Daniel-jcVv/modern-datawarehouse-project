/*
=============================================================
Create Database and Schemas
=============================================================
Script Purpose:
    This script creates a new database named 'DataWarehouse' after checking if it already exists.
    If the database exists, it is dropped and recreated. Additionally, the script sets up three schemas
    within the database: 'bronze', 'silver', and 'gold'.

WARNING:
    Running this script will drop the entire 'DataWarehouse' database if it exists.
    All data in the database will be permanently deleted. Proceed with caution
    and ensure you have proper backups before running this script.
*/

USE master;
GO

-- Drop and recreate the 'DataWarehouse' database
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'DataWarehouse')
BEGIN
    ALTER DATABASE DataWarehouse SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE DataWarehouse;
END;
GO

-- Create the 'DataWarehouse' database
CREATE DATABASE DataWarehouse;
GO



/*
===============================================================================
Schema Creation Script - Compatible with All SQL Server Versions
===============================================================================
Purpose: Create bronze, silver, gold schemas using compatible syntax
Author: Daniel G. B.
Date: 2025-09-07
Note: Execute each block separately if needed
===============================================================================
*/

USE DataWarehouse;
GO

-- Check current schemas first
PRINT 'Current schemas in database:';
SELECT name as schema_name, schema_id
FROM sys.schemas
WHERE name IN ('bronze', 'silver', 'gold', 'dbo')
ORDER BY name;
GO

-- Create bronze schema (compatible syntax)
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'bronze')
BEGIN
    EXEC sp_executesql N'CREATE SCHEMA bronze';
    PRINT 'Schema bronze created successfully';
END
ELSE
    PRINT 'Schema bronze already exists';
GO

-- Create silver schema (compatible syntax)
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'silver')
BEGIN
    EXEC sp_executesql N'CREATE SCHEMA silver';
    PRINT 'Schema silver created successfully';
END
ELSE
    PRINT 'Schema silver already exists';
GO

-- Create gold schema (compatible syntax)
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'gold')
BEGIN
    EXEC sp_executesql N'CREATE SCHEMA gold';
    PRINT 'Schema gold created successfully';
END
ELSE
    PRINT 'Schema gold already exists';
GO

-- Verify all schemas were created
PRINT 'Final verification - All schemas:';
SELECT name as schema_name, schema_id
FROM sys.schemas
WHERE name IN ('bronze', 'silver', 'gold', 'dbo')
ORDER BY name;
GO
