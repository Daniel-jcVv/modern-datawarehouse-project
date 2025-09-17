"""
Pipeline Runner - Single Entry Point for All ETL Operations
This script provides a unified interface to run different pipeline stages

Usage: python run_pipeline.py [action]
Where action can be: check, bronze, silver, gold, help
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def check_database_exists():
    """Verify DataWarehouse database exists before running pipelines"""
    try:
        import os
        import pyodbc
        from dotenv import load_dotenv
        
        load_dotenv()
        
        host = os.getenv('SQL_SERVER_HOST', 'localhost')
        port = os.getenv('SQL_SERVER_PORT', '1433')
        user = os.getenv('SQL_SERVER_USER', 'sa')
        password = os.getenv('SQL_SERVER_PASSWORD')
        
        # Connect to master database to check if DataWarehouse exists
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE=master;"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        with pyodbc.connect(connection_string, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases WHERE name = 'DataWarehouse'")
            result = cursor.fetchone()
            return result is not None
            
    except Exception:
        return False


def show_usage():
    """Display usage instructions when no arguments provided"""
    print("\n" + "=" * 60)
    print("Modern Data Warehouse - Pipeline Runner")
    print("=" * 60)
    print("\nUsage: python run_pipeline.py [action]")
    print("\nAvailable actions:")
    print("  check   - Run system health checks")
    print("  bronze  - Execute Bronze layer ETL pipeline")
    print("  silver  - Execute Silver layer transformations")
    print("  gold    - Execute Gold layer aggregations")
    print("  help    - Show this help message")
    print("\nExamples:")
    print("  python run_pipeline.py check   # Verify system is ready")
    print("  python run_pipeline.py bronze  # Run Bronze ETL")
    print("\nPrerequisites:")
    print("  Run 'python setup.py' first to initialize database and tables")
    print("\n" + "=" * 60)


def run_check():
    """Execute system health check"""
    print("\nRunning system health check...")
    print("-" * 40)
    try:
        from scripts.diagnostics.system_check import main
        return main()
    except Exception as e:
        print(f"Error running system check: {e}")
        return False


def run_bronze():
    """Execute Bronze layer pipeline"""
    print("\nStarting Bronze Layer ETL Pipeline...")
    print("-" * 40)
    
    # Check if database exists before attempting ETL
    if not check_database_exists():
        print("ERROR: DataWarehouse database not found")
        print("SOLUTION: Run 'python setup.py' to initialize the database and tables")
        print("Then retry: python run_pipeline.py bronze")
        return False
    
    try:
        from src.pipelines.bronze_pipeline import main
        main()
        return True
    except Exception as e:
        print(f"Error running Bronze pipeline: {e}")
        return False


def run_silver():
    """Execute Silver layer pipeline with quality checks"""
    print("\nStarting Silver Layer ETL Pipeline...")
    print("-" * 40)
    
    # Check if database exists before attempting ETL
    if not check_database_exists():
        print("ERROR: DataWarehouse database not found")
        print("SOLUTION: Run 'python setup.py' to initialize the database and tables")
        print("Then retry: python run_pipeline.py silver")
        return False
    
    try:
        # Import and run silver procedures using modern pipeline
        from src.pipelines.silver_pipeline import main as silver_main
        from loguru import logger
        
        # Execute silver pipeline
        logger.info("Executing Silver layer pipeline...")
        silver_main()
        logger.success("Silver layer pipeline completed")
        
        return True
            
    except Exception as e:
        print(f"Error running Silver pipeline: {e}")
        return False


def run_gold():
    """Execute Gold layer pipeline"""
    print("\nStarting Gold Layer Pipeline (Star Schema)...")
    print("-" * 40)
    
    # Check if database exists before attempting ETL
    if not check_database_exists():
        print("ERROR: DataWarehouse database not found")
        print("SOLUTION: Run 'python setup.py' to initialize the database and tables")
        print("Then retry: python run_pipeline.py gold")
        return False
    
    try:
        from src.pipelines.gold_pipeline import main
        success = main()
        if success:
            print("Gold layer Star Schema created successfully!")
        return success
    except Exception as e:
        print(f"Error running Gold pipeline: {e}")
        return False


def main():
    """Main entry point - route to appropriate pipeline based on argument"""
    
    # Check if user provided an argument
    if len(sys.argv) < 2:
        show_usage()
        return 0
    
    # Get the action requested (convert to lowercase for flexibility)
    action = sys.argv[1].lower()
    
    # Route to appropriate function based on action
    actions = {
        'check': run_check,
        'bronze': run_bronze,
        'silver': run_silver,
        'gold': run_gold,
        'help': show_usage,
        '--help': show_usage,
        '-h': show_usage
    }
    
    # Execute the requested action
    if action in actions:
        result = actions[action]()
        # Return 0 for success, 1 for failure (Unix convention)
        return 0 if result is not False else 1
    else:
        print(f"\n❌ Error: '{sys.argv[1]}' is not a valid action")
        print(f"   Valid actions: {', '.join(actions.keys())}")
        show_usage()
        return 1


if __name__ == "__main__":
    # Exit with appropriate code (0 = success, 1 = error)
    exit_code = main()
    sys.exit(exit_code)
