#!/usr/bin/env python3
"""
Ultra-simple cookie save test - No browser crashes
"""

import sys
import time
import tempfile
import shutil
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager


def main():
    print("=" * 70)
    print("SIMPLE COOKIE TEST")
    print("=" * 70)
    
    cm = CookieManager()
    domain = "www.sahibinden.com"
    
    print("\n✅ Step 1: Check if cookies already exist")
    status = cm.status(domain)
    if status['valid']:
        print(f"   Cookies found! Age: {status['age']}")
        print(f"   We can skip to Step 3")
    else:
        print(f"   No cookies yet")
    
    print("\n✅ Step 2: Open browser")
    print("   Creating Chrome instance... (this may take 10-15 seconds)")

    def create_driver():
        profile_dir = tempfile.mkdtemp(prefix="uc-profile-")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=tr-TR")

        driver = uc.Chrome(
            headless=False,
            version_main=144,
            use_subprocess=True,
            suppress_welcome=True,
            user_data_dir=profile_dir,
            options=options,
        )
        return driver, profile_dir

    driver = None
    profile_dir = None
    for attempt in range(2):
        try:
            driver, profile_dir = create_driver()
            print("   Browser created")
            time.sleep(2)
            break
        except Exception as e:
            print(f"   ❌ Failed to create browser (attempt {attempt + 1}): {e}")
            if profile_dir:
                shutil.rmtree(profile_dir, ignore_errors=True)
            if attempt == 0:
                print("   Retrying once with a fresh profile...")
            else:
                print("   This may be a macOS Chrome crash issue.")
                print("   Try: killall chrome && killall chromedriver")
                return 1
    
    try:
        # Navigate
        print(f"\n✅ Step 3: Navigate to Sahibinden")
        print(f"   Going to https://www.sahibinden.com/")
        
        try:
            driver.get("https://www.sahibinden.com/")
            print("   Page loaded, waiting 5 seconds...")
            time.sleep(5)
        except (NoSuchWindowException, WebDriverException) as e:
            print(f"\n❌ Browser closed unexpectedly: {e}")
            print("   Recreating browser and retrying once...")
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass
            if profile_dir:
                shutil.rmtree(profile_dir, ignore_errors=True)

            driver, profile_dir = create_driver()
            driver.get("https://www.sahibinden.com/")
            print("   Page loaded, waiting 5 seconds...")
            time.sleep(5)
        
        # Get info
        title = driver.title
        url = driver.current_url
        
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        
        # Check page content
        page_source = driver.page_source
        
        has_captcha = 'captcha' in page_source.lower() or 'Bir dakika' in page_source
        has_login = 'login' in url.lower() or 'sign in' in page_source.lower()
        has_content = len(page_source) > 10000
        
        print(f"\n✅ Step 4: Check page status")
        print(f"   Has CAPTCHA: {has_captcha}")
        print(f"   Has login page: {has_login}")
        print(f"   Has content: {has_content} ({len(page_source)} bytes)")
        
        if has_captcha:
            print(f"\n🤖 CAPTCHA DETECTED")
            print(f"   Please solve the CAPTCHA in the browser")
            print(f"   Then come back here and press ENTER...")
            print(f"   (Or press Ctrl+C to cancel)")
            
            try:
                input()
            except KeyboardInterrupt:
                print(f"   Cancelled")
                driver.quit()
                if profile_dir:
                    shutil.rmtree(profile_dir, ignore_errors=True)
                return 0
            
            # Wait for page to load after CAPTCHA
            print(f"   Waiting 5 seconds for page to load...")
            time.sleep(5)
            
            page_source = driver.page_source
            title = driver.title
            
            has_captcha = 'captcha' in page_source.lower()
            print(f"   CAPTCHA still there: {has_captcha}")
        
        # Save cookies if successful
        if not has_captcha and len(page_source) > 5000:
            print(f"\n✅ Step 5: Save cookies")
            cm.save_from_driver(driver, domain)
            print(f"   ✅ SUCCESS: Cookies saved!")
            print(f"\n   Next time you run this:")
            print(f"   • Cookies will load automatically")
            print(f"   • No CAPTCHA solving needed")
            print(f"   • Page loads instantly")
            driver.quit()
            return 0
        else:
            print(f"\n❌ Could not save cookies")
            print(f"   Page may not have loaded properly")
            print(f"   Keep browser open for manual check...")
            time.sleep(30)
            driver.quit()
            if profile_dir:
                shutil.rmtree(profile_dir, ignore_errors=True)
            return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()
        if profile_dir:
            shutil.rmtree(profile_dir, ignore_errors=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
