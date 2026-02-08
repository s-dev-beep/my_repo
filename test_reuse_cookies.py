#!/usr/bin/env python3
"""
Test if saved cookies work for accessing Sahibinden without CAPTCHA
"""

import sys
import time
import undetected_chromedriver as uc

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager


def main():
    print("=" * 70)
    print("TEST COOKIE REUSE - ACCESS WITHOUT CAPTCHA")
    print("=" * 70)
    
    cm = CookieManager()
    domain = "www.sahibinden.com"
    
    # Check if cookies exist
    print(f"\n1️⃣ CHECK FOR SAVED COOKIES")
    status = cm.status(domain)
    
    if not status['valid']:
        print(f"   ❌ No valid cookies found")
        print(f"   Run 'python save_cookies_now.py' first to save cookies")
        return 1
    
    print(f"   ✅ Cookies found!")
    print(f"   Age: {status['age']}")
    
    # Open new browser
    print(f"\n2️⃣ OPEN NEW BROWSER (fresh session)")
    print(f"   Creating new Chrome instance...")
    
    try:
        driver = uc.Chrome(
            headless=False,
            version_main=144,
            use_subprocess=True,
        )
        print(f"   ✅ Browser opened")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return 1
    
    try:
        # Navigate to Sahibinden first (to set domain cookie)
        print(f"\n3️⃣ NAVIGATE TO SAHIBINDEN")
        driver.get("https://www.sahibinden.com/")
        time.sleep(2)
        
        print(f"   ✅ Page loaded")
        
        # Load cookies
        print(f"\n4️⃣ LOAD SAVED COOKIES INTO BROWSER")
        
        if cm.load_to_driver(driver, domain):
            print(f"   ✅ Cookies loaded")
        else:
            print(f"   ⚠️ Could not load cookies")
        
        # Navigate again with cookies
        print(f"\n5️⃣ NAVIGATE WITH COOKIES")
        driver.get("https://www.sahibinden.com/")
        time.sleep(5)
        
        # Check result
        title = driver.title
        url = driver.current_url
        page_source = driver.page_source
        page_size = len(page_source)
        
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        print(f"   Page size: {page_size} bytes")
        
        # Check for CAPTCHA or content
        has_captcha = 'captcha' in page_source.lower() or 'bir dakika' in page_source.lower()
        has_content = page_size > 20000
        
        print(f"\n6️⃣ RESULT")
        
        if has_captcha:
            print(f"   ❌ CAPTCHA appeared")
            print(f"   This means cookies expired or were rejected")
            print(f"   Need to solve CAPTCHA again and refresh cookies")
            driver.quit()
            return 1
        
        elif has_content:
            print(f"   ✅✅✅ SUCCESS!!!")
            print(f"   Page loaded WITHOUT CAPTCHA!")
            print(f"\n   What this means:")
            print(f"   • Cookies are valid and working")
            print(f"   • You can now access Sahibinden without CAPTCHA")
            print(f"   • For the next 24+ hours, all requests will be instant")
            print(f"   • Cost: $0!")
            
            print(f"\n   Browser stays open for 30 seconds for inspection...")
            time.sleep(30)
            
            driver.quit()
            return 0
        else:
            print(f"   ⚠️ Page loaded but content not found")
            print(f"   Keep browser open for manual check...")
            time.sleep(30)
            driver.quit()
            return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()
        return 1


if __name__ == "__main__":
    sys.exit(main())
