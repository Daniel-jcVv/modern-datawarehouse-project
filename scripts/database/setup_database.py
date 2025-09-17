#!/usr/bin/env python3
"""
Create DataWarehouse Database - Enterprise Version
Handles SQL Server transaction limitations properly
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import pyodbc
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def create_database_enterprise():
    """Create database using proper SQL Server approach"""
    
    # Build connection string for master database
    host = os.getenv('SQL_SERVER_HOST', 'localhost')
    port = os.getenv('SQL_SERVER_PORT', '1433')
    user = os.getenv('SQL_SERVER_USER', 'sa')
    password = os.getenv('SQL_SERVER_PASSWORD')
    
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={host},{port};"
        f"DATABASE=master;"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    
    try:
        logger.info("Connecting to master database...")
        
        # Step 1: Create database (no transaction, autocommit)
        conn = pyodbc.connect(connection_string, autocommit=True)
        cursor = conn.cursor()
        
        # Check if DataWarehouse exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'DataWarehouse'")
        
        if cursor.fetchone():
            logger.info("DataWarehouse already exists")
        else:
            logger.info("Creating DataWarehouse database...")
            cursor.execute("CREATE DATABASE DataWarehouse")
            logger.info("DataWarehouse created successfully!")
        
        cursor.close()
        conn.close()
        
        # Step 2: Create schemas (separate connection to DataWarehouse)
        dw_connection_string = connection_string.replace("DATABASE=master", "DATABASE=DataWarehouse")
        
        logger.info("🔗 Connecting to DataWarehouse for schema creation...")
        conn = pyodbc.connect(dw_connection_string, autocommit=True)
        cursor = conn.cursor()
        
        # Create schemas
        schemas = ['bronze', 'silver', 'gold']
        for schema in schemas:
            # Check if schema exists
            cursor.execute(f"SELECT name FROM sys.schemas WHERE name = '{schema}'")
            if cursor.fetchone():
                logger.info(f"Schema '{schema}' already exists")
            else:
                cursor.execute(f"CREATE SCHEMA {schema}")
                logger.info(f"Schema '{schema}' created")
        
        cursor.close()
        conn.close()
        
        logger.info("Database and schemas setup completed!")
        return True
        
    except Exception as e:
        logger.error(f"Database creation error: {str(e)}")
        return False


def verify_setup():
    """Verify database and schemas were created"""
    try:
        # Test connection using our connector
        from src.connectors.sql_server import db_connector
        
        if db_connector.test_connection():
            logger.info("Connection to DataWarehouse successful!")
            
            # List schemas
            schemas = db_connector.execute_query("""
                SELECT name FROM sys.schemas 
                WHERE name IN ('bronze', 'silver', 'gold')
                ORDER BY name
            """)
            
            logger.info("Available schemas:")
            for schema in schemas:
                logger.info(f"   {schema[0]}")
                
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False


def main():
    """Main execution"""
    logger.info("🚀 Starting database setup (Enterprise Version)...")
    
    # Create database and schemas
    if create_database_enterprise():
        # Verify everything works
        if verify_setup():
            logger.info("Complete database setup successful!")
            logger.info("🔗 Ready to create Bronze layer tables")
            return True
    
    logger.error("Database setup failed")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
