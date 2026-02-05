"""Deduplication & Entity Resolution module.

This module provides deduplication and entity resolution for three entity types:
1. Office: Identified by office_name + phone_number
2. Agent: Identified by agent_name + phone_number
3. Listing: Identified by listing_url

Key principles:
- Deterministic only (no fuzzy matching, no guessing)
- Missing keys → cannot deduplicate → treated as new entity
- Same input must always give same decision
- In-memory deduplicator (no database writes)
"""

from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass

from src.core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DeduplicationResult:
    """Result of deduplication check for an entity."""
    
    is_new: bool
    """True if entity is new, False if duplicate."""
    
    dedupe_key: Optional[str]
    """The deduplication key used (e.g., office_name+phone_number)."""
    
    reason: str
    """Human-readable explanation of the decision."""


class Deduplicator:
    """Detects duplicate entities (offices, agents, listings).
    
    This deduplicator uses deterministic, key-based matching with no fuzzy
    logic. Each entity type has a specific deduplication strategy:
    
    - Office: office_name + phone_number
    - Agent: agent_name + phone_number
    - Listing: listing_url
    
    Missing keys cannot be deduplicated and are always treated as new.
    
    Example:
        >>> dedup = Deduplicator()
        >>> 
        >>> # Register some entities
        >>> dedup.add_listing("https://www.sahibinden.com/ilan/123")
        >>> dedup.add_office("EV GAYRIMENKUL", "+905321234567")
        >>> dedup.add_agent("AHMET YILMAZ", "+905325555555")
        >>> 
        >>> # Check for duplicates
        >>> result = dedup.check_listing("https://www.sahibinden.com/ilan/123")
        >>> print(result.is_new)  # False - already seen
        False
        >>> 
        >>> # New listing
        >>> result = dedup.check_listing("https://www.sahibinden.com/ilan/456")
        >>> print(result.is_new)  # True - not seen before
        True
    """
    
    def __init__(self):
        """Initialize deduplicator with empty entity sets.
        
        Maintains three separate in-memory sets for fast lookups:
        - Office keys: office_name + phone_number
        - Agent keys: agent_name + phone_number
        - Listing keys: listing_url
        """
        # Storage for seen entities
        self.offices: set = set()  # Set of (office_name, phone_number) tuples
        self.agents: set = set()   # Set of (agent_name, phone_number) tuples
        self.listings: set = set() # Set of listing_urls
        
        logger.info("Deduplicator initialized with empty entity sets")
    
    # ============================================================================
    # LISTING DEDUPLICATION (by URL)
    # ============================================================================
    
    def check_listing(self, normalized_data: Dict[str, Any]) -> DeduplicationResult:
        """Check if a listing is new or duplicate based on URL.
        
        Listing deduplication is simple and deterministic:
        - Key: listing_url
        - Missing URL → cannot deduplicate → treated as new (with warning)
        
        Args:
            normalized_data: Normalized data dict from STEP 5 with fields:
                - listing_url: str (REQUIRED)
                - Other fields are ignored
        
        Returns:
            DeduplicationResult with is_new, dedupe_key, and reason
        
        Raises:
            ValueError: If listing_url is missing or invalid
        
        Example:
            >>> dedup = Deduplicator()
            >>> data = {'listing_url': 'https://www.sahibinden.com/ilan/123'}
            >>> result = dedup.check_listing(data)
            >>> print(result.is_new)
            True
            >>> dedup.add_listing(data['listing_url'])
            >>> result = dedup.check_listing(data)
            >>> print(result.is_new)
            False
        """
        # Validate input
        if not isinstance(normalized_data, dict):
            raise ValueError("Expected normalized_data to be a dict")
        
        listing_url = normalized_data.get('listing_url')
        
        # Missing URL cannot be deduplicated
        if not listing_url:
            logger.warning(
                "Cannot deduplicate listing: missing or empty listing_url. "
                "Treating as new entity."
            )
            return DeduplicationResult(
                is_new=True,
                dedupe_key=None,
                reason="Missing listing_url - cannot deduplicate"
            )
        
        # Check if already seen
        if listing_url in self.listings:
            logger.debug(f"Listing duplicate detected: {listing_url}")
            return DeduplicationResult(
                is_new=False,
                dedupe_key=listing_url,
                reason=f"Listing URL already seen: {listing_url}"
            )
        
        # New listing
        logger.debug(f"New listing detected: {listing_url}")
        return DeduplicationResult(
            is_new=True,
            dedupe_key=listing_url,
            reason=f"New listing URL: {listing_url}"
        )
    
    def add_listing(self, listing_url: str) -> None:
        """Register a listing as seen.
        
        Args:
            listing_url: The listing URL to register
        
        Raises:
            ValueError: If listing_url is missing or invalid
        
        Example:
            >>> dedup = Deduplicator()
            >>> dedup.add_listing("https://www.sahibinden.com/ilan/123")
            >>> result = dedup.check_listing({"listing_url": "https://..."})
            >>> print(result.is_new)
            False
        """
        if not listing_url:
            raise ValueError("listing_url cannot be empty")
        
        self.listings.add(listing_url)
        logger.debug(f"Registered listing: {listing_url}")
    
    # ============================================================================
    # OFFICE DEDUPLICATION (by name + phone)
    # ============================================================================
    
    def check_office(self, normalized_data: Dict[str, Any]) -> DeduplicationResult:
        """Check if an office is new or duplicate based on name + phone.
        
        Office deduplication requires both fields:
        - office_name: UPPERCASE, trimmed (from normalizer)
        - phone_number: E.164 format (from normalizer)
        
        If EITHER field is missing → cannot deduplicate → treated as new
        
        Args:
            normalized_data: Normalized data dict from STEP 5 with fields:
                - office_name: str | None
                - phone_number: str | None (E.164 format: +905XXXXXXXXX)
                - Other fields are ignored
        
        Returns:
            DeduplicationResult with is_new, dedupe_key, and reason
        
        Raises:
            ValueError: If normalized_data is not a dict
        
        Example:
            >>> dedup = Deduplicator()
            >>> data = {
            ...     'office_name': 'EV GAYRIMENKUL',
            ...     'phone_number': '+905321234567'
            ... }
            >>> result = dedup.check_office(data)
            >>> print(result.is_new)
            True
            >>> dedup.add_office(data['office_name'], data['phone_number'])
            >>> result = dedup.check_office(data)
            >>> print(result.is_new)
            False
        """
        # Validate input
        if not isinstance(normalized_data, dict):
            raise ValueError("Expected normalized_data to be a dict")
        
        office_name = normalized_data.get('office_name')
        phone_number = normalized_data.get('phone_number')
        
        # Missing either field → cannot deduplicate
        if not office_name or not phone_number:
            missing = []
            if not office_name:
                missing.append("office_name")
            if not phone_number:
                missing.append("phone_number")
            
            reason = f"Cannot deduplicate office: missing {', '.join(missing)}"
            logger.debug(reason)
            return DeduplicationResult(
                is_new=True,
                dedupe_key=None,
                reason=reason
            )
        
        # Create dedupe key
        dedupe_key = (office_name, phone_number)
        
        # Check if already seen
        if dedupe_key in self.offices:
            logger.debug(
                f"Office duplicate detected: {office_name} / {phone_number}"
            )
            return DeduplicationResult(
                is_new=False,
                dedupe_key=f"{office_name}#{phone_number}",
                reason=f"Office already seen: {office_name} @ {phone_number}"
            )
        
        # New office
        logger.debug(
            f"New office detected: {office_name} / {phone_number}"
        )
        return DeduplicationResult(
            is_new=True,
            dedupe_key=f"{office_name}#{phone_number}",
            reason=f"New office: {office_name} @ {phone_number}"
        )
    
    def add_office(self, office_name: str, phone_number: str) -> None:
        """Register an office as seen.
        
        Args:
            office_name: Office name (UPPERCASE, trimmed)
            phone_number: Phone number (E.164 format)
        
        Raises:
            ValueError: If either field is missing or invalid
        
        Example:
            >>> dedup = Deduplicator()
            >>> dedup.add_office("EV GAYRIMENKUL", "+905321234567")
            >>> result = dedup.check_office({
            ...     'office_name': 'EV GAYRIMENKUL',
            ...     'phone_number': '+905321234567'
            ... })
            >>> print(result.is_new)
            False
        """
        if not office_name or not phone_number:
            raise ValueError("office_name and phone_number cannot be empty")
        
        dedupe_key = (office_name, phone_number)
        self.offices.add(dedupe_key)
        logger.debug(f"Registered office: {office_name} @ {phone_number}")
    
    # ============================================================================
    # AGENT DEDUPLICATION (by name + phone)
    # ============================================================================
    
    def check_agent(self, normalized_data: Dict[str, Any]) -> DeduplicationResult:
        """Check if an agent is new or duplicate based on name + phone.
        
        Agent deduplication requires both fields:
        - agent_name: UPPERCASE, trimmed (from normalizer)
        - phone_number: E.164 format (from normalizer)
        
        If EITHER field is missing → cannot deduplicate → treated as new
        
        Args:
            normalized_data: Normalized data dict from STEP 5 with fields:
                - agent_name: str | None
                - phone_number: str | None (E.164 format: +905XXXXXXXXX)
                - Other fields are ignored
        
        Returns:
            DeduplicationResult with is_new, dedupe_key, and reason
        
        Raises:
            ValueError: If normalized_data is not a dict
        
        Example:
            >>> dedup = Deduplicator()
            >>> data = {
            ...     'agent_name': 'AHMET YILMAZ',
            ...     'phone_number': '+905321234567'
            ... }
            >>> result = dedup.check_agent(data)
            >>> print(result.is_new)
            True
            >>> dedup.add_agent(data['agent_name'], data['phone_number'])
            >>> result = dedup.check_agent(data)
            >>> print(result.is_new)
            False
        """
        # Validate input
        if not isinstance(normalized_data, dict):
            raise ValueError("Expected normalized_data to be a dict")
        
        agent_name = normalized_data.get('agent_name')
        phone_number = normalized_data.get('phone_number')
        
        # Missing either field → cannot deduplicate
        if not agent_name or not phone_number:
            missing = []
            if not agent_name:
                missing.append("agent_name")
            if not phone_number:
                missing.append("phone_number")
            
            reason = f"Cannot deduplicate agent: missing {', '.join(missing)}"
            logger.debug(reason)
            return DeduplicationResult(
                is_new=True,
                dedupe_key=None,
                reason=reason
            )
        
        # Create dedupe key
        dedupe_key = (agent_name, phone_number)
        
        # Check if already seen
        if dedupe_key in self.agents:
            logger.debug(
                f"Agent duplicate detected: {agent_name} / {phone_number}"
            )
            return DeduplicationResult(
                is_new=False,
                dedupe_key=f"{agent_name}#{phone_number}",
                reason=f"Agent already seen: {agent_name} @ {phone_number}"
            )
        
        # New agent
        logger.debug(
            f"New agent detected: {agent_name} / {phone_number}"
        )
        return DeduplicationResult(
            is_new=True,
            dedupe_key=f"{agent_name}#{phone_number}",
            reason=f"New agent: {agent_name} @ {phone_number}"
        )
    
    def add_agent(self, agent_name: str, phone_number: str) -> None:
        """Register an agent as seen.
        
        Args:
            agent_name: Agent name (UPPERCASE, trimmed)
            phone_number: Phone number (E.164 format)
        
        Raises:
            ValueError: If either field is missing or invalid
        
        Example:
            >>> dedup = Deduplicator()
            >>> dedup.add_agent("AHMET YILMAZ", "+905321234567")
            >>> result = dedup.check_agent({
            ...     'agent_name': 'AHMET YILMAZ',
            ...     'phone_number': '+905321234567'
            ... })
            >>> print(result.is_new)
            False
        """
        if not agent_name or not phone_number:
            raise ValueError("agent_name and phone_number cannot be empty")
        
        dedupe_key = (agent_name, phone_number)
        self.agents.add(dedupe_key)
        logger.debug(f"Registered agent: {agent_name} @ {phone_number}")
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    def load_entities(self, entities: list[Dict[str, Any]]) -> None:
        """Load multiple previously-seen entities from a list.
        
        This method loads entities from an in-memory list (or iterable),
        extracting the appropriate dedupe keys for each entity type.
        
        Args:
            entities: List of normalized data dicts, each with:
                - listing_url: str
                - office_name: str | None
                - phone_number: str | None
                - agent_name: str | None
        
        Example:
            >>> dedup = Deduplicator()
            >>> entities = [
            ...     {
            ...         'listing_url': 'https://...',
            ...         'office_name': 'EV GAYRIMENKUL',
            ...         'phone_number': '+905321234567',
            ...         'agent_name': 'AHMET YILMAZ'
            ...     },
            ...     # more entities...
            ... ]
            >>> dedup.load_entities(entities)
            >>> # Now deduplicator has loaded all entities
        """
        if not entities:
            logger.debug("No entities to load")
            return
        
        count_offices = 0
        count_agents = 0
        count_listings = 0
        
        for entity in entities:
            if not isinstance(entity, dict):
                logger.warning(f"Skipping non-dict entity: {type(entity)}")
                continue
            
            # Load listing if present
            if entity.get('listing_url'):
                self.add_listing(entity['listing_url'])
                count_listings += 1
            
            # Load office if both fields present
            if entity.get('office_name') and entity.get('phone_number'):
                try:
                    self.add_office(
                        entity['office_name'],
                        entity['phone_number']
                    )
                    count_offices += 1
                except ValueError as e:
                    logger.debug(f"Could not add office: {e}")
            
            # Load agent if both fields present
            if entity.get('agent_name') and entity.get('phone_number'):
                try:
                    self.add_agent(
                        entity['agent_name'],
                        entity['phone_number']
                    )
                    count_agents += 1
                except ValueError as e:
                    logger.debug(f"Could not add agent: {e}")
        
        logger.info(
            f"Loaded {count_listings} listings, {count_offices} offices, "
            f"{count_agents} agents"
        )
    
    # ============================================================================
    # STATISTICS & DIAGNOSTICS
    # ============================================================================
    
    def stats(self) -> Dict[str, int]:
        """Get deduplication statistics.
        
        Returns:
            Dictionary with counts of registered entities
        
        Example:
            >>> dedup = Deduplicator()
            >>> dedup.add_listing("https://...")
            >>> dedup.add_office("EV GAYRIMENKUL", "+905321234567")
            >>> stats = dedup.stats()
            >>> print(stats)
            {'listings': 1, 'offices': 1, 'agents': 0}
        """
        return {
            'listings': len(self.listings),
            'offices': len(self.offices),
            'agents': len(self.agents),
        }
    
    def clear(self) -> None:
        """Clear all registered entities (reset deduplicator).
        
        Useful for testing or restarting deduplication.
        
        Example:
            >>> dedup = Deduplicator()
            >>> dedup.add_listing("https://...")
            >>> dedup.clear()
            >>> stats = dedup.stats()
            >>> print(stats)  # {'listings': 0, 'offices': 0, 'agents': 0}
        """
        self.listings.clear()
        self.offices.clear()
        self.agents.clear()
        logger.info("Deduplicator cleared")
