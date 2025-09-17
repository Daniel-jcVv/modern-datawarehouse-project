"""
Data Quality Configuration - Enterprise Quality Standards
This module defines quality thresholds and alerting configurations
"""

# Quality Thresholds Configuration
QUALITY_THRESHOLDS = {
    # Overall thresholds
    "overall": {
        "min_table_success_rate": 100.0,  # All tables must pass
        "min_check_success_rate": 95.0,   # 95% of checks must pass
    },
    
    # Table-specific thresholds
    "table_specific": {
        "silver.crm_sales_details": {
            "min_success_rate": 100.0,  # Critical table - must be perfect
            "critical_checks": ["PRIMARY_KEY", "DATA_CONSISTENCY"]
        },
        "silver.crm_cust_info": {
            "min_success_rate": 98.0,
            "critical_checks": ["PRIMARY_KEY"]
        },
        "silver.crm_prd_info": {
            "min_success_rate": 98.0,
            "critical_checks": ["PRIMARY_KEY", "DATA_RANGES"]
        },
        "silver.erp_cust_az12": {
            "min_success_rate": 95.0,
            "critical_checks": ["PRIMARY_KEY", "DATA_RANGES"]
        },
        "silver.erp_loc_a101": {
            "min_success_rate": 95.0,
            "critical_checks": ["PRIMARY_KEY"]
        },
        "silver.erp_px_cat_g1v2": {
            "min_success_rate": 95.0,
            "critical_checks": ["PRIMARY_KEY", "DATA_TRIMMING"]
        }
    },
    
    # Check-specific thresholds
    "check_types": {
        "PRIMARY_KEY": {
            "severity": "CRITICAL",
            "max_failures": 0  # No failures allowed
        },
        "DATA_CONSISTENCY": {
            "severity": "CRITICAL",
            "max_failures": 0
        },
        "DATA_RANGES": {
            "severity": "HIGH",
            "max_failure_rate": 0.01  # 1% failure rate allowed
        },
        "DATA_TRIMMING": {
            "severity": "MEDIUM",
            "max_failure_rate": 0.05  # 5% failure rate allowed
        },
        "STANDARDIZATION": {
            "severity": "LOW",
            "max_failure_rate": 0.10  # 10% failure rate allowed
        }
    }
}

# Alert Configuration
ALERT_CONFIG = {
    "enabled": True,
    "channels": {
        "log_file": {
            "enabled": True,
            "path": "logs/quality_alerts.log",
            "level": "WARNING"
        },
        "console": {
            "enabled": True,
            "level": "ERROR"
        },
        "email": {
            "enabled": False,  # Set to True in production
            "smtp_server": "smtp.company.com",
            "smtp_port": 587,
            "from_email": "data-quality@company.com",
            "to_emails": ["data-team@company.com"],
            "subject_prefix": "[DWH Quality Alert]"
        },
        "slack": {
            "enabled": False,  # Set to True in production
            "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "channel": "#data-quality-alerts",
            "mention_users": ["@data-engineer-oncall"]
        }
    },
    
    # Alert rules
    "rules": {
        "critical_failure": {
            "condition": "Any CRITICAL check fails",
            "channels": ["log_file", "console", "email", "slack"],
            "priority": "P1"
        },
        "high_failure_rate": {
            "condition": "Overall success rate < 90%",
            "channels": ["log_file", "console", "email"],
            "priority": "P2"
        },
        "repeated_failures": {
            "condition": "Same check fails 3 times in a row",
            "channels": ["log_file", "console"],
            "priority": "P3"
        }
    }
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "enabled": True,
    "metrics": {
        "quality_trends": {
            "retention_days": 30,
            "aggregation_levels": ["hourly", "daily", "weekly"]
        },
        "table_health": {
            "update_frequency": "after_each_run",
            "show_top_issues": 10
        },
        "check_performance": {
            "track_execution_time": True,
            "slow_query_threshold_seconds": 10
        }
    },
    "export": {
        "format": "json",
        "path": "logs/quality_metrics/",
        "filename_pattern": "quality_metrics_{date}_{time}.json"
    }
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "parallel_checks": False,  # Set to True for parallel execution
    "max_workers": 4,
    "query_timeout_seconds": 30,
    "batch_size": 1000
}
