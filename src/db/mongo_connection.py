"""MongoDB connection management.

STEP 7: Database Persistence Layer

Extracted from mongo.py for better modularity.
This module handles connection pooling, initialization, and index creation.
"""

import os
from typing import Optional

from pymongo import MongoClient as PyMongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from src.core.logger import setup_logger

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
        if self.db is None:
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
    
    # Statistics methods (kept here for connection-level operations)
    def count_listings(self) -> int:
        """Get total number of listings."""
        return self.db.listings.count_documents({})
    
    def count_offices(self) -> int:
        """Get total number of offices."""
        return self.db.offices.count_documents({})
    
    def count_agents(self) -> int:
        """Get total number of agents."""
        return self.db.agents.count_documents({})
