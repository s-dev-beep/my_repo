#!/usr/bin/env python3
"""
Collect listing URLs from Hepsiemlak category pages (satilik/kiralik).
Saves to data/urls_hepsiemlak.txt
"""

import asyncio
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright

DEFAULT_URL = "https://www.hepsiemlak.com/satilik"
OUTPUT_PATH = Path("/Users/mustafaaksoz/Bot/data/urls_hepsiemlak.txt")


async def collect_urls(start_url: str, scroll_times: int = 8) -> list[str]:
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

        await page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)

        # Try to wait for listing anchors to appear
        try:
            await page.wait_for_selector('a[href*="/ilan/"]', timeout=10000)
        except Exception:
            pass

        for _ in range(scroll_times):
            await page.mouse.wheel(0, 2400)
            await page.wait_for_timeout(2000)

        hrefs = await page.evaluate(
            """
            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
            """
        )

        html = await page.content()

        await context.close()
        await browser.close()

    urls = []
    for href in hrefs:
        if not href:
            continue
        if "hepsiemlak.com" not in href:
            continue
        if "/ilan/" in href:
            urls.append(href.split("?")[0])

    # Fallback: regex extraction from HTML if no anchors found
    if not urls:
        matches = re.findall(r"https?://www\.hepsiemlak\.com/ilan/[^\"'>\s]+", html)
        urls.extend([m.split("?")[0] for m in matches])

    # Deduplicate while preserving order
    seen = set()
    result = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            result.append(u)

    return result


async def main():
    start_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    print(f"Collecting from: {start_url}")
    urls = await collect_urls(start_url)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(urls), encoding="utf-8")

    print(f"Saved {len(urls)} URLs to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
