"""Execution mode handlers for crawler.

STEP 10: Execution Modes (Updated STEP 18)

Extracted from crawler.py for better modularity.
This module contains the logic for different execution modes (dry_run, safe_run, full_run).

STEP 18 UPDATE:
- All persistence now flows through IdentitySink
- No direct MongoDB writes from crawler
- Identity graph is the ONLY persistence path
"""

from typing import TYPE_CHECKING, Tuple, Literal
from src.core.logger import setup_logger
from src.pipeline import IdentitySink

if TYPE_CHECKING:
    from src.db.mongo import MongoDBConnection

logger = setup_logger(__name__)


class ExecutionMode:
    """Base class for execution modes."""
    
    def __init__(self, source: str = "sahibinden"):
        """Initialize execution mode.
        
        Args:
            source: Data source (sahibinden, hepsiemlak, google)
        """
        self.source = source
    
    def persist_listing(
        self,
        url: str,
        normalized_data: dict,
        db: 'MongoDBConnection'
    ) -> Tuple[str, str]:
        """Persist listing based on execution mode logic.
        
        Args:
            url: Listing URL
            normalized_data: Normalized listing data
            db: MongoDB connection
            
        Returns:
            Tuple of (identity_id, operation)
        """
        raise NotImplementedError


class DryRunMode(ExecutionMode):
    """Dry run mode - no database writes.
    
    STEP 18: Routes through IdentitySink in dry_run mode.
    """
    
    def persist_listing(
        self,
        url: str,
        normalized_data: dict,
        db: 'MongoDBConnection'
    ) -> Tuple[str, str]:
        """Simulate persistence without database writes."""
        confidence = normalized_data.get('confidence', 'unknown')
        
        # Use IdentitySink in dry_run mode
        sink = IdentitySink(
            db=db.db,
            source=self.source,
            run_mode="dry_run"
        )
        
        identity_id, operation = sink.process_listing(
            url=url,
            normalized_data=normalized_data,
            confidence=confidence
        )
        
        return identity_id, operation


class SafeRunMode(ExecutionMode):
    """Safe run mode - only persist high/medium confidence.
    
    STEP 18: Routes through IdentitySink to identity graph.
    Low confidence observations are skipped.
    """
    
    def persist_listing(
        self,
        url: str,
        normalized_data: dict,
        db: 'MongoDBConnection'
    ) -> Tuple[str, Literal["inserted", "updated", "skipped"]]:
        """Persist only high/medium confidence listings."""
        confidence = normalized_data.get('confidence', 'unknown')
        
        # Use IdentitySink in safe_run mode
        sink = IdentitySink(
            db=db.db,
            source=self.source,
            run_mode="safe_run"
        )
        
        identity_id, operation = sink.process_listing(
            url=url,
            normalized_data=normalized_data,
            confidence=confidence
        )
        
        return identity_id, operation


class FullRunMode(ExecutionMode):
    """Full run mode - persist everything.
    
    STEP 18: Routes through IdentitySink to identity graph.
    All observations are written regardless of confidence.
    """
    
    def persist_listing(
        self,
        url: str,
        normalized_data: dict,
        db: 'MongoDBConnection'
    ) -> Tuple[str, Literal["inserted", "updated"]]:
        """Persist all listings regardless of confidence."""
        confidence = normalized_data.get('confidence', 'unknown')
        
        # Use IdentitySink in full_run mode
        sink = IdentitySink(
            db=db.db,
            source=self.source,
            run_mode="full_run"
        )
        
        identity_id, operation = sink.process_listing(
            url=url,
            normalized_data=normalized_data,
            confidence=confidence
        )
        
        return identity_id, operation


def get_execution_mode(run_mode: str, source: str = "sahibinden") -> ExecutionMode:
    """Factory function to get execution mode handler.
    
    Args:
        run_mode: One of 'dry_run', 'safe_run', 'full_run'
        source: Data source (sahibinden, hepsiemlak, google)
        
    Returns:
        ExecutionMode instance
        
    Raises:
        ValueError: If run_mode is invalid
    """
    modes = {
        'dry_run': DryRunMode(source=source),
        'safe_run': SafeRunMode(source=source),
        'full_run': FullRunMode(source=source),
    }
    
    if run_mode not in modes:
        raise ValueError(
            f"Invalid run_mode: {run_mode}. "
            f"Must be one of: {', '.join(modes.keys())}"
        )
    
    return modes[run_mode]
