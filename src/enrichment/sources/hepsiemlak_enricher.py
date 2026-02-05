"""Hepsiemlak enrichment source.

STEP 19: Enrichment Queue

Enriches phone identities by searching Hepsiemlak for:
- Recent listings by this phone
- Office name confirmation
- Office address
- Office contact info

Note: This is READ-ONLY enrichment, not crawling.
Searches for existing public listings, doesn't extract new ones.
"""

from typing import List, Dict, Any
from datetime import datetime
import aiohttp

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class HepsiemlakEnricher:
    """Enrichment source: Hepsiemlak public data."""
    
    def __init__(self, db):
        """Initialize Hepsiemlak enricher.
        
        Args:
            db: MongoDB database (for storing enrichment results)
        """
        self.db = db
        self.base_url = "https://www.hepsiemlak.com"
    
    async def enrich(
        self,
        phone_e164: str,
        missing_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Enrich a phone identity from Hepsiemlak.
        
        Args:
            phone_e164: Phone in E.164 format
            missing_fields: Which fields to try to fill
            
        Returns:
            List of observations (field_name, value, timestamp)
        """
        observations = []
        
        # Only enrich if Hepsiemlak is relevant
        if not missing_fields:
            logger.debug(f"No missing fields for {phone_e164}, skipping enrichment")
            return observations
        
        # For now, return empty - actual Hepsiemlak integration would:
        # 1. Search Hepsiemlak API for listings by this phone
        # 2. Extract office name, address, contact from results
        # 3. Return as observations
        # 
        # IMPORTANT: This is READ-ONLY enrichment from public sources
        # Does not trigger new crawling or extraction
        
        logger.debug(
            f"Hepsiemlak enrichment for {phone_e164}: "
            f"missing_fields={missing_fields} (stub implementation)"
        )
        
        return observations
