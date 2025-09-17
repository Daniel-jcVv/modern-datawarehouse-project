"""
Data Pipeline Module
Orchestrates ETL processes across Bronze, Silver, and Gold layers
"""

from .bronze_pipeline import main as run_bronze_pipeline
from .silver_pipeline import main as run_silver_pipeline
from .gold_pipeline import main as run_gold_pipeline

__all__ = ["run_bronze_pipeline", "run_silver_pipeline", "run_gold_pipeline"]
