"""
ETL Package - Bronze Layer
==========================
This package contains all Bronze layer ETL components including:
- bronze_data_loader.py: Main ETL engine for Bronze data ingestion
- Additional Bronze layer utilities and transformations

Author: Data Engineering Team
Date: 2025-09-11
"""

from .bronze_data_loader import BronzeETLTypeSafe

__all__ = ['BronzeETLTypeSafe']
