"""
Browser cookie management for persisting Cloudflare authentication.
Allows solving CAPTCHA once and reusing session across multiple requests.
"""

import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta


class Cookie:
    """Represents a browser cookie."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize from Selenium cookie dict."""
        self.name = data.get('name')
        self.value = data.get('value')
        self.domain = data.get('domain')
        self.path = data.get('path', '/')
        self.expires = data.get('expiry')  # Unix timestamp
        self.http_only = data.get('httpOnly', False)
        self.secure = data.get('secure', False)
        self.same_site = data.get('sameSite', 'Lax')
    
    def is_expired(self) -> bool:
        """Check if cookie is expired."""
        if not self.expires:
            return False  # Session cookie, assume not expired
        return self.expires < time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        return {
            'name': self.name,
            'value': self.value,
            'domain': self.domain,
            'path': self.path,
            'expires': self.expires,
            'httpOnly': self.http_only,
            'secure': self.secure,
            'sameSite': self.same_site,
        }


class CookieJar:
    """Manages persistent browser cookies."""
    
    def __init__(self, storage_dir: str = "/Users/mustafaaksoz/Bot/data/cookies"):
        """Initialize cookie jar."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def get_cookie_file(self, domain: str) -> Path:
        """Get path for domain's cookie file."""
        safe_domain = domain.replace('/', '_').replace(':', '_')
        return self.storage_dir / f"{safe_domain}.json"
    
    def save_cookies(self, domain: str, selenium_cookies: List[Dict]) -> int:
        """
        Save Selenium cookies to disk.
        
        Args:
            domain: Domain to save for (e.g., 'sahibinden.com')
            selenium_cookies: List of dicts from driver.get_cookies()
            
        Returns:
            Number of cookies saved
        """
        cookies = [Cookie(c) for c in selenium_cookies]
        
        cookie_file = self.get_cookie_file(domain)
        
        with open(cookie_file, 'w') as f:
            json.dump([c.to_dict() for c in cookies], f, indent=2)
        
        print(f"✅ Saved {len(cookies)} cookies to {cookie_file.name}")
        return len(cookies)
    
    def load_cookies(self, domain: str) -> Optional[List[Dict]]:
        """
        Load cookies from disk.
        
        Args:
            domain: Domain to load for
            
        Returns:
            List of valid (non-expired) cookies, or None if file doesn't exist
        """
        cookie_file = self.get_cookie_file(domain)
        
        if not cookie_file.exists():
            print(f"⚠️ No cookies found for {domain}")
            return None
        
        try:
            with open(cookie_file, 'r') as f:
                cookie_dicts = json.load(f)
            
            cookies = [Cookie(c) for c in cookie_dicts]
            
            # Filter out expired cookies
            valid_cookies = [c for c in cookies if not c.is_expired()]
            expired = len(cookies) - len(valid_cookies)
            
            if expired > 0:
                print(f"⚠️ Filtered out {expired} expired cookies")
            
            print(f"✅ Loaded {len(valid_cookies)} valid cookies from {cookie_file.name}")
            
            return [c.to_dict() for c in valid_cookies] if valid_cookies else None
            
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return None
    
    def apply_cookies_to_driver(self, driver, domain: str) -> bool:
        """
        Apply stored cookies to Selenium driver.
        
        Args:
            driver: Selenium WebDriver
            domain: Domain to load cookies for
            
        Returns:
            True if cookies were applied, False otherwise
        """
        cookies = self.load_cookies(domain)
        if not cookies:
            return False
        
        try:
            # Must visit domain first to set cookies
            driver.get(f"https://{domain}")
            time.sleep(1)
            
            for cookie in cookies:
                try:
                    # Remove certain fields that Selenium doesn't accept
                    cookie_to_add = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie['path'],
                    }
                    
                    if cookie.get('expires'):
                        cookie_to_add['expiry'] = cookie['expires']
                    if cookie.get('secure'):
                        cookie_to_add['secure'] = cookie['secure']
                    
                    driver.add_cookie(cookie_to_add)
                except Exception as e:
                    # Some cookies may fail, continue with others
                    pass
            
            print(f"✅ Applied cookies to driver")
            return True
            
        except Exception as e:
            print(f"❌ Error applying cookies: {e}")
            return False
    
    def clear_cookies(self, domain: str) -> bool:
        """Clear stored cookies for a domain."""
        cookie_file = self.get_cookie_file(domain)
        
        try:
            if cookie_file.exists():
                os.remove(cookie_file)
                print(f"✅ Cleared cookies for {domain}")
                return True
            else:
                print(f"⚠️ No cookies found for {domain}")
                return False
        except Exception as e:
            print(f"❌ Error clearing cookies: {e}")
            return False
    
    def get_cookies_age(self, domain: str) -> Optional[str]:
        """Get age of stored cookies."""
        cookie_file = self.get_cookie_file(domain)
        
        if not cookie_file.exists():
            return None
        
        mtime = os.path.getmtime(cookie_file)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        
        if age.days > 0:
            return f"{age.days} days {age.seconds // 3600} hours"
        else:
            return f"{age.seconds // 3600} hours {(age.seconds % 3600) // 60} minutes"
    
    def cookies_exist_and_valid(self, domain: str) -> bool:
        """Check if valid cookies exist for domain."""
        cookies = self.load_cookies(domain)
        return cookies is not None and len(cookies) > 0


class CookieManager:
    """High-level cookie management."""
    
    def __init__(self):
        """Initialize cookie manager."""
        self.jar = CookieJar()
    
    def save_from_driver(self, driver, domain: str) -> bool:
        """Save all cookies from browser driver."""
        try:
            cookies = driver.get_cookies()
            self.jar.save_cookies(domain, cookies)
            return True
        except Exception as e:
            print(f"❌ Error saving cookies from driver: {e}")
            return False
    
    def load_to_driver(self, driver, domain: str) -> bool:
        """Load cookies into browser driver."""
        return self.jar.apply_cookies_to_driver(driver, domain)
    
    def status(self, domain: str) -> Dict[str, Any]:
        """Get status of cookies for a domain."""
        exists = self.jar.get_cookie_file(domain).exists()
        age = self.jar.get_cookies_age(domain)
        valid = self.jar.cookies_exist_and_valid(domain)
        
        return {
            'exists': exists,
            'valid': valid,
            'age': age,
            'file': str(self.jar.get_cookie_file(domain)),
        }
