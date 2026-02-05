"""EvidenceStore for audit trail.

Every write must be backed by SourceEvidence.
Evidence is immutable and never deleted.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from pymongo.database import Database
import hashlib

from src.identity.exceptions import MissingEvidenceError, InvalidPhoneError


class EvidenceStore:
    """Manages immutable SourceEvidence records."""
    
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.source_evidence
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create required indexes."""
        self.collection.create_index([("phone_e164", 1), ("timestamp", -1)])
        self.collection.create_index([("source", 1), ("timestamp", -1)])
        self.collection.create_index("url")
    
    def add_evidence(
        self,
        phone_e164: str,
        source: str,
        url: str,
        fields_detected: List[str],
        raw_html: Optional[str] = None,
        confidence: str = "medium",
        timestamp: Optional[datetime] = None
    ) -> dict:
        """Add new SourceEvidence record.
        
        Args:
            phone_e164: Phone in E.164 format (required)
            source: sahibinden | hepsiemlak | google
            url: Original listing/page URL
            fields_detected: List of fields extracted (phone, name, office, city, district)
            raw_html: Raw HTML content (optional, for verification)
            confidence: high | medium | low
            timestamp: Extraction timestamp (defaults to now)
            
        Returns:
            Evidence document
            
        Raises:
            InvalidPhoneError: If phone is missing
            MissingEvidenceError: If required fields are missing
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        if not source:
            raise MissingEvidenceError("Source is required")
        
        if not url:
            raise MissingEvidenceError("URL is required")
        
        if not fields_detected:
            raise MissingEvidenceError("At least one detected field is required")
        
        timestamp = timestamp or datetime.utcnow()
        
        # Compute hash of raw HTML if provided
        raw_html_hash = None
        if raw_html:
            raw_html_hash = hashlib.sha256(raw_html.encode('utf-8')).hexdigest()
        
        doc = {
            "id": str(uuid4()),
            "phone_e164": phone_e164,
            "source": source,
            "url": url,
            "fields_detected": fields_detected,
            "raw_html_hash": raw_html_hash,
            "timestamp": timestamp,
            "confidence": confidence
        }
        
        self.collection.insert_one(doc)
        return doc
    
    def get_evidence_for_phone(
        self,
        phone_e164: str,
        source: Optional[str] = None
    ) -> List[dict]:
        """Get all evidence records for a phone.
        
        Args:
            phone_e164: Phone in E.164 format
            source: Optional filter by source
            
        Returns:
            List of evidence documents
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        query = {"phone_e164": phone_e164}
        if source:
            query["source"] = source
        
        return list(self.collection.find(query).sort("timestamp", -1))
    
    def verify_field_has_evidence(
        self,
        phone_e164: str,
        field_name: str
    ) -> bool:
        """Check if a field has at least one evidence record.
        
        Args:
            phone_e164: Phone in E.164 format
            field_name: Field to check (phone, name, office, city, district)
            
        Returns:
            True if evidence exists, False otherwise
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        evidence = self.collection.find_one({
            "phone_e164": phone_e164,
            "fields_detected": field_name
        })
        
        return evidence is not None
    
    def require_evidence(
        self,
        phone_e164: str,
        field_name: str
    ) -> None:
        """Enforce that a field has evidence.
        
        Raises:
            MissingEvidenceError: If no evidence exists for field
        """
        if not self.verify_field_has_evidence(phone_e164, field_name):
            raise MissingEvidenceError(
                f"No evidence found for field '{field_name}' on phone {phone_e164}"
            )
