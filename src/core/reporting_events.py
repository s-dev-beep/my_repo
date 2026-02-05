"""Event tracking for crawl runs.

STEP 9: OBSERVABILITY & QUALITY GATES

Extracted from reporting.py for better modularity.
This module contains the Reporter class for tracking crawl events.
"""

from typing import Optional, Literal, Dict, Any
from datetime import datetime
from src.core.logger import setup_logger
from src.core.reporting_report import (
    CrawlReport,
    FailureRecord,
    QualityRejection,
    SuccessRecord,
    FailureCategory
)

logger = setup_logger(__name__)


class Reporter:
    """Crawl event tracker and report generator.
    
    Tracks all events during a crawl run and generates a comprehensive
    JSON report at the end.
    
    Usage:
        reporter = Reporter(run_id="crawl_20260202_101530")
        
        # Track events
        reporter.record_success(url, listing_id, operation, confidence)
        reporter.record_failure(url, category, reason, step)
        reporter.record_quality_rejection(url, reason, data)
        
        # Generate report
        report = reporter.generate_report()
        report.save(Path("reports/crawl_20260202_101530.json"))
    """
    
    def __init__(
        self,
        run_id: Optional[str] = None,
        parser_type: str = "unknown",
        run_mode: str = "full_run"
    ):
        """Initialize reporter.
        
        Args:
            run_id: Unique ID for this run (auto-generated if not provided)
            parser_type: Type of parser used (e.g., 'sahibinden')
            run_mode: Execution mode (dry_run, safe_run, full_run)
        """
        self.run_id = run_id or self._generate_run_id()
        self.parser_type = parser_type
        self.run_mode = run_mode
        self.start_time = datetime.now()
        self.stop_reason: Optional[str] = None
        
        # Event storage
        self.successes: list[SuccessRecord] = []
        self.failures: list[FailureRecord] = []
        self.quality_rejections: list[QualityRejection] = []
        
        # Statistics
        self.total_urls = 0
        self.stats = {
            "fetched": 0,
            "parsed": 0,
            "normalized": 0,
            "inserted": 0,
            "updated": 0,
            "failed": 0,
            "quality_rejected": 0,
        }
        self.failure_breakdown = {
            "fetch_failed": 0,
            "parse_failed": 0,
            "normalize_failed": 0,
            "persist_failed": 0,
            "quality_rejected": 0,
        }
        
        logger.info(f"Reporter initialized: run_id={self.run_id}")
    
    def _generate_run_id(self) -> str:
        """Generate a unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"crawl_{timestamp}"
    
    def _now_iso(self) -> str:
        """Get current time as ISO string."""
        return datetime.now().isoformat()
    
    def set_total_urls(self, count: int) -> None:
        """Set total URL count for this run."""
        self.total_urls = count
    
    def set_stop_reason(self, reason: str) -> None:
        """Set the stop reason for early termination.
        
        Args:
            reason: Human-readable explanation for why crawl stopped early
        """
        self.stop_reason = reason
        logger.warning(f"Crawl stopped early: {reason}")
    
    def record_success(
        self,
        url: str,
        listing_id: str,
        operation: Literal["inserted", "updated"],
        confidence: str
    ) -> None:
        """Record a successfully processed listing.
        
        Args:
            url: Listing URL
            listing_id: MongoDB document ID
            operation: 'inserted' or 'updated'
            confidence: Quality confidence level
        """
        record = SuccessRecord(
            url=url,
            listing_id=listing_id,
            operation=operation,
            timestamp=self._now_iso(),
            confidence=confidence
        )
        self.successes.append(record)
        
        # Update stats
        if operation == "inserted":
            self.stats["inserted"] += 1
        elif operation == "updated":
            self.stats["updated"] += 1
        
        logger.debug(f"Recorded success: {url} ({operation})")
    
    def record_failure(
        self,
        url: str,
        category: FailureCategory,
        reason: str,
        step: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a failed listing.
        
        Args:
            url: Listing URL
            category: Type of failure
            reason: Human-readable explanation
            step: Pipeline step where failure occurred
            details: Additional context (optional)
        """
        record = FailureRecord(
            url=url,
            category=category,
            reason=reason,
            timestamp=self._now_iso(),
            step=step,
            details=details
        )
        self.failures.append(record)
        
        # Update stats
        self.stats["failed"] += 1
        self.failure_breakdown[category] += 1
        
        logger.debug(f"Recorded failure: {url} ({category}: {reason})")
    
    def record_quality_rejection(
        self,
        url: str,
        reason: str,
        data_snapshot: Dict[str, Any]
    ) -> None:
        """Record a quality-rejected listing.
        
        Args:
            url: Listing URL
            reason: Which quality gate failed
            data_snapshot: Normalized data at time of rejection
        """
        record = QualityRejection(
            url=url,
            reason=reason,
            timestamp=self._now_iso(),
            data_snapshot=data_snapshot
        )
        self.quality_rejections.append(record)
        
        # Update stats
        self.stats["quality_rejected"] += 1
        self.failure_breakdown["quality_rejected"] += 1
        
        logger.info(f"Quality rejection: {url} - {reason}")
    
    def increment_stat(self, stat_name: str) -> None:
        """Increment a statistic counter.
        
        Args:
            stat_name: Name of stat to increment (fetched, parsed, normalized)
        """
        if stat_name in self.stats:
            self.stats[stat_name] += 1
    
    def generate_report(self) -> CrawlReport:
        """Generate final crawl report.
        
        Returns:
            Complete CrawlReport object
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = CrawlReport(
            run_id=self.run_id,
            start_time=self.start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            run_mode=self.run_mode,
            stop_reason=self.stop_reason,
            parser_type=self.parser_type,
            total_urls=self.total_urls,
            successful=self.successes,
            failures=self.failures,
            quality_rejections=self.quality_rejections,
            stats={
                "total": self.total_urls,
                **self.stats
            },
            failure_breakdown=self.failure_breakdown.copy()
        )
        
        logger.info(
            f"Report generated: {len(self.successes)} success, "
            f"{len(self.failures)} failed, "
            f"{len(self.quality_rejections)} quality rejected"
        )
        
        return report
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current statistics summary.
        
        Returns:
            Dictionary with current stats
        """
        return {
            "run_id": self.run_id,
            "total_urls": self.total_urls,
            "stats": self.stats.copy(),
            "failure_breakdown": self.failure_breakdown.copy()
        }
