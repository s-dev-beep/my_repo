#!/usr/bin/env python3
"""Test STEP 24 again but with NordVPN routing to validate VPN solution."""

import asyncio
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.nordvpn_fetcher import NordVPNFetcher
from src.core.logger import setup_logger

logger = setup_logger(__name__)


# Test URLs (same as STEP 24)
TEST_URLS = [
    "https://www.sahibinden.com/ilan/konut-satilik-istanbul-sancaktepe-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-istanbul-kapali-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-istanbul-belediye-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-ankara-cebeci-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-ankara-kecioren-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-izmir-alsancak-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-izmir-buca-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-antalya-muratpasa-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-gaziantep-sahinbey-38851619540",
    "https://www.sahibinden.com/ilan/konut-satilik-bursa-niluferpasa-38851619540",
]


async def run_vpn_access_test():
    """Run live access test through NordVPN."""
    
    # Check credentials
    username = os.getenv("NORDVPN_USER")
    password = os.getenv("NORDVPN_PASS")
    
    if not username or not password:
        print("\n❌ Error: NordVPN credentials not provided")
        print("\nPlease set environment variables:")
        print("  export NORDVPN_USER='your_email@nordvpn.com'")
        print("  export NORDVPN_PASS='your_password'")
        sys.exit(1)
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         STEP 24 RETEST: LIVE ACCESS WITH NORDVPN ROUTING                   ║
║                                                                            ║
║ Testing 10 URLs with:                                                      ║
║   • Turkey VPN routing (clean IP)                                          ║
║   • 10-15 second delays between requests                                  ║
║   • 0 retries (fail fast on blocking)                                     ║
║   • 6 requests/minute rate limit                                          ║
║                                                                            ║
║ Comparison: STEP 24 (direct) = 0% success, STEP 26 (VPN) = ?              ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "test_type": "STEP 24 with NordVPN",
        "timestamp": datetime.now().isoformat(),
        "vpn_country": "Turkey",
        "urls_tested": len(TEST_URLS),
        "requests": [],
        "summary": {},
    }
    
    successful = 0
    blocked = 0
    errors = 0
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with NordVPNFetcher(
            nordvpn_username=username,
            nordvpn_password=password,
            nordvpn_country="Turkey",
            max_retries=0,
            requests_per_minute=6,
        ) as fetcher:
            
            print("\n✓ NordVPN connected, starting tests...\n")
            
            for idx, url in enumerate(TEST_URLS, 1):
                try:
                    # Random delay before request (except first)
                    if idx > 1:
                        delay = random.uniform(10, 15)
                        print(f"Waiting {delay:.1f}s before request {idx}/{len(TEST_URLS)}")
                        await asyncio.sleep(delay)
                    
                    print(f"\n[{idx}/{len(TEST_URLS)}] Fetching: {url[:60]}...")
                    
                    html = await fetcher.fetch(url)
                    
                    # Check for blocking indicators
                    is_error = "olağan dışı" in html.lower() or "403" in html or "429" in html
                    has_listing = "ilan" in html.lower() or "fiyat" in html.lower()
                    content_length = len(html)
                    
                    if is_error:
                        print(f"  ⚠ Status: 403 (blocking page)")
                        blocked += 1
                        results["requests"].append({
                            "url": url,
                            "status": "blocked",
                            "content_length": content_length,
                            "error": "403 or error page detected",
                        })
                    elif has_listing and content_length > 1000:
                        print(f"  ✓ Status: 200 OK ({content_length} bytes)")
                        successful += 1
                        results["requests"].append({
                            "url": url,
                            "status": "success",
                            "content_length": content_length,
                        })
                    else:
                        print(f"  ⚠ Status: 200 but unexpected content ({content_length} bytes)")
                        errors += 1
                        results["requests"].append({
                            "url": url,
                            "status": "error",
                            "content_length": content_length,
                            "error": "received data but not listing content",
                        })
                        
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    errors += 1
                    results["requests"].append({
                        "url": url,
                        "status": "error",
                        "error": str(e),
                    })
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    end_time = asyncio.get_event_loop().time()
    total_duration = end_time - start_time
    success_rate = (successful / len(TEST_URLS)) * 100 if TEST_URLS else 0
    
    # Print summary
    print("\n" + "=" * 80)
    print("STEP 24 RETEST (WITH NORDVPN): SUMMARY")
    print("=" * 80)
    print(f"Successful:         {successful}/{len(TEST_URLS)}")
    print(f"Blocked:            {blocked}/{len(TEST_URLS)}")
    print(f"Errors:             {errors}/{len(TEST_URLS)}")
    print(f"Success Rate:       {success_rate:.1f}%")
    print(f"Total Duration:     {total_duration:.1f}s")
    print("=" * 80)
    
    # Comparison with STEP 24 direct access
    print("\n📊 COMPARISON:")
    print("  STEP 24 (Direct, no VPN):     0% success (0/3 before blocking)")
    print(f"  STEP 26 (Turkey VPN):         {success_rate:.1f}% success ({successful}/{len(TEST_URLS)})")
    print(f"  Improvement:                  +{success_rate:.1f}% 📈" if success_rate > 0 else "  Improvement:                  No improvement ⚠")
    
    # Interpretation
    print("\n💡 INTERPRETATION:")
    if success_rate == 100:
        print("  ✅ VPN solution works perfectly - ready for production")
    elif success_rate >= 70:
        print("  ✅ VPN solution works well - acceptable for production")
    elif success_rate >= 50:
        print("  ⚠ VPN solution partially works - needs optimization")
    elif success_rate > 0:
        print("  ⚠ VPN solution shows some improvement but not reliable")
    else:
        print("  ❌ VPN solution doesn't work - may be:")
        print("     - NordVPN provider blocked by Sahibinden")
        print("     - VPN connection failed (check status)")
        print("     - Different blocking method now in place")
    
    # Save results
    results["summary"] = {
        "successful": successful,
        "blocked": blocked,
        "errors": errors,
        "total": len(TEST_URLS),
        "success_rate": success_rate,
        "total_duration_seconds": total_duration,
        "improvement_vs_step24": f"+{success_rate:.1f}%",
    }
    
    report_path = Path("reports/step26_vpn_routed_test.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Report saved: {report_path}")
    
    return success_rate > 0


if __name__ == "__main__":
    success = asyncio.run(run_vpn_access_test())
    sys.exit(0 if success else 1)
