# STEP 3: HTTP Fetcher Implementation - Summary

## What Was Implemented

A production-grade, domain-agnostic HTTP fetcher with:
- ✅ Async-first architecture (`aiohttp`)
- ✅ Per-domain rate limiting
- ✅ Configurable delays and retries
- ✅ User-Agent rotation
- ✅ Exponential backoff retry logic
- ✅ HTTP 403/429 blocking detection
- ✅ Auto-stop on repeated blocking
- ✅ Optional proxy support via environment
- ✅ Comprehensive error handling

## Files Created/Modified

### Core Implementation
- **[src/core/fetcher.py](src/core/fetcher.py)** (350 lines)
  - `Fetcher` class with full production logic
  - `FetchError` and `BlockedError` exceptions
  - Rate limiting, retry, and blocking detection

- **[src/utils/constants.py](src/utils/constants.py)** (48 lines)
  - Configuration constants
  - User-Agent pool (8 agents)
  - Rate limiting defaults
  - Block detection thresholds

### Documentation
- **[FETCHER_DESIGN.md](FETCHER_DESIGN.md)** - Complete design doc with examples
- **[test_fetcher.py](test_fetcher.py)** - Unit tests (7 test suites)

## Key Design Decisions

### 1. Per-Domain Rate Limiting

```python
# Different domains have independent rate limits
fetcher.last_request_time = {
    "sahibinden.com": 1234567.89,
    "hepsiemlak.com": 1234568.12,
}
```

**Why?** Allows safe concurrent crawling of multiple domains while respecting each individually.

### 2. Exponential Backoff on Retries

```
Attempt 1: Fail → wait 1s → retry
Attempt 2: Fail → wait 2s → retry  
Attempt 3: Fail → wait 4s → retry
Attempt 4: Fail → raise FetchError
```

**Why?** Standard practice for transient failures; reduces server load on backoff.

### 3. Blocking Detection with Auto-Stop

```python
if 3+ blocks in 60-second window:
    raise BlockedError("Stopping to respect server limits")
```

**Why?** Prevents aggressive retrying against a server that clearly doesn't want us crawling.

### 4. User-Agent Rotation

```python
# Random selection on each request
headers["User-Agent"] = random.choice(USER_AGENTS)
```

**Why?** Helps avoid simple user-agent-based blocking; makes requests appear as different browsers.

## Rate Limiting Examples

### Configuration → Actual Delay

| Config | Min Delay | + Random | Total |
|--------|-----------|----------|-------|
| 60 req/min | 1.0s | 1-3s | 2-4s |
| 10 req/min | 6.0s | 1-3s | 7-9s |
| 5 req/min | 12.0s | 1-3s | 13-15s |
| 1 req/min | 60.0s | 1-3s | 61-63s |

### Real-World Scenario (10 req/min)

```
Time  Action
0.0s  Request 1: sahibinden.com → success
6.5s  Request 2: hepsiemlak.com → success (no wait, different domain)
12.8s Request 3: sahibinden.com → wait 6s, then request (respects rate limit)
19.2s Request 4: hepsiemlak.com → wait 6s, then request
```

## Error Handling

```python
try:
    html = await fetcher.fetch(url)
except BlockedError:
    # Server is blocking us; stop gracefully
    logger.error("Domain blocked, stopping crawl")
    break
except FetchError as e:
    # Network or HTTP error; try next URL
    logger.error(f"Fetch failed: {e}")
    continue
except ValueError:
    # Invalid URL format
    logger.error(f"Invalid URL: {url}")
```

## Configuration Options

```python
fetcher = Fetcher(
    # Network
    timeout=30,                      # seconds
    
    # Retries
    max_retries=3,                   # attempts
    
    # Rate limiting
    requests_per_minute=10,          # requests per minute per domain
    random_delay_min=1.0,            # minimum random delay (seconds)
    random_delay_max=3.0,            # maximum random delay (seconds)
    
    # Proxy
    use_proxy=False,                 # disable by default
    proxy_url=None,                  # set via PROXY_URL env var
)
```

## Test Results

All 7 test suites passed:

```
✓ Configuration Validation (invalid inputs rejected)
✓ Valid Initialization (fetcher creates successfully)
✓ URL Validation (invalid URLs caught)
✓ User-Agent Rotation (generates variety from pool)
✓ Rate Limit Calculations (correct delays computed)
✓ Block Tracking (3-strike rule implemented)
✓ Exception Hierarchy (proper inheritance)
```

## What's NOT Included

❌ **Parsing** - Fetcher returns raw HTML only
❌ **Crawling loops** - Fetcher doesn't iterate, caller does
❌ **Domain-specific logic** - Works with any domain
❌ **Database writes** - No persistence yet
❌ **Captcha solving** - We're polite, not adversarial
❌ **JavaScript rendering** - For static HTML only
❌ **IP rotation** - Proxy support only, no rotating VPN

## Usage Example

```python
import asyncio
from src.core.fetcher import Fetcher, BlockedError, FetchError

async def main():
    fetcher = Fetcher(
        requests_per_minute=5,  # Conservative rate
        timeout=30,
    )
    
    urls = [
        "https://sahibinden.com/kiralik-satilik-emlak",
        "https://hepsiemlak.com",
    ]
    
    async with fetcher:
        for url in urls:
            try:
                html = await fetcher.fetch(url)
                print(f"Got {len(html)} bytes")
            except BlockedError:
                print(f"Blocked by {url}")
                break
            except FetchError as e:
                print(f"Failed: {e}")

asyncio.run(main())
```

## Next Steps

The `Fetcher` will be integrated with:
1. **Parser** (STEP 4) - Parses HTML into structured data
2. **Normalizer** (STEP 5) - Validates and normalizes data
3. **Crawler** (STEP 6) - Orchestrates crawling workflow

## Production Deployment

Before production:
1. ✅ Install aiohttp: `pip install aiohttp`
2. ✅ Tune `requests_per_minute` based on target site's tolerance
3. ✅ Set `USE_PROXY` and `PROXY_URL` if using proxy
4. ✅ Monitor logs for blocking patterns
5. ✅ Adjust `random_delay_min/max` for politeness vs speed tradeoff
