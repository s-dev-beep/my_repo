#!/usr/bin/env python3
"""
Open a Hepsiemlak listing and reveal phone number by clicking the button.
"""

import asyncio
import re
import sys
from playwright.async_api import async_playwright

DEFAULT_URL = "https://www.hepsiemlak.com/mugla-ortaca-cayli-satilik/daire/142651-248"

PHONE_RE = re.compile(r"\+?90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}")


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    if url.strip().upper() == "PASTE_LISTING_URL_HERE" or not url.startswith("http"):
        print("❌ Invalid URL provided.")
        print("Usage:")
        print("  /Users/mustafaaksoz/Bot/.venv/bin/python /Users/mustafaaksoz/Bot/hepsiemlak_reveal_phone.py ")
        print("  \"https://www.hepsiemlak.com/mugla-ortaca-cayli-satilik/daire/142651-248\"")
        print("\nTip: You can run without arguments to use the default example URL.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            viewport={"width": 1365, "height": 900},
            extra_http_headers={
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        )
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Click phone reveal button
        button = page.get_by_role("button", name=re.compile("Telefon Numarasını Göster", re.I))
        if await button.count() == 0:
            # Fallback: text-based selector
            button = page.locator("text=Telefon Numarasını Göster")

        if await button.count() > 0:
            await button.first.click()
            await page.wait_for_timeout(3000)
        else:
            print("❌ Phone reveal button not found")

        content = await page.content()
        match = PHONE_RE.search(content)

        print("=" * 70)
        print("HEPSIEMLAK PHONE REVEAL")
        print("=" * 70)
        print(f"URL: {url}")
        if match:
            print(f"Phone: {match.group(0)}")
        else:
            print("Phone: NOT FOUND")

        print("\nBrowser stays open for 20 seconds...")
        await page.wait_for_timeout(20000)

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
