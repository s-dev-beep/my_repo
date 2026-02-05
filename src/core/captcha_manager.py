"""
CAPTCHA solving integration for Cloudflare challenges.
Supports multiple services: 2Captcha, Anti-Captcha, CapSolver.
"""

import os
import time
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class CaptchaSolver(ABC):
    """Abstract base for CAPTCHA solving services."""
    
    @abstractmethod
    async def solve_cloudflare(self, sitekey: str, url: str) -> Optional[str]:
        """Solve Cloudflare CAPTCHA, return token or None if failed."""
        pass


class TwoCaptchaSolver(CaptchaSolver):
    """2Captcha.com integration for Cloudflare CAPTCHA solving."""
    
    BASE_URL = "http://2captcha.com"
    
    def __init__(self, api_key: str):
        """Initialize with 2Captcha API key."""
        self.api_key = api_key
        self.timeout = 180  # 3 minutes timeout
        
    async def solve_cloudflare(self, sitekey: str, url: str) -> Optional[str]:
        """
        Solve Cloudflare CAPTCHA using 2Captcha.
        
        Args:
            sitekey: Cloudflare sitekey
            url: URL being accessed
            
        Returns:
            Token string or None if failed
        """
        print(f"🤖 Sending CAPTCHA to 2Captcha service...")
        
        # Submit CAPTCHA
        submit_data = {
            'key': self.api_key,
            'method': 'cloudflare',
            'sitekey': sitekey,
            'pageurl': url,
            'json': 1,
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/captcha",
                data=submit_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') != 1:
                print(f"❌ CAPTCHA submission failed: {result.get('error_text')}")
                return None
            
            captcha_id = result.get('captcha_id')
            print(f"⏳ CAPTCHA ID: {captcha_id}, waiting for solution...")
            
            # Poll for result
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                time.sleep(5)  # Check every 5 seconds
                
                result_data = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1,
                }
                
                result = requests.get(
                    f"{self.BASE_URL}/api/res",
                    params=result_data,
                    timeout=10
                ).json()
                
                if result.get('status') == 1:
                    token = result.get('request')
                    print(f"✅ CAPTCHA solved! Token: {token[:20]}...")
                    return token
                elif result.get('status') == 0:
                    if result.get('request') == 'CAPCHA_NOT_READY':
                        continue  # Still processing
                    else:
                        print(f"❌ Error: {result.get('request')}")
                        return None
            
            print(f"❌ CAPTCHA timeout after {self.timeout}s")
            return None
            
        except Exception as e:
            print(f"❌ CAPTCHA service error: {e}")
            return None


class AntiCaptchaSolver(CaptchaSolver):
    """Anti-Captcha.com integration."""
    
    BASE_URL = "https://api.anti-captcha.com"
    
    def __init__(self, api_key: str):
        """Initialize with Anti-Captcha API key."""
        self.api_key = api_key
        self.timeout = 180
        
    async def solve_cloudflare(self, sitekey: str, url: str) -> Optional[str]:
        """Solve Cloudflare CAPTCHA using Anti-Captcha."""
        print(f"🤖 Sending CAPTCHA to Anti-Captcha service...")
        
        # Create task
        task_data = {
            'clientKey': self.api_key,
            'task': {
                'type': 'NoCaptchaTaskProxyless',
                'websiteURL': url,
                'websiteKey': sitekey,
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/createTask",
                json=task_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('errorId') != 0:
                print(f"❌ Task creation failed: {result.get('errorDescription')}")
                return None
            
            task_id = result.get('taskId')
            print(f"⏳ Task ID: {task_id}, waiting for solution...")
            
            # Poll for result
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                time.sleep(5)
                
                result_data = {
                    'clientKey': self.api_key,
                    'taskId': task_id,
                }
                
                result = requests.post(
                    f"{self.BASE_URL}/getTaskResult",
                    json=result_data,
                    timeout=10
                ).json()
                
                if result.get('ready'):
                    token = result.get('solution', {}).get('gRecaptchaResponse')
                    if token:
                        print(f"✅ CAPTCHA solved!")
                        return token
                    else:
                        print(f"❌ No token in solution")
                        return None
            
            print(f"❌ CAPTCHA timeout after {self.timeout}s")
            return None
            
        except Exception as e:
            print(f"❌ CAPTCHA service error: {e}")
            return None


class CaptchaManager:
    """High-level CAPTCHA management with multiple solver support."""
    
    def __init__(self, provider: str = "2captcha", api_key: Optional[str] = None):
        """
        Initialize CAPTCHA manager.
        
        Args:
            provider: 'twocaptcha', 'anticaptcha', or 'capsolver'
            api_key: API key for the service (or read from env var)
        """
        self.provider = provider.lower()
        
        # Get API key from parameter or environment
        if api_key:
            self.api_key = api_key
        else:
            env_key = {
                'twocaptcha': 'CAPTCHA_2CAPTCHA_KEY',
                'anticaptcha': 'CAPTCHA_ANTICAPTCHA_KEY',
                'capsolver': 'CAPTCHA_CAPSOLVER_KEY',
            }.get(self.provider)
            
            self.api_key = os.getenv(env_key)
        
        if not self.api_key:
            print(f"⚠️ Warning: No API key found for {provider}")
            self.solver = None
        else:
            self.solver = self._init_solver()
    
    def _init_solver(self) -> Optional[CaptchaSolver]:
        """Initialize the appropriate solver."""
        if self.provider == 'twocaptcha':
            return TwoCaptchaSolver(self.api_key)
        elif self.provider == 'anticaptcha':
            return AntiCaptchaSolver(self.api_key)
        else:
            print(f"❌ Unknown provider: {self.provider}")
            return None
    
    async def solve_cloudflare(self, sitekey: str, url: str) -> Optional[str]:
        """
        Solve Cloudflare CAPTCHA.
        
        Args:
            sitekey: Cloudflare sitekey from page
            url: Current page URL
            
        Returns:
            Token string or None if failed
        """
        if not self.solver:
            print("❌ CAPTCHA solver not initialized")
            return None
        
        try:
            return await self.solver.solve_cloudflare(sitekey, url)
        except Exception as e:
            print(f"❌ CAPTCHA solving error: {e}")
            return None
    
    def get_balance_2captcha(self) -> Optional[float]:
        """Get 2Captcha account balance."""
        if self.provider != 'twocaptcha':
            return None
        
        try:
            response = requests.get(
                "http://2captcha.com/api/user",
                params={'apikey': self.api_key, 'action': 'getbalance'},
                timeout=5
            )
            if response.status_code == 200:
                return float(response.text)
        except Exception as e:
            print(f"Error getting balance: {e}")
        
        return None
