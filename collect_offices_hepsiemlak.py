#!/usr/bin/env python3
"""
Office-first collector for Hepsiemlak.
Runs headless, perfect for servers (Hetzner, etc).
NO deduplication - saves everything raw to JSONL.

Usage:
    python collect_offices_hepsiemlak.py https://www.hepsiemlak.com/satilik
    python collect_offices_hepsiemlak.py https://www.hepsiemlak.com/kiralik
"""
import asyncio
import json
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PHONE_RE = re.compile(r'\+?90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}')


async def collect_office_urls(page, category_url: str, max_pages: int = 3) -> set:
    """Collect office URLs from search results."""
    office_urls = set()
    
    print(f"\nCollecting office URLs from: {category_url}")
    await page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)
    
    for page_num in range(1, max_pages + 1):
        print(f"  Page {page_num}/{max_pages}...")
        
        # Scroll to load listings
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.5)
        
        # Extract office links
        html = await page.content()
        
        # Pattern: /emlak-ofisi/office-name-id
        office_links = re.findall(r'/emlak-ofisi/[a-z0-9-]+', html)
        office_urls.update(f"https://www.hepsiemlak.com{link}" for link in office_links)
        
        print(f"    Found {len(office_links)} offices on this page (total: {len(office_urls)})")
        
        # Go to next page if available
        if page_num < max_pages:
            try:
                next_btn = page.locator('a[aria-label="Go to next page"], a:has-text("Sonraki")').first
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await asyncio.sleep(2)
                else:
                    print("    No more pages")
                    break
            except:
                break
    
    print(f"\n✓ Collected {len(office_urls)} unique office URLs")
    return office_urls


async def extract_office_data(page, office_url: str) -> dict:
    """Extract office info and all their listings."""
    print(f"\n  Extracting: {office_url}")
    
    await page.goto(office_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)
    
    data = {
        "office_url": office_url,
        "office_name": None,
        "phone_number": None,
        "city": None,
        "district": None,
        "address": None,
        "listings": [],
        "source": "hepsiemlak"
    }
    
    # Extract from JSON-LD structured data (most reliable)
    try:
        scripts = page.locator('script[type="application/ld+json"]')
        count = await scripts.count()
        
        for i in range(count):
            script_text = await scripts.nth(i).inner_text()
            json_data = json.loads(script_text)
            
            if json_data.get('@type') == 'RealEstateAgent':
                data['office_name'] = json_data.get('name')
                data['phone_number'] = json_data.get('telephone')
                
                # Parse address
                address = json_data.get('address', '')
                if isinstance(address, str) and ',' in address:
                    parts = [p.strip() for p in address.split(',')]
                    data['city'] = parts[0] if len(parts) > 0 else None
                    data['district'] = parts[1] if len(parts) > 1 else None
                data['address'] = address if isinstance(address, str) else None
                
                # Extract listings
                catalog = json_data.get('hasOfferCatalog', {})
                items = catalog.get('itemListElement', [])
                
                for item in items:
                    listing = {
                        "listing_url": item.get('url'),
                        "title": item.get('name'),
                        "date_posted": item.get('datePosted'),
                        "price": item.get('offers', {}).get('price'),
                        "currency": item.get('offers', {}).get('priceCurrency')
                    }
                    data['listings'].append(listing)
                
                break
    except Exception as e:
        print(f"    ✗ JSON-LD extraction failed: {e}")
    
    # Fallback: Extract from page elements if JSON-LD failed
    if not data['office_name']:
        try:
            office_name_elem = page.locator('h1').first
            if await office_name_elem.count() > 0:
                data['office_name'] = (await office_name_elem.inner_text()).strip()
        except:
            pass
    
    if not data['phone_number']:
        try:
            # Click phone reveal button
            phone_btn = page.get_by_role("button", name=re.compile("Telefon|Göster", re.I))
            if await phone_btn.count() > 0:
                await phone_btn.first.click()
                await asyncio.sleep(1)
                
                # Extract from tel: link
                tel_link = page.locator('a[href^="tel:"]').first
                if await tel_link.count() > 0:
                    phone = await tel_link.get_attribute("href")
                    data['phone_number'] = phone.replace("tel:", "").strip()
        except:
            pass
    
    # Fallback: Regex phone extraction
    if not data['phone_number']:
        try:
            html = await page.content()
            phones = PHONE_RE.findall(html)
            if phones:
                data['phone_number'] = phones[0]
        except:
            pass
    
    print(f"    ✓ Office: {data['office_name']}")
    print(f"    ✓ Phone: {data['phone_number']}")
    print(f"    ✓ Location: {data['city']}, {data['district']}")
    print(f"    ✓ Listings: {len(data['listings'])}")
    
    return data


async def main():
    if len(sys.argv) < 2:
        print("Usage: python collect_offices_hepsiemlak.py <category_url>")
        print("Example: python collect_offices_hepsiemlak.py https://www.hepsiemlak.com/satilik")
        sys.exit(1)
    
    category_url = sys.argv[1]
    output_file = Path("data/hepsiemlak_offices.jsonl")
    output_file.parent.mkdir(exist_ok=True)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          Hepsiemlak Office Collector (Headless)              ║
║                  No Deduplication                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    async with async_playwright() as p:
        # HEADLESS mode - perfect for servers
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='tr-TR',
            timezone_id='Europe/Istanbul',
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Step 1: Collect office URLs
        office_urls = await collect_office_urls(page, category_url, max_pages=3)
        
        # Step 2: Extract data from each office
        print(f"\n{'='*60}")
        print(f"Extracting data from {len(office_urls)} offices...")
        print(f"{'='*60}")
        
        collected = 0
        failed = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, office_url in enumerate(office_urls, 1):
                print(f"\n[{i}/{len(office_urls)}]", end="")
                
                try:
                    office_data = await extract_office_data(page, office_url)
                    
                    # Save to JSONL (no dedup)
                    f.write(json.dumps(office_data, ensure_ascii=False) + '\n')
                    f.flush()
                    
                    collected += 1
                    
                except Exception as e:
                    print(f"    ✗ Failed: {e}")
                    failed += 1
                    continue
        
        await browser.close()
        
        print(f"\n{'='*60}")
        print(f"✓ Collection complete!")
        print(f"  Collected: {collected} offices")
        print(f"  Failed: {failed} offices")
        print(f"  Output: {output_file}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
