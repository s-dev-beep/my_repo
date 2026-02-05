"""Pydantic models for data validation.

STEP 7 Implementation: Database models for MongoDB persistence.

Models are designed to be flexible and allow missing fields,
as per the requirements of the database layer.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Office(BaseModel):
    """Office schema for MongoDB.
    
    Unique constraint: office_name + phone_number
    Both fields are required for deduplication, but we allow None for
    flexibility when these fields are missing in the source data.
    """
    
    office_name: Optional[str] = Field(None, description="Office name (uppercase, trimmed)")
    phone_number: Optional[str] = Field(None, description="Phone number (E.164 format)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Agent(BaseModel):
    """Agent schema for MongoDB.
    
    Unique constraint: agent_name + phone_number
    Both fields are required for deduplication, but we allow None for
    flexibility when these fields are missing in the source data.
    """
    
    agent_name: Optional[str] = Field(None, description="Agent name (uppercase, trimmed)")
    phone_number: Optional[str] = Field(None, description="Phone number (E.164 format)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Listing(BaseModel):
    """Property listing schema for MongoDB.
    
    Unique constraint: listing_url
    Stores normalized data from STEP 5 with references to office and agent.
    """
    
    listing_url: str = Field(..., description="Listing URL (unique identifier)")
    
    # Contact information (from normalized data)
    office_name: Optional[str] = Field(None, description="Office name")
    agent_name: Optional[str] = Field(None, description="Agent name")
    phone_number: Optional[str] = Field(None, description="Contact phone number")
    
    # Location information (from normalized data)
    city: Optional[str] = Field(None, description="City (title case)")
    district: Optional[str] = Field(None, description="District (title case)")
    
    # Source and confidence (from normalized data)
    source: Optional[str] = Field(None, description="Source site (sahibinden, hepsiemlak, etc)")
    confidence: Optional[str] = Field(None, description="Data confidence level (high/medium/low)")
    
    # References to related entities (populated during upsert)
    office_id: Optional[str] = Field(None, description="MongoDB ObjectId reference to Office")
    agent_id: Optional[str] = Field(None, description="MongoDB ObjectId reference to Agent")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class CrawlMetadata(BaseModel):
    """Metadata for a crawl run."""
    
    site: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_listings: int = 0
    new_listings: int = 0
    duplicates: int = 0
    errors: int = 0
    
    # TODO: Add more statistics
