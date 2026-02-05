"""PhoneIdentity management.

Phone number is the immutable root of the identity graph.
"""

from datetime import datetime
from typing import Optional, List
from pymongo.database import Database

from src.identity.exceptions import InvalidPhoneError


class PhoneIdentityManager:
    """Manages PhoneIdentity entities (root of identity graph)."""
    
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.phone_identities
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create required indexes."""
        self.collection.create_index("phone_e164", unique=True)
        self.collection.create_index("last_seen_at")
        self.collection.create_index("status")
    
    def get_or_create(
        self,
        phone_e164: str,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Get existing or create new PhoneIdentity.
        
        Args:
            phone_e164: Phone in E.164 format (required)
            source: Source platform (sahibinden, hepsiemlak, google)
            timestamp: Observation timestamp (defaults to now)
        
        Returns:
            PhoneIdentity document
            
        Raises:
            InvalidPhoneError: If phone is missing or invalid
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        if not phone_e164.startswith("+"):
            raise InvalidPhoneError(f"Phone must be in E.164 format: {phone_e164}")
        
        timestamp = timestamp or datetime.utcnow()
        
        # Try to find existing
        existing = self.collection.find_one({"phone_e164": phone_e164})
        
        if existing:
            # Update last_seen_at and sources
            self.collection.update_one(
                {"phone_e164": phone_e164},
                {
                    "$set": {"last_seen_at": timestamp},
                    "$addToSet": {"sources": source},
                    "$inc": {"observation_count": 1}
                }
            )
            return self.collection.find_one({"phone_e164": phone_e164})
        
        # Create new
        doc = {
            "phone_e164": phone_e164,
            "first_seen_at": timestamp,
            "last_seen_at": timestamp,
            "sources": [source],
            "status": "active",
            "confidence_score": 0.7,  # Medium by default
            "observation_count": 1
        }
        
        self.collection.insert_one(doc)
        return doc
    
    def update_status(self, phone_e164: str) -> None:
        """Update status based on last_seen_at.
        
        active: seen in last 30 days
        dormant: not seen for 30-180 days
        reassigned: not seen for 180+ days (possible reassignment)
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        identity = self.collection.find_one({"phone_e164": phone_e164})
        if not identity:
            raise InvalidPhoneError(f"Phone not found: {phone_e164}")
        
        days_since_seen = (datetime.utcnow() - identity["last_seen_at"]).days
        
        if days_since_seen <= 30:
            new_status = "active"
        elif days_since_seen <= 180:
            new_status = "dormant"
        else:
            new_status = "reassigned"
        
        if new_status != identity.get("status"):
            self.collection.update_one(
                {"phone_e164": phone_e164},
                {"$set": {"status": new_status}}
            )
    
    def update_confidence(
        self,
        phone_e164: str,
        new_confidence: float
    ) -> None:
        """Update confidence score (0.0 - 1.0).
        
        Confidence increases when multiple sources confirm same data.
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        if not 0.0 <= new_confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0: {new_confidence}")
        
        self.collection.update_one(
            {"phone_e164": phone_e164},
            {"$set": {"confidence_score": new_confidence}}
        )
    
    def get_all_sources(self, phone_e164: str) -> List[str]:
        """Get all sources that have observed this phone."""
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        identity = self.collection.find_one({"phone_e164": phone_e164})
        if not identity:
            raise InvalidPhoneError(f"Phone not found: {phone_e164}")
        
        return identity.get("sources", [])
