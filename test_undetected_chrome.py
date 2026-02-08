#!/usr/bin/env python3
"""
Test undetected-chromedriver for bypassing Cloudflare CAPTCHA.
This tool is specifically designed to avoid bot detection.
"""

import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_vpn():
    """Check VPN connection via ipinfo.io."""
    print("\n[1/2] Checking VPN Connection")
    print("-" * 60)
    
    driver = uc.Chrome(headless=False, use_subprocess=True, version_main=144)
    
    try:
        driver.get("https://ipinfo.io/json")
        time.sleep(2)
        
        # Get JSON content
        body = driver.find_element(By.TAG_NAME, "body").text
        
        if '"country": "TR"' in body:
            # Extract IP
            import re
            ip_match = re.search(r'"ip":\s*"([^"]+)"', body)
            city_match = re.search(r'"city":\s*"([^"]+)"', body)
            
            ip = ip_match.group(1) if ip_match else "Unknown"
            city = city_match.group(1) if city_match else "Unknown"
            
            print(f"✓ Current IP: {ip}")
            print(f"✓ Location: {city}, TR")
            print("✅ Connected to Turkey VPN!")
            return True, driver
        else:
            print("⚠️ Not connected to Turkey VPN")
            return False, driver
            
    except Exception as e:
        print(f"❌ VPN check failed: {e}")
        driver.quit()
        return False, None


def test_sahibinden(driver):
    """Test Sahibinden access."""
    print("\n[2/2] Testing Sahibinden Access")
    print("-" * 60)
    
    url = "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540"
    print(f"URL: {url}")
    print("⏳ Loading page...")
    
    try:
        driver.get(url)
        
        # Wait for page to load (giving time for Cloudflare if needed)
        print("⏳ Waiting for content...")
        time.sleep(10)
        
        # Get page details
        title = driver.title
        page_source = driver.page_source
        
        print(f"✓ Page Title: {title}")
        print(f"✓ Content Length: {len(page_source)} bytes")
        
        # Check indicators
        has_cloudflare = 'Cloudflare' in page_source or 'cf-browser-verification' in page_source
        has_captcha = 'captcha' in page_source.lower() or 'Bir dakika lütfen' in page_source
        has_listing = 'classifiedDetail' in page_source or 'ilan' in title.lower()
        has_price = 'price' in page_source or 'fiyat' in page_source.lower()
        
        print(f"Has Cloudflare challenge: {has_cloudflare}")
        print(f"Has CAPTCHA: {has_captcha}")
        print(f"Has listing data: {has_listing}")
        print(f"Has price info: {has_price}")
        
        if has_listing and not has_captcha:
            print("\n✅ SUCCESS: Bypassed Cloudflare and loaded listing!")
            print(f"   Page Title: {title}")
            return True
        elif has_captcha:
            print("\n⚠️ CAPTCHA still detected")
            print("   Even undetected-chromedriver triggers it.")
            print("   This may require:")
            print("   1. Manual CAPTCHA solving")
            print("   2. CAPTCHA solving service (2captcha, anticaptcha)")
            print("   3. Different bypass method")
            return False
        else:
            print("\n❌ Page loaded but no listing content found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("UNDETECTED-CHROMEDRIVER VPN TEST")
    print("=" * 60)
    
    vpn_ok, driver = check_vpn()
    
    if not vpn_ok or not driver:
        print("\n❌ VPN check failed")
        return 1
    
    try:
        success = test_sahibinden(driver)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ TEST PASSED - Ready for production")
            print("=" * 60)
            return 0
        else:
            print("❌ TEST FAILED - CAPTCHA still blocking")
            print("=" * 60)
            return 1
            
    finally:
        print("\n⏳ Closing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    sys.exit(main())
