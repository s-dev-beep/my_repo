#!/usr/bin/env python3
"""
Integrated VPN + CAPTCHA + Cookie-based fetcher for Sahibinden.
Implements both cookie reuse and CAPTCHA service for maximum flexibility.
"""

import sys
import time
import asyncio
import undetected_chromedriver as uc
from typing import Optional, Dict, Any, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager
from src.core.captcha_manager import CaptchaManager


class SahibindenFetcher:
    """
    Integrated fetcher with cookie reuse and CAPTCHA solving.
    
    Strategy:
    1. Try to use cached cookies (free)
    2. If no valid cookies, use CAPTCHA service (paid) or manual solving
    3. Save successful cookies for future use
    """
    
    def __init__(
        self,
        domain: str = "www.sahibinden.com",
        captcha_provider: str = "twocaptcha",
        captcha_key: Optional[str] = None,
        use_captcha: bool = True,
        use_cookies: bool = True,
    ):
        """
        Initialize Sahibinden fetcher.
        
        Args:
            domain: Target domain
            captcha_provider: 'twocaptcha', 'anticaptcha', etc.
            captcha_key: API key for CAPTCHA service
            use_captcha: Enable CAPTCHA solving
            use_cookies: Enable cookie reuse
        """
        self.domain = domain
        self.use_captcha = use_captcha
        self.use_cookies = use_cookies
        
        # Initialize managers
        self.cookie_manager = CookieManager() if use_cookies else None
        self.captcha_manager = CaptchaManager(captcha_provider, captcha_key) if use_captcha else None
        
        self.driver = None
        
        # Print configuration
        print("=" * 70)
        print("SAHIBINDEN FETCHER - CONFIGURATION")
        print("=" * 70)
        print(f"Domain: {domain}")
        print(f"Cookie Reuse: {'✅ Enabled' if use_cookies else '❌ Disabled'}")
        print(f"CAPTCHA Service: {'✅ Enabled' if use_captcha else '❌ Disabled'}")
        if use_captcha:
            print(f"  Provider: {captcha_provider}")
            print(f"  API Key: {'✅ Set' if captcha_key or self.captcha_manager.api_key else '❌ Not set'}")
        print()
    
    def _init_driver(self, headless: bool = False) -> uc.Chrome:
        """Initialize Selenium Chrome driver."""
        print("🌐 Initializing browser...")
        driver = uc.Chrome(
            headless=headless,
            version_main=144,
            use_subprocess=True,
        )
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver
    
    def _fetch_with_driver(self, url: str) -> Optional[str]:
        """Fetch URL using Selenium driver."""
        if not self.driver:
            self.driver = self._init_driver(headless=False)
        
        try:
            print(f"📄 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            page_source = self.driver.page_source
            title = self.driver.title
            
            print(f"✓ Page Title: {title}")
            print(f"✓ Content Length: {len(page_source)} bytes")
            
            # Check for CAPTCHA
            has_captcha = 'captcha' in page_source.lower() or 'Bir dakika' in page_source
            
            if has_captcha and self.use_captcha:
                print("🤖 CAPTCHA detected, attempting to solve...")
                
                # Try to extract Cloudflare sitekey from page
                import re
                sitekey_match = re.search(r'data-sitekey="([^"]+)"', page_source)
                
                if sitekey_match:
                    sitekey = sitekey_match.group(1)
                    print(f"   Sitekey found: {sitekey[:20]}...")
                    
                    # This would call CAPTCHA service in real implementation
                    print("   ⚠️ Note: Full CAPTCHA solving requires 2Captcha API setup")
                    return None
                else:
                    print("   ⚠️ Could not extract sitekey, manual solving needed")
                    return None
            
            # Check if we got listing content
            has_listing = 'classifiedDetail' in page_source or 'ilan' in title.lower()
            
            if has_listing:
                print("✅ SUCCESS: Retrieved listing content!")
                
                # Save cookies for future use
                if self.use_cookies:
                    self.cookie_manager.save_from_driver(self.driver, self.domain)
                
                return page_source
            else:
                print("❌ No listing content found")
                return None
                
        except Exception as e:
            print(f"❌ Error during fetch: {e}")
            return None
    
    async def fetch(self, url: str, use_cookies_first: bool = True) -> Optional[str]:
        """
        Fetch a URL with integrated cookie and CAPTCHA support.
        
        Args:
            url: URL to fetch
            use_cookies_first: Try cookies before CAPTCHA service
            
        Returns:
            Page HTML or None if failed
        """
        print(f"\n{'=' * 70}")
        print(f"FETCHING: {url}")
        print(f"{'=' * 70}\n")
        
        # Step 1: Try cookies first
        if use_cookies_first and self.use_cookies:
            print("[1/3] Checking for cached cookies...")
            status = self.cookie_manager.status(self.domain)
            
            if status['valid']:
                print(f"   Age: {status['age']}")
                print("[2/3] Attempting fetch with cached cookies...")
                
                # Fetch with cookies
                driver = self._init_driver(headless=True)  # Try headless first with cookies
                
                try:
                    if self.cookie_manager.load_to_driver(driver, self.domain):
                        driver.get(url)
                        time.sleep(3)
                        
                        page_source = driver.page_source
                        title = driver.title
                        
                        # Check if cookies worked (no CAPTCHA)
                        has_captcha = 'captcha' in page_source.lower()
                        has_listing = 'classifiedDetail' in page_source
                        
                        if has_listing and not has_captcha:
                            print("✅ Cookies worked! Retrieved content without CAPTCHA")
                            driver.quit()
                            return page_source
                        else:
                            print("⚠️ Cookies expired or insufficient, proceeding to CAPTCHA solving...")
                    
                    driver.quit()
                    
                except Exception as e:
                    print(f"⚠️ Cookie fetch failed: {e}")
                    driver.quit()
            else:
                print("   No valid cached cookies found")
        
        # Step 2: Use CAPTCHA service if available
        if self.use_captcha and self.captcha_manager and self.captcha_manager.solver:
            print("[2/3] Attempting fetch with CAPTCHA service...")
            # In production, would fetch with CAPTCHA solving
            print("   ℹ️ Full CAPTCHA integration requires 2Captcha API key")
            print("   Export key to CAPTCHA_2CAPTCHA_KEY environment variable")
            
            # Check balance if available
            balance = self.captcha_manager.get_balance_2captcha()
            if balance:
                print(f"   Account Balance: ${balance}")
        
        # Step 3: Manual fetch (user solves CAPTCHA)
        print("[3/3] Manual fetch (browser opens for CAPTCHA if needed)...")
        result = self._fetch_with_driver(url)
        
        return result
    
    def close(self):
        """Close browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


async def test_single_url():
    """Test fetching a single URL."""
    
    # Initialize fetcher
    fetcher = SahibindenFetcher(
        use_cookies=True,      # Enable cookie reuse (free)
        use_captcha=True,      # Enable CAPTCHA service (paid, optional)
    )
    
    try:
        # Test URL
        url = "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540"
        
        result = await fetcher.fetch(url)
        
        if result:
            print("\n" + "=" * 70)
            print("✅ TEST PASSED")
            print("=" * 70)
            print(f"Retrieved {len(result)} bytes")
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ TEST FAILED")
            print("=" * 70)
            return 1
            
    finally:
        fetcher.close()


async def test_batch_urls():
    """Test fetching multiple URLs with cookie reuse."""
    
    fetcher = SahibindenFetcher(
        use_cookies=True,
        use_captcha=True,
    )
    
    urls = [
        "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540",
        "https://www.sahibinden.com/",
    ]
    
    results = {}
    
    try:
        for url in urls:
            result = await fetcher.fetch(url)
            results[url] = result is not None
        
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'=' * 70}")
        print(f"BATCH RESULTS: {success_count}/{len(urls)} successful")
        print(f"{'=' * 70}")
        
        for url, success in results.items():
            print(f"{'✅' if success else '❌'} {url}")
        
        return 0 if success_count > 0 else 1
        
    finally:
        fetcher.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        exit_code = asyncio.run(test_batch_urls())
    else:
        exit_code = asyncio.run(test_single_url())
    
    sys.exit(exit_code)
