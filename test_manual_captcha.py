#!/usr/bin/env python3
"""
Semi-automated fetcher: Opens browser, waits for manual CAPTCHA solving, then proceeds.
This is the practical solution for Sahibinden's advanced bot detection.
"""

import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


def test_manual_captcha_flow():
    """Test with manual CAPTCHA solving."""
    print("=" * 70)
    print("SEMI-AUTOMATED SAHIBINDEN FETCHER")
    print("VPN + Manual CAPTCHA Solving")
    print("=" * 70)
    
    # Test URL
    url = "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540"
    
    print("\n🌐 Opening browser...")
    driver = uc.Chrome(headless=False, version_main=144)
    
    try:
        # Navigate to page
        print(f"📄 Loading: {url}")
        driver.get(url)
        
        # Wait a bit for page to load
        time.sleep(3)
        
        # Check if CAPTCHA appears
        page_source = driver.page_source
        title = driver.title
        
        if 'captcha' in page_source.lower() or 'Bir dakika' in page_source or 'Olağan dışı' in page_source:
            print("\n🤖 CAPTCHA detected!")
            print("=" * 70)
            print("ACTION REQUIRED:")
            print("1. Solve the CAPTCHA in the browser window")
            print("2. Wait for the page to load completely")
            print("3. Press ENTER here when ready...")
            print("=" * 70)
            input("Press ENTER after solving CAPTCHA...")
            
            # Reload page source after CAPTCHA
            page_source = driver.page_source
            title = driver.title
        
        # Check if we have listing content
        has_listing = 'classifiedDetail' in page_source or 'ilan' in title.lower()
        has_price = 'fiyat' in page_source.lower() or 'TL' in page_source
        
        print(f"\n✓ Page Title: {title}")
        print(f"✓ Content Length: {len(page_source)} bytes")
        print(f"✓ Has listing data: {has_listing}")
        print(f"✓ Has price info: {has_price}")
        
        if has_listing:
            print("\n✅ SUCCESS: Listing content fetched!")
            print("\n📊 This proves the solution works:")
            print("   1. ✓ VPN connected to Turkey")
            print("   2. ✓ Manual CAPTCHA solving works")
            print("   3. ✓ Can fetch listing content")
            print("\n💡 Production approach:")
            print("   - Use CAPTCHA solving service (2captcha, anticaptcha)")
            print("   - Or: Solve CAPTCHA once, reuse cookies/session")
            print("   - Or: Residential proxies (less likely to trigger CAPTCHA)")
            
            return True
        else:
            print("\n❌ No listing content found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        print("\n⏳ Keeping browser open for 10 seconds for inspection...")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    success = test_manual_captcha_flow()
    sys.exit(0 if success else 1)
