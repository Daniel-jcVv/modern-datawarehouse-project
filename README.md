# Modern Data Warehouse with SQL Server & Medallion Architecture

![Status](https://img.shields.io/badge/Status-MVP%202%20Complete-brightgreen?style=flat-square)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2022%20Docker-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-orange?style=flat-square)
![Architecture](https://img.shields.io/badge/Architecture-Medallion-lightgrey?style=flat-square)

## 🏗️ Project Overview

Production-ready Data Warehouse implementation demonstrating **systematic Data Engineering problem-solving** through iterative architecture evolution. This project showcases real-world troubleshooting, infrastructure decision-making, and technical adaptability required in production environments.

## 🎯 Technical Evolution & Problem-Solving Journey

### Architecture Iteration Process

```
Initial Challenge → Technical Analysis → Solution Implementation → Validation
      ↓                    ↓                      ↓                ↓
  Port Conflicts    →  Docker Diagnostics  →  Port Strategy  →  Health Checks
  SQL Execution     →  SQLAlchemy Analysis →  PyODBC Switch  →  Script Success
  Integration       →  Connection Testing  →  Robust Design  →  End-to-End
```

### 🔧 Critical Technical Challenges Overcome

#### Challenge 1: Infrastructure Port Conflicts
**Problem:** Docker SQL Server conflicting with local installation on port 1433
```bash
# Error Encountered
Error: Bind for 0.0.0.0:1433 failed: port is already allocated
```

**Technical Analysis:** Used Docker logs and netstat to diagnose port allocation conflicts

**Solution Implemented:**
```yaml
# Before: Standard port mapping
ports:
  - "1433:1433"

# After: Strategic port isolation
ports:
  - "1434:1433"  # External 1434 → Internal 1433
```
**Business Impact:** Enables multiple SQL Server environments for development flexibility

#### Challenge 2: SQL Script Execution Engine Limitation
**Problem:** SQLAlchemy failing on complex DDL with conditional logic
```python
# Error Pattern
sqlalchemy.exc.ProgrammingError: There is already an object named 'table' in database
```

**Root Cause Analysis:** SQLAlchemy processing batches individually, losing conditional context

**Technical Solution:**
```python
# Before: SQLAlchemy text() execution
def execute_script(self, script_path: str) -> bool:
    with self.get_connection() as conn:
        conn.execute(text(clean_block))

# After: Direct PyODBC batch execution  
def execute_script(self, script_path: str) -> bool:
    with pyodbc.connect(pyodbc_conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(clean_batch)  # Maintains full context
```
**Technical Impact:** Enables complex DDL execution matching SQL Server behavior

## 📊 Current Architecture (MVP 2)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Docker Stack   │    │  Client Tools   │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • CSV Files     │───▶│ SQL Server 2022  │◀───│ • Python ETL    │
│ • Future APIs   │    │ Port: 1434       │    │ • Azure Data    │
│ • Streaming     │    │ Volume: Persist  │    │   Studio        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   DataWarehouse  │
                    ├──────────────────┤
                    │ • bronze schema  │
                    │ • silver schema  │
                    │ • gold schema    │
                    └──────────────────┘
```

## 🚀 Technology Stack Demonstrated

### Infrastructure & DevOps
- **Docker Compose**: Multi-service orchestration with health checks
- **SQL Server 2022**: Database engine in containers
- **Git Workflow**: MVP-based branching with semantic tagging

### Python Engineering
- **SQLAlchemy**: Connection pooling and ORM capabilities
- **PyODBC**: Direct database protocol for complex operations
- **Loguru**: Structured logging for observability
- **Pydantic**: Data validation and configuration management

### Database Engineering
- **Medallion Architecture**: Bronze-Silver-Gold layered approach
- **Schema Design**: Multi-tenant namespace organization
- **DDL Management**: Complex conditional logic execution
- **Connection Management**: Robust error handling and retry logic

## 📈 MVP Roadmap & Progress

- [x] **MVP 1**: Foundation Setup *(Completed)*
- [x] **MVP 2**: Docker Infrastructure + Bronze Layer *(Current)*
  - [x] Containerized SQL Server 2022
  - [x] Python integration with robust connection management
  - [x] Bronze schema with all tables operational
  - [x] Systematic troubleshooting and problem resolution
- [ ] **MVP 3**: ETL Pipelines + Silver Layer *(Next)*
  - [ ] Automated data transformation pipelines
  - [ ] Data quality validation framework
  - [ ] Error handling and monitoring
- [ ] **MVP 4**: Gold Layer + Analytics APIs *(Future)*
  - [ ] Dimensional modeling (star schema)
  - [ ] FastAPI endpoints for data consumption
  - [ ] Performance optimization and indexing

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- Git

### Setup
```bash
# Clone and setup
git clone [repository-url]
cd dwh-portfolio

# Start infrastructure
docker-compose up -d

# Verify health
docker-compose ps  # Should show "healthy"

# Initialize database
python setup.py

# Test integration
python test_docker_connection.py
```

## 🧪 Validation & Testing

### Infrastructure Validation
```bash
# Docker health check
docker-compose ps
# Expected: datawarehouse-sql-server (healthy)

# Connection test
python test_docker_connection.py
# Expected: ✅ Docker SQL Server integration successful!
```

### Database Validation (Azure Data Studio)
- **Server**: `localhost,1434`
- **Authentication**: SQL Login (sa/MyPass123!)
- **Database**: DataWarehouse

## 📚 Technical Learning Outcomes

This project demonstrates:

### Problem-Solving Methodology
- **Systematic Diagnosis**: Using logs, error analysis, and root cause investigation
- **Iterative Solutions**: Evolving architecture based on real constraints
- **Tool Selection**: Choosing appropriate technologies for specific challenges

### Professional Engineering Practices
- **Infrastructure as Code**: Docker Compose for reproducible environments
- **Connection Management**: Robust database connectivity with pooling and error handling
- **Version Control**: Professional Git workflow with meaningful commits and tags

### Data Engineering Foundations
- **Medallion Architecture**: Industry-standard layered data processing approach
- **Schema Design**: Multi-environment database organization
- **ETL Framework**: Scalable foundation for data pipeline development

## 🔗 Repository Links

- **Latest Release**: [mvp-2-complete](../../releases/tag/mvp-2-complete)
- **Active Development**: [mvp/2-docker-etl](../../tree/mvp/2-docker-etl)
- **Project Tracking**: [Context Documentation](./context/)

## 🏷️ Tags

`data-warehouse` `sql-server` `docker` `medallion-architecture` `python` `etl` `data-engineering` `professional-development` `problem-solving` `infrastructure`

---

**Developed by Daniel G. B.** - Data Engineer demonstrating systematic technical problem-solving, infrastructure management, and professional development practices for modern data platforms.