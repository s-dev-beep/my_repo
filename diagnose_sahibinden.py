#!/usr/bin/env python3
"""
Quick diagnostic - Check what's happening with Sahibinden access
"""

import sys
import time
import undetected_chromedriver as uc

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager


def main():
    print("=" * 70)
    print("SAHIBINDEN ACCESS DIAGNOSTIC")
    print("=" * 70)
    
    # Check saved cookies
    cm = CookieManager()
    status = cm.status("www.sahibinden.com")
    
    print(f"\n1️⃣ COOKIE STATUS")
    print(f"   Exists: {status['exists']}")
    print(f"   Valid: {status['valid']}")
    if status['age']:
        print(f"   Age: {status['age']}")
    
    # Open browser
    print(f"\n2️⃣ OPENING BROWSER (headed mode)...")
    driver = uc.Chrome(headless=False, version_main=144, use_subprocess=True)
    
    try:
        # Check IP
        print(f"\n3️⃣ CHECKING IP...")
        driver.get("https://ipinfo.io/json")
        time.sleep(2)
        body = driver.find_element("tag name", "body").text
        if '"country": "TR"' in body:
            print(f"   ✅ IP: Turkey (VPN working)")
        else:
            print(f"   ❌ Not Turkey IP - VPN may be disconnected")
        
        # Try homepage without cookies
        print(f"\n4️⃣ ACCESSING HOMEPAGE (no cookies)...")
        driver.get("https://www.sahibinden.com/")
        time.sleep(3)
        
        title = driver.title
        url = driver.current_url
        
        print(f"   URL: {url}")
        print(f"   Title: {title}")
        
        # Check what page loaded
        page_source = driver.page_source
        
        if "login" in url.lower():
            print(f"   ❌ REDIRECTED TO LOGIN")
            print(f"   This means: Sahibinden redirected us to login page")
            print(f"   Possible causes:")
            print(f"     • Session expired")
            print(f"     • VPN IP is flagged")
            print(f"     • Cloudflare challenge before redirect")
        elif "captcha" in page_source.lower() or "bir dakika" in page_source.lower():
            print(f"   ⏳ CLOUDFLARE CAPTCHA")
            print(f"   Action: Solve CAPTCHA in browser, then press ENTER...")
            input()
            
            # Check after CAPTCHA
            time.sleep(2)
            page_source = driver.page_source
            title = driver.title
            
            if "login" in page_source.lower():
                print(f"   Still login page after CAPTCHA")
            else:
                print(f"   ✅ Page loaded!")
        else:
            print(f"   ✅ PAGE LOADED")
            print(f"   Content size: {len(page_source)} bytes")
        
        # Now try with cookies if they exist
        if status['valid']:
            print(f"\n5️⃣ TESTING WITH COOKIES...")
            driver.delete_all_cookies()
            driver.get("https://www.sahibinden.com/")
            time.sleep(1)
            
            cm.load_to_driver(driver, "www.sahibinden.com")
            driver.get("https://www.sahibinden.com/")
            time.sleep(3)
            
            page_source = driver.page_source
            title = driver.title
            
            if "captcha" in page_source.lower():
                print(f"   ⚠️ CAPTCHA appeared (cookies invalid)")
            elif "login" in page_source.lower():
                print(f"   ⚠️ Login page (cookies expired)")
            else:
                print(f"   ✅ WORKED WITH COOKIES!")
        
        print(f"\n6️⃣ KEEP BROWSER OPEN FOR 30 SECONDS FOR INSPECTION...")
        print(f"   You can manually navigate and test")
        time.sleep(30)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
