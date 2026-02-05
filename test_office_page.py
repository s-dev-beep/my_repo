#!/usr/bin/env python3
"""
Test script to explore Hepsiemlak office pages.
Clicks "Firmanın Diğer İlanları" to see what data is available.
"""
import asyncio
import re
from playwright.async_api import async_playwright

PHONE_RE = re.compile(r'\+?90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}')


async def explore_office_page():
    # Start from a listing that has an office
    listing_url = "https://www.hepsiemlak.com/mugla-ortaca-cayli-satilik/daire/142651-248"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale='tr-TR',
            timezone_id='Europe/Istanbul'
        )
        page = await context.new_page()
        
        print(f"\n1. Loading listing: {listing_url}")
        await page.goto(listing_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # Look for "Firmanın Diğer İlanları" link
        print("\n2. Looking for 'Firmanın Diğer İlanları' link...")
        
        # Try different selectors
        office_link = None
        
        # Option 1: Look for link with text containing "Firmanın" or "İlanları"
        try:
            office_link = page.locator('a:has-text("Firmanın Diğer İlanları")').first
            if await office_link.count() > 0:
                print("   ✓ Found via text match")
        except Exception as e:
            print(f"   ✗ Text match failed: {e}")
        
        # Option 2: Look for link in the office/consultant section
        if not office_link or await office_link.count() == 0:
            try:
                office_link = page.locator('[class*="office"], [class*="consultant"], [class*="danışman"]').locator('a[href*="/"]').first
                if await office_link.count() > 0:
                    print("   ✓ Found in office section")
            except Exception as e:
                print(f"   ✗ Office section failed: {e}")
        
        # Debug: Show all links that might be relevant
        print("\n3. Scanning all links on page...")
        all_links = await page.locator('a[href]').all()
        office_related = []
        
        for link in all_links[:50]:  # Check first 50 links
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                
                # Skip empty links and anchors
                if not href or href == '#' or href.startswith('javascript:'):
                    continue
                
                if any(keyword in text.lower() for keyword in ['firma', 'ilan', 'danışman', 'emlak', 'ofis']):
                    office_related.append((text.strip(), href))
                    print(f"   - {text.strip()[:50]} → {href[:80]}")
            except:
                continue
        
        if not office_related:
            print("   ✗ No office-related links found")
            print("\n4. Page HTML structure:")
            html = await page.content()
            
            # Look for office/company info in HTML
            if 'firma' in html.lower():
                print("   ✓ 'firma' found in HTML")
            if 'işletme' in html.lower():
                print("   ✓ 'işletme' found in HTML")
            if 'danışman' in html.lower():
                print("   ✓ 'danışman' found in HTML")
            
            # Save HTML for inspection
            with open('debug_listing_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\n   Saved full HTML to debug_listing_page.html for inspection")
            
            await browser.close()
            return
        
        # Click on the most promising link
        print(f"\n5. Clicking on: {office_related[0][0]}")
        print(f"   URL: {office_related[0][1]}")
        
        # Make full URL if relative
        office_url = office_related[0][1]
        if not office_url.startswith('http'):
            office_url = f"https://www.hepsiemlak.com{office_url}"
        
        # Navigate to office page
        await page.goto(office_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        print("\n6. Office page loaded!")
        print(f"   Title: {await page.title()}")
        print(f"   URL: {page.url}")
        
        # Extract office information
        print("\n7. Extracting office information...")
        
        # Office name
        try:
            office_name_elem = page.locator('h1, [class*="office-name"], [class*="company"]').first
            office_name = await office_name_elem.inner_text() if await office_name_elem.count() > 0 else None
            print(f"   Office Name: {office_name}")
        except Exception as e:
            print(f"   ✗ Office name extraction failed: {e}")
        
        # Phone number - look for reveal button
        try:
            phone_button = page.get_by_role("button", name=re.compile("Telefon|Göster", re.I))
            if await phone_button.count() > 0:
                print(f"   ✓ Found phone reveal button")
                await phone_button.first.click()
                await asyncio.sleep(1)
                
                # Extract from tel: link
                tel_link = page.locator('a[href^="tel:"]').first
                if await tel_link.count() > 0:
                    phone = (await tel_link.get_attribute("href")).replace("tel:", "").strip()
                    print(f"   Phone (tel:): {phone}")
                else:
                    # Fallback to regex
                    html = await page.content()
                    phones = PHONE_RE.findall(html)
                    print(f"   Phones (regex): {phones}")
            else:
                print(f"   ✗ No phone reveal button found")
        except Exception as e:
            print(f"   ✗ Phone extraction failed: {e}")
        
        # Address
        try:
            address_elem = page.locator('[class*="address"], [class*="adres"]').first
            address = await address_elem.inner_text() if await address_elem.count() > 0 else None
            print(f"   Address: {address}")
        except Exception as e:
            print(f"   ✗ Address extraction failed: {e}")
        
        # Get all listings from this office
        print("\n8. Counting office listings...")
        listing_links = page.locator('a[href*="/ilan/"]')
        count = await listing_links.count()
        print(f"   Found {count} listing links")
        
        if count > 0:
            print("\n   First 5 listings:")
            for i in range(min(5, count)):
                link = listing_links.nth(i)
                href = await link.get_attribute('href')
                print(f"   - {href}")
        
        # Save office page HTML
        html = await page.content()
        with open('debug_office_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n   Saved office page HTML to debug_office_page.html")
        
        print("\n✓ Exploration complete! Review the debug HTML files.")
        input("\nPress Enter to close browser...")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(explore_office_page())
