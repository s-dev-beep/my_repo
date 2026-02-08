# STEP 8 Quick Reference

## Basic Usage

```python
from src.core.crawler import Crawler
from src.adapters.sahibinden.parser import SahibindenParser

# Initialize
crawler = Crawler(
    parser=SahibindenParser(),
    mongo_uri="mongodb://localhost:27017"
)

# Crawl
urls = ["https://www.sahibinden.com/ilan/..."]
stats = await crawler.run(urls)

# Results
print(f"Inserted: {stats.inserted}, Failed: {stats.failed}")
```

## Configuration

```python
crawler = Crawler(
    parser=SahibindenParser(),
    mongo_uri="mongodb://localhost:27017",
    db_name="real_estate_crawler",
    fetcher_config={
        'timeout': 30,
        'max_retries': 3,
        'requests_per_minute': 10,
        'random_delay_min': 2.0,
        'random_delay_max': 5.0,
    }
)
```

## Pipeline Flow

```
URL → Fetch → Parse → Normalize → Deduplicate → Persist
      (HTML)  (data)  (clean)     (check)       (DB)
```

## Statistics

```python
stats.total       # Total URLs
stats.fetched     # Successfully fetched
stats.parsed      # Successfully parsed
stats.normalized  # Successfully normalized
stats.inserted    # New in database
stats.updated     # Updated in database
stats.skipped     # Duplicates in memory
stats.failed      # Failed to process
```

## Error Handling

- Individual failures don't stop crawl
- All errors logged with context
- Continue with next URL
- Final stats show success rate

## Deduplication

**Level 1:** In-memory (fast, session-only)  
**Level 2:** Database (persistent, authoritative)

## Rate Limiting

- Per-domain tracking
- Configurable limits
- Random delays
- Blocking detection

## Running Examples

```bash
export MONGO_URI='mongodb://localhost:27017'
python examples/crawler_demo.py
```

## Files

- `src/core/crawler.py` - Implementation
- `examples/crawler_demo.py` - Examples
- `STEP8_README.md` - Full docs
- `STEP8_SUMMARY.md` - Overview
