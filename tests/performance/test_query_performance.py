"""
Performance tests for data warehouse queries
"""
import pytest
import time
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestQueryPerformance:
    """Test query performance across layers"""
    
    def test_gold_analytical_query_performance(self, database_connection):
        """Test that analytical queries execute within acceptable time"""
        # Complex analytical query
        query = """
        SELECT 
            c.country,
            p.category,
            COUNT(*) as order_count,
            SUM(f.sales_amount) as total_sales,
            AVG(f.sales_amount) as avg_sales
        FROM gold.fact_sales f
        JOIN gold.dim_customers c ON f.customer_key = c.customer_key
        JOIN gold.dim_products p ON f.product_key = p.product_key
        GROUP BY c.country, p.category
        ORDER BY total_sales DESC
        """
        
        start_time = time.time()
        result = database_connection.execute_query(query)
        execution_time = time.time() - start_time
        
        # Should execute in under 5 seconds for good performance
        assert execution_time < 5.0, f"Query too slow: {execution_time:.3f} seconds"
        assert result is not None
        assert len(result) > 0
    
    def test_dimension_lookup_performance(self, database_connection):
        """Test dimension table lookup performance"""
        queries = [
            "SELECT COUNT(*) FROM gold.dim_customers",
            "SELECT COUNT(*) FROM gold.dim_products",
            "SELECT COUNT(*) FROM gold.fact_sales"
        ]
        
        for query in queries:
            start_time = time.time()
            result = database_connection.execute_query(query)
            execution_time = time.time() - start_time
            
            # Dimension lookups should be very fast (< 1 second)
            assert execution_time < 1.0, f"Dimension query too slow: {execution_time:.3f} seconds"
            assert result is not None
    
    def test_large_aggregation_performance(self, database_connection):
        """Test performance of large aggregations"""
        query = """
        SELECT 
            YEAR(order_date) as year,
            MONTH(order_date) as month,
            COUNT(*) as total_orders,
            SUM(sales_amount) as total_revenue,
            COUNT(DISTINCT customer_key) as unique_customers,
            COUNT(DISTINCT product_key) as unique_products
        FROM gold.fact_sales
        WHERE order_date >= '2020-01-01'
        GROUP BY YEAR(order_date), MONTH(order_date)
        ORDER BY year DESC, month DESC
        """
        
        start_time = time.time()
        result = database_connection.execute_query(query)
        execution_time = time.time() - start_time
        
        # Large aggregations should complete in reasonable time (< 10 seconds)
        assert execution_time < 10.0, f"Aggregation too slow: {execution_time:.3f} seconds"
        assert result is not None
    
    @pytest.mark.parametrize("table", [
        "bronze.crm_sales_details",
        "silver.crm_sales_details", 
        "gold.fact_sales"
    ])
    def test_record_count_performance(self, database_connection, table):
        """Test record counting performance across layers"""
        query = f"SELECT COUNT(*) FROM {table}"
        
        start_time = time.time()
        result = database_connection.execute_query(query)
        execution_time = time.time() - start_time
        
        # Count queries should be fast (< 2 seconds)
        assert execution_time < 2.0, f"Count query too slow for {table}: {execution_time:.3f} seconds"
        assert result is not None
        assert result[0][0] >= 0  # Should return a non-negative count