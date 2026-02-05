"""Enrichment task data structure.

STEP 19: Enrichment Queue

Represents a single enrichment task for a phone identity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class EnrichmentTask:
    """A single enrichment task for a phone identity."""
    
    phone_e164: str
    """Phone in E.164 format (e.g., +905551234567)."""
    
    current_confidence: float
    """Current confidence score (0.0 to 1.0)."""
    
    missing_fields: List[str]
    """Fields that are missing or low-confidence:
    - agent_name
    - office_name
    - office_address
    - office_phone
    - office_website
    - office_photo_url
    - is_active
    """
    
    sources_to_try: List[str] = field(default_factory=lambda: ["hepsiemlak", "google_places"])
    """Ordered list of sources to try enrichment from."""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    """When this task was created."""
    
    completed_at: Optional[datetime] = None
    """When enrichment was completed (None if not yet)."""
    
    enrichment_count: int = 0
    """Number of enrichment observations made."""
    
    errors: List[str] = field(default_factory=list)
    """Errors encountered during enrichment."""
    
    def mark_completed(self):
        """Mark task as completed."""
        self.completed_at = datetime.utcnow()
    
    def add_error(self, error: str):
        """Record an error."""
        self.errors.append(error)
    
    def is_completed(self) -> bool:
        """Whether task has been completed."""
        return self.completed_at is not None
    
    def __str__(self) -> str:
        """Human-readable task description."""
        missing = ", ".join(self.missing_fields) if self.missing_fields else "none"
        return (
            f"EnrichmentTask("
            f"phone={self.phone_e164}, "
            f"confidence={self.current_confidence:.2f}, "
            f"missing=[{missing}], "
            f"completed={self.is_completed()}"
            f")"
        )
