#!/usr/bin/env python3
"""
Universal Pipeline Runner - Single Entry Point for All ETL Operations
This script provides a unified interface to run different pipeline stages

Usage: python run_pipeline.py [action]
Where action can be: check, bronze, silver, gold, help
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def show_usage():
    """Display usage instructions when no arguments provided"""
    print("\n" + "=" * 60)
    print("Modern Data Warehouse - Pipeline Runner")
    print("=" * 60)
    print("\nUsage: python run_pipeline.py [action]")
    print("\nAvailable actions:")
    print("  check   - Run system health checks")
    print("  bronze  - Execute Bronze layer ETL pipeline")
    print("  silver  - Execute Silver layer transformations")
    print("  gold    - Execute Gold layer aggregations")
    print("  help    - Show this help message")
    print("\nExamples:")
    print("  python run_pipeline.py check   # Verify system is ready")
    print("  python run_pipeline.py bronze  # Run Bronze ETL")
    print("\n" + "=" * 60)


def run_check():
    """Execute system health check"""
    print("\nRunning system health check...")
    print("-" * 40)
    try:
        from scripts.diagnostics.system_check import main
        return main()
    except Exception as e:
        print(f"Error running system check: {e}")
        return False


def run_bronze():
    """Execute Bronze layer pipeline"""
    print("\nStarting Bronze Layer ETL Pipeline...")
    print("-" * 40)
    try:
        from src.pipelines.bronze_pipeline import main
        main()
        return True
    except Exception as e:
        print(f"Error running Bronze pipeline: {e}")
        return False


def run_silver():
    """Execute Silver layer pipeline"""
    print("\nSilver Layer Pipeline")
    print("-" * 40)
    print("Silver pipeline is under development")
    print("   Expected completion: Next sprint")
    return True


def run_gold():
    """Execute Gold layer pipeline"""
    print("\n🥇 Gold Layer Pipeline")
    print("-" * 40)
    print("⚠️  Gold pipeline is under development")
    print("   Expected completion: Future sprint")
    return True


def main():
    """Main entry point - route to appropriate pipeline based on argument"""
    
    # Check if user provided an argument
    if len(sys.argv) < 2:
        show_usage()
        return 0
    
    # Get the action requested (convert to lowercase for flexibility)
    action = sys.argv[1].lower()
    
    # Route to appropriate function based on action
    actions = {
        'check': run_check,
        'bronze': run_bronze,
        'silver': run_silver,
        'gold': run_gold,
        'help': show_usage,
        '--help': show_usage,
        '-h': show_usage
    }
    
    # Execute the requested action
    if action in actions:
        result = actions[action]()
        # Return 0 for success, 1 for failure (Unix convention)
        return 0 if result is not False else 1
    else:
        print(f"\n❌ Error: '{sys.argv[1]}' is not a valid action")
        print(f"   Valid actions: {', '.join(actions.keys())}")
        show_usage()
        return 1


if __name__ == "__main__":
    # Exit with appropriate code (0 = success, 1 = error)
    exit_code = main()
    sys.exit(exit_code)
