/*
===============================================================================
DDL Script: Bronze Layer Table Creation (Raw Data Ingestion Layer)
===============================================================================
Script Purpose:
    This script defines and creates tables in the 'bronze' schema following
    medallion architecture pattern. Implements DROP/CREATE approach to ensure
    updated table structure consistency across environments. The bronze layer
    serves as the landing zone for raw, unprocessed data from source systems.

Usage Instructions:
    - Execute this script to completely redefine the DDL structure of bronze tables
    - Existing tables will be dropped and recreated with updated schema definition
    - Ensure proper database privileges and backup procedures before execution
    - Recommended for deployment across DEV/QA/PROD environments

Prerequisites:
    - DDL execution privileges on target database
    - Bronze schema must exist or be created prior to execution

Created: 2025-09-01
Author: Juan Daniel Garcia Belman
Version: 1.0
===============================================================================
*/

USE DataWarehouse;
GO

PRINT '=== Creating Bronze Tables ===';
PRINT '=== Creating Bronze CRM Tables ===';

-- CRM Customer information
IF OBJECT_ID('bronze.crm_cust_info', 'U') IS NOT NULL
    DROP TABLE bronze.crm_cust_info;
GO

CREATE TABLE bronze.crm_cust_info (
    cst_id              INT,
    cst_key             NVARCHAR(50),
    cst_firstname       NVARCHAR(50),
    cst_lastname        NVARCHAR(50),
    cst_marital_status  NVARCHAR(50),
    cst_gndr            NVARCHAR(50),
    cst_create_date     DATE,
    dwh_create_date     DATETIME DEFAULT GETDATE()
);
GO


-- CRM Product information
IF OBJECT_ID('bronze.crm_prd_info', 'U') IS NOT NULL
    DROP TABLE bronze.crm_prd_info;
GO

CREATE TABLE bronze.crm_prd_info (
    prd_id       INT,
    prd_key      NVARCHAR(50),
    prd_nm       NVARCHAR(50),
    prd_cost     DECIMAL(10,2),
    prd_line     NVARCHAR(50),
    prd_start_dt DATETIME,
    prd_end_dt   DATETIME,
    dwh_create_date DATETIME2 DEFAULT GETDATE()
);
GO


-- CRM Sales Details
IF OBJECT_ID('bronze.crm_sales_details', 'U') IS NOT NULL
    DROP TABLE bronze.crm_sales_details;
GO

CREATE TABLE bronze.crm_sales_details (
    sls_ord_num  NVARCHAR(50),
    sls_prd_key  NVARCHAR(50),
    sls_cust_id  INT,
    sls_order_dt INT,
    sls_ship_dt  INT,
    sls_due_dt   INT,
    sls_sales    DECIMAL(10, 2),
    sls_quantity INT,
    sls_price    DECIMAL(10, 2),
    dwh_create_date DATETIME2 DEFAULT GETDATE()
);
GO


PRINT '=== Creating Bronze ERP Tables ===';

-- ERP Tables
IF OBJECT_ID('bronze.erp_loc_a101', 'U') IS NOT NULL
    DROP TABLE bronze.erp_loc_a101;
GO

CREATE TABLE bronze.erp_loc_a101 (
    cid    NVARCHAR(50),
    cntry  NVARCHAR(50),
    dwh_create_date DATETIME2 DEFAULT GETDATE()
);
GO


IF OBJECT_ID('bronze.erp_cust_az12', 'U') IS NOT NULL
    DROP TABLE bronze.erp_cust_az12;
GO

CREATE TABLE bronze.erp_cust_az12 (
    cid    NVARCHAR(50),
    bdate  DATE,
    gen    NVARCHAR(50),
    dwh_create_date DATETIME2 DEFAULT GETDATE()
);
GO


IF OBJECT_ID('bronze.erp_px_cat_g1v2', 'U') IS NOT NULL
    DROP TABLE bronze.erp_px_cat_g1v2;
GO

CREATE TABLE bronze.erp_px_cat_g1v2 (
    id           NVARCHAR(50),
    cat          NVARCHAR(50),
    subcat       NVARCHAR(50),
    maintenance  NVARCHAR(50),
    dwh_create_date DATETIME2 DEFAULT GETDATE()
);
GO


/*
===============================================================================
BRONZE LAYER - LOG TABLE SETUP
===============================================================================
Purpose:
    Creates a simple logging table to track ETL execution results for each table.
    This table stores success/failure status and execution details.

Usage:
    Run this script once to create the logging infrastructure in Bronze table.
===============================================================================
*/

PRINT '=== Creating Logging Bronze Table ===';

IF OBJECT_ID('bronze.etl_execution_log', 'U') IS NOT NULL
    DROP TABLE bronze.etl_execution_log;
GO

CREATE TABLE bronze.etl_execution_log (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    table_name NVARCHAR(100) NOT NULL,           -- Target table name
    source_file NVARCHAR(500) NOT NULL,          -- Source CSV file path
    status NVARCHAR(20) NOT NULL,                -- SUCCESS / ERROR
    rows_affected INT DEFAULT 0,                 -- Number of rows loaded
    execution_time_seconds INT DEFAULT 0,        -- Duration in seconds
    error_message NVARCHAR(MAX) NULL,            -- Error details if failed
    executed_date DATETIME DEFAULT GETDATE(),    -- Execution timestamp
    executed_by NVARCHAR(100) DEFAULT SUSER_NAME() -- User who executed
);
GO
