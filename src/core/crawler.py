"""Pipeline orchestrator for crawling real estate listings.

FACADE MODULE FOR BACKWARD COMPATIBILITY

This module re-exports all public APIs from the refactored modules:
- crawler_core: Main Crawler class and CrawlStats
- crawler_modes: Execution mode handlers
- crawler_safety: Safety check logic

All existing imports like `from src.core.crawler import Crawler` continue to work.
"""

# Re-export main classes from refactored modules
from src.core.crawler_core import Crawler, CrawlStats
from src.core.crawler_modes import (
    ExecutionMode,
    DryRunMode,
    SafeRunMode,
    FullRunMode,
    get_execution_mode
)
from src.core.crawler_safety import SafetyChecker

# Maintain backward compatibility with all public APIs
__all__ = [
    # Core classes
    'Crawler',
    'CrawlStats',
    
    # Execution modes
    'ExecutionMode',
    'DryRunMode',
    'SafeRunMode',
    'FullRunMode',
    'get_execution_mode',
    
    # Safety
    'SafetyChecker',
]
