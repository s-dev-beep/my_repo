"""Sahibinden-specific parser implementation.

This parser extracts structured data from Sahibinden.com listing detail pages.

Key assumptions:
1. City and district MUST come from breadcrumb navigation
2. Phone number extraction may require dynamic loading (marked as TODO)
3. Office and agent names are extracted from designated sections
4. All fields are optional - parser gracefully handles missing data
"""

from typing import Dict, Any, Optional
import re

from src.core.parser import Parser
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class SahibindenParser(Parser):
    """Parser for sahibinden.com listing detail pages.
    
    This parser is designed to extract contact and location information
    from individual property listing pages on Sahibinden.com.
    
    Target fields:
    - office_name: Real estate office name
    - agent_name: Agent's name
    - phone_number: Contact phone number
    - city: City (from breadcrumb only)
    - district: District (from breadcrumb only)
    - listing_url: The listing URL
    
    Note: This parser does NOT extract property details (price, sqm, etc.)
    as those are outside the scope of Step 4.
    """
    
    def __init__(self):
        """Initialize Sahibinden parser."""
        super().__init__("sahibinden")
        
        # CSS selectors for Sahibinden.com structure
        # These may need adjustment based on actual HTML structure
        self.selectors = {
            # Breadcrumb navigation for location
            'breadcrumb': '.breadcrumb',
            'breadcrumb_items': 'li',
            
            # Agent/office information section
            'agent_section': '.classifiedInfo',
            'office_name': '.classifiedInfoCell .name',
            'agent_name': '.classifiedInfoCell .userName',
            
            # Phone number (may be in a button or hidden element)
            'phone_container': '.classifiedInfoCell',
            'phone_button': '[title*="Telefon"]',
        }
    
    def parse_listing_page(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse a Sahibinden listing detail page.
        
        Args:
            html: Raw HTML content of the listing page
            url: The URL of the listing
            
        Returns:
            Dictionary with extracted fields:
            {
                'office_name': str | None,
                'agent_name': str | None,
                'phone_number': str | None,
                'city': str | None,
                'district': str | None,
                'listing_url': str
            }
            
            Returns None if HTML parsing completely fails.
        """
        soup = self._make_soup(html)
        if soup is None:
            logger.error(f"Failed to parse HTML for URL: {url}")
            return None
        
        logger.info(f"Parsing Sahibinden listing: {url}")
        
        # Extract all fields
        result = {
            'office_name': self._extract_office_name(soup),
            'agent_name': self._extract_agent_name(soup),
            'phone_number': self._extract_phone_number(soup),
            'city': None,
            'district': None,
            'listing_url': url
        }
        
        # Extract location from breadcrumb
        location = self._extract_location_from_breadcrumb(soup)
        if location:
            result['city'] = location.get('city')
            result['district'] = location.get('district')
        
        # Log what was successfully extracted
        extracted_fields = [k for k, v in result.items() if v is not None]
        logger.info(f"Extracted fields: {', '.join(extracted_fields)}")
        
        # Log missing fields
        missing_fields = [k for k, v in result.items() if v is None and k != 'listing_url']
        if missing_fields:
            logger.warning(f"Missing fields: {', '.join(missing_fields)}")
        
        return result
    
    def _extract_location_from_breadcrumb(self, soup) -> Optional[Dict[str, str]]:
        """Extract city and district from breadcrumb navigation.
        
        Breadcrumb structure typically looks like:
        Anasayfa > İlan > Emlak > İlanlar > [City] > [District] > ...
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dict with 'city' and 'district' keys, or None if not found
        """
        breadcrumb = soup.select_one(self.selectors['breadcrumb'])
        if not breadcrumb:
            logger.warning("Breadcrumb not found - cannot extract city/district")
            return None
        
        # Get all breadcrumb items
        items = breadcrumb.select(self.selectors['breadcrumb_items'])
        if not items:
            logger.warning("No breadcrumb items found")
            return None
        
        # Extract text from each item
        breadcrumb_texts = [self._safe_text(item) for item in items]
        breadcrumb_texts = [t for t in breadcrumb_texts if t]  # Remove None values
        
        logger.debug(f"Breadcrumb trail: {' > '.join(breadcrumb_texts)}")
        
        # TODO: This is a heuristic - may need adjustment based on actual HTML
        # Typical structure: [Home] > [Ads] > [Real Estate] > [Rentals] > [City] > [District]
        # We assume city and district are the last two meaningful items before the listing title
        
        location = {'city': None, 'district': None}
        
        if len(breadcrumb_texts) >= 2:
            # Try to identify city and district
            # Common pattern: skip generic items like "Anasayfa", "İlan", "Emlak"
            generic_terms = ['anasayfa', 'ilan', 'emlak', 'ilanlar', 'konut', 'kiralik', 'satilik']
            
            # Filter out generic terms (case-insensitive)
            location_items = [
                t for t in breadcrumb_texts 
                if t.lower() not in generic_terms
            ]
            
            # Last two items are likely city and district (or district and neighborhood)
            if len(location_items) >= 2:
                location['city'] = location_items[-2]
                location['district'] = location_items[-1]
                logger.info(f"Extracted location: {location['city']} > {location['district']}")
            elif len(location_items) == 1:
                location['city'] = location_items[0]
                logger.info(f"Extracted city only: {location['city']}")
        
        # TODO: Handle edge cases:
        # - Breadcrumb structure variations
        # - Missing breadcrumb elements
        # - Non-standard location hierarchies
        
        return location if (location['city'] or location['district']) else None
    
    def _extract_office_name(self, soup) -> Optional[str]:
        """Extract real estate office name.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Office name or None if not found
        """
        # Try to find office name in the classified info section
        office_elem = soup.select_one(self.selectors['office_name'])
        office_name = self._safe_text(office_elem)
        
        if office_name:
            logger.debug(f"Found office name: {office_name}")
        else:
            logger.debug("Office name not found")
            # TODO: Try alternative selectors if primary fails
            # TODO: Handle private listings (no office)
        
        return office_name
    
    def _extract_agent_name(self, soup) -> Optional[str]:
        """Extract agent's name.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Agent name or None if not found
        """
        agent_elem = soup.select_one(self.selectors['agent_name'])
        agent_name = self._safe_text(agent_elem)
        
        if agent_name:
            logger.debug(f"Found agent name: {agent_name}")
        else:
            logger.debug("Agent name not found")
            # TODO: Try alternative selectors
            # TODO: Handle individual sellers (non-agents)
        
        return agent_name
    
    def _extract_phone_number(self, soup) -> Optional[str]:
        """Extract phone number.
        
        Note: Phone numbers on Sahibinden are often hidden behind a button
        and loaded dynamically via JavaScript. This implementation attempts
        to find visible phone numbers but may not work for all listings.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Phone number or None if not found
            
        TODO: Handle dynamic phone number loading:
        - Phone numbers may be revealed only after clicking a button
        - May need Selenium/Playwright for full extraction
        - Current implementation only finds already-visible numbers
        """
        # Look for phone number patterns in the agent/contact section
        phone_container = soup.select_one(self.selectors['phone_container'])
        
        if not phone_container:
            logger.debug("Phone container not found")
            return None
        
        # Try to find phone number button or link
        phone_button = phone_container.select_one(self.selectors['phone_button'])
        
        # Search for phone number patterns in text
        # Turkish phone format: 0XXX XXX XX XX or +90 XXX XXX XX XX
        phone_pattern = r'(\+90|0)\s?(\d{3})\s?(\d{3})\s?(\d{2})\s?(\d{2})'
        
        container_text = phone_container.get_text()
        match = re.search(phone_pattern, container_text)
        
        if match:
            phone_number = match.group(0)
            logger.debug(f"Found phone number: {phone_number}")
            return phone_number
        
        logger.debug("Phone number not found in static HTML")
        # TODO: Implement dynamic phone number extraction with Selenium
        # TODO: Handle "Show phone" button click simulation
        
        return None
        # TODO: Extract listing date
        # TODO: Extract agent info
        
        return {}
