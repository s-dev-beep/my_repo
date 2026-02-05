"""MongoDB connection and operations.

STEP 7: Database Persistence Layer

This module has been refactored into smaller modules for better maintainability:
- mongo_connection.py: Connection management and index creation
- mongo_repositories.py: CRUD operations for Office, Agent, and Listing

This file now serves as a facade to maintain backward compatibility.
All imports from this module will continue to work unchanged.
"""

# Import connection class first
from src.db.mongo_connection import MongoDBConnection

# Import repositories to inject methods into MongoDBConnection
# The repositories module automatically injects its methods via _inject_repository_methods()
import src.db.mongo_repositories

# Re-export the main class
__all__ = ["MongoDBConnection"]
