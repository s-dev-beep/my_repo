"""MongoDB connection and operations.

STEP 7: Database Persistence Layer

This module provides:
1. MongoDB connection management
2. Upsert operations for Office, Agent, and Listing entities
3. Schema validation with Pydantic
4. Idempotent persistence (never blind inserts)

Key concepts:
- Upserts use deterministic keys (not _id)
- Missing fields are allowed
- All operations are logged
- Connection management with context managers
"""

import os
from typing import Dict, Any, Optional, Literal, Tuple
from datetime import datetime

from pymongo import MongoClient as PyMongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId

from src.core.logger import setup_logger
from src.db.models.listing import Office, Agent, Listing

logger = setup_logger(__name__)


class MongoDBConnection:
    """Manages MongoDB connection and operations.
    
    This class handles:
    - Connection pooling and management
    - Database and collection initialization
    - Index creation for unique constraints
    - Context manager support for safe resource cleanup
    
    Example:
        >>> with MongoDBConnection() as db:
        ...     result = db.upsert_listing(normalized_data)
        ...     print(result)
    """
    
    def __init__(self, uri: Optional[str] = None, db_name: str = "real_estate_crawler"):
        """Initialize MongoDB connection.
        
        Args:
            uri: MongoDB connection URI (defaults to MONGO_URI env var)
            db_name: Database name
            
        Raises:
            ValueError: If URI is not provided and MONGO_URI env var is not set
        """
        self.uri = uri or os.getenv('MONGO_URI')
        self.db_name = db_name
        self.client: Optional[PyMongoClient] = None
        self.db = None
        self.is_connected = False
        
        if not self.uri:
            raise ValueError(
                "MongoDB URI not provided. Set MONGO_URI environment variable "
                "or pass uri parameter."
            )
        
        logger.info(f"MongoDBConnection initialized (db={db_name})")
    
    def connect(self) -> None:
        """Establish MongoDB connection and create indexes.
        
        Raises:
            ConnectionFailure: If connection cannot be established
        """
        if self.is_connected:
            logger.debug("Already connected to MongoDB")
            return
        
        try:
            self.client = PyMongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            
            logger.info(f"Connected to MongoDB: {self.db_name}")
            
            # Create indexes for unique constraints
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    def _create_indexes(self) -> None:
        """Create indexes for unique constraints."""
        if not self.db:
            return
        
        try:
            # Office collection: unique by (office_name, phone_number)
            self.db.offices.create_index(
                [("office_name", 1), ("phone_number", 1)],
                unique=False,  # Not strict unique since fields can be null
                sparse=True,    # Sparse index to handle null values
                name="office_name_phone_number_idx"
            )
            logger.debug("Created index on offices collection")
            
            # Agent collection: unique by (agent_name, phone_number)
            self.db.agents.create_index(
                [("agent_name", 1), ("phone_number", 1)],
                unique=False,
                sparse=True,
                name="agent_name_phone_number_idx"
            )
            logger.debug("Created index on agents collection")
            
            # Listing collection: unique by listing_url
            self.db.listings.create_index(
                "listing_url",
                unique=True,
                name="listing_url_idx"
            )
            logger.debug("Created index on listings collection")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    # ========================================================================
    # OFFICE OPERATIONS
    # ========================================================================
    
    def upsert_office(
        self,
        office_name: Optional[str],
        phone_number: Optional[str]
    ) -> Tuple[str, Literal["inserted", "updated"]]:
        """Upsert an office by (office_name, phone_number).
        
        Office deduplication key: office_name + phone_number
        
        If both fields are None → cannot deduplicate → will still insert/update
        based on other criteria (currently will be treated as new each time).
        
        Args:
            office_name: Office name (uppercase, trimmed) or None
            phone_number: Phone number (E.164 format) or None
        
        Returns:
            Tuple of (office_id, operation_type)
            where operation_type is 'inserted' or 'updated'
        
        Raises:
            ValueError: If both office_name and phone_number are None
        """
        # Validate: at least one field must be present for meaningful deduplication
        if not office_name and not phone_number:
            logger.warning(
                "Cannot upsert office: both office_name and phone_number are None. "
                "Treating as new office."
            )
        
        # Build query filter (upsert key)
        filter_query = {}
        if office_name:
            filter_query['office_name'] = office_name
        if phone_number:
            filter_query['phone_number'] = phone_number
        
        # If no filter, create one based on timestamp (prevent duplicates)
        if not filter_query:
            logger.warning("Office upsert with no name/phone - using timestamp-based uniqueness")
            filter_query = {'created_at': {'$exists': False}}
        
        # Build update document
        office = Office(office_name=office_name, phone_number=phone_number)
        update_doc = {
            '$set': {
                'office_name': office.office_name,
                'phone_number': office.phone_number,
                'updated_at': datetime.now(),
            },
            '$setOnInsert': {
                'created_at': datetime.now(),
            }
        }
        
        # Upsert
        result = self.db.offices.update_one(filter_query, update_doc, upsert=True)
        
        # Determine operation type
        if result.upserted_id:
            operation = 'inserted'
            office_id = str(result.upserted_id)
            logger.info(
                f"Inserted office: {office_name or 'None'} / {phone_number or 'None'} "
                f"(id={office_id})"
            )
        else:
            operation = 'updated'
            # Fetch the document to get its ID
            doc = self.db.offices.find_one(filter_query)
            office_id = str(doc['_id']) if doc else None
            logger.info(
                f"Updated office: {office_name or 'None'} / {phone_number or 'None'} "
                f"(id={office_id})"
            )
        
        return office_id, operation
    
    def get_office(
        self,
        office_name: Optional[str],
        phone_number: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve an office by (office_name, phone_number).
        
        Args:
            office_name: Office name or None
            phone_number: Phone number or None
        
        Returns:
            Office document or None if not found
        """
        filter_query = {}
        if office_name:
            filter_query['office_name'] = office_name
        if phone_number:
            filter_query['phone_number'] = phone_number
        
        if not filter_query:
            return None
        
        return self.db.offices.find_one(filter_query)
    
    # ========================================================================
    # AGENT OPERATIONS
    # ========================================================================
    
    def upsert_agent(
        self,
        agent_name: Optional[str],
        phone_number: Optional[str]
    ) -> Tuple[str, Literal["inserted", "updated"]]:
        """Upsert an agent by (agent_name, phone_number).
        
        Agent deduplication key: agent_name + phone_number
        
        Args:
            agent_name: Agent name (uppercase, trimmed) or None
            phone_number: Phone number (E.164 format) or None
        
        Returns:
            Tuple of (agent_id, operation_type)
            where operation_type is 'inserted' or 'updated'
        """
        # Validate
        if not agent_name and not phone_number:
            logger.warning(
                "Cannot upsert agent: both agent_name and phone_number are None. "
                "Treating as new agent."
            )
        
        # Build query filter (upsert key)
        filter_query = {}
        if agent_name:
            filter_query['agent_name'] = agent_name
        if phone_number:
            filter_query['phone_number'] = phone_number
        
        # If no filter, use timestamp-based uniqueness
        if not filter_query:
            logger.warning("Agent upsert with no name/phone - using timestamp-based uniqueness")
            filter_query = {'created_at': {'$exists': False}}
        
        # Build update document
        agent = Agent(agent_name=agent_name, phone_number=phone_number)
        update_doc = {
            '$set': {
                'agent_name': agent.agent_name,
                'phone_number': agent.phone_number,
                'updated_at': datetime.now(),
            },
            '$setOnInsert': {
                'created_at': datetime.now(),
            }
        }
        
        # Upsert
        result = self.db.agents.update_one(filter_query, update_doc, upsert=True)
        
        # Determine operation type
        if result.upserted_id:
            operation = 'inserted'
            agent_id = str(result.upserted_id)
            logger.info(
                f"Inserted agent: {agent_name or 'None'} / {phone_number or 'None'} "
                f"(id={agent_id})"
            )
        else:
            operation = 'updated'
            doc = self.db.agents.find_one(filter_query)
            agent_id = str(doc['_id']) if doc else None
            logger.info(
                f"Updated agent: {agent_name or 'None'} / {phone_number or 'None'} "
                f"(id={agent_id})"
            )
        
        return agent_id, operation
    
    def get_agent(
        self,
        agent_name: Optional[str],
        phone_number: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve an agent by (agent_name, phone_number).
        
        Args:
            agent_name: Agent name or None
            phone_number: Phone number or None
        
        Returns:
            Agent document or None if not found
        """
        filter_query = {}
        if agent_name:
            filter_query['agent_name'] = agent_name
        if phone_number:
            filter_query['phone_number'] = phone_number
        
        if not filter_query:
            return None
        
        return self.db.agents.find_one(filter_query)
    
    # ========================================================================
    # LISTING OPERATIONS
    # ========================================================================
    
    def upsert_listing(
        self,
        normalized_data: Dict[str, Any]
    ) -> Tuple[str, Literal["inserted", "updated"]]:
        """Upsert a listing by listing_url.
        
        Listing deduplication key: listing_url
        
        This also upserts related Office and Agent entities.
        
        Args:
            normalized_data: Normalized data from STEP 5 with fields:
                - listing_url (REQUIRED)
                - office_name (optional)
                - agent_name (optional)
                - phone_number (optional)
                - city (optional)
                - district (optional)
                - source (optional)
                - confidence (optional)
        
        Returns:
            Tuple of (listing_id, operation_type)
            where operation_type is 'inserted' or 'updated'
        
        Raises:
            ValueError: If listing_url is missing
        """
        # Validate required field
        listing_url = normalized_data.get('listing_url')
        if not listing_url:
            raise ValueError("listing_url is required")
        
        # Extract fields
        office_name = normalized_data.get('office_name')
        agent_name = normalized_data.get('agent_name')
        phone_number = normalized_data.get('phone_number')
        city = normalized_data.get('city')
        district = normalized_data.get('district')
        source = normalized_data.get('source')
        confidence = normalized_data.get('confidence')
        
        # Upsert related entities
        office_id = None
        agent_id = None
        
        if office_name and phone_number:
            office_id, _ = self.upsert_office(office_name, phone_number)
        
        if agent_name and phone_number:
            agent_id, _ = self.upsert_agent(agent_name, phone_number)
        
        # Build listing document
        listing = Listing(
            listing_url=listing_url,
            office_name=office_name,
            agent_name=agent_name,
            phone_number=phone_number,
            city=city,
            district=district,
            source=source,
            confidence=confidence,
            office_id=office_id,
            agent_id=agent_id,
        )
        
        # Upsert listing by URL
        update_doc = {
            '$set': {
                **listing.dict(exclude={'created_at'}),
                'updated_at': datetime.now(),
            },
            '$setOnInsert': {
                'created_at': datetime.now(),
            }
        }
        
        # Upsert
        result = self.db.listings.update_one(
            {'listing_url': listing_url},
            update_doc,
            upsert=True
        )
        
        # Determine operation type
        if result.upserted_id:
            operation = 'inserted'
            listing_id = str(result.upserted_id)
            logger.info(f"Inserted listing: {listing_url} (id={listing_id})")
        else:
            operation = 'updated'
            doc = self.db.listings.find_one({'listing_url': listing_url})
            listing_id = str(doc['_id']) if doc else None
            logger.info(f"Updated listing: {listing_url} (id={listing_id})")
        
        return listing_id, operation
    
    def get_listing(self, listing_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve a listing by URL.
        
        Args:
            listing_url: The listing URL
        
        Returns:
            Listing document or None if not found
        """
        return self.db.listings.find_one({'listing_url': listing_url})
    
    # ========================================================================
    # BULK OPERATIONS & STATISTICS
    # ========================================================================
    
    def count_listings(self) -> int:
        """Get total number of listings."""
        return self.db.listings.count_documents({})
    
    def count_offices(self) -> int:
        """Get total number of offices."""
        return self.db.offices.count_documents({})
    
    def count_agents(self) -> int:
        """Get total number of agents."""
        return self.db.agents.count_documents({})
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.
        
        Returns:
            Dictionary with collection counts
        """
        return {
            'listings': self.count_listings(),
            'offices': self.count_offices(),
            'agents': self.count_agents(),
        }
