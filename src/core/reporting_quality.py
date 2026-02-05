"""Quality gates for data validation.

STEP 9: OBSERVABILITY & QUALITY GATES

Extracted from reporting.py for better modularity.
This module contains deterministic quality validation rules.
"""

from typing import Dict, Any, Optional
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class QualityGates:
    """Deterministic quality validation rules.
    
    These gates reject listings that don't meet minimum quality standards.
    All rules are deterministic (no ML or fuzzy matching).
    
    Quality gates:
    1. Low confidence + no phone → reject
    2. Missing both city and district → reject
    3. Parser output has < 2 meaningful fields → reject
    """
    
    @staticmethod
    def check_normalized_data(normalized_data: Dict[str, Any]) -> Optional[str]:
        """Check normalized data against quality gates.
        
        Args:
            normalized_data: Normalized data from normalizer
            
        Returns:
            Rejection reason if data fails quality gates, None if passes
        """
        # Gate 1: Low confidence + no phone
        if (normalized_data.get('confidence') == 'low' and 
            not normalized_data.get('phone_number')):
            return "Low confidence listing with no phone number"
        
        # Gate 2: Missing both city and district
        if (not normalized_data.get('city') and 
            not normalized_data.get('district')):
            return "Missing both city and district location data"
        
        # Passed all gates
        return None
    
    @staticmethod
    def check_parsed_data(parsed_data: Dict[str, Any]) -> Optional[str]:
        """Check parsed data for minimum field count.
        
        Args:
            parsed_data: Raw parsed data from parser
            
        Returns:
            Rejection reason if data fails, None if passes
        """
        # Count meaningful fields (non-None, non-empty, excluding listing_url)
        meaningful_fields = [
            'office_name', 'agent_name', 'phone_number', 'city', 'district'
        ]
        
        count = sum(
            1 for field in meaningful_fields
            if parsed_data.get(field) and str(parsed_data.get(field)).strip()
        )
        
        # Gate 3: Less than 2 meaningful fields
        if count < 2:
            return f"Parser extracted only {count} meaningful field(s), minimum is 2"
        
        return None
