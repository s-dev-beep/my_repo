"""GraphResolver - orchestrates identity graph writes.

Accepts normalized extraction and decides what to append to the graph.
Enforces all invariants and guards.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.database import Database

from src.identity.phone_identity import PhoneIdentityManager
from src.identity.agent_profile import AgentProfileManager
from src.identity.office_entity import OfficeEntityManager
from src.identity.history_writer import HistoryWriter
from src.identity.evidence_store import EvidenceStore
from src.identity.exceptions import (
    InvalidPhoneError,
    MissingEvidenceError
)


class IdentityGraphResolver:
    """Orchestrates all identity graph writes.
    
    This is the single entry point for adding data to the graph.
    All writes must pass through here to enforce invariants.
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.phone_manager = PhoneIdentityManager(db)
        self.profile_manager = AgentProfileManager(db)
        self.office_manager = OfficeEntityManager(db)
        self.history_writer = HistoryWriter(db)
        self.evidence_store = EvidenceStore(db)
    
    def process_extraction(
        self,
        phone_e164: str,
        source: str,
        url: str,
        agent_name: Optional[str] = None,
        office_name: Optional[str] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
        confidence: str = "medium",
        timestamp: Optional[datetime] = None,
        raw_html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a single extraction and update identity graph.
        
        This is the main entry point for crawler data.
        
        Args:
            phone_e164: Phone in E.164 format (REQUIRED)
            source: sahibinden | hepsiemlak | google
            url: Original listing/page URL
            agent_name: Agent's name (optional)
            office_name: Office name (optional)
            city: City name (optional)
            district: District name (optional)
            confidence: high | medium | low
            timestamp: Extraction timestamp (defaults to now)
            raw_html: Raw HTML for verification (optional)
            
        Returns:
            Dict with created/updated entity IDs
            
        Raises:
            InvalidPhoneError: If phone is missing or invalid
            MissingEvidenceError: If required evidence is missing
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        if not source:
            raise MissingEvidenceError("Source is required")
        
        if not url:
            raise MissingEvidenceError("URL is required")
        
        timestamp = timestamp or datetime.utcnow()
        
        result = {
            "phone_e164": phone_e164,
            "phone_identity_created": False,
            "agent_profile_created": False,
            "office_created": False,
            "location_added": False,
            "office_association_added": False,
            "evidence_id": None
        }
        
        # Step 1: Record evidence FIRST (everything must be evidence-backed)
        fields_detected = ["phone"]
        if agent_name:
            fields_detected.append("name")
        if office_name:
            fields_detected.append("office")
        if city:
            fields_detected.append("city")
        if district:
            fields_detected.append("district")
        
        evidence = self.evidence_store.add_evidence(
            phone_e164=phone_e164,
            source=source,
            url=url,
            fields_detected=fields_detected,
            raw_html=raw_html,
            confidence=confidence,
            timestamp=timestamp
        )
        result["evidence_id"] = evidence["id"]
        
        # Step 2: Ensure PhoneIdentity exists (root of graph)
        phone_identity = self.phone_manager.get_or_create(
            phone_e164=phone_e164,
            source=source,
            timestamp=timestamp
        )
        result["phone_identity_created"] = True
        
        # Step 3: Add/update AgentProfile if name provided
        if agent_name:
            profile = self.profile_manager.add_or_update_profile(
                phone_e164=phone_e164,
                full_name=agent_name,
                confidence=confidence,
                timestamp=timestamp
            )
            result["agent_profile_created"] = True
            result["agent_profile_id"] = profile["agent_profile_id"]
        
        # Step 4: Add location history if city/district provided
        if city and district:
            location = self.history_writer.add_location(
                phone_e164=phone_e164,
                city=city,
                district=district,
                source=source,
                confidence=confidence,
                timestamp=timestamp
            )
            result["location_added"] = True
            result["location_id"] = location["id"]
        
        # Step 5: Add office and association if office_name provided
        if office_name and city and district:
            office = self.office_manager.get_or_create(
                office_name=office_name,
                city=city,
                district=district,
                confidence=confidence,
                timestamp=timestamp
            )
            result["office_created"] = True
            result["office_id"] = office["office_id"]
            
            # Create office association
            association = self.history_writer.add_office_association(
                phone_e164=phone_e164,
                office_id=office["office_id"],
                role="agent",  # Default role
                source=source,
                confidence=confidence,
                timestamp=timestamp
            )
            result["office_association_added"] = True
            result["office_association_id"] = association["id"]
        
        # Step 6: Update confidence if multiple sources
        sources = self.phone_manager.get_all_sources(phone_e164)
        if len(sources) >= 2:
            # Multiple sources → higher confidence
            new_confidence = 0.95
            self.phone_manager.update_confidence(phone_e164, new_confidence)
        
        # Step 7: Update status (active/dormant/reassigned)
        self.phone_manager.update_status(phone_e164)
        
        return result
    
    def add_enrichment_observation(
        self,
        phone_e164: str,
        field_name: str,
        value: str,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Add enrichment observation to an existing phone identity.
        
        STEP 19: Enrichment-only observation (no new fields creation).
        
        Args:
            phone_e164: Existing phone (must exist)
            field_name: Field being enriched (agent_name, office_name, etc.)
            value: Value for the field
            source: Source of enrichment (hepsiemlak, google_places)
            timestamp: When observation was made
            
        Returns:
            Dict with enrichment result
            
        Raises:
            InvalidPhoneError: If phone doesn't exist
            MissingEvidenceError: If evidence cannot be created
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Verify phone exists
        phone_doc = self.db.phone_identities.find_one({"phone_e164": phone_e164})
        if not phone_doc:
            raise InvalidPhoneError(f"Phone not found: {phone_e164}")
        
        # Create evidence record for enrichment source
        evidence_id = self.evidence_store.add_evidence(
            phone_e164=phone_e164,
            source=source,
            url=f"enrichment://{source}/{phone_e164}",
            fields_detected=[field_name],  # Only this field was enriched
            raw_html=None,  # No HTML for enrichment observations
            confidence="high",  # Enrichment sources are verified
            timestamp=timestamp
        )
        
        # Attempt to append to appropriate field based on field_name
        enrichment_result = {}
        
        if field_name == "agent_name":
            # Try to add as profile if not already known
            try:
                self.profile_manager.add_or_update_profile(
                    phone_e164=phone_e164,
                    full_name=value,
                    confidence="high",
                    timestamp=timestamp
                )
                enrichment_result["profile_added"] = True
            except Exception as e:
                # Profile might already exist - that's fine
                enrichment_result["profile_added"] = False
                enrichment_result["reason"] = str(e)
        
        elif field_name in ("office_name", "office_address", "office_phone", "office_website"):
            # Try to enhance existing office
            enrichment_result["field_enhanced"] = True
            enrichment_result["field_name"] = field_name
            enrichment_result["value"] = value
        
        elif field_name == "is_active":
            # Update phone status if enrichment suggests activity
            if value == "true":
                self.phone_manager.update_status(phone_e164, new_status="active")
                enrichment_result["status_updated"] = True
        
        # Record enrichment observation in phone_identities
        self.db.phone_identities.update_one(
            {"phone_e164": phone_e164},
            {
                "$push": {
                    "enrichment_observations": {
                        "field_name": field_name,
                        "value": value,
                        "source": source,
                        "timestamp": timestamp,
                        "evidence_id": evidence_id
                    }
                },
                "$set": {
                    "last_enriched_at": timestamp
                }
            }
        )
        
        return {
            "phone_e164": phone_e164,
            "field_name": field_name,
            "value": value,
            "source": source,
            "evidence_id": evidence_id,
            "enrichment": enrichment_result
        }
    
    def get_agent_summary(self, phone_e164: str) -> Dict[str, Any]:
        """Get complete summary of agent's identity graph.
        
        Returns all related entities and history for a phone.
        """
        if not phone_e164:
            raise InvalidPhoneError("Phone number is required")
        
        # Get root identity
        identity = self.db.phone_identities.find_one({"phone_e164": phone_e164})
        
        if not identity:
            raise InvalidPhoneError(f"Phone not found: {phone_e164}")
        
        # Get current profile
        current_profile = self.profile_manager.get_current_profile(phone_e164)
        
        # Get all historical profiles
        all_profiles = self.profile_manager.get_all_profiles(phone_e164)
        
        # Get active locations
        active_locations = self.history_writer.get_active_locations(phone_e164)
        
        # Get active office
        active_office = self.history_writer.get_active_office(phone_e164)
        
        # Get all evidence
        evidence = self.evidence_store.get_evidence_for_phone(phone_e164)
        
        return {
            "phone_identity": identity,
            "current_profile": current_profile,
            "all_profiles": all_profiles,
            "active_locations": active_locations,
            "active_office": active_office,
            "evidence_count": len(evidence),
            "sources": identity.get("sources", []),
            "confidence_score": identity.get("confidence_score", 0.0),
            "status": identity.get("status", "unknown")
        }
