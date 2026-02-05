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
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize cookie jar."""
        base_dir = storage_dir or os.getenv("BOT_DATA_DIR") or str(Path("data"))
        self.storage_dir = Path(base_dir) / "cookies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def get_cookie_file(self, label: str) -> Path:
        """Get path for a label-specific cookie file."""
        safe_label = label.replace('/', '_').replace(':', '_').replace(' ', '_')
        return self.storage_dir / f"{safe_label}.json"
    
    def save_cookies(self, domain: str, selenium_cookies: List[Dict], label: Optional[str] = None, category: Optional[str] = None) -> int:
        """
        Save Selenium cookies to disk.
        
        Args:
            domain: Domain to save for (e.g., 'sahibinden.com')
            selenium_cookies: List of dicts from driver.get_cookies()
            label: Label for cookie set (e.g., 'sahibinden.com_real-estate')
            category: Content category (e.g., 'real-estate', 'araba')
            
        Returns:
            Number of cookies saved
        """
        label = label or domain
        cookies = [Cookie(c) for c in selenium_cookies]
        
        cookie_file = self.get_cookie_file(label)
        
        payload = {
            "label": label,
            "domain": domain,
            "category": category,
            "updated_at": datetime.utcnow().isoformat(),
            "cookies": [c.to_dict() for c in cookies],
        }
        
        with open(cookie_file, 'w') as f:
            json.dump(payload, f, indent=2)
        
        print(f"✅ Saved {len(cookies)} cookies to {cookie_file.name} (label={label})")
        return len(cookies)
    
    def load_cookies(self, label: str) -> Optional[List[Dict]]:
        """
        Load cookies from disk.
        
        Args:
            label: Label to load for
            
        Returns:
            List of valid (non-expired) cookies, or None if file doesn't exist
        """
        cookie_file = self.get_cookie_file(label)
        
        if not cookie_file.exists():
            print(f"⚠️ No cookies found for {label}")
            return None
        
        try:
            with open(cookie_file, 'r') as f:
                payload = json.load(f)
            
            cookie_dicts = payload.get("cookies", []) if isinstance(payload, dict) else payload
            cookies = [Cookie(c) for c in cookie_dicts]
            
            # Filter out expired cookies
            valid_cookies = [c for c in cookies if not c.is_expired()]
            expired = len(cookies) - len(valid_cookies)
            
            if expired > 0:
                print(f"⚠️ Filtered out {expired} expired cookies")
            
            print(f"✅ Loaded {len(valid_cookies)} valid cookies from {cookie_file.name}")
            
            if not valid_cookies:
                try:
                    cookie_file.unlink(missing_ok=True)
                    print(f"🧹 Removed stale cookie file {cookie_file.name}")
                except Exception:
                    pass
                return None

            return [c.to_dict() for c in valid_cookies]
            
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return None
    
    def apply_cookies_to_driver(self, driver, domain: str, label: Optional[str] = None) -> bool:
        """
        Apply stored cookies to Selenium driver.
        
        Args:
            driver: Selenium WebDriver
            domain: Domain to load cookies for
            label: Label to load cookies for (defaults to domain)
            
        Returns:
            True if cookies were applied, False otherwise
        """
        label = label or domain
        cookies = self.load_cookies(label)
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
            
            print(f"✅ Applied cookies to driver (label={label})")
            return True
            
        except Exception as e:
            print(f"❌ Error applying cookies: {e}")
            return False
    
    def clear_cookies(self, label: str) -> bool:
        """Clear stored cookies for a label."""
        cookie_file = self.get_cookie_file(label)
        
        try:
            if cookie_file.exists():
                os.remove(cookie_file)
                print(f"✅ Cleared cookies for {label}")
                return True
            else:
                print(f"⚠️ No cookies found for {label}")
                return False
        except Exception as e:
            print(f"❌ Error clearing cookies: {e}")
            return False
    
    def get_cookies_age(self, label: str) -> Optional[str]:
        """Get age of stored cookies."""
        cookie_file = self.get_cookie_file(label)
        
        if not cookie_file.exists():
            return None
        
        mtime = os.path.getmtime(cookie_file)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        
        if age.days > 0:
            return f"{age.days} days {age.seconds // 3600} hours"
        else:
            return f"{age.seconds // 3600} hours {(age.seconds % 3600) // 60} minutes"
    
    def cookies_exist_and_valid(self, label: str) -> bool:
        """Check if valid cookies exist for label."""
        cookies = self.load_cookies(label)
        return cookies is not None and len(cookies) > 0


class CookieManager:
    """High-level cookie management."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize cookie manager."""
        self.jar = CookieJar(storage_dir=storage_dir)
    
    def save_from_driver(self, driver, domain: str, label: Optional[str] = None, category: Optional[str] = None) -> bool:
        """Save all cookies from browser driver."""
        try:
            cookies = driver.get_cookies()
            self.jar.save_cookies(domain, cookies, label=label, category=category)
            return True
        except Exception as e:
            print(f"❌ Error saving cookies from driver: {e}")
            return False
    
    def load_to_driver(self, driver, domain: str, label: Optional[str] = None) -> bool:
        """Load cookies into browser driver."""
        return self.jar.apply_cookies_to_driver(driver, domain, label=label)
    
    def status(self, label: str) -> Dict[str, Any]:
        """Get status of cookies for a label."""
        exists = self.jar.get_cookie_file(label).exists()
        age = self.jar.get_cookies_age(label)
        valid = self.jar.cookies_exist_and_valid(label)
        
        return {
            'exists': exists,
            'valid': valid,
            'age': age,
            'file': str(self.jar.get_cookie_file(label)),
        }
