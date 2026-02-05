"""Crawl reporting and quality gates.

STEP 9: OBSERVABILITY & QUALITY GATES

This module provides:
1. Structured crawl reporting (JSON format)
2. Quality rejection rules (deterministic)
3. Failure categorization
4. Run report generation

Key principles:
- No ML or fuzzy matching
- Deterministic quality gates
- One report per crawl run
- Reports saved locally as JSON
"""

import json
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from src.core.logger import setup_logger

logger = setup_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# FAILURE CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

FailureCategory = Literal[
    "fetch_failed",
    "parse_failed",
    "normalize_failed",
    "persist_failed",
    "quality_rejected"
]


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FailureRecord:
    """Record of a failed listing."""
    
    url: str
    """The listing URL that failed."""
    
    category: FailureCategory
    """Type of failure."""
    
    reason: str
    """Human-readable explanation."""
    
    timestamp: str
    """ISO timestamp of failure."""
    
    step: str
    """Pipeline step where failure occurred."""
    
    details: Optional[Dict[str, Any]] = None
    """Additional context (optional)."""


@dataclass
class QualityRejection:
    """Record of a quality-rejected listing."""
    
    url: str
    """The listing URL."""
    
    reason: str
    """Which quality gate failed."""
    
    timestamp: str
    """ISO timestamp."""
    
    data_snapshot: Dict[str, Any]
    """Normalized data at time of rejection."""


@dataclass
class SuccessRecord:
    """Record of a successfully processed listing."""
    
    url: str
    """The listing URL."""
    
    listing_id: str
    """MongoDB listing ID."""
    
    operation: Literal["inserted", "updated"]
    """Database operation performed."""
    
    timestamp: str
    """ISO timestamp."""
    
    confidence: str
    """Data quality confidence (high/medium/low)."""


@dataclass
class CrawlReport:
    """Complete report for a crawl run."""
    
    # Metadata
    run_id: str
    """Unique ID for this crawl run."""
    
    start_time: str
    """ISO timestamp when crawl started."""
    
    end_time: Optional[str] = None
    """ISO timestamp when crawl completed."""
    
    duration_seconds: Optional[float] = None
    """Total duration in seconds."""
    
    # STEP 10: Execution mode and stop reason
    run_mode: str = "full_run"
    """Execution mode: dry_run, safe_run, or full_run."""
    
    stop_reason: Optional[str] = None
    """Reason for early stop (if applicable)."""
    
    # Configuration
    parser_type: str = ""
    """Parser used (e.g., 'sahibinden')."""
    
    total_urls: int = 0
    """Number of URLs to process."""
    
    # Success metrics
    successful: List[SuccessRecord] = field(default_factory=list)
    """Successfully processed listings."""
    
    # Failure metrics
    failures: List[FailureRecord] = field(default_factory=list)
    """Failed listings."""
    
    quality_rejections: List[QualityRejection] = field(default_factory=list)
    """Quality-rejected listings."""
    
    # Summary statistics
    stats: Dict[str, int] = field(default_factory=lambda: {
        "total": 0,
        "fetched": 0,
        "parsed": 0,
        "normalized": 0,
        "inserted": 0,
        "updated": 0,
        "failed": 0,
        "quality_rejected": 0,
    })
    
    # Failure breakdown
    failure_breakdown: Dict[str, int] = field(default_factory=lambda: {
        "fetch_failed": 0,
        "parse_failed": 0,
        "normalize_failed": 0,
        "persist_failed": 0,
        "quality_rejected": 0,
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: Path) -> None:
        """Save report to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        logger.info(f"Report saved to: {filepath}")


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY GATES
# ═══════════════════════════════════════════════════════════════════════════════

class QualityGates:
    """Deterministic quality validation rules.
    
    These gates reject listings that don't meet minimum quality standards.
    All rules are deterministic (no ML or fuzzy matching).
    
    Quality gates:
    1. Low confidence + no phone → reject
    2. Missing both city and district → reject
    3. Parser output has < 2 meaningful fields → reject
    """
    
    @staticmethod
    def check_normalized_data(normalized_data: Dict[str, Any]) -> Optional[str]:
        """Check normalized data against quality gates.
        
        Args:
            normalized_data: Normalized data from normalizer
            
        Returns:
            Rejection reason if data fails quality gates, None if passes
        """
        # Gate 1: Low confidence + no phone
        if (normalized_data.get('confidence') == 'low' and 
            not normalized_data.get('phone_number')):
            return "Low confidence listing with no phone number"
        
        # Gate 2: Missing both city and district
        if (not normalized_data.get('city') and 
            not normalized_data.get('district')):
            return "Missing both city and district location data"
        
        # Passed all gates
        return None
    
    @staticmethod
    def check_parsed_data(parsed_data: Dict[str, Any]) -> Optional[str]:
        """Check parsed data for minimum field count.
        
        Args:
            parsed_data: Raw parsed data from parser
            
        Returns:
            Rejection reason if data fails, None if passes
        """
        # Count meaningful fields (non-None, non-empty, excluding listing_url)
        meaningful_fields = [
            'office_name', 'agent_name', 'phone_number', 'city', 'district'
        ]
        
        count = sum(
            1 for field in meaningful_fields
            if parsed_data.get(field) and str(parsed_data.get(field)).strip()
        )
        
        # Gate 3: Less than 2 meaningful fields
        if count < 2:
            return f"Parser extracted only {count} meaningful field(s), minimum is 2"
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTER
# ═══════════════════════════════════════════════════════════════════════════════

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
        self.successes: List[SuccessRecord] = []
        self.failures: List[FailureRecord] = []
        self.quality_rejections: List[QualityRejection] = []
        
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
    
    def set_stop_reason(self, reason: str) -> None:
        """Set the stop reason for early termination.
        
        Args:
            reason: Human-readable explanation for why crawl stopped early
        """
        self.stop_reason = reason
        logger.warning(f"Crawl stopped early: {reason}")
    
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
