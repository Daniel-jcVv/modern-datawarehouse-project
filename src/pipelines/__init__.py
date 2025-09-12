#!/usr/bin/env python3
"""
Initialize ETL Pipelines Module
This __init__ file marks the pipelines directory as a Python package
"""

from pathlib import Path

# Pipeline module metadata
__version__ = "1.0.0"
__author__ = "Data Engineering Team"

# Define available pipelines
AVAILABLE_PIPELINES = {
    "bronze": "bronze_pipeline",
    "silver": "silver_pipeline",  # Coming soon
    "gold": "gold_pipeline"       # Coming soon
}

# Get the pipelines directory path
PIPELINES_DIR = Path(__file__).parent
