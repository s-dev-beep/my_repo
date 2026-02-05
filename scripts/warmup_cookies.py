#!/usr/bin/env python3
"""Interactive cookie warm-up using Playwright.

Opens a browser so you can solve CAPTCHA/login, then saves cookies under a label.
"""

from __future__ import annotations

import argparse
from typing import List, Dict, Any

from src.core.cookie_manager import CookieManager


def _playwright_to_selenium(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted = []
    for c in cookies:
        converted.append(
            {
                "name": c.get("name"),
                "value": c.get("value"),
                "domain": c.get("domain"),
                "path": c.get("path", "/"),
                "expiry": c.get("expires"),
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", False),
                "sameSite": c.get("sameSite", "Lax"),
            }
        )
    return converted


def main() -> int:
    parser = argparse.ArgumentParser(description="Warm up cookies and save with a label")
    parser.add_argument("--url", required=True, help="URL to open for warm-up")
    parser.add_argument("--label", required=True, help="Cookie label (e.g., sahibinden.com_real-estate)")
    parser.add_argument("--category", default=None, help="Optional category (e.g., real-estate, araba)")
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Playwright is required for warm-up. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium\n"
        ) from e

    manager = CookieManager()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        input("Solve CAPTCHA/login, then press Enter to save cookies...")
        cookies = context.cookies()
        selenium_cookies = _playwright_to_selenium(cookies)
        manager.jar.save_cookies(domain=page.url.split("/")[2], selenium_cookies=selenium_cookies, label=args.label, category=args.category)
        browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
