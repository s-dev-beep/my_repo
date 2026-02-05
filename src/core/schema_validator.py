"""STEP 13: Entity Schema Validation

Lightweight validation module that enforces the canonical schema.
Validates entities without changing behavior.
Logs issues for manual review without crashing.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from src.core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating an entity."""
    valid: bool
    entity_type: str
    entity_id: str
    errors: List[str]
    warnings: List[str]
    
    def __str__(self) -> str:
        """Format as human-readable string."""
        status = "✓ VALID" if self.valid else "✗ INVALID"
        msg = f"{status} [{self.entity_type}] {self.entity_id}"
        
        if self.warnings:
            msg += f"\n  Warnings: {'; '.join(self.warnings)}"
        
        if self.errors:
            msg += f"\n  Errors: {'; '.join(self.errors)}"
        
        return msg


class SchemaValidator:
    """Validates entities against canonical schema."""
    
    # URL pattern (basic validation)
    URL_PATTERN = re.compile(
        r'^https?://'  # http or https
        r'(?:[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=])+$'
    )
    
    # E.164 phone pattern: +90XXXXXXXXXX
    PHONE_PATTERN = re.compile(r'^\+90\d{9,}$')
    
    # Known sources
    KNOWN_SOURCES = {'sahibinden', 'hepsiemlak'}
    
    # Valid confidence levels
    VALID_CONFIDENCE = {'high', 'medium', 'low'}
    
    def validate_listing(self, listing: Dict[str, Any]) -> ValidationResult:
        """Validate a listing against schema.
        
        Args:
            listing: Listing document
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # REQUIRED: listing_url
        url = listing.get('listing_url')
        if not url:
            errors.append("listing_url is required and cannot be empty")
        elif not isinstance(url, str):
            errors.append(f"listing_url must be string, got {type(url)}")
        elif not self.URL_PATTERN.match(url):
            warnings.append(f"listing_url doesn't match URL pattern: {url}")
        
        entity_id = url or "unknown"
        
        # OPTIONAL: office_name
        office = listing.get('office_name')
        if office is not None:
            if not isinstance(office, str):
                warnings.append(f"office_name must be string, got {type(office)}")
            elif not office.isupper() and office:
                warnings.append(f"office_name should be uppercase: {office}")
            elif len(office) > 255:
                warnings.append(f"office_name exceeds 255 chars: {len(office)}")
        
        # OPTIONAL: agent_name
        agent = listing.get('agent_name')
        if agent is not None:
            if not isinstance(agent, str):
                warnings.append(f"agent_name must be string, got {type(agent)}")
            elif not agent.isupper() and agent:
                warnings.append(f"agent_name should be uppercase: {agent}")
            elif len(agent) > 255:
                warnings.append(f"agent_name exceeds 255 chars: {len(agent)}")
        
        # OPTIONAL: phone_number
        phone = listing.get('phone_number')
        if phone is not None:
            if not isinstance(phone, str):
                warnings.append(f"phone_number must be string, got {type(phone)}")
            elif not self.PHONE_PATTERN.match(phone):
                warnings.append(f"phone_number doesn't match E.164 format: {phone}")
            elif len(phone) > 15:
                warnings.append(f"phone_number exceeds 15 chars: {len(phone)}")
        
        # OPTIONAL: city
        city = listing.get('city')
        if city is not None:
            if not isinstance(city, str):
                warnings.append(f"city must be string, got {type(city)}")
            elif len(city) > 100:
                warnings.append(f"city exceeds 100 chars: {len(city)}")
        
        # OPTIONAL: district
        district = listing.get('district')
        if district is not None:
            if not isinstance(district, str):
                warnings.append(f"district must be string, got {type(district)}")
            elif len(district) > 100:
                warnings.append(f"district exceeds 100 chars: {len(district)}")
        
        # OPTIONAL: source
        source = listing.get('source')
        if source is not None:
            if not isinstance(source, str):
                warnings.append(f"source must be string, got {type(source)}")
            elif source not in self.KNOWN_SOURCES:
                warnings.append(f"source is unknown: {source}")
        
        # OPTIONAL: confidence
        confidence = listing.get('confidence')
        if confidence is not None:
            if not isinstance(confidence, str):
                warnings.append(f"confidence must be string, got {type(confidence)}")
            elif confidence not in self.VALID_CONFIDENCE:
                warnings.append(f"confidence must be one of {self.VALID_CONFIDENCE}, got {confidence}")
        
        # Check metadata
        metadata = listing.get('_metadata', {})
        if not isinstance(metadata, dict):
            warnings.append(f"_metadata must be dict, got {type(metadata)}")
        elif 'run_id' not in metadata:
            warnings.append("_metadata missing run_id")
        elif 'source' not in metadata:
            warnings.append("_metadata missing source")
        
        # Log results
        valid = len(errors) == 0
        result = ValidationResult(
            valid=valid,
            entity_type='Listing',
            entity_id=entity_id,
            errors=errors,
            warnings=warnings
        )
        
        if not valid:
            logger.error(f"Listing validation failed: {result}")
        elif warnings:
            logger.warning(f"Listing validation warnings: {result}")
        
        return result
    
    def validate_office(self, office: Dict[str, Any]) -> ValidationResult:
        """Validate an office against schema.
        
        Args:
            office: Office document
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # REQUIRED: name (for deduplication)
        name = office.get('name')
        if not name:
            errors.append("office name is required and cannot be empty")
        elif not isinstance(name, str):
            errors.append(f"office name must be string, got {type(name)}")
        elif not name.isupper():
            warnings.append(f"office name should be uppercase: {name}")
        elif len(name) > 255:
            warnings.append(f"office name exceeds 255 chars: {len(name)}")
        
        entity_id = name or "unknown"
        
        # OPTIONAL: phone_number
        phone = office.get('phone_number')
        if phone is not None:
            if not isinstance(phone, str):
                warnings.append(f"phone_number must be string, got {type(phone)}")
            elif not self.PHONE_PATTERN.match(phone):
                warnings.append(f"phone_number doesn't match E.164 format: {phone}")
            elif len(phone) > 15:
                warnings.append(f"phone_number exceeds 15 chars: {len(phone)}")
        else:
            warnings.append(f"office '{name}' has no phone number - deduplication by name only")
        
        # Check metadata
        metadata = office.get('_metadata', {})
        if not isinstance(metadata, dict):
            warnings.append(f"_metadata must be dict, got {type(metadata)}")
        elif 'source' not in metadata:
            warnings.append("_metadata missing source")
        
        # Log results
        valid = len(errors) == 0
        result = ValidationResult(
            valid=valid,
            entity_type='Office',
            entity_id=entity_id,
            errors=errors,
            warnings=warnings
        )
        
        if not valid:
            logger.error(f"Office validation failed: {result}")
        elif warnings:
            logger.warning(f"Office validation warnings: {result}")
        
        return result
    
    def validate_agent(self, agent: Dict[str, Any]) -> ValidationResult:
        """Validate an agent against schema.
        
        Args:
            agent: Agent document
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # REQUIRED: name (for deduplication)
        name = agent.get('name')
        if not name:
            errors.append("agent name is required and cannot be empty")
        elif not isinstance(name, str):
            errors.append(f"agent name must be string, got {type(name)}")
        elif not name.isupper():
            warnings.append(f"agent name should be uppercase: {name}")
        elif len(name) > 255:
            warnings.append(f"agent name exceeds 255 chars: {len(name)}")
        
        entity_id = name or "unknown"
        
        # OPTIONAL: phone_number
        phone = agent.get('phone_number')
        if phone is not None:
            if not isinstance(phone, str):
                warnings.append(f"phone_number must be string, got {type(phone)}")
            elif not self.PHONE_PATTERN.match(phone):
                warnings.append(f"phone_number doesn't match E.164 format: {phone}")
            elif len(phone) > 15:
                warnings.append(f"phone_number exceeds 15 chars: {len(phone)}")
        else:
            warnings.append(f"agent '{name}' has no phone number - deduplication by name only")
        
        # Check metadata
        metadata = agent.get('_metadata', {})
        if not isinstance(metadata, dict):
            warnings.append(f"_metadata must be dict, got {type(metadata)}")
        elif 'source' not in metadata:
            warnings.append("_metadata missing source")
        
        # Log results
        valid = len(errors) == 0
        result = ValidationResult(
            valid=valid,
            entity_type='Agent',
            entity_id=entity_id,
            errors=errors,
            warnings=warnings
        )
        
        if not valid:
            logger.error(f"Agent validation failed: {result}")
        elif warnings:
            logger.warning(f"Agent validation warnings: {result}")
        
        return result
    
    def validate_batch(
        self,
        listings: List[Dict[str, Any]] = None,
        offices: List[Dict[str, Any]] = None,
        agents: List[Dict[str, Any]] = None
    ) -> Tuple[int, int]:
        """Validate a batch of entities.
        
        Args:
            listings: List of listing documents
            offices: List of office documents
            agents: List of agent documents
            
        Returns:
            Tuple of (valid_count, warning_count)
        """
        valid = 0
        warnings = 0
        
        if listings:
            logger.info(f"Validating {len(listings)} listings...")
            for listing in listings:
                result = self.validate_listing(listing)
                if result.valid:
                    valid += 1
                else:
                    warnings += 1
        
        if offices:
            logger.info(f"Validating {len(offices)} offices...")
            for office in offices:
                result = self.validate_office(office)
                if result.valid:
                    valid += 1
                else:
                    warnings += 1
        
        if agents:
            logger.info(f"Validating {len(agents)} agents...")
            for agent in agents:
                result = self.validate_agent(agent)
                if result.valid:
                    valid += 1
                else:
                    warnings += 1
        
        logger.info(f"Batch validation complete: {valid} valid, {warnings} with warnings")
        
        return valid, warnings


# Singleton instance
_validator = SchemaValidator()


def get_validator() -> SchemaValidator:
    """Get the global schema validator instance."""
    return _validator
