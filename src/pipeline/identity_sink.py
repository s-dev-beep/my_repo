"""Identity Sink - converts crawler output to identity graph writes.

STEP 18: Crawler → Identity Graph Integration

This module is the ONLY persistence path from crawler to database.
All writes must flow through IdentityGraphResolver.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Literal, Optional
from pymongo.database import Database

from src.identity import IdentityGraphResolver
from src.identity.exceptions import IdentityGraphError
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class IdentitySink:
    """Converts normalized crawler output into identity graph writes.
    
    This is the bridge between the crawler (listing-centric) and
    the identity graph (phone-centric).
    
    Responsibilities:
    - Extract phone, name, office, location from normalized listing
    - Convert to identity graph format
    - Attach SourceEvidence for every field
    - Call IdentityGraphResolver
    - Respect execution modes (dry_run vs. safe_run vs. full_run)
    - Surface graph violations as exceptions
    
    Design:
    - Crawler emits normalized listings
    - IdentitySink extracts identity fields
    - IdentityGraph decides what to write
    - MongoDB persists via graph only
    """
    
    def __init__(
        self,
        db: Database,
        source: str = "sahibinden",
        run_mode: str = "safe_run"
    ):
        """Initialize identity sink.
        
        Args:
            db: MongoDB database instance
            source: Data source (sahibinden, hepsiemlak, google)
            run_mode: dry_run | safe_run | full_run
        """
        self.db = db
        self.source = source
        self.run_mode = run_mode
        
        # Only initialize resolver if not dry_run
        if run_mode != "dry_run":
            self.resolver = IdentityGraphResolver(db)
        else:
            self.resolver = None
        
        logger.info(
            f"IdentitySink initialized: source={source}, mode={run_mode}"
        )
    
    def process_listing(
        self,
        url: str,
        normalized_data: Dict[str, Any],
        confidence: str = "medium",
        timestamp: Optional[datetime] = None
    ) -> Tuple[str, Literal["inserted", "updated", "skipped", "simulated"]]:
        """Process normalized listing and write to identity graph.
        
        Args:
            url: Listing URL (used as evidence)
            normalized_data: Normalized listing data from crawler
            confidence: high | medium | low
            timestamp: Extraction timestamp (defaults to now)
            
        Returns:
            Tuple of (identity_id, operation)
            - identity_id: phone_e164 (primary identity key)
            - operation: inserted | updated | skipped | simulated
            
        Raises:
            IdentityGraphError: If graph invariants are violated
            ValueError: If required fields are missing
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Extract identity fields from listing
        identity_fields = self._extract_identity_fields(normalized_data)
        
        # Validate required fields
        if not identity_fields.get("phone_e164"):
            raise ValueError(
                f"Phone number is required for identity graph. "
                f"URL: {url}, Agent: {identity_fields.get('agent_name')}"
            )
        
        phone_e164 = identity_fields["phone_e164"]
        
        # Dry run mode: simulate only
        if self.run_mode == "dry_run":
            logger.info(
                f"[DRY RUN] Would process identity: phone={phone_e164}, "
                f"name={identity_fields.get('agent_name')}, "
                f"office={identity_fields.get('office_name')}, "
                f"location={identity_fields.get('city')}/{identity_fields.get('district')}"
            )
            return phone_e164, "simulated"
        
        # Safe run mode: skip low confidence
        if self.run_mode == "safe_run" and confidence == "low":
            logger.info(
                f"[SAFE RUN] Skipped low confidence identity: "
                f"phone={phone_e164}, confidence={confidence}"
            )
            return phone_e164, "skipped"
        
        # Process through identity graph
        try:
            result = self.resolver.process_extraction(
                phone_e164=phone_e164,
                source=self.source,
                url=url,
                agent_name=identity_fields.get("agent_name"),
                office_name=identity_fields.get("office_name"),
                city=identity_fields.get("city"),
                district=identity_fields.get("district"),
                confidence=confidence,
                timestamp=timestamp,
                raw_html=None  # Don't store HTML (too large)
            )
            
            # Determine operation type
            if result["phone_identity_created"]:
                if result.get("agent_profile_created"):
                    operation = "inserted"
                    logger.info(
                        f"✓ Inserted identity: phone={phone_e164}, "
                        f"name={identity_fields.get('agent_name')}, "
                        f"office={identity_fields.get('office_name')}"
                    )
                else:
                    operation = "updated"
                    logger.info(
                        f"✓ Updated identity: phone={phone_e164} (observation added)"
                    )
            else:
                operation = "updated"
            
            return phone_e164, operation
            
        except IdentityGraphError as e:
            logger.error(
                f"Identity graph error for {url}: {e}. "
                f"Phone: {phone_e164}, "
                f"This indicates a graph invariant violation."
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error processing identity for {url}: {e}. "
                f"Phone: {phone_e164}"
            )
            raise
    
    def _extract_identity_fields(
        self,
        normalized_data: Dict[str, Any]
    ) -> Dict[str, Optional[str]]:
        """Extract identity-relevant fields from normalized listing.
        
        Maps listing fields to identity graph fields:
        - agent.phone_number → phone_e164
        - agent.agent_name → agent_name
        - agent.office_name → office_name
        - listing.city → city
        - listing.district → district
        
        Args:
            normalized_data: Normalized listing from crawler
            
        Returns:
            Dict with identity fields (phone_e164, agent_name, etc.)
        """
        # Extract agent data
        agent_data = normalized_data.get("agent", {})
        
        # Extract listing location data
        listing_data = normalized_data.get("listing", {})
        
        identity_fields = {
            "phone_e164": agent_data.get("phone_number"),
            "agent_name": agent_data.get("agent_name"),
            "office_name": agent_data.get("office_name"),
            "city": listing_data.get("city"),
            "district": listing_data.get("district"),
        }
        
        return identity_fields
    
    def get_agent_summary(self, phone_e164: str) -> Dict[str, Any]:
        """Get complete agent summary from identity graph.
        
        This is a passthrough to IdentityGraphResolver.
        
        Args:
            phone_e164: Phone in E.164 format
            
        Returns:
            Complete agent summary from graph
        """
        if self.run_mode == "dry_run":
            logger.warning("Cannot get agent summary in dry_run mode")
            return {}
        
        return self.resolver.get_agent_summary(phone_e164)
