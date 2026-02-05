"""Safety stop conditions for crawler.

STEP 10: Safety Controls

Extracted from crawler.py for better modularity.
This module contains the safety check logic that determines when to stop a crawl early.
"""

from typing import TYPE_CHECKING, Optional
from src.core.logger import setup_logger

if TYPE_CHECKING:
    from src.core.crawler_core import CrawlStats
    from src.core.reporting import Reporter

logger = setup_logger(__name__)


class SafetyChecker:
    """Checks safety conditions to determine if crawl should stop early.
    
    Safety conditions:
    1. Fetch failure rate exceeds threshold
    2. Too many consecutive fetch failures (blocks)
    3. Quality rejection rate exceeds threshold
    """
    
    def __init__(self, safety_config: dict):
        """Initialize safety checker with configuration.
        
        Args:
            safety_config: Dictionary with safety thresholds:
                - max_fetch_failure_rate: float (0.0-1.0)
                - max_consecutive_blocks: int
                - max_quality_rejection_rate: float (0.0-1.0)
                - min_urls_before_checks: int
        """
        self.config = safety_config
    
    def should_stop(
        self,
        current_idx: int,
        stats: 'CrawlStats',
        reporter: Optional['Reporter'],
        enable_quality_gates: bool
    ) -> tuple[bool, Optional[str]]:
        """Check if crawler should stop early based on safety conditions.
        
        Args:
            current_idx: Current URL index (1-based)
            stats: Current crawl statistics
            reporter: Reporter instance (optional, needed for quality checks)
            enable_quality_gates: Whether quality gates are enabled
            
        Returns:
            Tuple of (should_stop: bool, stop_reason: Optional[str])
        """
        min_urls = self.config["min_urls_before_checks"]
        
        # Don't apply checks until minimum URLs processed
        if current_idx < min_urls:
            return False, None
        
        # Check 1: Fetch failure rate
        total_attempted = stats.fetched + stats.failed
        if total_attempted > 0:
            fetch_failure_rate = stats.failed / total_attempted
            max_fetch_failure_rate = self.config["max_fetch_failure_rate"]
            
            if fetch_failure_rate > max_fetch_failure_rate:
                reason = (
                    f"Fetch failure rate {fetch_failure_rate:.1%} exceeds "
                    f"threshold {max_fetch_failure_rate:.1%} "
                    f"({stats.failed}/{total_attempted} failed)"
                )
                logger.error(f"SAFETY STOP: {reason}")
                return True, reason
        
        # Check 2: Consecutive fetch failures (blocks)
        max_consecutive = self.config["max_consecutive_blocks"]
        if stats.consecutive_fetch_failures >= max_consecutive:
            reason = (
                f"Consecutive fetch failures ({stats.consecutive_fetch_failures}) "
                f"reached threshold ({max_consecutive}). Possible rate limiting or IP block."
            )
            logger.error(f"SAFETY STOP: {reason}")
            return True, reason
        
        # Check 3: Quality rejection rate
        if reporter and enable_quality_gates:
            total_parsed = stats.parsed
            quality_rejected = reporter.stats.get("quality_rejected", 0)
            
            if total_parsed > 0:
                quality_rejection_rate = quality_rejected / total_parsed
                max_quality_rejection_rate = self.config["max_quality_rejection_rate"]
                
                if quality_rejection_rate > max_quality_rejection_rate:
                    reason = (
                        f"Quality rejection rate {quality_rejection_rate:.1%} exceeds "
                        f"threshold {max_quality_rejection_rate:.1%} "
                        f"({quality_rejected}/{total_parsed} rejected)"
                    )
                    logger.error(f"SAFETY STOP: {reason}")
                    return True, reason
        
        return False, None
