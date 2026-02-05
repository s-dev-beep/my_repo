#!/usr/bin/env python3
"""
Export storage state (cookies/localStorage) from a real Chrome session
started with remote debugging. This avoids automation detection.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

STORAGE_PATH = Path("/Users/mustafaaksoz/Bot/data/cookies/sahibinden_storage.json")
CDP_URL = "http://127.0.0.1:9222"


async def main():
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("EXPORT CHROME STORAGE STATE")
    print("=" * 70)
    print("\nMake sure Chrome is running with remote debugging:")
    print("open -na \"Google Chrome\" --args --remote-debugging-port=9222 --user-data-dir=/Users/mustafaaksoz/Bot/data/chrome-remote")
    print("\nThen open https://www.sahibinden.com/ and finish verification.")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)

        # Reuse existing context
        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = await browser.new_context()

        await context.storage_state(path=str(STORAGE_PATH))
        print(f"\n✅ Saved storage to: {STORAGE_PATH}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
