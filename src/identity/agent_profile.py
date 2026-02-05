"""AgentProfile management.

Names are append-only and versioned by phone.
Never overwrite; always create new profile for name changes.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from pymongo.database import Database

from src.identity.exceptions import InvalidPhoneError, ImmutabilityViolationError


class AgentProfileManager:
    """Manages versioned AgentProfile entities."""
    
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.agent_profiles
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create required indexes."""
        self.collection.create_index([("phone_e164", 1), ("last_seen_at", -1)])
        self.collection.create_index("normalized_name")
        self.collection.create_index("is_current")
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison.
        
        - Uppercase
        - Remove titles (Bay, Bayan, Mr., Ms.)
        - Trim whitespace
        """
        if not name:
            return ""
        
        name = name.upper().strip()
        
        # Remove common titles
        titles = ["BAY", "BAYAN", "MR.", "MS.", "MRS.", "DR.", "PROF."]
        for title in titles:
            if name.startswith(title + " "):
                name = name[len(title):].strip()
        
        return name
    
    def add_or_update_profile(
        self,
        phone_e164: str,
        full_name: str,
        confidence: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Add new profile or update existing if name matches.
        
        Args:
            phone_e164: Phone in E.164 format (required)
            full_name: Agent's full name
            confidence: high | medium | low
            timestamp: Observation timestamp (defaults to now)
            
        Returns:
            AgentProfile document (existing or newly created)
            
        Raises:
            InvalidPhoneError: If phone is missing
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        if not full_name:
            # Allow empty name but create placeholder profile
            full_name = ""
        
        normalized = self._normalize_name(full_name)
        timestamp = timestamp or datetime.utcnow()
        
        # Check if this exact normalized name already exists for this phone
        existing = self.collection.find_one({
            "phone_e164": phone_e164,
            "normalized_name": normalized
        })
        
        if existing:
            # Update last_seen_at only (no overwrites)
            self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"last_seen_at": timestamp}}
            )
            return existing
        
        # New name variant → create new profile
        # Mark all other profiles for this phone as not current
        self.collection.update_many(
            {"phone_e164": phone_e164, "is_current": True},
            {"$set": {"is_current": False}}
        )
        
        doc = {
            "agent_profile_id": str(uuid4()),
            "phone_e164": phone_e164,
            "full_name": full_name,
            "normalized_name": normalized,
            "first_seen_at": timestamp,
            "last_seen_at": timestamp,
            "confidence": confidence,
            "is_current": True
        }
        
        self.collection.insert_one(doc)
        return doc
    
    def get_current_profile(self, phone_e164: str) -> Optional[dict]:
        """Get the most recent (current) profile for a phone."""
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        return self.collection.find_one({
            "phone_e164": phone_e164,
            "is_current": True
        })
    
    def get_all_profiles(self, phone_e164: str) -> List[dict]:
        """Get all historical profiles for a phone (name history)."""
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        return list(self.collection.find(
            {"phone_e164": phone_e164}
        ).sort("last_seen_at", -1))
    
    def prevent_overwrite(self, phone_e164: str, new_name: str) -> None:
        """Guard against accidental overwrites.
        
        This method intentionally does nothing but serves as documentation
        that overwrites are prevented by design (append-only).
        
        Raises:
            ImmutabilityViolationError: Always (this is a guard function)
        """
        raise ImmutabilityViolationError(
            f"Cannot overwrite name for {phone_e164}. "
            f"Names are append-only. Use add_or_update_profile instead."
        )
