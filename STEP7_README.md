"""STEP 7: DATABASE PERSISTENCE (MongoDB)

Implementation Complete

═══════════════════════════════════════════════════════════════════════════════
OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

This document describes STEP 7: Database Persistence, the final layer that
safely and idempotently persists deduplicated entities to MongoDB.

STEP 7 accepts:
- Normalized data (STEP 5): office_name, agent_name, phone_number, etc.
- Deduplication results (STEP 6): is_new, dedupe_key, reason

STEP 7 delivers:
- Safe upsert operations (never blind inserts)
- MongoDB ObjectIds (document IDs)
- Operation indicators (inserted vs updated)
- Flexible schemas (missing fields allowed)


═══════════════════════════════════════════════════════════════════════════════
SCHEMA DESIGN DECISIONS
═══════════════════════════════════════════════════════════════════════════════

1. OFFICE COLLECTION
   ────────────────────────────────────────────────────────────────────────

   Unique Key: office_name + phone_number
   
   Document structure:
   {
       _id: ObjectId,
       office_name: String | null,
       phone_number: String | null,  // E.164 format
       created_at: DateTime,
       updated_at: DateTime
   }
   
   Index: compound sparse index on (office_name, phone_number)
   Rationale:
   - Sparse index handles null values properly
   - Compound index allows efficient deduplication queries
   - Not strict unique because both fields can be null (different entities)
   - Minimal schema focused on dedup key only
   - Timestamps for audit trail


2. AGENT COLLECTION
   ────────────────────────────────────────────────────────────────────────

   Unique Key: agent_name + phone_number
   
   Document structure:
   {
       _id: ObjectId,
       agent_name: String | null,
       phone_number: String | null,  // E.164 format
       created_at: DateTime,
       updated_at: DateTime
   }
   
   Index: compound sparse index on (agent_name, phone_number)
   Rationale:
   - Same design as Office for consistency
   - Supports both company agents and independent agents
   - Sparse index for robust null handling


3. LISTING COLLECTION
   ────────────────────────────────────────────────────────────────────────

   Unique Key: listing_url
   
   Document structure:
   {
       _id: ObjectId,
       listing_url: String,  // UNIQUE, REQUIRED
       office_name: String | null,
       agent_name: String | null,
       phone_number: String | null,
       city: String | null,        // Title case
       district: String | null,    // Title case
       source: String | null,      // sahibinden, hepsiemlak, etc
       confidence: String | null,  // high, medium, low
       office_id: ObjectId | null, // Reference to Office
       agent_id: ObjectId | null,  // Reference to Agent
       created_at: DateTime,
       updated_at: DateTime
   }
   
   Index: unique index on listing_url
   Rationale:
   - Listing URL is the primary identifier (most deterministic)
   - Stores normalized data from STEP 5 for audit trail
   - References to Office and Agent for efficient queries
   - Flexible schema allows missing contact info or location
   - All contact/location data duplicated for search/analysis


═══════════════════════════════════════════════════════════════════════════════
UPSERT SEMANTICS & IDEMPOTENCY
═══════════════════════════════════════════════════════════════════════════════

KEY PRINCIPLE: Never blind inserts. Always upsert with deterministic filters.

OFFICE UPSERT:
──────────────
Filter: { office_name: "...", phone_number: "..." }
Action: 
  - If exists: update with current data, set updated_at
  - If not exists: insert new document with created_at

Behavior with missing keys:
  - If both office_name AND phone_number are null:
    Cannot deduplicate properly, but operation proceeds
    (will create separate doc each time - caller should prevent this)
  - If only one field null:
    Matches on available field only
    Example: { phone_number: "+905321234567" } matches all offices with this phone

AGENT UPSERT:
─────────────
Identical to Office - filter on (agent_name, phone_number)

LISTING UPSERT:
───────────────
Filter: { listing_url: "..." }
Action:
  - If exists: update all fields, set updated_at
  - If not exists: insert new document with created_at
  - Also upserts referenced Office and Agent (if both name AND phone exist)

Side effects:
  - Calling upsert_listing() automatically calls:
    - upsert_office() if office_name AND phone_number exist
    - upsert_agent() if agent_name AND phone_number exist
  - Populates office_id and agent_id in listing document


IDEMPOTENCY GUARANTEES:
──────────────────────
Calling upsert_listing(data) twice with identical data:
  1. First call: inserts listing, office, agent → returns (id, 'inserted')
  2. Second call: updates same docs → returns (id, 'updated')
  3. Same ID returned both times → idempotent!


═══════════════════════════════════════════════════════════════════════════════
DATA FLOW: From STEP 6 to STEP 7
═══════════════════════════════════════════════════════════════════════════════

Input: DeduplicationResult from STEP 6
{
    is_new: True,
    dedupe_key: "https://www.sahibinden.com/ilan/...",
    reason: "New listing URL: ..."
}

Processing Flow:
────────────────
1. Normalize data (STEP 5) → dictionary with all fields
2. Check deduplication (STEP 6) → is_new indicator
3. If is_new OR already stored, proceed to persistence
4. Call db.upsert_listing(normalized_data)
5. Database returns (listing_id, operation_type)

Example Flow:
─────────────
# STEP 5: Normalize
normalized = normalizer.normalize(raw_parser_data)
# Result: {
#   'listing_url': 'https://...',
#   'office_name': 'EV GAYRIMENKUL',
#   'agent_name': 'AHMET YILMAZ',
#   'phone_number': '+905321234567',
#   'city': 'İstanbul',
#   'district': 'Kadıköy',
#   'source': 'sahibinden',
#   'confidence': 'high'
# }

# STEP 6: Deduplicate (in-memory)
dedup_result = deduplicator.check_listing(normalized)
# Result: DeduplicationResult(is_new=True, dedupe_key='https://...', reason='...')

# STEP 7: Persist
with MongoDBConnection() as db:
    listing_id, operation = db.upsert_listing(normalized)
    
    # Logs:
    # INFO: Inserted office: EV GAYRIMENKUL / +905321234567 (id=507f1f77bcf86cd799439011)
    # INFO: Inserted agent: AHMET YILMAZ / +905321234567 (id=507f1f77bcf86cd799439012)
    # INFO: Inserted listing: https://... (id=507f1f77bcf86cd799439013)
    
    # Result: ('507f1f77bcf86cd799439013', 'inserted')


═══════════════════════════════════════════════════════════════════════════════
FLEXIBLE SCHEMA & MISSING FIELDS
═══════════════════════════════════════════════════════════════════════════════

The database is designed to accept ANY subset of fields.

Example 1: Complete listing
──────────────────────────
{
    'listing_url': 'https://...',
    'office_name': 'COMPANY',
    'agent_name': 'JOHN',
    'phone_number': '+905321234567',
    'city': 'Istanbul',
    'district': 'Kadikoy',
    'source': 'sahibinden',
    'confidence': 'high'
}
→ Upserts office and agent, stores all fields

Example 2: Incomplete listing (missing agent)
──────────────────────────────────────────────
{
    'listing_url': 'https://...',
    'office_name': 'COMPANY',
    'agent_name': None,  # No agent
    'phone_number': None,  # No phone to deduplicate agent
    'city': 'Istanbul',
    'district': None,
    'source': 'sahibinden',
    'confidence': 'medium'
}
→ Does NOT upsert agent (missing phone)
→ Does NOT upsert office (missing phone)
→ Stores listing with null office_id and agent_id

Example 3: Private seller (minimal info)
──────────────────────────────────────────
{
    'listing_url': 'https://...',
    'office_name': None,  # Private seller, no office
    'agent_name': 'MEHMET',
    'phone_number': '+905558889900',
    'city': 'Ankara',
    'district': 'Cankaya',
    'source': 'sahibinden',
    'confidence': 'medium'
}
→ Does NOT upsert office (no office_name)
→ Upserts agent with (agent_name, phone_number)
→ Stores listing with null office_id and valid agent_id


═══════════════════════════════════════════════════════════════════════════════
API REFERENCE
═══════════════════════════════════════════════════════════════════════════════

CLASS: MongoDBConnection

1. Constructor & Connection
   ─────────────────────────

   MongoDBConnection(uri=None, db_name="real_estate_crawler")
   
   - uri: MongoDB connection URI (defaults to MONGO_URI env var)
   - db_name: Database name to use
   - Raises ValueError if uri not provided and env var not set
   
   with MongoDBConnection() as db:
       # Connection auto-opened on entry
       result = db.upsert_listing(data)
       # Connection auto-closed on exit


2. OFFICE OPERATIONS
   ──────────────────

   upsert_office(office_name: str | None, phone_number: str | None)
   → (office_id: str, operation: 'inserted' | 'updated')
   
   Example:
     office_id, op = db.upsert_office("EV GAYRIMENKUL", "+905321234567")
     print(op)  # 'inserted' or 'updated'
   
   get_office(office_name: str | None, phone_number: str | None)
   → dict | None
   
   Example:
     office = db.get_office("EV GAYRIMENKUL", "+905321234567")
     print(office['_id'])  # ObjectId as string


3. AGENT OPERATIONS
   ─────────────────

   upsert_agent(agent_name: str | None, phone_number: str | None)
   → (agent_id: str, operation: 'inserted' | 'updated')
   
   Example:
     agent_id, op = db.upsert_agent("AHMET YILMAZ", "+905321234567")
   
   get_agent(agent_name: str | None, phone_number: str | None)
   → dict | None


4. LISTING OPERATIONS
   ───────────────────

   upsert_listing(normalized_data: dict)
   → (listing_id: str, operation: 'inserted' | 'updated')
   
   Required fields in normalized_data:
   - listing_url: str (REQUIRED)
   
   Optional fields (copied as-is):
   - office_name, agent_name, phone_number
   - city, district, source, confidence
   
   Behavior:
   - Automatically upserts Office if office_name AND phone_number exist
   - Automatically upserts Agent if agent_name AND phone_number exist
   - Sets office_id and agent_id in listing document
   
   Example:
     listing_id, op = db.upsert_listing({
         'listing_url': 'https://...',
         'office_name': 'EV GAYRIMENKUL',
         'agent_name': 'AHMET YILMAZ',
         'phone_number': '+905321234567',
         'city': 'İstanbul',
         'district': 'Kadıköy',
         'source': 'sahibinden',
         'confidence': 'high'
     })
   
   get_listing(listing_url: str) → dict | None


5. STATISTICS
   ───────────

   count_listings() → int
   count_offices() → int
   count_agents() → int
   
   get_stats() → dict
   
   Example:
     stats = db.get_stats()
     print(stats)  # {'listings': 1000, 'offices': 150, 'agents': 200}


═══════════════════════════════════════════════════════════════════════════════
USAGE PATTERNS & EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

PATTERN 1: Persist single listing after deduplication
──────────────────────────────────────────────────────

from src.core.normalizer import Normalizer
from src.core.deduplicator import Deduplicator
from src.db.mongo import MongoDBConnection

normalizer = Normalizer()
deduplicator = Deduplicator()

raw_data = {...}  # From parser

# STEP 5: Normalize
normalized = normalizer.normalize(raw_data)

# STEP 6: Deduplicate
dedup_result = deduplicator.check_listing(normalized)

# STEP 7: Persist (regardless of dedup result - store everything)
if dedup_result.dedupe_key:
    deduplicator.add_listing(dedup_result.dedupe_key)

with MongoDBConnection() as db:
    listing_id, op = db.upsert_listing(normalized)
    print(f"Listing {op}: {listing_id}")


PATTERN 2: Batch persistence with statistics
──────────────────────────────────────────────

with MongoDBConnection() as db:
    inserted_count = 0
    updated_count = 0
    
    for normalized_data in batch_of_listings:
        try:
            listing_id, op = db.upsert_listing(normalized_data)
            if op == 'inserted':
                inserted_count += 1
            else:
                updated_count += 1
        except Exception as e:
            logger.error(f"Failed to persist: {e}")
    
    stats = db.get_stats()
    print(f"Batch completed:")
    print(f"  Inserted: {inserted_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Total in DB: {stats['listings']}")


PATTERN 3: Idempotent re-processing
────────────────────────────────────

# Safe to run multiple times
def process_listing(raw_data):
    normalized = normalizer.normalize(raw_data)
    
    with MongoDBConnection() as db:
        listing_id, op = db.upsert_listing(normalized)
    
    return listing_id

# Can call multiple times with same data, always idempotent
id1 = process_listing(raw_data)
id2 = process_listing(raw_data)
assert id1 == id2  # Always true!


PATTERN 4: Office/Agent lookups after persistence
───────────────────────────────────────────────────

with MongoDBConnection() as db:
    # Upsert listing (creates office/agent)
    listing_id, _ = db.upsert_listing(normalized)
    
    # Later, look up the office
    office = db.get_office(
        normalized['office_name'],
        normalized['phone_number']
    )
    
    print(f"Office ID: {office['_id']}")
    print(f"Created at: {office['created_at']}")
    print(f"All listings from this office can be found by filtering agent_id")


═══════════════════════════════════════════════════════════════════════════════
ENVIRONMENT CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

Required environment variable:
  MONGO_URI: MongoDB connection string

Examples:

1. Local MongoDB
   export MONGO_URI="mongodb://localhost:27017"

2. MongoDB Atlas (cloud)
   export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"

3. Docker MongoDB
   export MONGO_URI="mongodb://mongo:27017"

4. With authentication
   export MONGO_URI="mongodb://user:pass@host:27017/db_name?authSource=admin"

If not set, MongoDBConnection raises ValueError on initialization.


═══════════════════════════════════════════════════════════════════════════════
DATABASE DESIGN PHILOSOPHY
═══════════════════════════════════════════════════════════════════════════════

1. MINIMAL SCHEMAS
   ────────────────
   Each collection has only necessary fields:
   - Offices: name, phone, timestamps
   - Agents: name, phone, timestamps
   - Listings: URL, contact info, location, refs to office/agent, timestamps
   
   No unnecessary enrichment, no stored computation


2. FLEXIBILITY
   ────────────
   All fields except listing_url are optional:
   - Missing data is acceptable (stored as null)
   - No validation enforced (trust STEP 5)
   - Easy to add fields later without migration


3. IDEMPOTENCY
   ────────────
   Every operation is deterministic:
   - Same input → same database state
   - No random IDs in filter keys
   - Upserts use business keys (name+phone, URL)
   - Can safely replay operations


4. AUDITABILITY
   ──────────────
   All documents have timestamps:
   - created_at: when first inserted
   - updated_at: when last updated
   - Tracks data lifecycle


5. RELATIONSHIPS
   ───────────────
   Listings reference Offices and Agents by ObjectId:
   - Enables efficient queries (find all listings for an office)
   - Supports data analysis and reporting
   - Loose coupling (office can be updated independently)


═══════════════════════════════════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════════

All upsert operations handle errors gracefully:

1. Connection errors → ConnectionFailure exception
2. Missing listing_url → ValueError exception
3. MongoDB duplicate key → handled by upsert (updates existing)
4. Index creation errors → logged as warning, continues

Example:

try:
    with MongoDBConnection() as db:
        listing_id, op = db.upsert_listing(normalized)
except ConnectionFailure as e:
    logger.error(f"Database connection failed: {e}")
except ValueError as e:
    logger.error(f"Invalid data: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")


═══════════════════════════════════════════════════════════════════════════════
TESTING THE IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════════════

Run the example:

1. Ensure MongoDB is running:
   mongod --dbpath /path/to/db

2. Set environment variable:
   export MONGO_URI="mongodb://localhost:27017"

3. Run the demo:
   python examples/mongo_db_demo.py

Expected output:
- Demo 1: Basic upsert operations
- Demo 2: Agent deduplication
- Demo 3: Handling incomplete data
- Demo 4: Statistics
- Demo 5: Idempotency testing


═══════════════════════════════════════════════════════════════════════════════
FUTURE ENHANCEMENTS
═══════════════════════════════════════════════════════════════════════════════

Potential improvements (not in STEP 7 scope):

1. Async/await support (currently sync)
2. Bulk operations for batch inserts
3. Transactions for multi-document consistency
4. Full-text search indexes on names
5. TTL indexes for data expiration
6. Aggregation pipelines for reporting
7. Backup and export functionality
8. Query builder for complex searches


═══════════════════════════════════════════════════════════════════════════════
SUMMARY
═══════════════════════════════════════════════════════════════════════════════

STEP 7 Implementation provides:

✅ Safe MongoDB persistence with upsert semantics
✅ Three collections: offices, agents, listings
✅ Deterministic deduplication keys
✅ Idempotent operations (safe to replay)
✅ Flexible schemas (missing fields allowed)
✅ Relationship tracking (office_id, agent_id)
✅ Audit trail (created_at, updated_at)
✅ No hardcoded credentials
✅ Comprehensive logging
✅ Example usage and demos

All input comes from STEP 5 (normalized data) and is persisted exactly as
received, with automatic relationship tracking for offices and agents.

No crawling. No parsing. No normalization. No deduplication logic.
Pure persistence layer.
"""
