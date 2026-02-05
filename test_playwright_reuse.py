#!/usr/bin/env python3
"""
Test Playwright storage reuse (no CAPTCHA expected if storage is valid).
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).resolve().parent
STORAGE_PATH = PROJECT_ROOT / "data" / "cookies" / "sahibinden_storage.json"


async def main():
    if not STORAGE_PATH.exists():
        print("❌ Storage file not found.")
        print("Run: python save_playwright_storage.py")
        return 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(STORAGE_PATH))
        page = await context.new_page()

        test_urls = [
            "https://www.sahibinden.com/",
            "https://www.sahibinden.com/kategori/emlak-konut",
        ]

        print("=" * 70)
        print("PLAYWRIGHT REUSE HEALTH CHECK")
        print("=" * 70)

        all_ok = True
        for url in test_urls:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            title = await page.title()
            content = await page.content()
            has_captcha = "Bir dakika" in content or "captcha" in content.lower()

            print(f"URL:   {url}")
            print(f"Title: {title}")
            print(f"CAPTCHA detected: {has_captcha}")
            print("-" * 70)

            if has_captcha:
                all_ok = False

        if all_ok:
            print("✅ Cookie health check PASSED")
        else:
            print("❌ Cookie health check FAILED (CAPTCHA detected)")

        print("\nBrowser stays open for 20 seconds...")
        await page.wait_for_timeout(20000)

        await context.close()
        await browser.close()

        return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
