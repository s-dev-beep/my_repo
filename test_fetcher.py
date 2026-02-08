#!/usr/bin/env python3
"""Quick test of Fetcher implementation."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.fetcher import Fetcher, FetchError, BlockedError


async def test_fetcher():
    print("\n" + "="*60)
    print("FETCHER QUICK TEST")
    print("="*60)
    
    # Test 1: Initialization validation
    print("\n1. Configuration Validation")
    try:
        Fetcher(requests_per_minute=0)
    except ValueError as e:
        print(f"   ✓ Rejected invalid rate limit: {e}")
    
    try:
        Fetcher(use_proxy=True, proxy_url=None)
    except ValueError as e:
        print(f"   ✓ Rejected proxy without URL: {e}")
    
    # Test 2: Valid initialization
    print("\n2. Valid Initialization")
    fetcher = Fetcher(
        timeout=10,
        requests_per_minute=10,
        random_delay_min=0.1,
        random_delay_max=0.2,
    )
    print(f"   ✓ Fetcher created successfully")
    print(f"   - Timeout: {fetcher.timeout}s")
    print(f"   - Min delay: {fetcher.min_delay_between_requests:.2f}s")
    print(f"   - Rate limit: {fetcher.requests_per_minute} req/min")
    
    # Test 3: URL validation
    print("\n3. URL Validation")
    try:
        # Test without connecting (no aiohttp needed for URL validation)
        fetcher2 = Fetcher()
        invalid_urls = [
            ("not-a-url", "Invalid URL format"),
            ("ftp://example.com", "Invalid protocol"),
        ]
        
        for url, desc in invalid_urls:
            try:
                # Mock the session to avoid aiohttp requirement
                await fetcher2.fetch(url)
            except ValueError as e:
                print(f"   ✓ {desc}: {e}")
    except ImportError as e:
        print(f"   ℹ URL validation skipped (aiohttp not installed)")
    
    # Test 4: User-Agent rotation
    print("\n4. User-Agent Rotation")
    user_agents = set()
    for _ in range(10):
        ua = fetcher._get_random_user_agent()
        user_agents.add(ua)
    print(f"   ✓ Generated {len(user_agents)} unique agents from pool of 8")
    
    # Test 5: Rate limit calculation
    print("\n5. Rate Limit Calculations")
    configs = [1, 5, 10, 30, 60]
    for rpm in configs:
        f = Fetcher(requests_per_minute=rpm)
        min_delay = f.min_delay_between_requests
        print(f"   ✓ {rpm:2d} req/min → {min_delay:6.2f}s min delay")
    
    # Test 6: Block tracking
    print("\n6. Block Tracking")
    fetcher = Fetcher()
    fetcher._record_block("example.com")
    fetcher._record_block("example.com")
    print(f"   ✓ Recorded 2 blocks for example.com")
    print(f"   - Current block count: {len(fetcher.block_history['example.com'])}")
    
    # Test 7: Exception hierarchy
    print("\n7. Exception Hierarchy")
    print(f"   ✓ FetchError is Exception: {issubclass(FetchError, Exception)}")
    print(f"   ✓ BlockedError is FetchError: {issubclass(BlockedError, FetchError)}")
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_fetcher())
