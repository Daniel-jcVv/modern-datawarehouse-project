# Enterprise Data Warehouse Architecture

## Overview
This project implements a **Medallion Architecture** (Bronze-Silver-Gold) data warehouse using modern enterprise patterns and technologies. The architecture follows industry best practices for data engineering, quality assurance, and scalability.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BRONZE LAYER  │    │  SILVER LAYER   │    │   GOLD LAYER    │
│   (Raw Data)    │───▶│ (Cleaned Data)  │───▶│ (Analytics)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Raw CSV Files │    │ • Data Quality  │    │ • Star Schema   │
│ • Direct Ingestion│   │ • Transformations│   │ • BI Ready      │
│ • 116K+ Records │    │ • Deduplication │    │ • Fact Tables   │
│ • BULK INSERT   │    │ • Type Casting  │    │ • Dimensions    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Core Technologies
- **Database**: Microsoft SQL Server 2022 (Docker Container)
- **ETL Engine**: Python 3.11+ with enterprise libraries
- **Container Platform**: Docker with persistent volumes
- **Version Control**: Git with branching strategy

### Python Stack
```python
# Core Data Engineering
pandas>=2.0.0          # Data manipulation
sqlalchemy>=2.0.0      # Database ORM
pyodbc>=4.0.34         # SQL Server connectivity

# Quality Assurance
pydantic>=2.0.0        # Data validation
loguru>=0.7.0          # Enterprise logging

# Development
pytest>=7.4.0          # Testing framework
black>=23.0.0          # Code formatting
```

## Layer Architecture Details

### Bronze Layer (Raw Data)
**Purpose**: Ingest raw data with minimal transformation

**Implementation**:
- **Data Volume**: 116,294 records across 6 source files
- **Storage**: Bronze schema tables with original data types
- **ETL Method**: Dual approach (SQL BULK INSERT + Python ETL)
- **Monitoring**: Complete execution logging in `bronze.etl_execution_log`

**Tables**:
```sql
bronze.crm_cust_info        # Customer information (18,490 records)
bronze.crm_prd_info         # Product catalog (397 records)  
bronze.crm_sales_details    # Sales transactions (89,833 records)
bronze.erp_cust_az12        # ERP customer data
bronze.erp_loc_a101         # Location data
bronze.erp_px_cat_g1v2      # Product categories
```

**Quality Checks**: 
- Table existence validation
- Record count verification
- Data type integrity

### Silver Layer (Cleaned Data)
**Purpose**: Apply business rules and data quality transformations

**Implementation**:
- **Data Volume**: 116,290 records (99.97% retention rate)
- **Storage**: Silver schema with clean, validated data
- **ETL Method**: Stored procedures with comprehensive error handling
- **Quality**: Advanced validation rules and deduplication

**Tables**:
```sql
silver.crm_cust_info        # Cleaned customer data
silver.crm_prd_info         # Validated product information
silver.crm_sales_details    # Processed sales transactions
silver.erp_cust_az12        # Enriched ERP customer data
silver.erp_loc_a101         # Standardized location data
silver.erp_px_cat_g1v2      # Normalized product categories
```

**Transformations**:
- Data type standardization
- Null value handling
- Business rule validation
- Duplicate detection and removal

### Gold Layer (Analytics Ready)
**Purpose**: Business intelligence and analytics consumption

**Implementation**:
- **Data Volume**: 108,720 records in star schema format
- **Storage**: Optimized views for analytical queries
- **Schema**: Star schema with fact and dimension tables
- **Performance**: Sub-second query execution for BI tools

**Star Schema Components**:
```sql
-- Dimension Tables
gold.dim_customers      # Customer dimension (18,490 records)
  ├─ customer_key       # Surrogate key
  ├─ customer_id        # Business key
  ├─ first_name, last_name
  ├─ country, marital_status
  └─ gender, birthdate

gold.dim_products       # Product dimension (397 records)
  ├─ product_key        # Surrogate key
  ├─ product_id         # Business key
  ├─ product_name, category
  ├─ subcategory, cost
  └─ product_line, start_date

-- Fact Table
gold.fact_sales         # Sales fact table (89,833 records)
  ├─ order_number       # Transaction ID
  ├─ product_key        # FK to dim_products
  ├─ customer_key       # FK to dim_customers
  ├─ order_date, shipping_date
  ├─ sales_amount, quantity
  └─ price
```

## ETL Pipeline Architecture

### Pipeline Orchestration
```bash
# Complete Pipeline Execution
python setup.py              # Infrastructure setup
python run_pipeline.py bronze # Bronze layer ETL
python run_pipeline.py silver # Silver layer transformations  
python run_pipeline.py gold   # Gold layer star schema
```

### Dual Implementation Pattern
**Bronze Layer**: 
- **Option A**: SQL Server BULK INSERT (optimized for large files)
- **Option B**: Python pandas ETL (flexible transformations)
- **Fallback**: Automatic fallback between methods

**Silver Layer**:
- **Primary**: SQL Server stored procedures
- **Secondary**: Python transformations
- **Quality**: Comprehensive data validation

**Gold Layer**:
- **Views**: SQL Server views for real-time analytics
- **Caching**: Optimized for BI tool consumption

## Quality Assurance Framework

### Multi-Layer Validation
**Bronze Layer**:
- File existence and accessibility
- Schema validation
- Record count verification

**Silver Layer**:
- Data quality rules enforcement
- Business rule validation
- Referential integrity checks

**Gold Layer**:
- Star schema integrity validation
- Dimension uniqueness verification
- Fact-dimension relationship validation

### Quality Metrics
```
Gold Layer Quality Validation:
├─ 12/12 quality checks passed (100% success rate)
├─ Python-based validations: 9/9 passed
├─ SQL-based integrity checks: 3/3 passed
├─ Star schema integrity: 100% fact-dimension relationships
└─ Execution time: ~1 second
```

## Features

### Monitoring & Logging
- **Execution Tracking**: Complete audit trail in `bronze.etl_execution_log`
- **Performance Metrics**: Execution times and record counts
- **Error Handling**: Comprehensive error logging with stack traces
- **Quality Reports**: Automated validation reporting

### Security & Configuration
- **Environment Variables**: Secure configuration management
- **Connection Pooling**: Optimized database connections
- **Error Isolation**: Graceful error handling without system crashes

### Scalability
- **Docker Containers**: Horizontal scaling capability
- **Modular Design**: Independent layer processing
- **Parallel Processing**: Concurrent file processing support

## Performance Metrics

### Processing Performance
```
Layer           Records    Processing Time    Throughput
Bronze          116,294    ~31 seconds       3,750 records/sec
Silver          116,290    ~30 seconds       3,876 records/sec  
Gold            108,720    ~1 second         108K records/sec
```

### Quality Assurance
```
Metric                    Value
Data Retention (B→S)      99.97%
Star Schema Integrity     100%
Quality Check Success     100%
Pipeline Reliability      100%
```

## Development Methodology

### Enterprise Development Patterns
- **Medallion Architecture**: Industry-standard data lake pattern
- **Dual Implementation**: Procedure + Python ETL approaches
- **Quality-First**: Comprehensive testing at each layer
- **Documentation-Driven**: Complete technical documentation

### Code Quality Standards
- **PEP 8 Compliance**: Professional Python code formatting
- **Error Handling**: Comprehensive exception management
- **Logging**: Enterprise-grade structured logging
- **Testing**: Automated quality validation

## Deployment Architecture

### Container Strategy
```dockerfile
# SQL Server Container
- Image: mcr.microsoft.com/mssql/server:2022-latest
- Persistent Volumes: Database + Log files
- Network: Internal Docker network
- Security: Environment-based authentication

# ETL Runtime Environment  
- Python 3.11+ with enterprise libraries
- Volume mounts for data files
- Configuration via environment variables
```

### Infrastructure Requirements
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM for SQL Server container
- **Storage**: 20GB+ for database and logs
- **Network**: Internal Docker network for security

## Business Value

### Analytics Capabilities
- **Real-time BI**: Sub-second query performance
- **Data Integrity**: 100% referential integrity maintained
- **Scalability**: Designed for enterprise growth
- **Flexibility**: Multiple consumption patterns supported

### Technical Excellence
- **Modern Stack**: Industry-standard technologies
- **Best Practices**: Enterprise development patterns
- **Maintainability**: Clean, documented, testable code
- **Reliability**: Comprehensive error handling and monitoring

---

*This architecture demonstrates enterprise-grade data engineering capabilities suitable for production environments in financial services, telecommunications, and other data-intensive industries.*