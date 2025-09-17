"""
pytest configuration and shared fixtures for all tests
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def database_connection():
    """Shared database connection for integration tests"""
    from src.connectors.sql_server import db_connector
    
    # Test if database is available
    if not db_connector.test_connection():
        pytest.skip("Database not available for testing")
    
    return db_connector

@pytest.fixture(scope="function")
def sample_data():
    """Sample test data for unit tests"""
    return {
        "customers": [
            {"customer_id": 1, "name": "Test Customer 1"},
            {"customer_id": 2, "name": "Test Customer 2"}
        ],
        "products": [
            {"product_id": 1, "name": "Test Product 1", "price": 100},
            {"product_id": 2, "name": "Test Product 2", "price": 200}
        ]
    }

@pytest.fixture(scope="function")
def temp_directory(tmp_path):
    """Temporary directory for test files"""
    test_dir = tmp_path / "dwh_tests"
    test_dir.mkdir(exist_ok=True)
    return test_dir