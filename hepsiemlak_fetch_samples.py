#!/usr/bin/env python3
"""
Fetch a small sample of Hepsiemlak listing pages and save HTML for parsing.
Reads from data/urls_hepsiemlak.txt.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

URLS_PATH = Path("/Users/mustafaaksoz/Bot/data/urls_hepsiemlak.txt")
OUT_DIR = Path("/Users/mustafaaksoz/Bot/data/raw_html/hepsiemlak")
SAMPLE_COUNT = 5


def slugify(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").replace("/", "_")


async def main():
    if not URLS_PATH.exists():
        print("No URLs file found. Run: python hepsiemlak_collect_urls.py")
        return

    urls = [u.strip() for u in URLS_PATH.read_text(encoding="utf-8").splitlines() if u.strip()]
    urls = urls[:SAMPLE_COUNT]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

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

        for url in urls:
            print(f"Fetching: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            file_path = OUT_DIR / f"{slugify(url)}.html"
            file_path.write_text(html, encoding="utf-8")
            print(f"Saved: {file_path.name}")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
