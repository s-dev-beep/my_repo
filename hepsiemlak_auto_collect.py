#!/usr/bin/env python3
"""
Automated collector for Hepsiemlak listings.
Extracts: phone, city, district, agent name, office name, listing_url.

Usage:
  /Users/mustafaaksoz/Bot/.venv/bin/python /Users/mustafaaksoz/Bot/hepsiemlak_auto_collect.py \
    /Users/mustafaaksoz/Bot/data/urls_hepsiemlak.txt

Output:
  data/hepsiemlak_listings.jsonl
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

URLS_PATH = Path("/Users/mustafaaksoz/Bot/data/urls_hepsiemlak.txt")
OUT_PATH = Path("/Users/mustafaaksoz/Bot/data/hepsiemlak_listings.jsonl")

PHONE_RE = re.compile(r"(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_phone_from_text(text: str) -> Optional[str]:
    match = PHONE_RE.search(text)
    if match:
        return clean_text(match.group(1))
    return None


async def extract_listing(page, url: str) -> dict:
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    # Try to reveal phone
    phone = None
    button = page.get_by_role("button", name=re.compile("Telefon Numarasını Göster", re.I))
    if await button.count() == 0:
        button = page.locator("text=Telefon Numarasını Göster")
    if await button.count() > 0:
        await button.first.click()
        await page.wait_for_timeout(1500)

    # Prefer tel: links after reveal
    tel_link = page.locator('a[href^="tel:"]')
    if await tel_link.count() > 0:
        href = await tel_link.first.get_attribute("href")
        if href:
            phone = href.replace("tel:", "").strip()

    # Fallback: scan page text
    if not phone:
        content_text = clean_text(await page.inner_text("body"))
        phone = extract_phone_from_text(content_text)

    # Agent name (usually near avatar)
    agent_name = None
    agent_loc = page.locator("text=/[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+/")
    if await agent_loc.count() > 0:
        agent_name = clean_text(await agent_loc.first.inner_text())

    # Office name (label: İşletme Ünvanı)
    office_name = None
    office_label = page.locator("text=İşletme Ünvanı")
    if await office_label.count() > 0:
        # Try to read the next sibling text
        office_container = office_label.first.locator("xpath=..")
        office_text = clean_text(await office_container.inner_text())
        # Remove label if present
        office_name = clean_text(office_text.replace("İşletme Ünvanı", "")) or None

    # City/District from breadcrumb or location block
    city = None
    district = None
    breadcrumb = page.locator("nav.breadcrumb, .breadcrumb")
    if await breadcrumb.count() > 0:
        crumb_text = clean_text(await breadcrumb.first.inner_text())
        # Example: Satılık > Muğla Satılık > Ortaca Satılık > Çaylı Satılık
        parts = [p.strip() for p in crumb_text.split(">") if p.strip()]
        if len(parts) >= 2:
            city = parts[1].replace("Satılık", "").replace("Kiralık", "").strip()
        if len(parts) >= 3:
            district = parts[2].replace("Satılık", "").replace("Kiralık", "").strip()

    # Fallback city/district from page text
    if not city or not district:
        content_text = clean_text(await page.inner_text("body"))
        m = re.search(r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s*/\s*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)", content_text)
        if m:
            city = city or m.group(1)
            district = district or m.group(2)

    return {
        "listing_url": url,
        "phone_number": phone,
        "agent_name": agent_name,
        "office_name": office_name,
        "city": city,
        "district": district,
        "source": "hepsiemlak",
        "confidence": "medium",
    }


async def main():
    urls_file = Path(sys.argv[1]) if len(sys.argv) > 1 else URLS_PATH
    if not urls_file.exists():
        print(f"❌ URLs file not found: {urls_file}")
        return

    urls = [u.strip() for u in urls_file.read_text(encoding="utf-8").splitlines() if u.strip()]
    if not urls:
        print("❌ URL list is empty. Run hepsiemlak_collect_urls.py first.")
        return

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

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

        with OUT_PATH.open("w", encoding="utf-8") as f:
            for idx, url in enumerate(urls, 1):
                print(f"[{idx}/{len(urls)}] {url}")
                try:
                    data = await extract_listing(page, url)
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                except Exception as e:
                    print(f"❌ Failed: {e}")
                    f.write(json.dumps({"listing_url": url, "error": str(e)}, ensure_ascii=False) + "\n")

        await context.close()
        await browser.close()

    print(f"\n✅ Saved to {OUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
