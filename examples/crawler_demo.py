"""STEP 8: Pipeline Orchestration Demo

This example demonstrates the complete crawling pipeline:
Fetch → Parse → Normalize → Deduplicate → Persist

The Crawler class wires together all existing components.
"""

import asyncio
import os
from src.core.crawler import Crawler
from src.adapters.sahibinden.parser import SahibindenParser
from src.core.logger import setup_logger

logger = setup_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Basic Crawler Usage
# ═══════════════════════════════════════════════════════════════════════════════

async def example_basic_crawl():
    """Basic example: crawl a few Sahibinden listings."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 1: BASIC CRAWLER USAGE")
    print("=" * 80)
    
    # Sample URLs (replace with real ones for actual testing)
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-456",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-789",
    ]
    
    # Initialize crawler
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        db_name="real_estate_crawler",
    )
    
    # Run crawl
    try:
        stats = await crawler.run(urls)
        
        print("\n" + "-" * 80)
        print("RESULTS:")
        print("-" * 80)
        print(f"Total processed:     {stats.total}")
        print(f"Successfully fetched: {stats.fetched}")
        print(f"Successfully parsed:  {stats.parsed}")
        print(f"Normalized:          {stats.normalized}")
        print(f"Inserted (new):      {stats.inserted}")
        print(f"Updated (existing):  {stats.updated}")
        print(f"Skipped (duplicates): {stats.skipped}")
        print(f"Failed:              {stats.failed}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        print(f"\n❌ Crawl failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Custom Fetcher Configuration
# ═══════════════════════════════════════════════════════════════════════════════

async def example_custom_config():
    """Example with custom fetcher configuration (rate limits, retries)."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: CUSTOM FETCHER CONFIGURATION")
    print("=" * 80)
    
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-111",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-222",
    ]
    
    # Custom fetcher configuration
    fetcher_config = {
        'timeout': 30,                  # 30 second timeout
        'max_retries': 3,               # Max 3 retries
        'requests_per_minute': 10,      # Conservative rate limit
        'random_delay_min': 2.0,        # Min 2 seconds between requests
        'random_delay_max': 5.0,        # Max 5 seconds between requests
        'use_proxy': False,             # No proxy
    }
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        db_name="real_estate_crawler",
        fetcher_config=fetcher_config,
    )
    
    try:
        stats = await crawler.run(urls)
        print(f"\n✓ Crawl completed: {stats}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        print(f"\n❌ Crawl failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Error Handling - Graceful Degradation
# ═══════════════════════════════════════════════════════════════════════════════

async def example_error_handling():
    """Example showing how crawler handles failures gracefully."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: ERROR HANDLING - GRACEFUL DEGRADATION")
    print("=" * 80)
    
    # Mix of valid and invalid URLs
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-valid-1",
        "https://www.invalid-domain-12345.com/ilan/test",  # Invalid domain
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-valid-2",
        "not-a-url",  # Invalid format
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-valid-3",
    ]
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
    )
    
    try:
        stats = await crawler.run(urls)
        
        print("\n" + "-" * 80)
        print("FAILURE HANDLING RESULTS:")
        print("-" * 80)
        print(f"Total:    {stats.total}")
        print(f"Success:  {stats.inserted + stats.updated}")
        print(f"Failed:   {stats.failed}")
        print("\nNote: Crawler continues processing after individual failures")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Deduplication in Action
# ═══════════════════════════════════════════════════════════════════════════════

async def example_deduplication():
    """Example showing deduplication behavior."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 4: DEDUPLICATION IN ACTION")
    print("=" * 80)
    
    # Same URL repeated multiple times
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-123",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-456",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-123",  # Duplicate
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-789",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-456",  # Duplicate
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-test-123",  # Duplicate
    ]
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
    )
    
    try:
        stats = await crawler.run(urls)
        
        print("\n" + "-" * 80)
        print("DEDUPLICATION RESULTS:")
        print("-" * 80)
        print(f"Total URLs:          {stats.total}")
        print(f"Unique (in-memory):  {stats.total - stats.skipped}")
        print(f"Skipped (duplicates): {stats.skipped}")
        print(f"\nDatabase operations:")
        print(f"  Inserted (new):    {stats.inserted}")
        print(f"  Updated (existing): {stats.updated}")
        
        print("\nNote: In-memory deduplicator catches same URLs in one session")
        print("Database-level deduplication happens on upsert")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Run all examples."""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "STEP 8: PIPELINE ORCHESTRATION DEMO" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Check MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("\n⚠️  WARNING: MONGO_URI environment variable not set")
        print("   Some examples may fail without a MongoDB connection")
        print("   Set it with: export MONGO_URI='mongodb://localhost:27017'")
        print()
    
    print("\nRunning examples...")
    print("(Note: Examples use placeholder URLs - replace with real ones for testing)")
    
    # Run examples
    try:
        # Example 1: Basic usage
        await example_basic_crawl()
        
        # Example 2: Custom configuration
        # await example_custom_config()
        
        # Example 3: Error handling
        # await example_error_handling()
        
        # Example 4: Deduplication
        # await example_deduplication()
        
        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Examples failed: {e}", exc_info=True)
        print(f"\n❌ Examples failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE NOTES
# ═══════════════════════════════════════════════════════════════════════════════

"""
CONTROL FLOW:

1. Crawler.run(urls)
   ├─ Initialize components (Fetcher, Parser, Normalizer, Deduplicator, MongoDB)
   ├─ Connect to MongoDB
   └─ For each URL:
       ├─ Fetch HTML (Fetcher)
       │   └─ Respects rate limits, retries on failure
       ├─ Parse HTML → structured data (Parser)
       │   └─ Extracts: office_name, agent_name, phone, city, district, url
       ├─ Normalize data → clean format (Normalizer)
       │   └─ Uppercase names, E.164 phone, title case locations
       ├─ Check duplicates (Deduplicator - in-memory)
       │   └─ Skip if seen in this session
       └─ Persist to MongoDB (MongoDBConnection)
           └─ Upsert: insert if new, update if exists

2. Error Handling:
   - Individual listing failure → log and continue
   - Network errors → retry with backoff
   - Blocking (403/429) → detect and stop if repeated
   - Parse errors → log and continue

3. Logging:
   - Each step logs its progress
   - Summary at the end
   - Failed URLs are logged with reasons

4. Statistics:
   - Total processed
   - Fetched, parsed, normalized
   - Inserted (new), updated (existing), skipped (duplicates)
   - Failed

RUNNING THIS DEMO:

    # Set MongoDB connection
    export MONGO_URI='mongodb://localhost:27017'
    
    # Run the demo
    python -m examples.crawler_demo
    
    # Or run individual examples:
    python -c "
    import asyncio
    from examples.crawler_demo import example_basic_crawl
    asyncio.run(example_basic_crawl())
    "

INTEGRATION WITH CLI:

The CLI can use Crawler like this:

    from src.core.crawler import Crawler
    from src.adapters.sahibinden.parser import SahibindenParser
    
    # Get URLs from discovery (STEP 9 - future work)
    urls = discover_listing_urls(city='istanbul', district='kadikoy')
    
    # Crawl
    crawler = Crawler(parser=SahibindenParser())
    stats = await crawler.run(urls)
    
    print(f"Inserted: {stats.inserted}, Updated: {stats.updated}")
"""

if __name__ == "__main__":
    asyncio.run(main())
