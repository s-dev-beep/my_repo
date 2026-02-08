#!/usr/bin/env python3
"""
Test script to extract individual agent information from office page.
"""
import asyncio
import re
from playwright.async_api import async_playwright

PHONE_RE = re.compile(r'\+?90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}')


async def explore_agents():
    office_url = "https://www.hepsiemlak.com/emlak-ofisi/birlik-emlak-142651"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale='tr-TR',
            timezone_id='Europe/Istanbul'
        )
        page = await context.new_page()
        
        print(f"\n1. Loading office page: {office_url}")
        await page.goto(office_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        print("\n2. Looking for agents section...")
        
        # Look for "Danışmanlarımız" section
        agents_section = page.locator('text=Danışmanlarımız').first
        if await agents_section.count() > 0:
            print("   ✓ Found 'Danışmanlarımız' section")
        
        # Look for individual agent cards/links
        print("\n3. Extracting agent information...")
        
        # Try different selectors for agents
        html = await page.content()
        
        # Save for inspection
        with open('debug_agents.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   Saved HTML to debug_agents.html")
        
        # Look for agent names
        agent_names = []
        
        # Pattern 1: Look for "Danışman" text
        if 'Danışman' in html:
            print("\n   'Danışman' found in HTML")
            # Extract agent name elements
            agent_elements = page.locator('[class*="agent"], [class*="danışman"], [class*="consultant"]')
            count = await agent_elements.count()
            print(f"   Found {count} agent elements")
        
        # Pattern 2: Look for agent links
        agent_links = re.findall(r'/danisman/[^"\'>\s]+', html)
        if agent_links:
            print(f"\n   Found {len(agent_links)} agent links:")
            for link in agent_links[:5]:
                print(f"     - {link}")
        
        # Pattern 3: Look for "Danışmanın İlanları"
        agent_listing_links = page.locator('a:has-text("Danışmanın İlanları")')
        count = await agent_listing_links.count()
        print(f"\n   Found {count} 'Danışmanın İlanları' links")
        
        if count > 0:
            print("\n4. Testing agent page access...")
            # Click first agent link
            await agent_listing_links.first.click()
            await asyncio.sleep(3)
            
            print(f"   Agent page URL: {page.url}")
            print(f"   Agent page title: {await page.title()}")
            
            # Extract agent info
            print("\n5. Extracting agent details...")
            
            # Agent name
            try:
                h1 = page.locator('h1').first
                agent_name = await h1.inner_text() if await h1.count() > 0 else None
                print(f"   Name: {agent_name}")
            except Exception as e:
                print(f"   ✗ Name extraction failed: {e}")
            
            # Agent phone
            try:
                phone_btn = page.get_by_role("button", name=re.compile("Telefon|Göster", re.I))
                if await phone_btn.count() > 0:
                    await phone_btn.first.click()
                    await asyncio.sleep(1)
                    
                    tel_link = page.locator('a[href^="tel:"]').first
                    if await tel_link.count() > 0:
                        phone = await tel_link.get_attribute("href")
                        print(f"   Phone: {phone.replace('tel:', '')}")
                else:
                    print("   ✗ No phone reveal button")
            except Exception as e:
                print(f"   ✗ Phone extraction failed: {e}")
            
            # Agent office affiliation
            try:
                # Look for office name/link on agent page
                office_links = page.locator('a[href*="/emlak-ofisi/"]')
                if await office_links.count() > 0:
                    office_href = await office_links.first.get_attribute('href')
                    print(f"   Office link: {office_href}")
            except:
                pass
            
            # Save agent page HTML
            html = await page.content()
            with open('debug_agent_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("\n   Saved agent page to debug_agent_page.html")
        
        print("\n✓ Exploration complete!")
        input("\nPress Enter to close browser...")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(explore_agents())
