"""
Sample data fixtures for testing
"""

# Sample customer data
SAMPLE_CUSTOMERS = [
    {
        "customer_id": 1001,
        "customer_key": "CUST001",
        "first_name": "John",
        "last_name": "Doe",
        "country": "USA",
        "marital_status": "Married",
        "gender": "Male"
    },
    {
        "customer_id": 1002,
        "customer_key": "CUST002", 
        "first_name": "Jane",
        "last_name": "Smith",
        "country": "Canada",
        "marital_status": "Single",
        "gender": "Female"
    }
]

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "product_id": 2001,
        "product_key": "PROD001",
        "product_name": "Test Bike Model A",
        "category": "Bikes",
        "subcategory": "Mountain Bikes",
        "cost": 500,
        "product_line": "Mountain"
    },
    {
        "product_id": 2002,
        "product_key": "PROD002",
        "product_name": "Test Component X",
        "category": "Components", 
        "subcategory": "Wheels",
        "cost": 100,
        "product_line": "Standard"
    }
]

# Sample sales data
SAMPLE_SALES = [
    {
        "order_number": "SO999001",
        "customer_id": 1001,
        "product_key": "PROD001",
        "order_date": "2024-01-15",
        "shipping_date": "2024-01-20",
        "due_date": "2024-02-15",
        "sales_amount": 500,
        "quantity": 1,
        "price": 500
    },
    {
        "order_number": "SO999002",
        "customer_id": 1002,
        "product_key": "PROD002", 
        "order_date": "2024-01-16",
        "shipping_date": "2024-01-21",
        "due_date": "2024-02-16",
        "sales_amount": 200,
        "quantity": 2,
        "price": 100
    }
]

# Data quality test cases
DATA_QUALITY_TESTS = [
    {
        "test_name": "null_customer_id",
        "description": "Test handling of null customer IDs",
        "invalid_data": {
            "customer_id": None,
            "customer_key": "CUST999",
            "first_name": "Test",
            "last_name": "User"
        }
    },
    {
        "test_name": "duplicate_customer_key", 
        "description": "Test handling of duplicate customer keys",
        "invalid_data": {
            "customer_id": 9999,
            "customer_key": "CUST001",  # Duplicate key
            "first_name": "Duplicate",
            "last_name": "Customer"
        }
    },
    {
        "test_name": "negative_sales_amount",
        "description": "Test handling of negative sales amounts",
        "invalid_data": {
            "order_number": "SO999999",
            "sales_amount": -100,  # Invalid negative amount
            "quantity": 1,
            "price": 100
        }
    }
]

# Performance test data
PERFORMANCE_TEST_QUERIES = [
    {
        "name": "simple_count",
        "query": "SELECT COUNT(*) FROM gold.fact_sales",
        "expected_max_time": 1.0
    },
    {
        "name": "group_by_country",
        "query": """
            SELECT country, COUNT(*) 
            FROM gold.dim_customers 
            GROUP BY country
        """,
        "expected_max_time": 2.0
    },
    {
        "name": "complex_join",
        "query": """
            SELECT c.country, p.category, SUM(f.sales_amount)
            FROM gold.fact_sales f
            JOIN gold.dim_customers c ON f.customer_key = c.customer_key
            JOIN gold.dim_products p ON f.product_key = p.product_key
            GROUP BY c.country, p.category
        """,
        "expected_max_time": 5.0
    }
]