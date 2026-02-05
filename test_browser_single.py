#!/usr/bin/env python3
"""Quick browser test - test ONE URL like a real user would access it.

This uses Playwright (real Chromium) instead of HTTP client.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Phone and office regex
PHONE_REGEX = re.compile(
    r"(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})|"
    r"(0\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2})"
)

def test_with_browser(url: str) -> dict:
    """Test URL with real Chromium browser like a user would."""
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n❌ Playwright not installed!")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return None
    
    print(f"\n🌐 Opening in Chromium: {url}")
    print("=" * 80)
    
    result = {
        "url": url,
        "status": None,
        "title": None,
        "phone_found": False,
        "page_content_length": 0,
        "block_detected": False,
        "screenshot": None,
    }
    
    with sync_playwright() as p:
        # Launch real Chromium (like your browser)
        print("📱 Launching Chromium...")
        browser = p.chromium.launch(
            headless=False,  # Show the window so you can see
            args=["--disable-blink-features=AutomationControlled"],
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Hide webdriver detection
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
        )
        
        try:
            print("🔗 Loading page...")
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if response:
                result["status"] = response.status
                print(f"✓ Status: {response.status}")
            
            # Get page title
            result["title"] = page.title()
            print(f"✓ Title: {result['title']}")
            
            # Get page content
            text = page.inner_text("body")
            result["page_content_length"] = len(text)
            
            # Look for phone number
            if PHONE_REGEX.search(text):
                result["phone_found"] = True
                print(f"✓ Phone number found in page")
            else:
                print(f"✗ No phone found")
            
            # Check for blocks
            text_lower = text.lower()
            if any(x in text_lower for x in ["captcha", "robot", "erişim", "blocked"]):
                result["block_detected"] = True
                print(f"⚠️  Block detected in page content")
            
            # Take screenshot
            screenshot_file = Path("reports/browser_test_screenshot.png")
            screenshot_file.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_file), full_page=False)
            result["screenshot"] = str(screenshot_file)
            print(f"📸 Screenshot saved: {screenshot_file}")
            
            # Show summary
            print("=" * 80)
            print(f"Content length: {result['page_content_length']} bytes")
            print(f"Block detected:  {result['block_detected']}")
            print(f"Phone found:     {result['phone_found']}")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            result["error"] = str(e)
        
        finally:
            browser.close()
    
    return result


if __name__ == "__main__":
    # Use first URL from pilot file
    pilot_file = Path("examples/pilot_urls.txt")
    if not pilot_file.exists():
        print(f"❌ {pilot_file} not found")
        sys.exit(1)
    
    with open(pilot_file) as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("❌ No URLs in pilot file")
        sys.exit(1)
    
    test_url = urls[0]
    print(f"\n🧪 Browser Feasibility Test")
    print(f"URL: {test_url}\n")
    
    result = test_with_browser(test_url)
    
    if result:
        # Save report
        report_file = Path("reports/browser_test.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "result": result,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        print(f"\n📋 Report saved: {report_file}")
        
        # Exit code based on result
        if result.get("block_detected"):
            print("\n❌ Browser test: BLOCKED")
            sys.exit(2)
        elif result.get("phone_found"):
            print("\n✅ Browser test: SUCCESS - Phone found!")
            sys.exit(0)
        else:
            print("\n⚠️  Browser test: LOADED but no phone found")
            sys.exit(1)
