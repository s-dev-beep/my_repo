#!/usr/bin/env python3
"""
Save Playwright storage state (cookies + local storage) after manual CAPTCHA.
This avoids undetected_chromedriver crashes on macOS.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "cookies" / "sahibinden_storage.json"
USER_DATA_DIR = PROJECT_ROOT / "data" / "playwright_profile"

WARMUP_URLS = [
    "https://www.sahibinden.com/",
    "https://www.sahibinden.com/kategori/emlak-konut",
    "https://www.sahibinden.com/arama?query=istanbul",
]


async def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PLAYWRIGHT STORAGE SAVE")
    print("=" * 70)
    print("\nSteps:")
    print("1) A browser will open.")
    print("2) Complete Cloudflare verification / CAPTCHA if shown.")
    print("3) Accept cookies on the site if prompted.")
    print("4) Browse normally for 5–10 minutes (search, filter, open listings).")
    print("5) Press ENTER here to save storage when you're ready.")

    async with async_playwright() as p:
        last_error = None

        launch_options = [
            # 1) Real Chrome channel (most human-like)
            {
                "browser_type": p.chromium,
                "channel": "chrome",
                "label": "Chrome channel",
            },
            # 2) Playwright Chromium fallback
            {
                "browser_type": p.chromium,
                "channel": None,
                "label": "Chromium",
            },
        ]

        for attempt, option in enumerate(launch_options, start=1):
            try:
                # Common args to reduce crashes and keep profile stable
                args = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-gpu",
                    "--use-gl=swiftshader",
                ]

                context = await option["browser_type"].launch_persistent_context(
                    user_data_dir=str(USER_DATA_DIR),
                    headless=False,
                    channel=option["channel"],
                    locale="tr-TR",
                    timezone_id="Europe/Istanbul",
                    viewport={"width": 1365, "height": 900},
                    device_scale_factor=1,
                    java_script_enabled=True,
                    accept_downloads=False,
                    args=args,
                )
                page = await context.new_page()
                await page.goto(WARMUP_URLS[0], wait_until="domcontentloaded")

                print("\nWarm-up guide:")
                print("- Spend time on the home page, scroll, and open a listing.")
                input("Press ENTER when you are ready to open the category page... ")
                await page.goto(WARMUP_URLS[1], wait_until="domcontentloaded")

                print("- Browse the category, open at least 2 listings, then go back.")
                input("Press ENTER when you are ready to open a search page... ")
                await page.goto(WARMUP_URLS[2], wait_until="domcontentloaded")

                print("- Use filters, change city, open a listing, then return.")
                input("\nPress ENTER here after the site feels fully accessible... ")

                await context.storage_state(path=str(OUTPUT_PATH))
                print(f"\n✅ Saved storage state to: {OUTPUT_PATH}")

                await context.close()
                return
            except Exception as exc:
                last_error = exc
                print(f"\n⚠️ Browser crashed on attempt {attempt} ({option['label']}): {exc}")
                print("Retrying with a different browser option...")

        raise last_error


if __name__ == "__main__":
    asyncio.run(main())
