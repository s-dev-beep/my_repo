"""Google Places enrichment source.

STEP 19: Enrichment Queue

Enriches phone identities using Google Places API:
- Office name
- Office address
- Office phone number
- Office website
- Office photos
- Office reviews/rating

Note: Requires Google Places API key.
Performs read-only lookups only (no crawling).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class GooglePlacesEnricher:
    """Enrichment source: Google Places API."""
    
    def __init__(self, db, api_key: Optional[str] = None):
        """Initialize Google Places enricher.
        
        Args:
            db: MongoDB database
            api_key: Google Places API key (optional)
        """
        self.db = db
        self.api_key = api_key
    
    async def enrich(
        self,
        phone_e164: str,
        missing_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Enrich a phone identity from Google Places.
        
        Args:
            phone_e164: Phone in E.164 format
            missing_fields: Which fields to try to fill
            
        Returns:
            List of observations (field_name, value, timestamp)
        """
        observations = []
        
        # Check if API key is available
        if not self.api_key:
            logger.debug("Google Places API key not configured, skipping enrichment")
            return observations
        
        # For now, return empty - actual Google Places integration would:
        # 1. Search Google Places for this phone
        # 2. Extract office details (name, address, phone, website, photos)
        # 3. Return as observations
        #
        # IMPORTANT: Uses public API, not crawling
        # Respects Google's Terms of Service
        
        logger.debug(
            f"Google Places enrichment for {phone_e164}: "
            f"missing_fields={missing_fields} (stub implementation)"
        )
        
        return observations
