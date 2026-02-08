# STEP 8: Pipeline Orchestration

## Overview

STEP 8 implements the **Crawler** class, which orchestrates the complete crawling pipeline by wiring together all previously implemented components.

### Pipeline Flow

```
URLs → Fetch → Parse → Normalize → Deduplicate → Persist → Statistics
       ↓        ↓        ↓           ↓             ↓
     Fetcher  Parser  Normalizer  Deduplicator  MongoDB
```

## Architecture

### Components Wired Together

1. **Fetcher** (STEP 2)
   - Downloads HTML from URLs
   - Handles rate limiting and retries
   - Respects politeness policies

2. **Parser** (STEP 4)
   - Extracts structured data from HTML
   - Site-specific adapters (Sahibinden, Hepsiemlak)

3. **Normalizer** (STEP 5)
   - Cleans and standardizes data
   - Phone number formatting (E.164)
   - Name normalization (uppercase)

4. **Deduplicator** (STEP 6)
   - In-memory duplicate detection
   - Prevents redundant processing

5. **MongoDB** (STEP 7)
   - Persists data with upsert semantics
   - Handles database-level deduplication

### Control Flow

```python
for url in urls:
    try:
        # 1. FETCH
        html = await fetcher.fetch(url)
        
        # 2. PARSE
        parsed_data = parser.parse_listing_page(html, url)
        
        # 3. NORMALIZE
        normalized_data = normalizer.normalize(parsed_data)
        
        # 4. DEDUPLICATE (in-memory)
        dedup_result = deduplicator.check_listing(normalized_data)
        if dedup_result.is_new:
            deduplicator.add_listing(url)
        
        # 5. PERSIST (database-level deduplication via upsert)
        listing_id, operation = db.upsert_listing(normalized_data)
        
        # Track statistics
        if operation == 'inserted':
            stats.inserted += 1
        elif operation == 'updated':
            stats.updated += 1
            
    except Exception as e:
        logger.error(f"Failed: {url}: {e}")
        stats.failed += 1
        continue  # Continue with next URL
```

## Usage

### Basic Example

```python
import asyncio
from src.core.crawler import Crawler
from src.adapters.sahibinden.parser import SahibindenParser

async def main():
    # Initialize crawler
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        db_name="real_estate_crawler"
    )
    
    # List of URLs to crawl
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-456",
    ]
    
    # Run crawl
    stats = await crawler.run(urls)
    
    # Print results
    print(f"Total:    {stats.total}")
    print(f"Inserted: {stats.inserted}")
    print(f"Updated:  {stats.updated}")
    print(f"Failed:   {stats.failed}")

asyncio.run(main())
```

### Custom Fetcher Configuration

```python
crawler = Crawler(
    parser=SahibindenParser(),
    mongo_uri="mongodb://localhost:27017",
    fetcher_config={
        'timeout': 30,
        'max_retries': 3,
        'requests_per_minute': 10,
        'random_delay_min': 2.0,
        'random_delay_max': 5.0,
    }
)
```

## Features

### 1. One Listing at a Time

- No batching (yet)
- Sequential processing
- Easier debugging and logging

### 2. Graceful Error Handling

- Individual failures don't stop the entire crawl
- Each error is logged with context
- Statistics track failed URLs

### 3. Rate Limiting

- Respects Fetcher's rate limits
- Random delays between requests
- Polite crawling

### 4. Deduplication Strategy

**Two-level deduplication:**

1. **In-memory (Deduplicator)**
   - Catches duplicates within same crawl session
   - Prevents redundant fetching in one run
   - Fast (O(1) lookups)

2. **Database-level (MongoDB)**
   - Upsert semantics: insert if new, update if exists
   - Handles duplicates across crawl sessions
   - Persistent deduplication

### 5. Clear Logging

Each step logs:
- Progress (URL x/n)
- Success/failure status
- Data summary
- Final statistics

Example log output:

```
2026-02-02 10:15:00 INFO [crawler] Starting crawl: 3 URLs to process
2026-02-02 10:15:00 INFO [crawler] [1/3] Processing: https://www.sahibinden.com/...
2026-02-02 10:15:01 INFO [fetcher] Fetching (attempt 1): https://www.sahibinden.com/...
2026-02-02 10:15:02 INFO [fetcher] Successfully fetched 45230 bytes from https://...
2026-02-02 10:15:02 INFO [parser] Parsing Sahibinden listing: https://...
2026-02-02 10:15:02 INFO [normalizer] Normalized: sahibinden listing with confidence=high
2026-02-02 10:15:02 INFO [mongo] Inserted listing: https://... (id=507f1f77bcf86cd799439011)
2026-02-02 10:15:02 INFO [crawler] ✓ Inserted listing: https://... (id=507f1f77bcf86cd799439011)
...
2026-02-02 10:15:10 INFO [crawler] ================================================================================
2026-02-02 10:15:10 INFO [crawler] CRAWL SUMMARY
2026-02-02 10:15:10 INFO [crawler] ================================================================================
2026-02-02 10:15:10 INFO [crawler] Total URLs:              3
2026-02-02 10:15:10 INFO [crawler] Successfully fetched:    3
2026-02-02 10:15:10 INFO [crawler] Successfully parsed:     3
2026-02-02 10:15:10 INFO [crawler] Successfully normalized: 3
2026-02-02 10:15:10 INFO [crawler] Inserted (new):          2
2026-02-02 10:15:10 INFO [crawler] Updated (existing):      1
2026-02-02 10:15:10 INFO [crawler] Skipped (duplicates):    0
2026-02-02 10:15:10 INFO [crawler] Failed:                  0
2026-02-02 10:15:10 INFO [crawler] ================================================================================
2026-02-02 10:15:10 INFO [crawler] Success rate: 100.0%
```

### 6. Statistics Tracking

The `CrawlStats` dataclass tracks:

- `total`: Total URLs to process
- `fetched`: Successfully fetched
- `parsed`: Successfully parsed
- `normalized`: Successfully normalized
- `inserted`: New listings inserted to database
- `updated`: Existing listings updated
- `skipped`: Duplicates skipped (in-memory)
- `failed`: Failed to process

## Error Scenarios

### Fetch Errors

```python
# Network timeout
FetchError: Timeout after 3 retries: https://...

# HTTP error
FetchError: HTTP 404 for https://...

# Repeated blocking
BlockedError: Repeated blocking detected for sahibinden.com: 5 blocks in 60s
```

**Handling:** Log error, increment `failed`, continue with next URL

### Parse Errors

```python
# Parser returned None
ValueError: Parser returned None

# HTML structure changed
Exception: Element not found: .breadcrumb
```

**Handling:** Log error, increment `failed`, continue with next URL

### Database Errors

```python
# Connection failed
ConnectionFailure: Failed to connect to MongoDB

# Validation error
ValueError: listing_url is required
```

**Handling:** Log error, increment `failed`, continue with next URL (or raise if critical)

## Design Decisions

### Why One at a Time?

- **Simplicity**: Easier to debug and understand
- **Rate limiting**: Natural throttling
- **Logging**: Clear sequential logs
- **Future work**: Batching can be added in STEP 9+

### Why Two-level Deduplication?

1. **In-memory (Deduplicator)**
   - Fast: Avoids redundant fetches in same session
   - Stateful: Knows what was processed this run
   
2. **Database (MongoDB)**
   - Persistent: Handles duplicates across sessions
   - Authoritative: Final source of truth

### Why Continue on Failure?

- **Resilience**: Don't let one bad URL stop entire crawl
- **Visibility**: All errors logged for debugging
- **Statistics**: Track success rate

## Testing

Run the demo:

```bash
# Set MongoDB connection
export MONGO_URI='mongodb://localhost:27017'

# Run demo
python examples/crawler_demo.py
```

### Example Output

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEP 8: PIPELINE ORCHESTRATION DEMO                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
EXAMPLE 1: BASIC CRAWLER USAGE
================================================================================

[Crawler processes URLs...]

--------------------------------------------------------------------------------
RESULTS:
--------------------------------------------------------------------------------
Total processed:      3
Successfully fetched: 3
Successfully parsed:  3
Normalized:          3
Inserted (new):      2
Updated (existing):  1
Skipped (duplicates): 0
Failed:              0
```

## Integration Points

### CLI Integration (Future)

```python
# In CLI command handler
from src.core.crawler import Crawler
from src.adapters.sahibinden.parser import SahibindenParser

async def crawl_command(city: str, district: str):
    # 1. Discover URLs (STEP 9 - not yet implemented)
    urls = discover_listing_urls(city, district)
    
    # 2. Crawl
    crawler = Crawler(parser=SahibindenParser())
    stats = await crawler.run(urls)
    
    # 3. Report
    print(f"Crawled {stats.total} listings")
    print(f"New: {stats.inserted}, Updated: {stats.updated}")
```

### Scheduler Integration (Future)

```python
# In scheduler
from src.core.crawler import Crawler

async def scheduled_crawl():
    crawler = Crawler(parser=SahibindenParser())
    
    # Get URLs from queue or configuration
    urls = get_urls_to_crawl()
    
    # Run
    stats = await crawler.run(urls)
    
    # Store stats for monitoring
    save_crawl_metrics(stats)
```

## Limitations (Current)

1. **No URL discovery**
   - URLs must be passed in
   - STEP 9 will add discovery

2. **No batching**
   - One URL at a time
   - Can be optimized later

3. **No resumability**
   - Can't resume failed crawls
   - Future: checkpoint/queue system

4. **No priority queue**
   - URLs processed in order
   - Future: prioritize by importance

## Next Steps (STEP 9+)

1. **URL Discovery**
   - Scrape listing pages
   - Extract listing URLs
   - Build URL queue

2. **Batching & Parallelism**
   - Fetch multiple URLs concurrently
   - Respect rate limits globally

3. **Scheduling**
   - Periodic crawls
   - Incremental updates

4. **Monitoring**
   - Metrics dashboard
   - Alerting on failures

## Files

- `src/core/crawler.py` - Main Crawler class
- `examples/crawler_demo.py` - Demo and usage examples
- `STEP8_README.md` - This file

## Summary

STEP 8 successfully implements pipeline orchestration by:

✅ Wiring together Fetcher, Parser, Normalizer, Deduplicator, MongoDB  
✅ Processing one listing at a time  
✅ Graceful error handling (continue on failure)  
✅ Rate limiting (via Fetcher)  
✅ Two-level deduplication (in-memory + database)  
✅ Clear logging at each step  
✅ Statistics tracking (inserted, updated, skipped, failed)  
✅ Example usage and documentation  

The crawler is now ready to process listing URLs and persist data to MongoDB.
