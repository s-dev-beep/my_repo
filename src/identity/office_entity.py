"""OfficeEntity management.

Offices are deduplicated by (normalized_name + city + district).
Same name in different district = different office.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from pymongo.database import Database

from src.identity.exceptions import InvalidPhoneError


class OfficeEntityManager:
    """Manages Office entities and deduplication."""
    
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.offices
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create required indexes."""
        self.collection.create_index([
            ("normalized_name", 1),
            ("city", 1),
            ("district", 1)
        ])
        self.collection.create_index("last_seen_at")
    
    def _normalize_office_name(self, name: str) -> str:
        """Normalize office name for deduplication.
        
        - Uppercase
        - Remove common suffixes (Emlak, Gayrimenkul)
        - Trim whitespace
        """
        if not name:
            return ""
        
        name = name.upper().strip()
        
        # Remove common real estate suffixes for better matching
        suffixes = ["EMLAK", "GAYRİMENKUL", "DANIŞMANLIK"]
        for suffix in suffixes:
            if name.endswith(" " + suffix):
                name = name[:-len(suffix)].strip()
        
        return name
    
    def get_or_create(
        self,
        office_name: str,
        city: str,
        district: str,
        confidence: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Get existing or create new Office.
        
        Deduplication key: normalized_name + city + district
        
        Args:
            office_name: Raw office name
            city: City name (required for dedup)
            district: District name (required for dedup)
            confidence: high | medium | low
            timestamp: Observation timestamp (defaults to now)
            
        Returns:
            Office document
        """
        if not office_name:
            office_name = ""
        
        normalized = self._normalize_office_name(office_name)
        timestamp = timestamp or datetime.utcnow()
        
        # Try to find existing by dedup key
        existing = self.collection.find_one({
            "normalized_name": normalized,
            "city": city,
            "district": district
        })
        
        if existing:
            # Update last_seen_at only
            self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"last_seen_at": timestamp}}
            )
            return existing
        
        # Create new office
        doc = {
            "office_id": str(uuid4()),
            "office_name": office_name,
            "normalized_name": normalized,
            "city": city,
            "district": district,
            "first_seen_at": timestamp,
            "last_seen_at": timestamp,
            "confidence": confidence,
            "status": "active"
        }
        
        self.collection.insert_one(doc)
        return doc
    
    def update_status(self, office_id: str) -> None:
        """Update status based on last_seen_at.
        
        active: seen in last 90 days
        inactive: not seen for 90+ days
        """
        office = self.collection.find_one({"office_id": office_id})
        if not office:
            return
        
        days_since_seen = (datetime.utcnow() - office["last_seen_at"]).days
        
        new_status = "active" if days_since_seen <= 90 else "inactive"
        
        if new_status != office.get("status"):
            self.collection.update_one(
                {"office_id": office_id},
                {"$set": {"status": new_status}}
            )
