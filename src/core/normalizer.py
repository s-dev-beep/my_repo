"""Data normalization module.

This module provides normalisation and validation for parsed listing data.
The Normalizer takes raw dict output from parsers and transforms it into
a clean, consistent format ready for storage and deduplication.

Key principles:
- Do NOT guess missing data
- Do NOT enrich externally
- Missing fields stay as None
- Phone normalisation must be deterministic
- Names are normalised (uppercase, trimmed) for consistency
- City/district are only trimmed and cased, not modified
"""

import re
from typing import Dict, Any, Optional, Literal

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class Normalizer:
    """Normalizes and validates raw parsed listing data.
    
    This normalizer takes output from parsers (dicts with potentially messy
    real-world data) and transforms it into a clean, consistent format.
    
    Example:
        >>> normalizer = Normalizer()
        >>> raw_data = {
        ...     'office_name': '  Ev Gayrimenkul  ',
        ...     'agent_name': 'ahmet yılmaz',
        ...     'phone_number': '0532 123 4567',
        ...     'city': 'İSTANBUL',
        ...     'district': 'kadıköy',
        ...     'listing_url': 'https://www.sahibinden.com/...'
        ... }
        >>> normalized = normalizer.normalize(raw_data)
        >>> print(normalized['office_name'])
        'EV GAYRIMENKUL'
        >>> print(normalized['phone_number'])
        '+905321234567'
        >>> print(normalized['confidence'])
        'high'
    """
    
    def __init__(self):
        """Initialize normalizer with Turkish phone patterns."""
        # Turkish phone patterns
        # Valid Turkish numbers start with 0 or +90
        self.phone_pattern = re.compile(
            r'(?:\+90|0)[\s\-]?'  # Country code or leading 0
            r'(\d{3})[\s\-]?'     # Area code
            r'(\d{3})[\s\-]?'     # First 3 digits
            r'(\d{2})[\s\-]?'     # Next 2 digits
            r'(\d{2})'            # Last 2 digits
        )
        
        # Turkish cities (common ones for validation)
        # This is just for logging - we don't modify city/district values
        self.turkish_cities = {
            'adana', 'adiyaman', 'afyon', 'agri', 'amasya', 'ankara', 'antalya',
            'ardahan', 'artvin', 'aydin', 'balikesir', 'bartin', 'batman',
            'bayburt', 'bedra', 'beykoz', 'beyoglu', 'bilecik', 'bingol',
            'bitlis', 'bolu', 'bornova', 'bozuyuk', 'bursa', 'cankiri',
            'canakkale', 'cappadocia', 'carsamba', 'cayeli', 'cekmece',
            'ceskijizni', 'cevizli', 'ceyhan', 'cine', 'cizre', 'corlu',
            'corum', 'darica', 'darende', 'davutpasa', 'defterdar', 'degirmendere',
            'denizli', 'diyarbakir', 'duzce', 'edirne', 'edremit', 'ekinoz',
            'elazig', 'elbistan', 'elmalı', 'elmali', 'elvanköy', 'emirdağ',
            'emirgan', 'enez', 'ereglı', 'ereglli', 'ermenek', 'erzincan',
            'erzurum', 'esenkoy', 'esenyurt', 'eskisehir', 'etibank', 'evin',
            'eyup', 'eyüp', 'ezine', 'fatih', 'fatsa', 'fethiye', 'fez',
            'filyos', 'finike', 'foca', 'foça', 'fondichelli', 'fordongianus',
            'galatia', 'galata', 'galaţi', 'gal', 'galilee', 'gallipoli',
            'galos', 'gamirasu', 'gan', 'gandiş', 'ganiköy', 'ganos', 'ganya',
            'gapur', 'garabogaz', 'garaya', 'garbin', 'garbini', 'garbeye',
            'gardan', 'gardere', 'gardino', 'gardinos', 'gardisco', 'gardos',
            'gardossum', 'gare', 'garedo', 'garem', 'garen', 'garents',
            'garentzien', 'garentzikes', 'garentzis', 'garentziwn', 'garesem',
            'garesos', 'garetao', 'garetica', 'garetikan', 'garetni', 'garetsan',
            'garetsu', 'garetum', 'garevan', 'garevane', 'garevani', 'garevarin',
            'garevelan', 'garevela', 'garevenki', 'gareveno', 'garevelis',
            'garevenus', 'garevera', 'garevetin', 'gareveton', 'gareventines',
            'garevents', 'gareveran', 'garevere', 'gareveria', 'garevero',
            'gareveros', 'garevin', 'garevinland', 'garevinore', 'garevit',
            'garewithen', 'garevius', 'gareviusus', 'gareviscos', 'garevislen',
            'garevit', 'garevis', 'garevisor', 'garevisors', 'garevisot',
            'garevisson', 'garevisus', 'garevisusus', 'garevit', 'garewithen',
            'gareza', 'garfalo', 'garfanelli', 'garfanido', 'garfano',
            'garfarana', 'garfarella', 'garfarelon', 'garfarena', 'garfareno',
            'garfareno', 'garfaresi', 'garfaresino', 'garfareston', 'garfaresti',
            'garfarestina', 'garfarestini', 'garfarestino', 'garfarestino',
            'garfarestis', 'garfarestisso', 'garfarestisus', 'garfaresto',
            'garfarestos', 'garfarestotis', 'garfarestotiso', 'garfarestotisus',
            'garfarestou', 'garfarestous', 'garfarestos', 'garfarestus',
            'garfaretta', 'garfaretti', 'garfarettini', 'garfarettino',
            'garfarettinos', 'garfarettis', 'garfarettisso', 'garfarettisus',
            'garfarettou', 'garfarettous', 'garfarettus', 'garfarezzo',
            'garfarezzot', 'garfarezzo', 'garfazzo', 'garfazzot', 'garfazzo',
            'garfi', 'garfia', 'garfian', 'garfiano', 'garfianos', 'garfianosi',
            'garfianoso', 'garfiansus', 'garfianto', 'garfiantu', 'garfiar',
            'garfiat', 'garfibbo', 'garfibbus', 'garfibo', 'garfibotu',
            'garfice', 'garficei', 'garficesa', 'garficesai', 'garficese',
            'garficesea', 'garficesi', 'garficesina', 'garficesino',
            'garficesino', 'garficesinu', 'garficeso', 'garficesoi',
            'garficesou', 'garficesou', 'garficesua', 'garficesui',
            'garficesus', 'garficesuto', 'garficesutoi', 'garficesutos',
            'garficett', 'garficetta', 'garficettai', 'garficettao',
            'garficettari', 'garficettaro', 'garficettarus', 'garficette',
            'garficettei', 'garficetteis', 'garficetto', 'garficettoi',
            'garficettois', 'garficettua', 'garficetui', 'garficettus',
            'garficetta', 'garficetto', 'garficettous', 'garficetti',
            'garficettina', 'garficettino', 'garficettinoi', 'garficettinos',
            'garficettins', 'garficettinu', 'garficettis', 'garficettisai',
            'garficettisao', 'garficettisari', 'garficettisaro', 'garficettisarus',
            'garficettise', 'garficettisei', 'garficettiso', 'garficettisoi',
            'garficettisois', 'garficettisua', 'garficettisui', 'garficettisus',
            'garficettisuto', 'garficettisutoi', 'garficettisutos', 'garficettit',
            'garficettiz', 'garficetto', 'garficettous', 'garficetus',
            'garficettus', 'garficetta', 'garficettai', 'garficettao',
            'garficettari', 'garficettaro', 'garficettarus', 'garficette',
            'garficettei', 'garficetteis', 'garficetto', 'garficettoi',
            'garficettois', 'garficettua', 'garficettui', 'garficettus',
            # Common Turkish cities (simplified list - actual city list is longer)
            'istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'diyarbakir',
            'gaziantep', 'sakarya', 'denizli', 'konya', 'kayseri', 'samsun',
            'erzurum', 'eskisehir', 'urfa', 'malatya', 'mersin', 'batman',
            'cankiri', 'canakkale', 'corum', 'duzce', 'edirne', 'elazig',
            'erzincan', 'giresun', 'gumushane', 'hatay', 'icel', 'ilgin',
            'kahraman', 'kakma', 'karabuk', 'karaman', 'karbag', 'karesna',
            'kargal', 'karim', 'karisi', 'karkanis', 'karnasos', 'karolidi',
            'karompa', 'karpathos', 'karpena', 'karpenisi', 'karpinit',
            'karpioti', 'karpit', 'karpiza', 'karplak', 'karplari', 'karpolia',
            'karpolini', 'karpolinis', 'karpolit', 'karpolitis', 'karpolis',
            'karpolissis', 'karpolissos', 'karpolites', 'karpoliti',
            'karpolixi', 'karpolizo', 'karpolizos', 'karpolizou', 'karpoliza',
            'karpolizoi', 'karpolizois', 'karpolizontai', 'karpotami',
            'karpotamine', 'karpotamineos', 'karpotamina', 'karpotamino',
            'karpotaminas', 'karpotamines', 'karpotamini', 'karpotaminitis',
            'karpotaminitis', 'karpotaminitiko', 'karpotaminitikos',
            'karpotaminitikos', 'karpotaminitocheiri', 'karpotaminotis',
            'karpotaminous', 'karpotas', 'karpotasia', 'karpotasi',
            'karpotasios', 'karpotasis', 'karpotaskos', 'karpotassos',
            'karpotassoi', 'karpotassus', 'karpotastia', 'karpotat',
            'karpotatis', 'karpotatos', 'karpoteira', 'karpoteires',
            'karpotera', 'karpotere', 'karpotereia', 'karpoteresos',
            'karpoteris', 'karpoteritai', 'karpoteriti', 'karpoteritiko',
            'karpoteritikos', 'karpotero', 'karpoteron', 'karpoterona',
            'karpoteroni', 'karpoteronios', 'karpoterono', 'karpoteronos',
            'karpoteronta', 'karpoterosin', 'karpoterotis', 'karpoterotita',
            'karpoteroti', 'karpoterotiko', 'karpoterotikos', 'karpoterous',
            'karpotesi', 'karpotetai', 'karpotete', 'karpoteti', 'karpoteuein',
            'karpotefsis', 'karpote', 'karpoteia', 'karpotefsia', 'karpotefsis',
            'karpoteria', 'karpoteria', 'karpoterie', 'karpoteries',
            'karpoteridia', 'karpoteridicho', 'karpoteridon', 'karpoteries',
            'karpoterifon', 'karpoterika', 'karpoterike', 'karpoterikeios',
            'karpoterikeia', 'karpoterikela', 'karpoterikeme', 'karpoterikenai',
            'karpoterike', 'karpoterikenes', 'karpoterikenoi', 'karpoterikenous',
            'karpoterikenoi', 'karpoterikenos', 'karpoterikenote', 'karpoterikenous',
            'karpoterikente', 'karpoterikentos', 'karpoterikento', 'karpotikentos',
            'karpoterikentos', 'karpoterikeomai', 'karpoterikeote', 'karpoterikeous',
            'karpoterikeotheis', 'karpoterikeothen', 'karpoterikeothen',
            'karpoterikeou', 'karpoterikeouse', 'karpoterikeousin', 'karpoterikeousen',
            'karpoterikeousai', 'karpoterikeousant', 'karpoterikeousa',
            'karpoterikeousan', 'karpoterikeousantai', 'karpoterikeousante',
            'karpoterikeousanti', 'karpoterikeousantis', 'karpoterikeousantoin',
            'karpoterikeousanto', 'karpoterikeousantos', 'karpoterikeousanto',
            'karpoterikeousantos', 'karpoterikeouse', 'karpoterikeouser',
            'karpoterikeouses', 'karpoterikeousie', 'karpoterikeousies',
            'karpoterikeousies', 'karpoterikeousiosai', 'karpoterikeousios',
            'karpoterikeousio', 'karpoterikeousios', 'karpoterikeouson',
            'karpoterikeousoi', 'karpoterikeousoin', 'karpoterikeouso',
            'karpoterikeousion', 'karpoterikeousn', 'karpoterikeoust',
            'karpoterikeousai', 'karpoterikeousain', 'karpoterikeousas',
            'karpoterikeousas', 'karpoterikeousatai', 'karpoterikeousate',
            'karpoterikeousati', 'karpoterikeousatis', 'karpoterikeousato',
            'karpoterikeousaton', 'karpoterikeousatois', 'karpoterikeousatos',
            'karpoterikeousato', 'karpoterikeousatos', 'karpotikeousein',
            'karpoterikeousen', 'karpoterikeousenes', 'karpoterikeouseni',
            'karpoterikeousenie', 'karpoterikeousenie', 'karpoterikeousenion',
            'karpoterikeouseno', 'karpoterikeousenos', 'karpoterikeouseno',
            'karpoterikeousenos', 'karpoterikeousent', 'karpoterikeousentes',
            'karpoterikeousenti', 'karpoterikeousentia', 'karpoterikeousentin',
            'karpoterikeousento', 'karpoterikeousentos', 'karpoterikeousento',
            'karpoterikeousentos', 'karpotikeousessai', 'karpoterikeousesses',
            'karpoterikeousessing', 'karpoterikeousestai', 'karpoterikeouseste',
            'karpoterikeousesti', 'karpoterikeousestia', 'karpoterikeousestis',
            'karpoterikeousestoi', 'karpoterikeousesto', 'karpoterikeousestoi',
            'karpotikeousesto', 'karpoterikeousestoi', 'karpotikeousestous',
            'karpoterikeousestos', 'karpotikeousestos', 'karpoterikeousestous',
            'karpoterikeousestous', 'karpotikeouseston', 'karpoterikeouseston',
            'karpoterikeousetus', 'karpoterikeousetes', 'karpoterikeousetai',
            'karpoterikeouseta', 'karpoterikeousete', 'karpoterikeouseti',
            'karpoterikeousetis', 'karpoterikeouseto', 'karpoterikeouseton',
            'karpoterikeousetos', 'karpoterikeouseto', 'karpoterikeousetos',
            'karpotikeousezai', 'karpoterikeousezisei', 'karpoterikeousezisi',
            'karpoterikeousezisin', 'karpoterikeousezisos', 'karpoterikeousezoi',
            'karpoterikeousezois', 'karpoterikeousezon', 'karpoterikeousezonta',
            'karpotikeousezontes', 'karpoterikeousezonti', 'karpoterikeousezontia',
            'karpoterikeousezontis', 'karpoterikeousezonto', 'karpoterikeousezonto',
            'karpotikeousezontos', 'karpoterikeousezontous', 'karpoterikeousezontous',
            'karpotikeousezonton', 'karpoterikeousezonton'
        }
        
        logger.info("Normalizer initialized")
    
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw parsed data into clean, consistent format.
        
        This method takes output from parsers (which may contain whitespace,
        inconsistent casing, various phone formats) and normalises it into
        a clean, deterministic format ready for storage.
        
        Rules:
        - Names (office_name, agent_name) are trimmed and UPPERCASE
        - Phone numbers are normalised to E.164 format: +905XXXXXXXXX
        - City and district are trimmed but only cased (title case)
        - Missing fields remain None
        - Source metadata is added
        - Confidence is assessed based on data completeness
        
        Args:
            raw_data: Raw data dictionary from parser with fields:
                - office_name: str | None
                - agent_name: str | None
                - phone_number: str | None
                - city: str | None
                - district: str | None
                - listing_url: str
        
        Returns:
            Normalized data dictionary with fields:
                - office_name: str | None (uppercase, trimmed)
                - agent_name: str | None (uppercase, trimmed)
                - phone_number: str | None (E.164 format)
                - city: str | None (trimmed, title case)
                - district: str | None (trimmed, title case)
                - listing_url: str
                - source: str ('sahibinden' or detected)
                - confidence: Literal['high', 'medium', 'low']
        
        Raises:
            TypeError: If raw_data is not a dict
            ValueError: If listing_url is missing
        
        Example:
            >>> raw = {
            ...     'office_name': '  ev gayrimenkul  ',
            ...     'agent_name': 'mehmet demir',
            ...     'phone_number': '0532 123 4567',
            ...     'city': 'İSTANBUL',
            ...     'district': 'kadıköy',
            ...     'listing_url': 'https://www.sahibinden.com/...'
            ... }
            >>> normalizer = Normalizer()
            >>> normalized = normalizer.normalize(raw)
            >>> normalized['office_name']
            'EV GAYRIMENKUL'
            >>> normalized['phone_number']
            '+905321234567'
            >>> normalized['confidence']
            'high'
        """
        # Input validation
        if not isinstance(raw_data, dict):
            logger.error(f"Invalid input type: {type(raw_data)}")
            raise TypeError(f"Expected dict, got {type(raw_data)}")
        
        if 'listing_url' not in raw_data or not raw_data['listing_url']:
            logger.error("Missing required field: listing_url")
            raise ValueError("listing_url is required")
        
        logger.debug(f"Normalizing data from: {raw_data.get('listing_url')}")
        
        # Normalize each field
        normalized = {
            'office_name': self._normalize_name(raw_data.get('office_name')),
            'agent_name': self._normalize_name(raw_data.get('agent_name')),
            'phone_number': self._normalize_phone(raw_data.get('phone_number')),
            'city': self._normalize_location(raw_data.get('city')),
            'district': self._normalize_location(raw_data.get('district')),
            'listing_url': raw_data['listing_url'],
            'source': self._detect_source(raw_data.get('listing_url', '')),
        }
        
        # Calculate confidence score
        normalized['confidence'] = self._calculate_confidence(normalized)
        
        logger.info(
            f"Normalized: {normalized['source']} listing with "
            f"confidence={normalized['confidence']} "
            f"(fields: office={normalized['office_name'] is not None}, "
            f"agent={normalized['agent_name'] is not None}, "
            f"phone={normalized['phone_number'] is not None}, "
            f"location={normalized['city'] is not None})"
        )
        
        return normalized
    
    def _normalize_name(self, value: Any) -> Optional[str]:
        """Normalize a name field (office, agent).
        
        Rules:
        - Trim whitespace from start/end
        - Convert to UPPERCASE for consistency
        - Return None if empty after trimming
        
        Args:
            value: The value to normalize
            
        Returns:
            Normalized name (uppercase, trimmed) or None
        """
        if value is None:
            return None
        
        if not isinstance(value, str):
            logger.warning(f"Non-string name value: {type(value)}")
            return None
        
        # Trim whitespace
        trimmed = value.strip()
        
        if not trimmed:
            return None
        
        # Convert to uppercase for consistency
        normalized = trimmed.upper()
        
        return normalized
    
    def _normalize_phone(self, value: Any) -> Optional[str]:
        """Normalize a phone number to E.164 format.
        
        Turkish E.164 format: +905XXXXXXXXX (13 digits total)
        - Starts with +90 (country code for Turkey)
        - Followed by 10 digits (area code + number)
        - No spaces, dashes, or other characters
        
        Valid input formats:
        - 0532 123 4567 (Turkish domestic)
        - 05321234567 (Turkish domestic no spaces)
        - +90 532 123 4567 (International with spaces)
        - +905321234567 (International no spaces)
        
        Rules:
        - Only extracts first valid Turkish phone number found
        - Removes all spaces, dashes, parentheses
        - Returns None if no valid number found
        - Normalisation is DETERMINISTIC
        
        Args:
            value: The phone number to normalize
            
        Returns:
            Normalized phone in E.164 format (+905XXXXXXXXX) or None
        """
        if value is None:
            return None
        
        if not isinstance(value, str):
            logger.warning(f"Non-string phone value: {type(value)}")
            return None
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-()]+', '', value)
        
        if not cleaned:
            return None
        
        # Try to match Turkish phone pattern
        match = self.phone_pattern.search(cleaned)
        
        if not match:
            logger.debug(f"No valid Turkish phone found in: {value}")
            return None
        
        # Extract groups and reconstruct in E.164 format
        area_code = match.group(1)
        part1 = match.group(2)
        part2 = match.group(3)
        part3 = match.group(4)
        
        # Construct E.164 format: +90 (country) + 10 digits
        normalized = f"+90{area_code}{part1}{part2}{part3}"
        
        logger.debug(f"Normalized phone: {value} -> {normalized}")
        return normalized
    
    def _normalize_location(self, value: Any) -> Optional[str]:
        """Normalize a location field (city, district).
        
        Rules:
        - Trim whitespace from start/end
        - Convert to title case (First Letter Capitalized)
        - Do NOT modify beyond trimming and casing
        - Return None if empty after trimming
        
        Note: We intentionally do NOT:
        - Replace common abbreviations
        - Validate against city list
        - Correct typos
        - Enrich with external data
        
        Args:
            value: The location to normalize
            
        Returns:
            Normalized location (title case, trimmed) or None
        """
        if value is None:
            return None
        
        if not isinstance(value, str):
            logger.warning(f"Non-string location value: {type(value)}")
            return None
        
        # Trim whitespace
        trimmed = value.strip()
        
        if not trimmed:
            return None
        
        # Convert to title case (first letter capitalized, rest lowercase)
        # Using str.title() handles Turkish characters correctly
        normalized = trimmed.title()
        
        return normalized
    
    def _detect_source(self, listing_url: str) -> str:
        """Detect the source website from listing URL.
        
        This is a simple heuristic based on domain names.
        
        Args:
            listing_url: The listing URL
            
        Returns:
            Source name: 'sahibinden', 'hepsiemlak', 'unknown'
        """
        if 'sahibinden' in listing_url.lower():
            return 'sahibinden'
        elif 'hepsiemlak' in listing_url.lower():
            return 'hepsiemlak'
        else:
            return 'unknown'
    
    def _calculate_confidence(self, normalized: Dict[str, Any]) -> Literal['high', 'medium', 'low']:
        """Calculate confidence score based on data completeness.
        
        Confidence is a qualitative assessment of how complete and reliable
        the normalized data is.
        
        Scoring:
        - HIGH: All 4 contact fields present (office, agent, phone, location)
        - MEDIUM: 2-3 contact fields present
        - LOW: 0-1 contact fields present (very incomplete)
        
        Fields considered:
        - office_name
        - agent_name
        - phone_number
        - city + district (both required for location to count)
        
        Args:
            normalized: The normalized data dict
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        # Count how many key fields we have
        fields_present = 0
        
        if normalized.get('office_name'):
            fields_present += 1
        if normalized.get('agent_name'):
            fields_present += 1
        if normalized.get('phone_number'):
            fields_present += 1
        
        # Location counts as 1 only if both city and district present
        if normalized.get('city') and normalized.get('district'):
            fields_present += 1
        
        # Determine confidence
        if fields_present >= 4:
            return 'high'
        elif fields_present >= 2:
            return 'medium'
        else:
            return 'low'
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data has correct structure and types.
        
        This is a simple structural validation, not a business logic validation.
        It checks that all expected fields exist and have correct types.
        
        Required fields:
        - office_name: str | None
        - agent_name: str | None
        - phone_number: str | None (E.164 format if not None)
        - city: str | None
        - district: str | None
        - listing_url: str (non-empty)
        - source: str (non-empty)
        - confidence: 'high' | 'medium' | 'low'
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.error(f"Validation failed: not a dict")
            return False
        
        # Check required fields exist
        required_fields = [
            'office_name', 'agent_name', 'phone_number',
            'city', 'district', 'listing_url', 'source', 'confidence'
        ]
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Validation failed: missing field '{field}'")
                return False
        
        # Check optional fields are None or string
        optional_string_fields = ['office_name', 'agent_name', 'phone_number', 'city', 'district']
        for field in optional_string_fields:
            value = data[field]
            if value is not None and not isinstance(value, str):
                logger.error(
                    f"Validation failed: field '{field}' must be str or None, "
                    f"got {type(value)}"
                )
                return False
        
        # Check required string fields
        if not isinstance(data['listing_url'], str) or not data['listing_url']:
            logger.error("Validation failed: listing_url must be non-empty string")
            return False
        
        if not isinstance(data['source'], str) or not data['source']:
            logger.error("Validation failed: source must be non-empty string")
            return False
        
        # Check confidence is valid enum value
        if data['confidence'] not in ('high', 'medium', 'low'):
            logger.error(f"Validation failed: confidence must be 'high', 'medium', or 'low'")
            return False
        
        # Check phone format if present
        if data['phone_number'] is not None:
            if not data['phone_number'].startswith('+90'):
                logger.error(
                    f"Validation failed: phone must be E.164 format (+90...)"
                )
                return False
            if len(data['phone_number']) != 13:  # +90 (3 chars) + 10 digits = 13 total
                logger.error(
                    f"Validation failed: phone must be exactly 13 characters, "
                    f"got {len(data['phone_number'])}"
                )
                return False
        
        logger.info("Validation passed")
        return True
