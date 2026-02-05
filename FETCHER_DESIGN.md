# HTTP Fetcher Implementation

## Overview

The `Fetcher` class is a production-grade, domain-agnostic HTTP client designed for web crawling with:

- **Async-first architecture** using `aiohttp` for concurrent requests
- **Rate limiting** (per-domain) to respect server resources
- **Polite crawling** with configurable delays
- **Exponential backoff retry logic** for transient failures
- **Blocking detection** (HTTP 403/429) with automatic stop-on-repeated-blocks
- **User-Agent rotation** to avoid detection
- **Optional proxy support** via environment variables
- **Comprehensive logging** for debugging and monitoring

## Architecture

```
Fetcher (Main class)
├── Rate Limiting (per-domain tracking)
├── Retry Logic (exponential backoff)
├── Block Detection (403/429 tracking)
├── User-Agent Rotation (random selection)
└── HTTP Session Management (aiohttp)
```

## Key Components

### Configuration

Located in [src/utils/constants.py](../src/utils/constants.py):

```python
# Rate limiting
DEFAULT_REQUESTS_PER_MINUTE = 10
DEFAULT_RANDOM_DELAY_MIN = 1.0
DEFAULT_RANDOM_DELAY_MAX = 3.0

# Retry behavior
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_FACTOR = 2.0

# Block detection
MAX_CONSECUTIVE_BLOCKS = 3
BLOCK_THRESHOLD_WINDOW = 60  # seconds
```

### Rate Limiting

**Per-Domain Tracking**:
- Maintains separate rate limits for each domain
- Enforces minimum delay between requests to the same domain
- Prevents overwhelming any single server

**Formula**:
```
min_delay_per_request = 60 / requests_per_minute
total_delay = min_delay + random(delay_min, delay_max)
```

**Example**:
- `requests_per_minute=10` → minimum 6 seconds between requests
- Plus random 1-3 second delay
- Total: 7-9 seconds between requests to same domain

### Retry Logic

**Exponential Backoff**:
```
Attempt 1: Fail → wait 1s, retry
Attempt 2: Fail → wait 2s, retry
Attempt 3: Fail → wait 4s, retry
Attempt 4: Fail → raise FetchError
```

**Triggering Retries**:
- Network timeouts (`asyncio.TimeoutError`)
- Connection errors (`aiohttp.ClientError`)
- HTTP 403/429 (blocking) with backoff

### Block Detection

**Tracking**:
- Records timestamps of 403/429 responses per domain
- Maintains a rolling window (default: 60 seconds)
- Counts recent blocks within the window

**Auto-Stop**:
```
If blocks >= MAX_CONSECUTIVE_BLOCKS (3) in BLOCK_THRESHOLD_WINDOW (60s):
    → Raise BlockedError and stop crawling for that domain
    → Prevents repeated hammering of blocked servers
```

### User-Agent Rotation

**Pool of 8 Common Agents**:
- Chrome Windows, macOS, Linux
- Firefox Windows, macOS, Linux
- Safari macOS
- Edge Windows, macOS

**Selection**:
- Random selection on each request
- Appears as different user browsing

### Error Handling

```
Exceptions:
├── FetchError (base)
│   ├── Network errors (connection, timeout)
│   ├── HTTP errors (4xx, 5xx)
│   └── Generic fetch failures
└── BlockedError (extends FetchError)
    └── Raised on repeated blocking detection
```

## Usage Examples

### Basic Usage

```python
import asyncio
from src.core.fetcher import Fetcher

async def main():
    fetcher = Fetcher(
        timeout=30,
        max_retries=3,
        requests_per_minute=10,
    )
    
    async with fetcher:
        html = await fetcher.fetch("https://example.com")
        print(f"Got {len(html)} bytes")

asyncio.run(main())
```

### Custom Configuration

```python
fetcher = Fetcher(
    timeout=45,
    max_retries=5,
    requests_per_minute=5,  # Slow crawling
    random_delay_min=2.0,
    random_delay_max=5.0,
)
```

### With Proxy

```python
# Set environment variables
export PROXY_URL="http://proxy.example.com:8080"
export USE_PROXY="true"

# Then use:
fetcher = Fetcher(use_proxy=True)
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
    # results = {url -> html or None}
```

### Error Handling

```python
from src.core.fetcher import FetchError, BlockedError

async with fetcher:
    try:
        html = await fetcher.fetch(url)
    except BlockedError:
        logger.error(f"Domain blocked. Stopping crawl.")
        break
    except FetchError as e:
        logger.error(f"Failed to fetch: {e}")
```

## Rate Limiting in Action

### Example: 3 requests/minute

```
Request 1: Fetch from sahibinden.com
  └─ Wait 20s (60/3) + 1.5s (random)
  └─ Total: 21.5s

Request 2: Fetch from sahibinden.com
  └─ Wait 20s + 2.3s
  └─ Total: 22.3s

Request 3: Fetch from sahibinden.com
  └─ Wait 20s + 1.8s
  └─ Total: 21.8s

Elapsed time: ~65 seconds for 3 requests
```

### Per-Domain Independence

```
Request 1 to sahibinden.com  ✓
  └─ Rate limit tracking starts for sahibinden.com

Request 2 to hepsiemlak.com  ✓ (no wait!)
  └─ Different domain, different rate limit

Request 3 to sahibinden.com  ⏳ (waits)
  └─ Same domain, respects minimum delay
```

## Blocking Behavior

### Scenario: Repeated 429 Responses

```
Request 1: → 429 (Too Many Requests)
           Record: 1 block, retry after 1s

Request 2: → 429
           Record: 2 blocks, retry after 2s

Request 3: → 429
           Record: 3 blocks
           → BlockedError raised
           → Crawling stops

Why? 
- 3 blocks in 60-second window = server wants us to stop
- Continuing would be disrespectful
```

## Configuration Best Practices

| Use Case | Config |
|----------|--------|
| **Aggressive** | 60 req/min, 0s-1s delay |
| **Balanced** | 10 req/min, 1s-3s delay |
| **Conservative** | 5 req/min, 2s-5s delay |
| **Very Polite** | 1 req/min, 3s-10s delay |

## Logging Output

```
INFO     | src.core.fetcher - Fetcher initialized: timeout=30s, max_retries=3, rate_limit=10req/min
INFO     | src.core.fetcher - Fetching (attempt 1): https://example.com
DEBUG    | src.core.fetcher - Rate limit: waiting 5.23s for example.com
DEBUG    | src.core.fetcher - Adding random delay: 1.85s
INFO     | src.core.fetcher - Successfully fetched 45230 bytes from https://example.com

WARNING  | src.core.fetcher - Block detected for example.com (status 429). Recent blocks: 1/3
WARNING  | src.core.fetcher - Got status 429, backing off and retrying (1/3)

ERROR    | src.core.fetcher - Repeated blocking detected for example.com: 3 blocks in 60s. Stopping.
```

## What's NOT Implemented

❌ Parsing or CSS selectors
❌ Database storage
❌ Captcha solving
❌ JavaScript rendering
❌ Hardcoded domain logic
❌ VPN/IP rotation (proxy-only)

## Next Steps

The `Fetcher` will be used by:
1. **Parser** - To fetch and parse HTML
2. **Crawler** - To orchestrate fetching tasks
3. **Adapters** - To fetch domain-specific pages

Example integration:
```python
fetcher = Fetcher(requests_per_minute=5)
parser = Parser("sahibinden")

for url in listing_urls:
    html = await fetcher.fetch(url)
    data = parser.parse(html)
    # ... normalize and store
```
