#!/usr/bin/env python3
"""
Test Playwright-based fetching with VPN for Sahibinden access.
This bypasses Cloudflare's JavaScript challenges using a real browser.
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def check_vpn_connection():
    """Check current IP and location using ipinfo.io."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://ipinfo.io/json", timeout=10000)
            content = await page.content()
            
            # Extract JSON from page
            import json
            import re
            json_match = re.search(r'<pre>(.*?)</pre>', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                ip = data.get('ip', 'Unknown')
                city = data.get('city', 'Unknown')
                country = data.get('country', 'Unknown')
                
                print(f"✓ Current IP: {ip}")
                print(f"✓ Location: {city}, {country}")
                
                if country == 'TR':
                    print("✅ Connected to Turkey VPN!")
                    return True
                else:
                    print(f"⚠️ Not connected to Turkey (current: {country})")
                    return False
            else:
                print("❌ Could not parse IP info")
                return False
                
        except Exception as e:
            print(f"❌ VPN check failed: {e}")
            return False
        finally:
            await browser.close()


async def test_sahibinden_access(url: str):
    """Test accessing Sahibinden with Playwright."""
    print(f"\nURL: {url}")
    print("⏳ Launching browser...")
    
    async with async_playwright() as p:
        # Launch browser with realistic settings
        browser = await p.chromium.launch(
            headless=False,  # Run WITH UI - avoids CAPTCHA
            args=[
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Create context with Turkish locale
        context = await browser.new_context(
            locale='tr-TR',
            timezone_id='Europe/Istanbul',
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        page = await context.new_page()
        
        try:
            print("⏳ Navigating to page...")
            # Navigate with longer timeout, wait for load event
            response = await page.goto(url, timeout=60000, wait_until='load')
            
            # Wait for content to load (Cloudflare challenge resolution)
            print("⏳ Waiting for page to fully load...")
            await page.wait_for_timeout(10000)  # Wait 10 seconds for Cloudflare
            
            # Wait a bit for any JavaScript to execute
            await page.wait_for_timeout(2000)
            
            # Get page content
            content = await page.content()
            title = await page.title()
            
            print(f"✓ Status Code: {response.status}")
            print(f"✓ Page Title: {title}")
            print(f"✓ Content Length: {len(content)} bytes")
            
            # Check for various indicators
            has_cloudflare = 'Cloudflare' in content or 'cf-browser-verification' in content
            has_captcha = 'captcha' in content.lower() or 'challenge' in content.lower()
            has_listing = 'classifiedDetail' in content or 'listing' in content.lower()
            has_price = 'price' in content.lower() or 'fiyat' in content.lower()
            is_error = response.status >= 400
            
            print(f"Has Cloudflare challenge: {has_cloudflare}")
            print(f"Has CAPTCHA: {has_captcha}")
            print(f"Has listing data: {has_listing}")
            print(f"Has price info: {has_price}")
            print(f"Is error page: {is_error}")
            
            # Determine success
            if response.status == 200 and has_listing and not has_cloudflare:
                print("\n✅ SUCCESS: Fetched real listing content!")
                print(f"   Page Title: {title}")
                return True, content
            elif response.status == 200 and has_cloudflare:
                print("\n⚠️ Cloudflare challenge detected (but page loaded)")
                print("   Playwright may need stealth plugin or longer wait")
                return False, content
            elif has_captcha:
                print("\n⚠️ CAPTCHA challenge detected")
                print("   Browser test showed CAPTCHA → headless may trigger it")
                print("   May need: playwright-stealth or headed mode")
                return False, content
            else:
                print(f"\n❌ FAILED: Status {response.status}")
                return False, content
                
        except Exception as e:
            print(f"\n❌ Error during fetch: {e}")
            return False, None
            
        finally:
            await browser.close()


async def main():
    """Main test flow."""
    print("=" * 60)
    print("PLAYWRIGHT VPN ACCESS TEST")
    print("=" * 60)
    
    # Step 1: Check VPN connection
    print("\n[1/2] Checking VPN Connection")
    print("-" * 60)
    
    vpn_ok = await check_vpn_connection()
    if not vpn_ok:
        print("\n❌ NOT CONNECTED TO TURKEY VPN")
        print("Please connect NordVPN to Turkey before running this test")
        return 1
    
    # Step 2: Test Sahibinden access
    print("\n[2/2] Testing Sahibinden Access")
    print("-" * 60)
    
    # Use a real listing URL from proof_of_truth
    test_url = "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540"
    
    success, content = await test_sahibinden_access(test_url)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ PLAYWRIGHT VPN TEST PASSED")
        print("=" * 60)
        print("\nNext: Run full STEP 24 test with Playwright")
        return 0
    else:
        print("❌ PLAYWRIGHT VPN TEST FAILED")
        print("=" * 60)
        print("\nCloudflare may be detecting headless browser.")
        print("Options:")
        print("1. Install playwright-stealth")
        print("2. Use headed mode (headless=False)")
        print("3. Add more realistic behavior (mouse movements, delays)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
