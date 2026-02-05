"""STEP 7: Integration with Complete Pipeline

Complete example showing all steps working together.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE PIPELINE EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════════

from src.core.normalizer import Normalizer
from src.core.deduplicator import Deduplicator
from src.db.mongo import MongoDBConnection

# Sample raw data from parser
raw_data = {
    'office_name': '  Ev Gayrimenkul  ',
    'agent_name': 'ahmet yılmaz',
    'phone_number': '0532 123 4567',
    'city': 'İSTANBUL',
    'district': 'kadıköy',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456'
}

print("=" * 80)
print("COMPLETE PIPELINE: CRAWL → PARSE → NORMALIZE → DEDUPLICATE → PERSIST")
print("=" * 80)

# STEP 1-4: Crawl & Parse (already done)
print("\nSTEP 1-4: CRAWL & PARSE")
print("-" * 80)
print(f"Raw parsed data: {raw_data}")

# STEP 5: NORMALIZE
print("\n\nSTEP 5: NORMALIZE")
print("-" * 80)

normalizer = Normalizer()
normalized = normalizer.normalize(raw_data)

print(f"Normalized data:")
for key, value in normalized.items():
    print(f"  {key:15} = {value!r}")

# STEP 6: DEDUPLICATE
print("\n\nSTEP 6: DEDUPLICATE")
print("-" * 80)

deduplicator = Deduplicator()

# Check if listing is new
listing_dedup = deduplicator.check_listing(normalized)
print(f"Listing deduplication:")
print(f"  is_new: {listing_dedup.is_new}")
print(f"  dedupe_key: {listing_dedup.dedupe_key}")
print(f"  reason: {listing_dedup.reason}")

# Check if office is new
office_dedup = deduplicator.check_office(normalized)
print(f"\nOffice deduplication:")
print(f"  is_new: {office_dedup.is_new}")
print(f"  dedupe_key: {office_dedup.dedupe_key}")
print(f"  reason: {office_dedup.reason}")

# Check if agent is new
agent_dedup = deduplicator.check_agent(normalized)
print(f"\nAgent deduplication:")
print(f"  is_new: {agent_dedup.is_new}")
print(f"  dedupe_key: {agent_dedup.dedupe_key}")
print(f"  reason: {agent_dedup.reason}")

# Register in deduplicator
if listing_dedup.is_new and listing_dedup.dedupe_key:
    deduplicator.add_listing(listing_dedup.dedupe_key)
    print(f"\n✓ Registered listing in deduplicator")

if office_dedup.is_new and office_dedup.dedupe_key:
    deduplicator.add_office(
        office_dedup.dedupe_key[0],
        office_dedup.dedupe_key[1]
    )
    print(f"✓ Registered office in deduplicator")

if agent_dedup.is_new and agent_dedup.dedupe_key:
    deduplicator.add_agent(
        agent_dedup.dedupe_key[0],
        agent_dedup.dedupe_key[1]
    )
    print(f"✓ Registered agent in deduplicator")

# STEP 7: PERSIST
print("\n\nSTEP 7: PERSIST")
print("-" * 80)
print("(Would connect to MongoDB here)")
print("\nExample code:")
print("""
try:
    with MongoDBConnection() as db:
        listing_id, operation = db.upsert_listing(normalized)
        print(f"Listing {operation}: {listing_id}")
        
        stats = db.get_stats()
        print(f"Total listings in DB: {stats['listings']}")
        print(f"Total offices in DB: {stats['offices']}")
        print(f"Total agents in DB: {stats['agents']}")
except ConnectionError as e:
    print(f"Could not connect to MongoDB: {e}")
""")

# STEP 7: Hypothetical result (without actual MongoDB)
print("\nExpected result:")
print("  Listing inserted: 507f1f77bcf86cd799439030")
print("  Office inserted: 507f1f77bcf86cd799439011")
print("  Agent inserted: 507f1f77bcf86cd799439020")

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print("=" * 80)
print("\nData flow summary:")
print("  Raw Data → Normalized → Deduplicated → Persisted")
print("  All transformations are:")
print("    - Deterministic (no randomness)")
print("    - Idempotent (safe to replay)")
print("    - Logged (visible for debugging)")
print("    - Non-destructive (data preserved)")


# ═══════════════════════════════════════════════════════════════════════════════
# KEY PRINCIPLES
# ═══════════════════════════════════════════════════════════════════════════════

"""
PIPELINE DESIGN PRINCIPLES:

1. SEPARATION OF CONCERNS
   - Each step has one responsibility
   - No step knows about others
   - Easy to test and maintain

2. DATA FLOW
   Parser Output → Normalizer → Deduplicator → Database
   
   Parser: Raw, messy data (from web)
   Normalizer: Clean, consistent format
   Deduplicator: Identifies duplicates (memory-only)
   Database: Persists (upsert semantics)

3. IDEMPOTENCY AT EACH STEP
   - Can run normalization multiple times
   - Can re-register in deduplicator
   - Can re-persist to database
   - Final state always the same

4. NO DATA LOSS
   - Every step preserves data
   - Failed steps don't corrupt data
   - Can rollback to previous state
   - Historical data always available

5. LOGGING & OBSERVABILITY
   - Every operation is logged
   - Can trace data through pipeline
   - Errors are explicit
   - Statistics available at each step

6. FLEXIBILITY
   - Schemas allow missing data
   - Can add fields without breaking
   - Can skip steps if needed
   - Easy to extend


TESTING THE COMPLETE PIPELINE:

1. Unit tests (each step independently)
   - Test normalizer with various inputs
   - Test deduplicator with duplicates
   - Test database with various schemas

2. Integration tests (steps together)
   - Test pipeline with sample data
   - Verify data consistency
   - Check idempotency

3. End-to-end tests (full pipeline)
   - Crawl → Parse → Normalize → Deduplicate → Persist
   - Verify final database state
   - Check statistics


MONITORING & ALERTS:

What to monitor:
- Items per step (throughput)
- Deduplication rate (quality)
- Error rate (reliability)
- Database size (storage)
- Operation latency (performance)

Example metrics dashboard:
- 10,000 items crawled
- 9,500 items parsed successfully
- 9,400 items normalized
- 8,000 items unique (new)
- 1,400 items duplicates
- 9,400 items persisted
- Error rate: 0.1%
- Avg persistence time: 45ms
"""
