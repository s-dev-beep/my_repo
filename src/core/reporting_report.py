"""Data structures for crawl reporting.

STEP 9: OBSERVABILITY & QUALITY GATES

Extracted from reporting.py for better modularity.
This module contains all data classes for reports.
"""

import json
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from pathlib import Path
from src.core.logger import setup_logger

logger = setup_logger(__name__)


# Type definitions
FailureCategory = Literal[
    "fetch_failed",
    "parse_failed",
    "normalize_failed",
    "persist_failed",
    "quality_rejected"
]


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
