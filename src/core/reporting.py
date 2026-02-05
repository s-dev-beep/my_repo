"""Crawl reporting and quality gates.

STEP 9: OBSERVABILITY & QUALITY GATES

This module has been refactored into smaller modules for better maintainability:
- reporting_events.py: Reporter class for event tracking
- reporting_quality.py: QualityGates for data validation
- reporting_report.py: Report data structures (CrawlReport, FailureRecord, etc.)

This file now serves as a facade to maintain backward compatibility.
All imports from this module will continue to work unchanged.
"""

# Re-export all public APIs for backward compatibility
from src.core.reporting_events import Reporter
from src.core.reporting_quality import QualityGates
from src.core.reporting_report import (
    CrawlReport,
    FailureRecord,
    QualityRejection,
    SuccessRecord,
    FailureCategory
)

__all__ = [
    # Main classes
    "Reporter",
    "QualityGates",
    "CrawlReport",
    
    # Data structures
    "FailureRecord",
    "QualityRejection",
    "SuccessRecord",
    "FailureCategory",
]
