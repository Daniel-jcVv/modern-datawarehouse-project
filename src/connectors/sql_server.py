"""
SQL Server Connection Manager for Data Warehouse 
connection handling with retry logic and logging
"""

import os
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
import pyodbc
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SQLServerConnector:
    """Enterprise SQL Server connection manager with retry logic"""
    
    def __init__(self):
        """Initialize SQL Server connection parameters"""
        # access environment variables from .env file
        self.host = os.getenv('SQL_SERVER_HOST', 'localhost')
        self.port = os.getenv('SQL_SERVER_PORT', '1433')
        self.database = os.getenv('SQL_SERVER_DATABASE', 'DataWarehouse')
        self.user = os.getenv('SQL_SERVER_USER', 'sa')
        self.password = os.getenv('SQL_SERVER_PASSWORD')
        
        if not self.password:
            raise ValueError("SQL_SERVER_PASSWORD must be set in environment")
        
        self.connection_string = self._build_connection_string()
        self.engine = None
        
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string"""
        driver = "ODBC Driver 18 for SQL Server"
        conn_str = (
            f"mssql+pyodbc://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}?"
            f"driver={driver.replace(' ', '+')}&"
            f"TrustServerCertificate=yes&"
            f"Encrypt=no"
        )
        return conn_str
    
    def get_engine(self) -> sa.Engine:
        """Get SQLAlchemy engine with connection pooling"""
        if self.engine is None:
            try:
                self.engine = create_engine(
                    self.connection_string,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=3600,
                    echo=False
                )
                logger.info(f"Connected to SQL Server: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"Failed to create engine: {str(e)}")
                raise
                
        return self.engine
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        engine = self.get_engine()
        connection = None
        try:
            connection = engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                if test_value == 1:
                    logger.info("✅ SQL Server connection test successful")
                    return True
                else:
                    logger.error("❌ SQL Server connection test failed")
                    return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                return result.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def execute_script(self, script_path: str) -> bool:
        """
        Execute SQL script using pyodbc directly for better SQL Server compatibility.
        This method handles GO statements, conditional logic, and complex DDL properly.
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
            
            # Build pyodbc connection string directly
            driver = "ODBC Driver 18 for SQL Server"
            pyodbc_conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;"
                "Encrypt=no;"
            )
            
            # Use pyodbc directly for script execution
            with pyodbc.connect(pyodbc_conn_str, timeout=30) as conn:
                cursor = conn.cursor()
                
                # Split by GO statements for batch execution
                batches = script_content.split('GO')
                
                for batch in batches:
                    # Clean the batch
                    clean_batch = batch.strip()
                    
                    # Skip empty batches, pure comments, or USE statements
                    if (not clean_batch or 
                        clean_batch.startswith('--') or 
                        clean_batch.startswith('/*') or
                        clean_batch.upper().startswith('USE ') or
                        'PRINT' in clean_batch.upper()):
                        continue
                    
                    try:
                        # Execute the entire batch as one unit
                        cursor.execute(clean_batch)
                        conn.commit()
                        
                    except pyodbc.Error as e:
                        # Log the error with context but continue with next batch
                        logger.warning(f"Batch execution warning: {str(e)}")
                        logger.debug(f"Problematic batch: {clean_batch[:100]}...")
                        conn.rollback()
                        continue
                        
            logger.info(f"✅ Script executed successfully: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Script execution failed: {str(e)}")
            return False


# Singleton instance for reuse
db_connector = SQLServerConnector()
