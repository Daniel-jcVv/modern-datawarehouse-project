"""
Integration tests for complete pipeline flow
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestPipelineIntegration:
    """Test complete pipeline integration"""
    
    def test_database_connectivity(self, database_connection):
        """Test that database connection works"""
        result = database_connection.execute_query("SELECT 1 as test_column")
        
        assert result is not None
        assert len(result) == 1
        assert result[0][0] == 1
    
    def test_bronze_to_silver_flow(self, database_connection):
        """Test Bronze to Silver data flow"""
        # Check if bronze tables exist
        bronze_tables = database_connection.execute_query("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'bronze'
        """)
        
        assert bronze_tables is not None
        assert len(bronze_tables) > 0
        
        # Check if silver tables exist
        silver_tables = database_connection.execute_query("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'silver'
        """)
        
        assert silver_tables is not None
        assert len(silver_tables) > 0
    
    def test_gold_views_accessibility(self, database_connection):
        """Test that Gold layer views are accessible"""
        gold_views = database_connection.execute_query("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.VIEWS 
            WHERE TABLE_SCHEMA = 'gold'
        """)
        
        assert gold_views is not None
        
        # Test that main views exist
        view_names = [view[0] for view in gold_views]
        expected_views = ['dim_customers', 'dim_products', 'fact_sales']
        
        for expected_view in expected_views:
            assert expected_view in view_names, f"Missing view: {expected_view}"
    
    def test_star_schema_integrity(self, database_connection):
        """Test star schema referential integrity"""
        # Test fact-dimension relationship
        integrity_query = """
        SELECT COUNT(*) as total_sales,
               COUNT(pr.product_key) as with_product,
               COUNT(cu.customer_key) as with_customer
        FROM gold.fact_sales fs
        LEFT JOIN gold.dim_products pr ON fs.product_key = pr.product_key
        LEFT JOIN gold.dim_customers cu ON fs.customer_key = cu.customer_key
        """
        
        result = database_connection.execute_query(integrity_query)
        
        assert result is not None
        assert len(result) == 1
        
        total, with_product, with_customer = result[0]
        
        # Should have high integrity rates (>95%)
        if total > 0:
            product_integrity = (with_product / total) * 100
            customer_integrity = (with_customer / total) * 100
            
            assert product_integrity >= 95, f"Product integrity too low: {product_integrity}%"
            assert customer_integrity >= 95, f"Customer integrity too low: {customer_integrity}%"