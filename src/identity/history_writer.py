"""HistoryWriter for temporal data.

All history is append-only.
Previous records are closed (end_date set), never deleted.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from pymongo.database import Database

from src.identity.exceptions import InvalidPhoneError, HistoryDeletionError


class HistoryWriter:
    """Manages append-only historical records."""
    
    def __init__(self, db: Database):
        self.db = db
        self.location_history = db.agent_location_history
        self.office_history = db.agent_office_history
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create required indexes."""
        # Location history
        self.location_history.create_index([("phone_e164", 1), ("end_date", 1)])
        self.location_history.create_index([("city", 1), ("district", 1)])
        
        # Office history
        self.office_history.create_index([("phone_e164", 1), ("end_date", 1)])
        self.office_history.create_index([("office_id", 1), ("end_date", 1)])
    
    def add_location(
        self,
        phone_e164: str,
        city: str,
        district: str,
        source: str,
        confidence: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Add new location record for agent.
        
        If agent already has an active location in different district,
        close previous record (set end_date).
        
        Args:
            phone_e164: Phone in E.164 format (required)
            city: City name
            district: District name
            source: sahibinden | hepsiemlak | google
            confidence: high | medium | low
            timestamp: Observation timestamp (defaults to now)
            
        Returns:
            New location history record
            
        Raises:
            InvalidPhoneError: If phone is missing
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        timestamp = timestamp or datetime.utcnow()
        
        # Check if same location already exists and is active
        existing = self.location_history.find_one({
            "phone_e164": phone_e164,
            "city": city,
            "district": district,
            "end_date": None
        })
        
        if existing:
            # Already tracking this location; just update last observation
            return existing
        
        # Close previous active location in different district (if any)
        self.location_history.update_many(
            {
                "phone_e164": phone_e164,
                "end_date": None,
                "$or": [
                    {"city": {"$ne": city}},
                    {"district": {"$ne": district}}
                ]
            },
            {"$set": {"end_date": timestamp}}
        )
        
        # Create new location record
        doc = {
            "id": str(uuid4()),
            "phone_e164": phone_e164,
            "city": city,
            "district": district,
            "start_date": timestamp,
            "end_date": None,  # Active
            "source": source,
            "confidence": confidence
        }
        
        self.location_history.insert_one(doc)
        return doc
    
    def add_office_association(
        self,
        phone_e164: str,
        office_id: str,
        role: str,
        source: str,
        confidence: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Add new office association for agent.
        
        If agent already associated with different office,
        close previous record (set end_date).
        
        Args:
            phone_e164: Phone in E.164 format (required)
            office_id: Office UUID
            role: agent | partner | owner | unknown
            source: sahibinden | hepsiemlak | google
            confidence: high | medium | low
            timestamp: Observation timestamp (defaults to now)
            
        Returns:
            New office history record
            
        Raises:
            InvalidPhoneError: If phone is missing
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        timestamp = timestamp or datetime.utcnow()
        
        # Check if same office association already exists and is active
        existing = self.office_history.find_one({
            "phone_e164": phone_e164,
            "office_id": office_id,
            "end_date": None
        })
        
        if existing:
            # Already tracking this association
            return existing
        
        # Close previous active office association (if different office)
        self.office_history.update_many(
            {
                "phone_e164": phone_e164,
                "office_id": {"$ne": office_id},
                "end_date": None
            },
            {"$set": {"end_date": timestamp}}
        )
        
        # Create new office association
        doc = {
            "id": str(uuid4()),
            "phone_e164": phone_e164,
            "office_id": office_id,
            "role": role,
            "start_date": timestamp,
            "end_date": None,  # Active
            "source": source,
            "confidence": confidence
        }
        
        self.office_history.insert_one(doc)
        return doc
    
    def get_active_locations(self, phone_e164: str) -> list:
        """Get all active locations for agent."""
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        return list(self.location_history.find({
            "phone_e164": phone_e164,
            "end_date": None
        }))
    
    def get_active_office(self, phone_e164: str) -> Optional[dict]:
        """Get current active office for agent."""
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        return self.office_history.find_one({
            "phone_e164": phone_e164,
            "end_date": None
        })
    
    def prevent_deletion(self, record_id: str) -> None:
        """Guard against history deletion.
        
        This method always raises an exception.
        History records must never be deleted, only closed (end_date set).
        
        Raises:
            HistoryDeletionError: Always
        """
        raise HistoryDeletionError(
            f"Cannot delete history record {record_id}. "
            f"History is immutable. Use end_date to close records."
        )
