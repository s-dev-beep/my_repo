#!/usr/bin/env python3
"""
Complete office + agents collector for Hepsiemlak.
Extracts full hierarchy: City → District → Office → Agents
Listing details are NOT collected; only listing counts are included.
Runs headless, server-ready, NO deduplication.

Usage:
    python collect_full_hierarchy.py https://www.hepsiemlak.com/satilik
"""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

PHONE_RE = re.compile(r'\+?90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}')
MANUAL_CHALLENGE = False
CHALLENGE_WAIT_MS = 180000


async def wait_for_cloudflare(page, timeout=30):
    """Wait for Cloudflare challenge to complete."""
    try:
        # Wait for main content to appear (Cloudflare will be gone)
        await page.wait_for_selector('h1, [class*="content"]', timeout=timeout * 1000)
        await asyncio.sleep(2)  # Extra buffer
        return True
    except PlaywrightTimeout:
        print("    ⚠ Cloudflare challenge timeout")
        return False


async def ensure_real_page(page, url: str, attempts: int = 3) -> bool:
    """Navigate and retry if Cloudflare challenge page is detected."""
    for attempt in range(1, attempts + 1):
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)

        title = await page.title()
        html = await page.content()

        is_challenge = (
            "Bir dakika" in title
            or "Just a moment" in title
            or "cf-turnstile" in html
            or "cdn-cgi/challenge" in html
        )

        if not is_challenge:
            return True

        print(f"    ⚠ Cloudflare challenge detected (attempt {attempt}/{attempts})")
        if MANUAL_CHALLENGE:
            print("    → Please solve the challenge in the browser window...")
            try:
                await page.wait_for_function(
                    """
                    () => {
                      const t = document.title || '';
                      const html = document.documentElement.innerHTML || '';
                      return !t.includes('Bir dakika') && !t.includes('Just a moment') && !html.includes('cf-turnstile');
                    }
                    """,
                    timeout=CHALLENGE_WAIT_MS
                )
                return True
            except PlaywrightTimeout:
                print("    ⚠ Challenge not solved in time")
        await asyncio.sleep(5)

    return False


async def extract_agent_data(page, agent_url: str) -> dict:
    """Extract individual agent information from their page (count only)."""
    print(f"      Extracting agent: {agent_url}")
    
    try:
        ready = await ensure_real_page(page, agent_url, attempts=3)
        if not ready:
            print("        ✗ Agent page blocked by Cloudflare")
            return None
        
        agent = {
            "agent_url": agent_url,
            "agent_name": None,
            "agent_phone": None,
            "listing_count": 0
        }
        
        # Agent name from h1
        try:
            h1 = page.locator('h1').first
            if await h1.count() > 0:
                agent['agent_name'] = (await h1.inner_text()).strip()
        except:
            pass
        
        # Click phone reveal button
        try:
            phone_btn = page.get_by_role("button", name=re.compile("Telefon|Göster", re.I))
            if await phone_btn.count() > 0:
                await phone_btn.first.click()
                await asyncio.sleep(1)
                
                # Extract from tel: link
                tel_link = page.locator('a[href^="tel:"]').first
                if await tel_link.count() > 0:
                    phone = await tel_link.get_attribute("href")
                    agent['agent_phone'] = phone.replace("tel:", "").strip()
        except:
            pass
        
        # Fallback: regex phone extraction
        if not agent['agent_phone']:
            try:
                html = await page.content()
                phones = PHONE_RE.findall(html)
                if phones:
                    agent['agent_phone'] = phones[0]
            except:
                pass
        
        # Count listings (no listing details collected)
        try:
            listing_links = page.locator('a[href*="/ilan/"]')
            agent['listing_count'] = await listing_links.count()
        except:
            pass
        
        print(f"        ✓ {agent['agent_name']} | {agent['agent_phone']} | {agent['listing_count']} listings")
        
        return agent
        
    except Exception as e:
        print(f"        ✗ Agent extraction failed: {e}")
        return None


async def extract_office_and_agents(page, office_url: str) -> dict:
    """Extract complete office hierarchy including all agents (count only)."""
    print(f"\n  Office: {office_url}")
    
    ready = await ensure_real_page(page, office_url, attempts=3)
    if not ready:
        raise RuntimeError("Office page blocked by Cloudflare")
    
    data = {
        "office_url": office_url,
        "office_name": None,
        "office_phone": None,
        "city": None,
        "district": None,
        "address": None,
        "agents": [],
        "total_listings": 0,
        "source": "hepsiemlak"
    }
    
    # Extract from JSON-LD structured data (most reliable for office info)
    try:
        scripts = page.locator('script[type="application/ld+json"]')
        count = await scripts.count()
        
        for i in range(count):
            script_text = await scripts.nth(i).inner_text()
            json_data = json.loads(script_text)
            
            if json_data.get('@type') == 'RealEstateAgent':
                data['office_name'] = json_data.get('name')
                data['office_phone'] = json_data.get('telephone')
                
                # Parse address
                address = json_data.get('address', '')
                if isinstance(address, str) and ',' in address:
                    parts = [p.strip() for p in address.split(',')]
                    data['city'] = parts[0] if len(parts) > 0 else None
                    data['district'] = parts[1] if len(parts) > 1 else None
                data['address'] = address if isinstance(address, str) else None
                
                # Count total listings from catalog (no listing details collected)
                catalog = json_data.get('hasOfferCatalog', {})
                items = catalog.get('itemListElement', [])
                data['total_listings'] = len(items)
                
                break
    except Exception as e:
        print(f"    ✗ JSON-LD extraction failed: {e}")
    
    # Fallback: Extract office info from page elements
    if not data['office_name']:
        try:
            h1 = page.locator('h1').first
            if await h1.count() > 0:
                data['office_name'] = (await h1.inner_text()).strip()
        except:
            pass
    
    if not data['office_phone']:
        try:
            phone_btn = page.get_by_role("button", name=re.compile("Telefon|Göster", re.I))
            if await phone_btn.count() > 0:
                await phone_btn.first.click()
                await asyncio.sleep(1)
                
                tel_link = page.locator('a[href^="tel:"]').first
                if await tel_link.count() > 0:
                    phone = await tel_link.get_attribute("href")
                    data['office_phone'] = phone.replace("tel:", "").strip()
        except:
            pass
    
    print(f"    ✓ Office: {data['office_name']}")
    print(f"    ✓ Phone: {data['office_phone']}")
    print(f"    ✓ Location: {data['city']}, {data['district']}")
    print(f"    ✓ Total listings: {data['total_listings']}")
    
    # Extract agent URLs from office page
    print(f"    Extracting agents...")
    html = await page.content()
    
    # Pattern: /emlak-ofisi/<office-slug>/<agent-slug-id>
    agent_links = re.findall(
        r'href="(/emlak-ofisi/[^"\s]+/[a-z0-9-]+-\d+)"',
        html,
        flags=re.I
    )
    agent_urls = list({f"https://www.hepsiemlak.com{link}" for link in agent_links})
    
    print(f"    Found {len(agent_urls)} agents")
    
    # Extract each agent's data
    for agent_url in agent_urls:
        agent_data = await extract_agent_data(page, agent_url)
        if agent_data:
            data['agents'].append(agent_data)
    
    return data


async def collect_office_urls(page, category_url: str, max_pages: int = 2) -> set:
    """Collect office URLs from search results."""
    office_urls = set()
    
    print(f"\nCollecting office URLs from: {category_url}")
    ready = await ensure_real_page(page, category_url, attempts=3)
    if not ready:
        print("⚠ Category page blocked by Cloudflare")
        return set()
    
    for page_num in range(1, max_pages + 1):
        print(f"  Page {page_num}/{max_pages}...")
        
        # Scroll to load listings
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.5)
        
        # Extract office links
        html = await page.content()
        office_links = re.findall(r'/emlak-ofisi/[a-z0-9-]+', html)
        new_offices = set(f"https://www.hepsiemlak.com{link}" for link in office_links)
        office_urls.update(new_offices)
        
        print(f"    Found {len(new_offices)} offices (total: {len(office_urls)})")
        
        # Go to next page
        if page_num < max_pages:
            try:
                next_btn = page.locator('a[aria-label="Go to next page"], a:has-text("Sonraki")').first
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await asyncio.sleep(2)
                else:
                    break
            except:
                break
    
    print(f"\n✓ Collected {len(office_urls)} unique offices")
    return office_urls


async def main():
    parser = argparse.ArgumentParser(description="Hepsiemlak full hierarchy collector")
    parser.add_argument("category_url", help="Category URL (e.g., https://www.hepsiemlak.com/satilik)")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser window")
    parser.add_argument("--storage-state", help="Path to Playwright storage state JSON")
    parser.add_argument("--max-pages", type=int, default=2, help="Number of category pages to scan")
    parser.add_argument("--manual-challenge", action="store_true", help="Allow manual Cloudflare solving in headed mode")
    parser.add_argument("--save-storage-state", help="Save storage state to JSON after login/challenge")
    args = parser.parse_args()
    
    category_url = args.category_url
    output_file = Path("data/hepsiemlak_full_hierarchy.jsonl")
    output_file.parent.mkdir(exist_ok=True)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║     Hepsiemlak Full Hierarchy Collector (Headless)            ║
║     City → District → Office → Agents                         ║
║     NO Deduplication                                          ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    global MANUAL_CHALLENGE
    MANUAL_CHALLENGE = args.manual_challenge

    async with async_playwright() as p:
        # Headless mode for servers
        browser = await p.chromium.launch(
            headless=not args.headed,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            locale='tr-TR',
            timezone_id='Europe/Istanbul',
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
            },
            storage_state=args.storage_state if args.storage_state else None
        )
        # Basic stealth tweaks
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR', 'tr', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Linux x86_64' });
            window.chrome = { runtime: {} };
            """
        )
        page = await context.new_page()
        
        # Step 1: Collect office URLs
        office_urls = await collect_office_urls(page, category_url, max_pages=args.max_pages)
        
        # Step 2: Extract full hierarchy for each office
        print(f"\n{'='*63}")
        print(f"Extracting complete data from {len(office_urls)} offices...")
        print(f"{'='*63}")
        
        collected = 0
        failed = 0
        total_agents = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, office_url in enumerate(office_urls, 1):
                print(f"\n[{i}/{len(office_urls)}]", end="")
                
                try:
                    office_data = await extract_office_and_agents(page, office_url)
                    
                    # Save to JSONL (no dedup)
                    f.write(json.dumps(office_data, ensure_ascii=False) + '\n')
                    f.flush()
                    
                    collected += 1
                    total_agents += len(office_data['agents'])
                    
                except Exception as e:
                    print(f"    ✗ Failed: {e}")
                    failed += 1
                    continue
        
        if args.save_storage_state:
            await context.storage_state(path=args.save_storage_state)
        await browser.close()
        
        print(f"\n{'='*63}")
        print(f"✓ Collection complete!")
        print(f"  Offices: {collected}")
        print(f"  Agents: {total_agents}")
        print(f"  Failed: {failed}")
        print(f"  Output: {output_file}")
        print(f"{'='*63}\n")


if __name__ == "__main__":
    asyncio.run(main())
