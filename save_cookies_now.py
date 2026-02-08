#!/usr/bin/env python3
"""
Save cookies after successful authentication
"""

import sys
import time
import undetected_chromedriver as uc

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager


def main():
    print("=" * 70)
    print("SAVE COOKIES FROM CURRENT BROWSER SESSION")
    print("=" * 70)
    
    cm = CookieManager()
    domain = "www.sahibinden.com"
    
    print("\n📋 Instructions:")
    print("   1. The browser should still be open from previous test")
    print("   2. We'll extract and save the cookies")
    print("   3. Cookies will be saved for future use")
    
    print("\n📂 Checking for browser session...")
    
    # Connect to existing browser or create new one
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Try to connect to existing Chrome instance
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Connected to existing browser")
        except:
            print("⚠️ Could not connect to existing browser")
            print("   Opening new browser...")
            
            driver = uc.Chrome(
                headless=False,
                version_main=144,
                use_subprocess=True,
            )
            
            # Navigate to Sahibinden
            print("   Navigating to Sahibinden...")
            driver.get("https://www.sahibinden.com/")
            
            print("   Browser opened")
            print("   If CAPTCHA/verification appears, solve it manually")
            print("   Press ENTER when page fully loads...")
            input()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    try:
        # Get current page info
        print(f"\n📄 Checking page...")
        title = driver.title
        url = driver.current_url
        
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        
        # Check page content
        page_source = driver.page_source
        page_size = len(page_source)
        
        # Check if we're on Sahibinden main page
        is_sahibinden = 'sahibinden' in page_source.lower() and page_size > 10000
        has_captcha = 'captcha' in page_source.lower() or 'verification' in page_source.lower()
        
        print(f"   Page size: {page_size} bytes")
        print(f"   Is Sahibinden: {is_sahibinden}")
        print(f"   Has CAPTCHA: {has_captcha}")
        
        if has_captcha:
            print(f"\n⏳ CAPTCHA/verification still loading...")
            print(f"   Waiting 10 seconds for it to complete...")
            time.sleep(10)
            
            page_source = driver.page_source
            has_captcha = 'captcha' in page_source.lower()
            
            if has_captcha:
                print(f"   Still there - might need manual action")
                print(f"   Keep browser open and manually navigate to homepage")
                print(f"   Then press ENTER here when ready...")
                input()
        
        # Save cookies
        print(f"\n💾 Saving cookies...")
        
        saved = cm.save_from_driver(driver, domain)
        
        if saved:
            print(f"   ✅ Cookies saved successfully!")
            
            # Show saved cookie info
            status = cm.status(domain)
            print(f"\n📊 Saved Cookie Info:")
            print(f"   File: {status['file']}")
            print(f"   Valid: {status['valid']}")
            
            print(f"\n✨ SUCCESS!")
            print(f"   Cookies are now saved and ready to use")
            print(f"   Next requests will use these cookies automatically")
            
            # Cleanup
            driver.quit()
            return 0
        else:
            print(f"   ❌ Failed to save cookies")
            print(f"   Page might not have loaded properly")
            print(f"   Keep browser open for 60 seconds to check...")
            time.sleep(60)
            driver.quit()
            return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
