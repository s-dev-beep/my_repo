#!/usr/bin/env python3
"""Test Sahibinden access with Cloudflare bypass (cloudscraper)."""

import cloudscraper
import requests

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║        SAHIBINDEN TEST WITH CLOUDFLARE BYPASS (VPN Required)               ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Check current IP first
print("📍 Checking your current IP and location...")
try:
    ip_info = requests.get("https://ipinfo.io/json", timeout=5).json()
    print(f"✓ Current IP: {ip_info.get('ip')}")
    print(f"✓ Location: {ip_info.get('city')}, {ip_info.get('country')}")
    print(f"✓ ISP: {ip_info.get('org')}")
    print()
    
    if ip_info.get('country') != 'TR':
        print("⚠️  WARNING: You're not connected to Turkey VPN!")
        print()
        print("Please connect to Turkey in NordVPN app first, then re-run this test.")
        print()
        exit(1)
    else:
        print("✅ Connected to Turkey VPN!")
        print()
except Exception as e:
    print(f"⚠️  Could not check IP: {e}")
    print("Continuing anyway...")
    print()

# Test Sahibinden with cloudscraper
test_url = "https://www.sahibinden.com/"  # Try homepage first

print(f"🧪 Testing Sahibinden access with Cloudflare bypass...")
print(f"URL: {test_url}")
print()

try:
    # Create a cloudscraper session with custom headers
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',  # macOS
            'desktop': True
        },
        delay=10  # Add delay to seem more human-like
    )
    
    # Add realistic headers
    scraper.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    print("⏳ Fetching with Cloudflare bypass...")
    response = scraper.get(test_url, timeout=30)
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Content Length: {len(response.text)} bytes")
    print()
    
    # Check content
    html = response.text
    has_cloudflare = "just a moment" in html.lower() or "cloudflare" in html.lower()
    has_listings = "emlak" in html.lower() or "ilan" in html.lower() or "fiyat" in html.lower()
    has_sahibinden = "sahibinden" in html.lower()
    is_error_403 = "olağan dışı" in html.lower() or response.status_code == 403
    
    print("📋 Content Analysis:")
    print(f"  Has Cloudflare challenge: {has_cloudflare}")
    print(f"  Has Sahibinden content: {has_sahibinden}")
    print(f"  Has listing data: {has_listings}")
    print(f"  Is 403 error page: {is_error_403}")
    print()
    
    if response.status_code == 200 and has_listings and not has_cloudflare:
        print("✅ SUCCESS! Sahibinden is accessible with Cloudflare bypass!")
        print()
        print("The VPN + Cloudflare bypass solution works! 🎉")
        print()
        print("Next steps:")
        print("  1. Integrate cloudscraper into Fetcher")
        print("  2. Run full 10-URL test")
        print("  3. Expect 70-90% success rate")
        print()
        
        # Show a snippet
        print("📄 Sample content (first 500 chars):")
        print("-" * 80)
        print(html[:500].replace('\n', ' ').replace('  ', ' '))
        print("-" * 80)
        print()
        
        exit(0)
    elif has_cloudflare:
        print("⚠️  Cloudflare challenge still present (cloudscraper may need different config)")
        print()
        exit(1)
    elif is_error_403:
        print("❌ Still getting 403 error - VPN IP might be flagged")
        print()
        print("Try:")
        print("  1. Disconnect and reconnect NordVPN to get new Turkey IP")
        print("  2. Wait 5 minutes")
        print("  3. Try a different Turkey server")
        print()
        exit(1)
    else:
        print("⚠️  Unexpected response - manual inspection needed")
        print()
        print("First 1000 chars of response:")
        print(html[:1000])
        print()
        exit(1)
        
except Exception as e:
    print(f"❌ Fetch failed: {e}")
    print()
    import traceback
    traceback.print_exc()
    exit(1)
