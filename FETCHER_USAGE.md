# HTTP Fetcher - Production-Grade Implementation

## Quick Summary

The `Fetcher` class is a domain-agnostic HTTP client designed for web crawling with:

| Feature | Status | Details |
|---------|--------|---------|
| **Async-first** | ✅ | Built on `aiohttp` |
| **Rate limiting** | ✅ | Per-domain, configurable |
| **Polite crawling** | ✅ | Random delays + respects servers |
| **Retry logic** | ✅ | Exponential backoff (1s → 2s → 4s) |
| **Block detection** | ✅ | Auto-stops on 403/429 (3+ hits) |
| **User-Agent rotation** | ✅ | Pool of 8 agents |
| **Proxy support** | ✅ | Via PROXY_URL env var |
| **Error handling** | ✅ | `FetchError`, `BlockedError` |

## Installation

```bash
# Core dependencies
pip install aiohttp beautifulsoup4 pydantic

# Then in your code
from src.core.fetcher import Fetcher, FetchError, BlockedError
```

## Basic Usage

### Minimal Example

```python
import asyncio
from src.core.fetcher import Fetcher

async def main():
    fetcher = Fetcher()
    
    async with fetcher:
        html = await fetcher.fetch("https://example.com")
        print(f"Got {len(html)} bytes")

asyncio.run(main())
```

### With Custom Configuration

```python
fetcher = Fetcher(
    timeout=45,                    # 45 second timeout
    max_retries=5,                 # 5 retry attempts
    requests_per_minute=5,         # Slow crawling
    random_delay_min=2.0,          # 2-5 second random delay
    random_delay_max=5.0,
)

async with fetcher:
    html = await fetcher.fetch("https://example.com")
```

### Batch Fetching

```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

async with fetcher:
    results = await fetcher.fetch_batch(urls)
    
    for url, html in results.items():
        if html:
            print(f"✓ {url}: {len(html)} bytes")
        else:
            print(f"✗ {url}: Failed")
```

## Error Handling

```python
from src.core.fetcher import FetchError, BlockedError

async with fetcher:
    try:
        html = await fetcher.fetch(url)
    except BlockedError as e:
        # Server is blocking us (403/429 repeated)
        # Stop crawling to respect server limits
        logger.error(f"Blocked: {e}")
        break
    except FetchError as e:
        # Network or HTTP error
        # Continue to next URL
        logger.error(f"Failed to fetch: {e}")
        continue
    except ValueError as e:
        # Invalid URL format
        logger.error(f"Invalid URL: {e}")
        continue
```

## Configuration Examples

### Aggressive Crawling (60 req/min)

```python
fetcher = Fetcher(
    requests_per_minute=60,
    random_delay_min=0.1,
    random_delay_max=0.5,
    timeout=10,
)
# Use only with permission or dedicated proxy
```

### Balanced Crawling (10 req/min)

```python
fetcher = Fetcher(
    requests_per_minute=10,
    random_delay_min=1.0,
    random_delay_max=3.0,
    timeout=30,
)
# Good default for most public crawling
```

### Respectful Crawling (1 req/min)

```python
fetcher = Fetcher(
    requests_per_minute=1,
    random_delay_min=3.0,
    random_delay_max=10.0,
    timeout=45,
)
# Very polite; minimal server impact
```

### With Proxy

```python
# Set environment variables
import os
os.environ["USE_PROXY"] = "true"
os.environ["PROXY_URL"] = "http://proxy.example.com:8080"

# Then use normally
fetcher = Fetcher(use_proxy=True)
```

## How It Works

### Rate Limiting

```python
# Per-domain tracking
last_request_time = {
    "sahibinden.com": 1707066850.234,
    "hepsiemlak.com": 1707066845.890,
}

# When requesting same domain
min_delay = 60 / 10  # = 6 seconds for 10 req/min
elapsed = now - last_request_time[domain]
if elapsed < min_delay:
    await sleep(min_delay - elapsed)
```

**Key feature**: Different domains have independent rate limits!

### Blocking Detection

```
Request 1 → 429 (Too Many Requests)
  Record block, retry after 1s
  count = 1/3

Request 2 → 429
  Record block, retry after 2s
  count = 2/3

Request 3 → 429
  Record block
  count = 3/3 → BlockedError raised
  Stop crawling for this domain
```

**Why?** The server clearly wants us to stop. Continuing would be disrespectful and wasteful.

### Retry Strategy

```
Attempt 1 → Fails (timeout/connection error)
  Wait 1s, retry

Attempt 2 → Fails
  Wait 2s, retry

Attempt 3 → Fails
  Wait 4s, retry

Attempt 4 → Max retries reached
  Raise FetchError
```

Total time: ~7 seconds before giving up.

### User-Agent Rotation

```python
# Each request uses random agent from pool of 8
- Chrome / Windows
- Chrome / macOS
- Chrome / Linux
- Firefox / Windows
- Firefox / macOS
- Firefox / Linux
- Safari / macOS
- Edge / Windows

# Appears as different users, helps avoid detection
```

## Logging Output

```
# Debug level shows all details
DEBUG    | src.core.fetcher - Rate limit: waiting 3.45s for example.com
DEBUG    | src.core.fetcher - Adding random delay: 2.17s

# Info level shows key events
INFO     | src.core.fetcher - Fetching (attempt 1): https://example.com
INFO     | src.core.fetcher - Successfully fetched 45230 bytes

# Warning level shows problems
WARNING  | src.core.fetcher - Block detected for example.com (status 429)
WARNING  | src.core.fetcher - Got status 429, backing off and retrying (1/3)
WARNING  | src.core.fetcher - Timeout on https://example.com, retrying

# Error level shows failures
ERROR    | src.core.fetcher - Repeated blocking detected for example.com
ERROR    | src.core.fetcher - Failed to fetch after 3 retries
```

## Constants

Located in [src/utils/constants.py](../src/utils/constants.py):

```python
# Rate limiting
DEFAULT_REQUESTS_PER_MINUTE = 10
DEFAULT_RANDOM_DELAY_MIN = 1.0
DEFAULT_RANDOM_DELAY_MAX = 3.0

# Retry
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_FACTOR = 2.0
DEFAULT_INITIAL_RETRY_DELAY = 1.0

# Blocking detection
MAX_CONSECUTIVE_BLOCKS = 3
BLOCK_THRESHOLD_WINDOW = 60  # seconds

# Network
DEFAULT_TIMEOUT = 30
```

## Performance Notes

### Concurrency

```python
# Safe to use multiple coroutines concurrently
tasks = [
    fetcher.fetch(url1),
    fetcher.fetch(url2),
    fetcher.fetch(url3),
]
results = await asyncio.gather(*tasks)
```

**Important**: Rate limits are per-domain, not global. Multiple URLs to the same domain will respect delays. Multiple URLs to different domains run concurrently.

### Memory Usage

- Minimal: Only stores recent request timestamps per domain
- Blocking history: ~1KB per blocked domain
- Session: Reused across requests (no memory leak)

### Timeout Handling

```python
# Default: 30 seconds per request
# Each timeout triggers retry with backoff
# Max total time per URL: 30s + (1s + 2s + 4s) + transfer time
```

## Testing

Run included tests:

```bash
python3 test_fetcher.py
```

Output:
```
============================================================
FETCHER QUICK TEST
============================================================

1. Configuration Validation
   ✓ Rejected invalid rate limit
   ✓ Rejected proxy without URL

2. Valid Initialization
   ✓ Fetcher created successfully

3. URL Validation
   ✓ Invalid URL format
   ✓ Invalid protocol

4. User-Agent Rotation
   ✓ Generated 5 unique agents

5. Rate Limit Calculations
   ✓  1 req/min →  60.00s min delay
   ✓ 10 req/min →   6.00s min delay

6. Block Tracking
   ✓ Recorded 2 blocks for example.com

7. Exception Hierarchy
   ✓ FetchError is Exception
   ✓ BlockedError is FetchError

============================================================
All tests passed!
============================================================
```

## What's NOT Included

❌ Parsing - Use BeautifulSoup separately
❌ Database - No persistence
❌ JavaScript - Static HTML only
❌ Captcha solving - We're ethical
❌ IP rotation - Proxy only
❌ Crawling loops - Caller orchestrates

## Integration Points

### With Parser (Next Step)

```python
from src.core.fetcher import Fetcher
from src.core.parser import Parser

async def crawl_page(url):
    fetcher = Fetcher()
    parser = Parser("sahibinden")
    
    async with fetcher:
        html = await fetcher.fetch(url)
        data = parser.parse(html)
        return data
```

### With CLI

```python
# CLI commands call crawling functions
# Crawling functions use Fetcher
# Fetcher returns raw HTML to parser

cli → fetch command → run_full_crawl() 
    → Crawler class → Fetcher → HTML
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'aiohttp'"

```bash
pip install aiohttp
```

### Getting 429 (Too Many Requests)

Reduce `requests_per_minute`:

```python
# Instead of 60:
fetcher = Fetcher(requests_per_minute=5)
```

### Connection timeouts

Increase timeout:

```python
fetcher = Fetcher(timeout=60)
```

### Blocked after many requests

The `BlockedError` is intentional. Server is asking to stop. Respect it by:
1. Increasing delays: `random_delay_max = 10.0`
2. Reducing rate: `requests_per_minute = 1`
3. Using proxy: `USE_PROXY = "true"`

## Design Philosophy

- **Simple API**: `fetch(url)` returns HTML
- **Polite by default**: Random delays, rate limits
- **Fail gracefully**: Retry transient errors, stop on persistent blocks
- **Observable**: Comprehensive logging
- **Configurable**: All parameters adjustable
- **Production-ready**: Error handling, timeouts, retries

## Files

- [src/core/fetcher.py](../src/core/fetcher.py) - Main implementation (350 lines)
- [src/utils/constants.py](../src/utils/constants.py) - Configuration constants (48 lines)
- [test_fetcher.py](../test_fetcher.py) - Unit tests (92 lines)
- [FETCHER_DESIGN.md](FETCHER_DESIGN.md) - Detailed design doc
- [FETCHER_DIAGRAMS.md](FETCHER_DIAGRAMS.md) - Visual diagrams
