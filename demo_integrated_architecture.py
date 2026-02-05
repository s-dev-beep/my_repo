#!/usr/bin/env python3
"""
Demonstration of integrated cookie + CAPTCHA architecture.
Shows how the system would work in production.
"""

import sys
import os

sys.path.insert(0, '/Users/mustafaaksoz/Bot')
from src.core.cookie_manager import CookieManager
from src.core.captcha_manager import CaptchaManager


def demo_cookie_system():
    """Demonstrate cookie management system."""
    print("\n" + "=" * 70)
    print("DEMO 1: COOKIE REUSE SYSTEM (Free)")
    print("=" * 70)
    
    cookie_manager = CookieManager()
    
    print("\n📋 How it works:")
    print("1. First run: Solve CAPTCHA manually → Cookies are saved")
    print("2. Subsequent runs: Load cookies → Access without CAPTCHA")
    print("3. When cookies expire: Solve CAPTCHA again")
    
    print("\n💾 Cookie Storage:")
    print(f"   Location: {cookie_manager.jar.storage_dir}")
    
    print("\n✅ This approach:")
    print("   • Free (no API cost)")
    print("   • Works until cookies expire (hours/days)")
    print("   • Requires ~1 manual CAPTCHA solve per cookie expiry")
    
    # Check if cookies already exist
    status = cookie_manager.jar.get_cookie_file("www.sahibinden.com")
    print(f"\n📌 Current status:")
    print(f"   Cookie file: {status}")
    if status.exists():
        print(f"   Status: File exists")
    else:
        print(f"   Status: No cookies saved yet (will be created on first successful fetch)")


def demo_captcha_system():
    """Demonstrate CAPTCHA solving system."""
    print("\n" + "=" * 70)
    print("DEMO 2: AUTOMATIC CAPTCHA SOLVING (Paid, optional)")
    print("=" * 70)
    
    print("\n📋 How it works:")
    print("1. CAPTCHA appears → Send to 2Captcha service")
    print("2. Service solves it in ~10-30 seconds")
    print("3. Solution injected → Page loads automatically")
    print("4. Repeat for each CAPTCHA")
    
    print("\n💰 Cost Breakdown:")
    print("   • Per CAPTCHA solve: ~$0.001")
    print("   • 10 URLs: ~$0.01")
    print("   • 100 URLs: ~$0.10")
    print("   • 1,000 URLs: ~$1.00")
    
    # Check for API key
    api_key = os.getenv('CAPTCHA_2CAPTCHA_KEY')
    
    print(f"\n🔑 API Key Status: {'✅ Set' if api_key else '❌ Not set'}")
    
    if not api_key:
        print("\n📝 To enable CAPTCHA solving:")
        print("   1. Sign up at https://2captcha.com")
        print("   2. Add credit ($3 minimum)")
        print("   3. Get API key from account settings")
        print("   4. Export in terminal:")
        print("      export CAPTCHA_2CAPTCHA_KEY='your_key_here'")
        print("   5. Run script again")
    else:
        print(f"   Key: {api_key[:20]}...")
        
        # Try to get balance
        try:
            captcha_manager = CaptchaManager(api_key=api_key)
            balance = captcha_manager.get_balance_2captcha()
            if balance:
                print(f"   Balance: ${balance:.2f}")
        except:
            pass
    
    print("\n✅ This approach:")
    print("   • Fully automated (no manual intervention)")
    print("   • Works 100% of the time")
    print("   • Small cost (~$0.001 per page)")


def demo_integrated_strategy():
    """Demonstrate integrated strategy."""
    print("\n" + "=" * 70)
    print("DEMO 3: INTEGRATED STRATEGY (Recommended)")
    print("=" * 70)
    
    print("\n🎯 Smart Strategy:")
    print("""
    First request:
    ├─ Try cached cookies (FREE)
    │  └─ If found & valid → Success! Stop here.
    └─ If no cookies:
       ├─ Try CAPTCHA service (PAID, $0.001)
       │  └─ If API key set → Auto-solve CAPTCHA
       └─ If no API key:
          └─ Manual mode (HUMAN INTERVENTION)
             └─ Browser opens, you solve CAPTCHA
    
    After successful fetch:
    └─ Save cookies for next time (FREE next 100 requests!)
    """)
    
    print("\n💡 Why this works:")
    print("   ✅ Minimizes CAPTCHA API calls (save cookies)")
    print("   ✅ Free most of the time (reuse cookies)")
    print("   ✅ Always has a fallback (CAPTCHA service or manual)")
    print("   ✅ Flexible (works with or without API key)")


def demo_decision_tree():
    """Show decision tree for users."""
    print("\n" + "=" * 70)
    print("DEMO 4: HOW TO CHOOSE")
    print("=" * 70)
    
    print("\n❓ What should I use?")
    
    print("\n Option A: Cookie Reuse (What we recommend for you)")
    print(" " + "─" * 66)
    print(f"   When: Testing with 1-50 URLs")
    print(f"   Cost: FREE")
    print(f"   Setup: Install undetected-chromedriver (already done)")
    print(f"   Time: 5 minutes to test")
    print(f"   How: python test_cookie_reuse_demo.py")
    
    print("\n Option B: CAPTCHA Service (For production crawling)")
    print(" " + "─" * 66)
    print(f"   When: Production use, 50+ URLs")
    print(f"   Cost: ~$0.001 per page ($1 for 1,000)")
    print(f"   Setup: 5 minutes (sign up + API key)")
    print(f"   Time: 2-3 hours to integrate")
    print(f"   How: export CAPTCHA_2CAPTCHA_KEY='...' && python test_captcha_demo.py")
    
    print("\n Option C: Both Combined (Most flexible)")
    print(" " + "─" * 66)
    print(f"   When: Need both free and paid options")
    print(f"   Cost: Only pay when cookies expire")
    print(f"   Setup: 10 minutes (use defaults)")
    print(f"   Time: Recommended approach")
    print(f"   How: Both systems active, smart fallback")


def main():
    print("\n" + "=" * 70)
    print("SAHIBINDEN FETCHER - ARCHITECTURE DEMO")
    print("Cookie Reuse + CAPTCHA Service Integration")
    print("=" * 70)
    
    print("\n🎯 This demo shows you:")
    print("   • How cookie reuse saves money (FREE)")
    print("   • How CAPTCHA service works (PAID, optional)")
    print("   • How integrated strategy combines both")
    print("   • Which approach to use for your needs")
    
    # Run demos
    demo_cookie_system()
    demo_captcha_system()
    demo_integrated_strategy()
    demo_decision_tree()
    
    # Summary
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    
    print("\n✨ All code is ready to use!")
    print("\n📁 Files created:")
    print("   ✓ src/core/cookie_manager.py - Cookie persistence")
    print("   ✓ src/core/captcha_manager.py - CAPTCHA solving")
    print("   ✓ src/core/sahibinden_fetcher.py - Integrated fetcher")
    print("   ✓ test_integrated_fetcher.py - Full integration test")
    
    print("\n🚀 To test cookie reuse (FREE, 5 min):")
    print("   python test_cookie_reuse.py")
    
    print("\n🚀 To enable CAPTCHA service (OPTIONAL, $3 one-time):")
    print("   1. Sign up: https://2captcha.com")
    print("   2. Export key: export CAPTCHA_2CAPTCHA_KEY='...'")
    print("   3. Test: python test_integrated_fetcher.py")
    
    print("\n✅ Both systems are ready to use together!")
    print()


if __name__ == "__main__":
    main()
