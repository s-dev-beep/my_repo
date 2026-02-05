#!/usr/bin/env python3
"""
Cookie reuse demonstration - SIMPLEST approach for testing.
Shows how to:
1. Solve CAPTCHA once manually
2. Save cookies automatically
3. Reuse cookies on next run (no CAPTCHA needed)
"""

import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager


def get_ip_info(driver):
    """Get current IP to confirm VPN."""
    try:
        driver.get("https://ipinfo.io/json")
        time.sleep(1)
        
        body_text = driver.find_element("tag name", "body").text
        if '"country": "TR"' in body_text:
            print("✅ VPN: Connected to Turkey")
            return True
        else:
            print("❌ VPN: Not connected to Turkey")
            return False
    except:
        print("⚠️ Could not verify VPN")
        return True


def test_with_cookies():
    """Test accessing Sahibinden with cookie reuse."""
    print("=" * 70)
    print("COOKIE REUSE TEST - Simple Approach")
    print("=" * 70)
    
    cookie_manager = CookieManager()
    domain = "www.sahibinden.com"
    
    # Check if cookies exist
    status = cookie_manager.status(domain)
    print(f"\n📋 Current Cookie Status:")
    print(f"   Cookies exist: {status['exists']}")
    print(f"   Valid: {status['valid']}")
    if status['age']:
        print(f"   Age: {status['age']}")
    
    # Initialize browser
    print(f"\n🌐 Opening browser...")
    driver = uc.Chrome(headless=False, version_main=144, use_subprocess=True)
    
    try:
        # Verify VPN
        print(f"\n🔍 Checking VPN connection...")
        if not get_ip_info(driver):
            print("❌ Please connect VPN to Turkey first")
            return False
        
        # Try to load cookies if they exist
        if status['valid']:
            print(f"\n💾 Loading saved cookies...")
            if cookie_manager.load_to_driver(driver, domain):
                # Try accessing homepage first (lighter)
                print(f"\n📄 Testing with cookies: https://www.sahibinden.com/")
                driver.get("https://www.sahibinden.com/")
                time.sleep(5)
            else:
                print(f"⚠️ Could not load cookies, proceeding without them")
            
            page_source = driver.page_source
            title = driver.title
            
            has_captcha = 'captcha' in page_source.lower() or 'Bir dakika' in page_source
            
            if not has_captcha:
                print(f"✅ SUCCESS: Accessed without CAPTCHA!")
                print(f"   Page title: {title}")
                print(f"\n💡 This means:")
                print(f"   • Cookies are still valid")
                print(f"   • No need to solve CAPTCHA again")
                print(f"   • Will work for ~{status['age']} more")
                return True
            else:
                print(f"⚠️ CAPTCHA appeared - cookies expired")
                print(f"   Will clear and resave after solving")
        
        # If no cookies or cookies expired, fetch and save new ones
        print(f"\n🔑 Accessing Sahibinden for first time (or cookies expired)...")
        print(f"📄 Loading: https://www.sahibinden.com/")
        driver.get("https://www.sahibinden.com/")
        
        print(f"\n⏳ Waiting for page to load (5 seconds)...")
        time.sleep(5)
        
        page_source = driver.page_source
        title = driver.title
        
        has_captcha = 'captcha' in page_source.lower() or 'Bir dakika' in page_source
        
        if has_captcha:
            print(f"\n🤖 CAPTCHA detected!")
            print(f"   Browser opened for manual CAPTCHA solving.")
            print(f"   Please solve the CAPTCHA in the browser window.")
            print(f"\n   ⏳ Waiting 60 seconds for you to solve it...")
            time.sleep(60)
            
            # After 60 seconds, check if page loaded
            page_source = driver.page_source
            title = driver.title
            has_captcha = 'captcha' in page_source.lower()
            
            if has_captcha:
                print(f"\n⏱️ CAPTCHA still present after 60 seconds")
                print(f"   Please solve it and press ENTER when done...")
                input()
                
                # Wait a bit more
                time.sleep(3)
                page_source = driver.page_source
        
        # Check if successful
        has_listing = 'ilan' in title.lower() or 'kategori' in page_source.lower()
        has_captcha = 'captcha' in page_source.lower()
        
        if not has_captcha and has_listing:
            print(f"\n✅ SUCCESS: Page loaded successfully!")
            print(f"   Page title: {title}")
            print(f"   Content: {len(page_source)} bytes")
            
            # Save cookies for next time
            print(f"\n💾 Saving cookies for future use...")
            saved = cookie_manager.save_from_driver(driver, domain)
            
            if saved:
                print(f"\n✨ Next time you run this:")
                print(f"   • Cookies will load automatically (FREE)")
                print(f"   • No CAPTCHA solving needed")
                print(f"   • Page loads instantly")
                
                return True
        else:
            print(f"\n❌ Could not load page")
            print(f"   Has CAPTCHA: {has_captcha}")
            print(f"   Has content: {has_listing}")
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        print(f"\n⏳ Closing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    success = test_with_cookies()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ COOKIE TEST PASSED")
        print("=" * 70)
        print("\n💡 Summary:")
        print("   ✓ First run: Solved CAPTCHA manually, saved cookies")
        print("   ✓ Next runs: Load cookies, no CAPTCHA needed")
        print("   ✓ Cost: $0 (completely free)")
        print("\n🎯 This works until cookies expire (hours/days)")
        print("   After expiry, just solve CAPTCHA once more → cookies refresh")
        sys.exit(0)
    else:
        print("❌ COOKIE TEST FAILED")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Ensure VPN is connected to Turkey")
        print("2. Make sure you can solve CAPTCHA in browser")
        print("3. Give enough time for CAPTCHA solving (60+ seconds)")
        sys.exit(1)
