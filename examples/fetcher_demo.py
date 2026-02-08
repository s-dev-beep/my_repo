"""Example usage and testing of the Fetcher module."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.fetcher import Fetcher, FetchError, BlockedError
from src.core.logger import setup_logger

logger = setup_logger(__name__, level="INFO")


async def example_basic_fetch():
    """Example 1: Basic fetch with default settings."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Fetch")
    print("="*60)
    
    fetcher = Fetcher(
        timeout=10,
        requests_per_minute=30,  # 2 seconds between requests
    )
    
    try:
        async with fetcher:
            # Fetch a public page (httpbin echoes requests back)
            html = await fetcher.fetch("http://httpbin.org/html")
            print(f"✓ Fetched {len(html)} bytes")
            print(f"✓ Content preview: {html[:100]}...")
    except FetchError as e:
        print(f"✗ Fetch failed: {e}")


async def example_rate_limiting():
    """Example 2: Rate limiting behavior."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Rate Limiting (3 requests/min = 20s between)")
    print("="*60)
    
    fetcher = Fetcher(
        timeout=10,
        requests_per_minute=3,  # Very slow for demo
    )
    
    urls = [
        "http://httpbin.org/html",
        "http://httpbin.org/html",
        "http://httpbin.org/html",
    ]
    
    try:
        async with fetcher:
            start = asyncio.get_event_loop().time()
            
            for url in urls:
                print(f"\nFetching {url}...")
                await fetcher.fetch(url)
            
            elapsed = asyncio.get_event_loop().time() - start
            print(f"\n✓ Fetched {len(urls)} URLs in {elapsed:.1f}s")
            print(f"  (Expected ~{(len(urls)-1) * 20:.0f}s+ due to rate limits)")
    except FetchError as e:
        print(f"✗ Fetch failed: {e}")


async def example_invalid_url():
    """Example 3: Error handling for invalid URLs."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Invalid URL Handling")
    print("="*60)
    
    fetcher = Fetcher()
    
    invalid_urls = [
        "not-a-url",
        "ftp://unsupported.com",
        None,
    ]
    
    async with fetcher:
        for url in invalid_urls:
            try:
                await fetcher.fetch(url)
            except ValueError as e:
                print(f"✓ Caught error for {url}: {e}")


async def example_batch_fetch():
    """Example 4: Batch fetching."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Fetch (handles partial failures)")
    print("="*60)
    
    fetcher = Fetcher(
        timeout=10,
        requests_per_minute=10,
    )
    
    urls = [
        "http://httpbin.org/html",
        "http://httpbin.org/status/404",  # Will fail
        "http://httpbin.org/html",
    ]
    
    async with fetcher:
        results = await fetcher.fetch_batch(urls)
        
        for url, content in results.items():
            if content:
                print(f"✓ {url[:40]:<40} - {len(content)} bytes")
            else:
                print(f"✗ {url[:40]:<40} - Failed")


async def example_rate_limit_config():
    """Example 5: Different rate limit configurations."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Rate Limit Configurations")
    print("="*60)
    
    configs = [
        {"requests_per_minute": 60, "name": "Fast (60 req/min)"},
        {"requests_per_minute": 10, "name": "Medium (10 req/min)"},
        {"requests_per_minute": 1, "name": "Slow (1 req/min)"},
    ]
    
    for config in configs:
        fetcher = Fetcher(
            requests_per_minute=config["requests_per_minute"],
            random_delay_min=0.1,  # Reduce for demo
            random_delay_max=0.3,
        )
        
        min_delay = 60.0 / config["requests_per_minute"]
        print(f"\n{config['name']}")
        print(f"  Minimum delay between requests: {min_delay:.2f}s")
        print(f"  + Random delay: 0.1-0.3s")


async def example_configuration_validation():
    """Example 6: Configuration validation."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Configuration Validation")
    print("="*60)
    
    invalid_configs = [
        {"requests_per_minute": -1, "error": "Negative rate limit"},
        {"requests_per_minute": 0, "error": "Zero rate limit"},
        {"timeout": 0, "error": "Zero timeout"},
        {"use_proxy": True, "proxy_url": None, "error": "Proxy without URL"},
    ]
    
    for config in invalid_configs:
        error_msg = config.pop("error")
        try:
            fetcher = Fetcher(**config)
            print(f"✗ {error_msg}: Should have raised error")
        except ValueError as e:
            print(f"✓ {error_msg}: {e}")


async def main():
    """Run all examples."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║  FETCHER MODULE - EXAMPLES AND TESTING".ljust(59) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    examples = [
        ("Configuration Validation", example_configuration_validation),
        ("Basic Fetch", example_basic_fetch),
        ("Rate Limiting", example_rate_limiting),
        ("Invalid URLs", example_invalid_url),
        ("Rate Limit Configs", example_rate_limit_config),
        ("Batch Fetch", example_batch_fetch),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n✗ Example '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("NOTES")
    print("="*60)
    print("""
✓ Rate limiting is per-domain (different domains have separate limits)
✓ Random delays are added between all requests for polite crawling
✓ Exponential backoff on retries (1s, 2s, 4s, ...)
✓ User-Agent rotates randomly on each request
✓ 403/429 blocks are tracked per domain
✓ Repeated blocking (3+ in 60s) raises BlockedError to stop crawling
✓ Proxy support via environment variables (PROXY_URL, USE_PROXY)
✓ All operations are async-first for scalability
    """)


if __name__ == "__main__":
    asyncio.run(main())
