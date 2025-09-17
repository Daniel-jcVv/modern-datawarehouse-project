/*
===============================================================================
DDL Script: Bronze Layer Table Creation (Raw Data Ingestion Layer)
===============================================================================
Script Purpose:
    This script defines and creates tables in the 'bronze' schema following
    medallion architecture best practices. Bronze layer accepts ALL data formats
    using NVARCHAR(MAX) to ensure zero data loss during ingestion and full
    Unicode support for international characters.

Design Pattern:
    - ALL columns use NVARCHAR(MAX) except system metadata
    - No data type validation at Bronze layer (accepts dirty data)
    - Type conversions and validations happen in Silver layer
    - Ensures 100% data capture from source systems
    - Unicode support for international data (UTF-16)

Technical Decisions:
    - NVARCHAR(MAX) instead of VARCHAR for Unicode support
    - No constraints or validations (not even NULL checks)
    - Only system column (dwh_create_date) maintains strong typing
    - Column names preserved exactly as source system

Prerequisites:
    - Database 'DataWarehouse' must exist
    - Schema 'bronze' must exist
    - User must have DDL privileges

Created: 2025-01-01
Modified: 2025-01-XX
Author: Data Engineering Team
Version: 2.0
===============================================================================
*/

USE DataWarehouse;
GO

-- ============================================================================
-- SECTION 1: CRM SOURCE SYSTEM TABLES
-- ============================================================================

PRINT '================================================';
PRINT 'Starting Bronze Layer DDL Deployment v2.0';
PRINT 'Timestamp: ' + CONVERT(VARCHAR(50), GETDATE(), 121);
PRINT '================================================';
PRINT '';

PRINT '=== SECTION 1: Creating Bronze CRM Tables ===';
PRINT 'Pattern: All columns NVARCHAR(MAX) for maximum flexibility';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.crm_cust_info
-- Source: CRM System - Customer Information
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.crm_cust_info';

IF OBJECT_ID('bronze.crm_cust_info', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.crm_cust_info;
END

CREATE TABLE bronze.crm_cust_info (
    -- All source columns as NVARCHAR(MAX) to accept any data format
    cst_id              NVARCHAR(MAX),  -- Source: Customer ID (may contain alphanumeric)
    cst_key             NVARCHAR(MAX),  -- Source: Customer Key
    cst_firstname       NVARCHAR(MAX),  -- Source: First Name (Unicode for international names)
    cst_lastname        NVARCHAR(MAX),  -- Source: Last Name (Unicode for international names)
    cst_marital_status  NVARCHAR(MAX),  -- Source: Marital Status (various formats)
    cst_gndr            NVARCHAR(MAX),  -- Source: Gender (M/F/Male/Female/1/0/Unknown)
    cst_create_date     NVARCHAR(MAX),  -- Source: Creation Date (various date formats)
    
    -- System metadata column (only column with strong typing)
    dwh_create_date     DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.crm_prd_info
-- Source: CRM System - Product Information
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.crm_prd_info';

IF OBJECT_ID('bronze.crm_prd_info', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.crm_prd_info;
END

CREATE TABLE bronze.crm_prd_info (
    -- All source columns as NVARCHAR(MAX) to accept any data format
    prd_id          NVARCHAR(MAX),  -- Source: Product ID (may be alphanumeric)
    prd_key         NVARCHAR(MAX),  -- Source: Product Key (concatenated values)
    prd_nm          NVARCHAR(MAX),  -- Source: Product Name (Unicode support)
    prd_cost        NVARCHAR(MAX),  -- Source: Product Cost (may include currency symbols)
    prd_line        NVARCHAR(MAX),  -- Source: Product Line (various formats)
    prd_start_dt    NVARCHAR(MAX),  -- Source: Start Date (various date formats)
    prd_end_dt      NVARCHAR(MAX),  -- Source: End Date (various date formats)
    
    -- System metadata column
    dwh_create_date DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.crm_sales_details
-- Source: CRM System - Sales Transaction Details
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.crm_sales_details';

IF OBJECT_ID('bronze.crm_sales_details', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.crm_sales_details;
END

CREATE TABLE bronze.crm_sales_details (
    -- All source columns as NVARCHAR(MAX) to accept any data format
    sls_ord_num     NVARCHAR(MAX),  -- Source: Order Number (alphanumeric)
    sls_prd_key     NVARCHAR(MAX),  -- Source: Product Key reference
    sls_cust_id     NVARCHAR(MAX),  -- Source: Customer ID reference
    sls_order_dt    NVARCHAR(MAX),  -- Source: Order Date (may be integer format)
    sls_ship_dt     NVARCHAR(MAX),  -- Source: Ship Date (may be integer format)
    sls_due_dt      NVARCHAR(MAX),  -- Source: Due Date (may be integer format)
    sls_sales       NVARCHAR(MAX),  -- Source: Sales Amount (may include symbols)
    sls_quantity    NVARCHAR(MAX),  -- Source: Quantity (may have decimals)
    sls_price       NVARCHAR(MAX),  -- Source: Unit Price (may include currency)
    
    -- System metadata column
    dwh_create_date DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ============================================================================
-- SECTION 2: ERP SOURCE SYSTEM TABLES
-- ============================================================================

PRINT '=== SECTION 2: Creating Bronze ERP Tables ===';
PRINT 'Pattern: Preserving cryptic column names from legacy system';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.erp_loc_a101
-- Source: ERP System - Location/Geography Data
-- Note: Column names preserved as-is from legacy system
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.erp_loc_a101';

IF OBJECT_ID('bronze.erp_loc_a101', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.erp_loc_a101;
END

CREATE TABLE bronze.erp_loc_a101 (
    -- Legacy column names preserved exactly
    cid             NVARCHAR(MAX),  -- Source: Customer ID (with hyphens/prefixes)
    cntry           NVARCHAR(MAX),  -- Source: Country (various formats/abbreviations)
    
    -- System metadata column
    dwh_create_date DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.erp_cust_az12
-- Source: ERP System - Customer Demographics
-- Note: Column names preserved as-is from legacy system
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.erp_cust_az12';

IF OBJECT_ID('bronze.erp_cust_az12', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.erp_cust_az12;
END

CREATE TABLE bronze.erp_cust_az12 (
    -- Legacy column names preserved exactly
    cid             NVARCHAR(MAX),  -- Source: Customer ID (with prefixes like 'NAS')
    bdate           NVARCHAR(MAX),  -- Source: Birth Date (various formats, may be future)
    gen             NVARCHAR(MAX),  -- Source: Gender (multiple format variations)
    
    -- System metadata column
    dwh_create_date DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.erp_px_cat_g1v2
-- Source: ERP System - Product Categories
-- Note: Column names preserved as-is from legacy system
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.erp_px_cat_g1v2';

IF OBJECT_ID('bronze.erp_px_cat_g1v2', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.erp_px_cat_g1v2;
END

CREATE TABLE bronze.erp_px_cat_g1v2 (
    -- Legacy column names preserved exactly
    id              NVARCHAR(MAX),  -- Source: Category ID
    cat             NVARCHAR(MAX),  -- Source: Category
    subcat          NVARCHAR(MAX),  -- Source: Subcategory
    maintenance     NVARCHAR(MAX),  -- Source: Maintenance info
    
    -- System metadata column
    dwh_create_date DATETIME2 DEFAULT GETDATE()  -- DWH ingestion timestamp
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- ============================================================================
-- SECTION 3: LOGGING AND MONITORING INFRASTRUCTURE
-- ============================================================================

PRINT '=== SECTION 3: Creating Bronze Logging Infrastructure ===';
PRINT '';

-- ----------------------------------------------------------------------------
-- Table: bronze.etl_execution_log
-- Purpose: Track all ETL executions for monitoring and debugging
-- ----------------------------------------------------------------------------
PRINT 'Creating table: bronze.etl_execution_log';

IF OBJECT_ID('bronze.etl_execution_log', 'U') IS NOT NULL
BEGIN
    PRINT '  Dropping existing table...';
    DROP TABLE bronze.etl_execution_log;
END

CREATE TABLE bronze.etl_execution_log (
    -- Primary key for log entries
    log_id                  INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Execution details
    table_name              NVARCHAR(100) NOT NULL,        -- Target table name
    source_file             NVARCHAR(500) NOT NULL,        -- Source CSV file path
    status                  NVARCHAR(20) NOT NULL,         -- SUCCESS / ERROR / WARNING
    rows_affected           INT DEFAULT 0,                 -- Number of rows loaded
    execution_time_seconds  INT DEFAULT 0,                 -- Duration in seconds
    
    -- Error tracking
    error_message           NVARCHAR(MAX) NULL,            -- Error details if failed
    error_line              INT NULL,                      -- Line number where error occurred
    
    -- Metadata
    executed_date           DATETIME2 DEFAULT GETDATE(),   -- Execution timestamp
    executed_by             NVARCHAR(100) DEFAULT SUSER_NAME(), -- User who executed
    execution_host          NVARCHAR(100) DEFAULT HOST_NAME()   -- Server/container name
);
GO

PRINT '  Table created successfully.';
PRINT '';

-- Create index on log table for performance
PRINT 'Creating indexes on logging table...';

CREATE NONCLUSTERED INDEX IX_etl_execution_log_executed_date 
ON bronze.etl_execution_log(executed_date DESC);
GO

CREATE NONCLUSTERED INDEX IX_etl_execution_log_table_status 
ON bronze.etl_execution_log(table_name, status);
GO

PRINT '  Indexes created successfully.';
PRINT '';

-- ============================================================================
-- SECTION 4: VALIDATION QUERIES
-- ============================================================================

PRINT '=== SECTION 4: Running Post-Deployment Validation ===';
PRINT '';

-- Check all tables were created
PRINT 'Validating Bronze schema objects:';

SELECT 
    'Tables Created' AS Validation_Type,
    COUNT(*) AS Object_Count,
    STRING_AGG(TABLE_NAME, ', ') AS Object_Names
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'bronze' 
    AND TABLE_TYPE = 'BASE TABLE';

PRINT '';

-- Display column information for verification
PRINT 'Bronze Table Structure Summary:';

SELECT 
    t.TABLE_NAME,
    COUNT(c.COLUMN_NAME) AS Column_Count,
    SUM(CASE WHEN c.DATA_TYPE = 'nvarchar' THEN 1 ELSE 0 END) AS NVARCHAR_Columns,
    SUM(CASE WHEN c.DATA_TYPE = 'datetime2' THEN 1 ELSE 0 END) AS DateTime_Columns
FROM INFORMATION_SCHEMA.TABLES t
JOIN INFORMATION_SCHEMA.COLUMNS c 
    ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
    AND t.TABLE_NAME = c.TABLE_NAME
WHERE t.TABLE_SCHEMA = 'bronze' 
    AND t.TABLE_TYPE = 'BASE TABLE'
GROUP BY t.TABLE_NAME
ORDER BY t.TABLE_NAME;

PRINT '';
PRINT '================================================';
PRINT 'Bronze Layer DDL Deployment Completed Successfully';
PRINT 'All tables ready to accept raw data without type restrictions';
PRINT 'Timestamp: ' + CONVERT(VARCHAR(50), GETDATE(), 121);
PRINT '================================================';
GO

/*
===============================================================================
Post-Deployment Notes:
===============================================================================
1. All Bronze tables now use NVARCHAR(MAX) for source columns
2. This ensures no data loss during initial ingestion
3. Data type conversions will be handled in Silver layer
4. Unicode support enabled for international characters
5. Logging infrastructure ready for ETL monitoring

Next Steps:
1. Test BULK INSERT operations with sample data
2. Verify dirty data acceptance (mixed formats, special characters)
3. Implement Bronze stored procedures for automated loading
4. Set up error handling and retry logic
===============================================================================
*/