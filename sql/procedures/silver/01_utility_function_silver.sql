
/*
===============================================================================
FILE: 01_utility_functions.sql
===============================================================================
All utility functions grouped together for easy maintenance.
Improved with robust error handling using dynamic SQL for CREATE OR ALTER to allow TRY...CATCH,
and detailed timing measurements for each function deployment according to best practices.
This ensures that errors during script execution are captured and reported without halting the entire script,
and provides performance insights into the deployment process.
===============================================================================
*/

SET NOCOUNT ON;
GO

-- Cleans special characters from text fields.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.clean_special_chars(@input NVARCHAR(MAX))
RETURNS NVARCHAR(MAX)
AS
BEGIN
    RETURN TRIM(REPLACE(REPLACE(REPLACE(REPLACE(ISNULL(@input, ''''), CHAR(9), ''''), CHAR(10), ''''), CHAR(13), ''''), CHAR(160), ''''));
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.clean_special_chars created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.clean_special_chars: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO

-- Standardizes gender values.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.clean_gender(@input NVARCHAR(50))
RETURNS NVARCHAR(10)
AS
BEGIN
    DECLARE @cleaned NVARCHAR(50) = UPPER(dbo.clean_special_chars(@input));
    RETURN CASE
        WHEN @cleaned IN (''F'', ''FEM'', ''FEMALE'', ''W'', ''WOMAN'') THEN ''Female''
        WHEN @cleaned IN (''M'', ''MALE'', ''MASC'', ''MAN'') THEN ''Male''
        WHEN @input IS NULL OR @cleaned IN ('''', ''N/A'', ''NA'', ''NULL'', ''UNKNOWN'') THEN ''n/a''
        ELSE ''n/a''
    END;
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.clean_gender created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.clean_gender: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO

-- Standardizes marital status.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.clean_marital_status(@input NVARCHAR(50))
RETURNS NVARCHAR(10)
AS
BEGIN
    DECLARE @cleaned NVARCHAR(50) = UPPER(dbo.clean_special_chars(@input));
    RETURN CASE
        WHEN @cleaned IN (''S'', ''SINGLE'') THEN ''Single''
        WHEN @cleaned IN (''M'', ''MARRIED'') THEN ''Married''
        ELSE ''n/a''
    END;
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.clean_marital_status created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.clean_marital_status: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO

-- Standardizes country codes and names.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.clean_country(@input NVARCHAR(100))
RETURNS NVARCHAR(50)
AS
BEGIN
    DECLARE @cleaned NVARCHAR(100) = UPPER(dbo.clean_special_chars(@input));
    RETURN CASE
        WHEN @cleaned IN (''DE'', ''DEU'', ''GERMANY'') THEN ''Germany''
        WHEN @cleaned IN (''US'', ''USA'', ''UNITED STATES'', ''AMERICA'') THEN ''United States''
        WHEN @cleaned IN (''CA'', ''CAN'', ''CANADA'') THEN ''Canada''
        WHEN @cleaned IN (''UK'', ''GB'', ''UNITED KINGDOM'', ''ENGLAND'') THEN ''United Kingdom''
        WHEN @cleaned IN (''FR'', ''FRA'', ''FRANCE'') THEN ''France''
        WHEN @cleaned IN (''ES'', ''ESP'', ''SPAIN'') THEN ''Spain''
        WHEN @cleaned IN (''MX'', ''MEX'', ''MEXICO'') THEN ''Mexico''
        WHEN @input IS NULL OR @cleaned IN ('''', ''N/A'', ''NA'', ''NULL'') THEN ''n/a''
        ELSE ''n/a''
    END;
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.clean_country created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.clean_country: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO

-- Standardizes product line codes.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.clean_product_line(@input NVARCHAR(50))
RETURNS NVARCHAR(20)
AS
BEGIN
    DECLARE @cleaned NVARCHAR(50) = UPPER(dbo.clean_special_chars(@input));
    RETURN CASE
        WHEN @cleaned = ''M'' THEN ''Mountain''
        WHEN @cleaned = ''R'' THEN ''Road''
        WHEN @cleaned = ''S'' THEN ''Other Sales''
        WHEN @cleaned = ''T'' THEN ''Touring''
        ELSE ''n/a''
    END;
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.clean_product_line created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.clean_product_line: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO

-- Converts 8-digit integer dates to DATE format.
DECLARE @start DATETIME = GETDATE();
DECLARE @sql NVARCHAR(MAX) = N'
CREATE OR ALTER FUNCTION dbo.convert_int_to_date(@date_int INT)
RETURNS DATE
AS
BEGIN
    IF @date_int IS NULL OR @date_int <= 0 OR LEN(CAST(@date_int AS VARCHAR(8))) <> 8
        RETURN NULL;

    RETURN TRY_CAST(
        SUBSTRING(CAST(@date_int AS VARCHAR(8)), 1, 4) + ''-'' +
        SUBSTRING(CAST(@date_int AS VARCHAR(8)), 5, 2) + ''-'' +
        SUBSTRING(CAST(@date_int AS VARCHAR(8)), 7, 2) AS DATE
    );
END
';
BEGIN TRY
    EXEC sp_executesql @sql;
    PRINT 'Function dbo.convert_int_to_date created successfully in ' + CAST(DATEDIFF(millisecond, @start, GETDATE()) AS VARCHAR(20)) + ' ms.';
END TRY
BEGIN CATCH
    PRINT 'Error creating function dbo.convert_int_to_date: ' + ERROR_MESSAGE() + ' (Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10)) + ')';
END CATCH
GO
