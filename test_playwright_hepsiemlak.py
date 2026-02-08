#!/usr/bin/env python3
"""
Quick access test for hepsiemlak.com using Playwright.
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            viewport={"width": 1365, "height": 900},
        )
        page = await context.new_page()

        url = "https://www.hepsiemlak.com/"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        title = await page.title()
        current_url = page.url
        content = await page.content()

        has_cf = "cloudflare" in content.lower() or "just a moment" in content.lower()
        has_captcha = "captcha" in content.lower()

        print("=" * 70)
        print("HEPSIEMLAK ACCESS TEST")
        print("=" * 70)
        print(f"Title: {title}")
        print(f"URL:   {current_url}")
        print(f"Cloudflare detected: {has_cf}")
        print(f"CAPTCHA detected: {has_captcha}")

        print("\nBrowser stays open for 20 seconds...")
        await page.wait_for_timeout(20000)

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
