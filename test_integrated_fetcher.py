"""
Quick test of integrated cookie + CAPTCHA fetcher.
"""

import sys
import asyncio

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.sahibinden_fetcher import SahibindenFetcher


async def main():
    print("=" * 70)
    print("SAHIBINDEN INTEGRATED FETCHER TEST")
    print("Cookie Reuse + CAPTCHA Service Support")
    print("=" * 70)
    
    fetcher = SahibindenFetcher(
        use_cookies=True,      # Try cached cookies first (free)
        use_captcha=True,      # Fall back to CAPTCHA service
    )
    
    try:
        # Test URL
        url = "https://www.sahibinden.com/"
        
        print("\n📋 Test Plan:")
        print("1. Check for cached cookies (free)")
        print("2. If valid cookies exist → Use them (no cost)")
        print("3. If no cookies → Can use CAPTCHA service ($0.001)")
        print("4. After successful fetch → Save cookies for next time")
        print()
        
        result = await fetcher.fetch(url)
        
        if result:
            print("\n✅ SUCCESS: Page fetched successfully!")
            print(f"   Content size: {len(result)} bytes")
            
            # Show cookie status
            status = fetcher.cookie_manager.status("www.sahibinden.com")
            print(f"\n💾 Cookie Status:")
            print(f"   File: {status['file']}")
            print(f"   Valid: {status['valid']}")
            if status['age']:
                print(f"   Age: {status['age']}")
            
            print("\n🎯 Next runs will:")
            if status['valid']:
                print("   → Reuse these cookies automatically (FREE)")
                print("   → May not need CAPTCHA solving")
            
            return 0
        else:
            print("\n⚠️ Fetch failed - CAPTCHA solving required")
            print("\nTo enable automatic CAPTCHA solving:")
            print("1. Sign up at 2Captcha.com (~$3 minimum)")
            print("2. Export your API key:")
            print("   export CAPTCHA_2CAPTCHA_KEY='your_key_here'")
            print("3. Run this test again")
            print("\nOr: Manually solve CAPTCHA when browser opens")
            
            return 1
    
    finally:
        fetcher.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
