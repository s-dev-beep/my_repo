"""Enrichment queue - identifies candidates for enrichment.

STEP 19: Enrichment Queue

Selects phone identities that would benefit from enrichment:
- Missing fields (agent_name, office info, etc.)
- Low confidence scores
- Multiple conflicting names

Query strategy:
- Active phones only
- Not enriched recently
- Missing office details
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo.database import Database

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class EnrichmentQueue:
    """Identifies phone identities needing enrichment."""
    
    def __init__(self, db: Database, max_age_hours: int = 24):
        """Initialize enrichment queue.
        
        Args:
            db: MongoDB database
            max_age_hours: Skip phones enriched in last N hours
        """
        self.db = db
        self.max_age_hours = max_age_hours
    
    def get_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get phone identities needing enrichment.
        
        Selection criteria:
        1. Status is 'active'
        2. Low confidence (< 0.8)
        3. Missing office details
        4. Not enriched recently
        
        Args:
            limit: Maximum candidates to return
            
        Returns:
            List of phone identity documents with enrichment metadata
        """
        # Query: Active phones with low confidence or missing office info
        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_age_hours)
        
        pipeline = [
            # Stage 1: Only active phones
            {
                "$match": {
                    "status": "active",
                    "$or": [
                        {"confidence_score": {"$lt": 0.85}},
                        {"last_enriched_at": {"$exists": False}},
                        {"last_enriched_at": {"$lt": cutoff_time}},
                    ]
                }
            },
            # Stage 2: Join with agent profiles to check for missing office info
            {
                "$lookup": {
                    "from": "agent_profiles",
                    "localField": "phone_e164",
                    "foreignField": "phone_e164",
                    "as": "profiles"
                }
            },
            # Stage 3: Count how many profiles have office names
            {
                "$addFields": {
                    "profiles_with_office": {
                        "$size": {
                            "$filter": {
                                "input": "$profiles",
                                "as": "p",
                                "cond": {"$ne": ["$$p.office_name", None]}
                            }
                        }
                    },
                    "total_profiles": {"$size": "$profiles"}
                }
            },
            # Stage 4: Candidates are those with < 80% office coverage
            {
                "$match": {
                    "$expr": {
                        "$lt": [
                            {"$divide": ["$profiles_with_office", "$total_profiles"]},
                            0.8
                        ]
                    }
                }
            },
            # Stage 5: Sort by confidence (lower first)
            {"$sort": {"confidence_score": 1}},
            # Stage 6: Limit results
            {"$limit": limit},
            # Stage 7: Keep only needed fields
            {
                "$project": {
                    "phone_e164": 1,
                    "confidence_score": 1,
                    "profiles_with_office": 1,
                    "total_profiles": 1,
                    "last_enriched_at": 1,
                }
            }
        ]
        
        try:
            candidates = list(self.db.phone_identities.aggregate(pipeline))
            logger.info(f"Found {len(candidates)} enrichment candidates")
            return candidates
        except Exception as e:
            logger.error(f"Error querying enrichment candidates: {e}")
            return []
    
    def get_missing_fields(self, phone_e164: str) -> List[str]:
        """Identify which fields are missing for a phone.
        
        Args:
            phone_e164: Phone number in E.164 format
            
        Returns:
            List of missing field names
        """
        # Get phone identity
        phone_doc = self.db.phone_identities.find_one(
            {"phone_e164": phone_e164}
        )
        if not phone_doc:
            return []
        
        missing = []
        
        # Check for agent_name
        profiles = list(self.db.agent_profiles.find(
            {"phone_e164": phone_e164}
        ))
        if not profiles:
            missing.append("agent_name")
        
        # Check for office name/info
        offices = list(self.db.agent_office_history.find(
            {
                "phone_e164": phone_e164,
                "end_date": None  # Currently active
            }
        ))
        
        if not offices:
            missing.append("office_name")
            missing.append("office_address")
            missing.append("office_phone")
        else:
            # Check if current office has details
            for office_assoc in offices:
                office_id = office_assoc.get("office_id")
                office = self.db.offices.find_one({"office_id": office_id})
                if office:
                    if not office.get("address"):
                        missing.append("office_address")
                    if not office.get("phone_number"):
                        missing.append("office_phone")
                    if not office.get("website"):
                        missing.append("office_website")
        
        # Deduplicate
        return list(set(missing))
    
    def mark_enriched(self, phone_e164: str):
        """Mark a phone as recently enriched.
        
        Args:
            phone_e164: Phone number to mark
        """
        self.db.phone_identities.update_one(
            {"phone_e164": phone_e164},
            {"$set": {"last_enriched_at": datetime.utcnow()}}
        )
        logger.debug(f"Marked {phone_e164} as enriched")
