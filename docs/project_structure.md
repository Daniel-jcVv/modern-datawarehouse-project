# Project Structure Documentation

## Modern Data Warehouse - Enterprise Directory Organization

This document explains the professional directory structure implemented for our Modern Data Warehouse project. The organization follows industry best practices and enterprise standards for maintainability, scalability, and collaboration.

## Directory Structure Overview

```
dwh-portfolio/
│
├── src/                        # Source code (production)
│   ├── pipelines/             # ETL pipeline orchestrators
│   │   ├── bronze_pipeline.py # Bronze layer main pipeline
│   │   ├── silver_pipeline.py # Silver layer pipeline (coming soon)
│   │   └── gold_pipeline.py   # Gold layer pipeline (coming soon)
│   │
│   ├── etl/                   # ETL business logic
│   │   ├── bronze_layer/      # Bronze layer processors
│   │   ├── silver_layer/      # Silver layer transformations
│   │   └── gold_layer/        # Gold layer aggregations
│   │
│   ├── connectors/            # Database and external connections
│   ├── validators/            # Data quality and validation
│   ├── models/                # Data models and schemas
│   └── config/                # Configuration files
│
├── scripts/                    # Utility and operational scripts
│   ├── diagnostics/           # System health and debugging
│   │   └── system_check.py   # Comprehensive environment verification
│   │
│   ├── temp/                  # Temporary scripts and debugging tools
│   │   ├── debug_schema.py   # Schema debugging utility
│   │   ├── test_paths.py     # Path resolution testing
│   │   └── *.old              # Backup files (ignored by git)
│   │
│   └── deployment/            # Deployment and setup scripts
│
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── performance/           # Performance tests
│
├── data_sets/                  # Source data files
│   ├── source_crm/            # CRM system data
│   └── source_erp/            # ERP system data
│
├── sql/                        # SQL scripts and DDL
│   ├── ddl/                   # Data Definition Language
│   ├── procedures/            # Stored procedures
│   └── migrations/            # Schema migrations
│
├── docker/                     # Docker configurations
├── docs/                       # Documentation
│
├── run_bronze_pipeline.py      # Convenience runner for Bronze ETL
├── run_system_check.py         # Convenience runner for diagnostics
├── Makefile                    # Command shortcuts (make bronze, make check)
└── README.md                   # Project documentation
```

## Key Design Decisions

### 1. Source Code Organization (`src/`)
The `src/` directory contains all production code, organized by functional area rather than technical layer. This makes it easy to find code related to specific business capabilities.

### 2. Pipeline Separation (`src/pipelines/`)
ETL pipelines are separated from their implementation logic. Pipelines orchestrate the execution flow, while the actual transformation logic lives in `src/etl/`. This separation allows for:
- Clear entry points for each data layer
- Easy testing of individual components
- Flexibility to change orchestration without affecting business logic

### 3. Scripts Organization (`scripts/`)
Utility scripts are organized by purpose:
- `diagnostics/`: Production-ready diagnostic tools
- `temp/`: Temporary debugging scripts (not committed to git)
- `deployment/`: Setup and deployment automation

### 4. Convenience Runners
Files like `run_bronze_pipeline.py` in the root provide simple entry points while keeping the actual implementation properly organized. This gives us the best of both worlds: clean organization and ease of use.

## How to Run Pipelines

From the project root, you have multiple options:

### Option 1: Using Make (Recommended)
```bash
make check   # Run system health checks
make bronze  # Run Bronze pipeline
make silver  # Run Silver pipeline (coming soon)
make gold    # Run Gold pipeline (coming soon)
```

### Option 2: Using Convenience Scripts
```bash
python run_system_check.py      # Check system health
python run_bronze_pipeline.py    # Run Bronze ETL
```

### Option 3: Direct Execution
```bash
python src/pipelines/bronze_pipeline.py    # Run from organized location
python scripts/diagnostics/system_check.py # Run diagnostics directly
```

## Benefits of This Structure

1. **Professional Appearance**: Immediately recognizable as an enterprise-grade project
2. **Scalability**: Easy to add new pipelines, layers, and components
3. **Maintainability**: Clear separation of concerns makes debugging easier
4. **Collaboration**: Team members can quickly find and understand code
5. **Testing**: Organized structure facilitates comprehensive testing
6. **Documentation**: Self-documenting through clear naming and organization

## Migration Notes

The following files were reorganized from the project root:
- `bronze_pipeline.py` → `src/pipelines/bronze_pipeline.py`
- `system_check.py` → `scripts/diagnostics/system_check.py`
- Temporary debug scripts → `scripts/temp/`

All path references have been updated to work from their new locations.

## Next Steps

1. Implement Silver layer pipeline in `src/pipelines/silver_pipeline.py`
2. Add comprehensive unit tests in `tests/unit/`
3. Create deployment scripts in `scripts/deployment/`
4. Add API layer in `src/api/` for data access

---

Last Updated: 2025-01-12
Author: Daniel G. B.
