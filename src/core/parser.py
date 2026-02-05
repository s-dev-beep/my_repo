"""HTML parsing module.

This module provides a base Parser interface for extracting structured data from HTML.
Parsers take raw HTML strings and return Python dictionaries with parsed data.

No network calls, no database access - just pure HTML to data transformation.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class Parser(ABC):
    """Base parser interface for extracting structured data from HTML.
    
    This is an abstract base class that defines the contract for all parsers.
    Each site adapter (Sahibinden, Hepsiemlak, etc.) should implement this interface.
    
    Key principles:
    - Parsers are stateless and reusable
    - Parsers receive raw HTML + URL as input
    - Parsers return structured Python dicts
    - No network calls, no database access
    - Graceful error handling with logging
    """
    
    def __init__(self, site_adapter: str):
        """Initialize parser.
        
        Args:
            site_adapter: Name of the site adapter (e.g., 'sahibinden')
        """
        self.site_adapter = site_adapter
        logger.info(f"Parser initialized for site: {site_adapter}")
    
    @abstractmethod
    def parse_listing_page(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single listing detail page.
        
        This is the main parsing method that must be implemented by each adapter.
        
        Args:
            html: Raw HTML content of a listing detail page
            url: The URL of the listing (for reference and extraction)
            
        Returns:
            Dictionary with extracted fields, or None if parsing fails
            
            Expected fields (all Optional[str] unless noted):
            - office_name: Real estate office name
            - agent_name: Agent's name
            - phone_number: Contact phone number
            - city: City name (from breadcrumb)
            - district: District name (from breadcrumb)
            - listing_url: The listing URL
        """
        pass
    
    def _make_soup(self, html: str) -> Optional[BeautifulSoup]:
        """Create BeautifulSoup object from HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            BeautifulSoup object or None if parsing fails
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML with BeautifulSoup: {e}")
            return None
    
    def _safe_text(self, element: Any) -> Optional[str]:
        """Safely extract and clean text from an element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Cleaned text string or None if element is None
        """
        if element is None:
            return None
        
        try:
            text = element.get_text(strip=True)
            return text if text else None
        except Exception as e:
            logger.debug(f"Failed to extract text from element: {e}")
            return None
    
    def _safe_attr(self, element: Any, attr: str) -> Optional[str]:
        """Safely extract an attribute from an element.
        
        Args:
            element: BeautifulSoup element
            attr: Attribute name (e.g., 'href', 'src')
            
        Returns:
            Attribute value or None if element is None or attribute doesn't exist
        """
        if element is None:
            return None
        
        try:
            return element.get(attr)
        except Exception as e:
            logger.debug(f"Failed to extract attribute '{attr}': {e}")
            return None
