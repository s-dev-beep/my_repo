#!/usr/bin/env python3
"""Simple test that works with NordVPN GUI app (no CLI needed)."""

import asyncio
import requests
from src.core.fetcher import Fetcher
from src.core.logger import setup_logger

logger = setup_logger(__name__)


async def test_with_manual_vpn():
    """Test Sahibinden access assuming VPN is already connected manually."""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           NORDVPN TEST (Manual Connection Required)                        ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check current IP and location
    print("📍 Checking your current IP and location...")
    try:
        ip_info = requests.get("https://ipinfo.io/json", timeout=5).json()
        print(f"✓ Current IP: {ip_info.get('ip')}")
        print(f"✓ Location: {ip_info.get('city')}, {ip_info.get('country')}")
        print(f"✓ ISP: {ip_info.get('org')}")
        print()
        
        if ip_info.get('country') != 'TR':
            print("⚠️  WARNING: You're not connected to Turkey VPN!")
            print()
            print("Please:")
            print("  1. Open NordVPN app")
            print("  2. Log in")
            print("  3. Connect to Turkey")
            print("  4. Wait for 'Connected' status")
            print("  5. Re-run this script")
            print()
            return False
        else:
            print("✅ Connected to Turkey VPN!")
            print()
    except Exception as e:
        print(f"⚠️  Could not check IP: {e}")
        print("Continuing anyway...")
        print()
    
    # Test Sahibinden access with a fresh listing URL
    # Using homepage first to test connectivity
    test_url = "https://www.sahibinden.com/kategori/emlak"
    
    print(f"🧪 Testing Sahibinden access...")
    print(f"URL: {test_url}")
    print()
    
    try:
        async with Fetcher(max_retries=0, requests_per_minute=6) as fetcher:
            print("⏳ Fetching...")
            html = await fetcher.fetch(test_url)
            
            # Check content
            has_listing = "ilan" in html.lower() or "fiyat" in html.lower()
            has_phone = len([c for c in html if c.isdigit()]) > 100
            is_error = "olağan dışı" in html.lower() or "403" in html
            content_length = len(html)
            
            print(f"✓ Fetch successful: {content_length} bytes")
            print()
            print(f"  Has listing content: {has_listing}")
            print(f"  Has phone data: {has_phone}")
            print(f"  Is error page: {is_error}")
            print()
            
            if is_error:
                print("❌ Still blocked! The VPN IP might also be blacklisted.")
                print()
                print("Try:")
                print("  1. Disconnect and reconnect to different Turkey server")
                print("  2. Wait 5 minutes and try again")
                print("  3. Try a different country (e.g., Germany)")
                return False
            elif has_listing and content_length > 10000:
                print("✅ SUCCESS! Sahibinden is accessible through VPN!")
                print()
                print("You can now run the full test:")
                print("  python src/experiments/live_access_test_manual.py")
                return True
            else:
                print("⚠️  Got response but content looks suspicious")
                print(f"Content length: {content_length} (expected > 10000)")
                return False
                
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        print()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_with_manual_vpn())
    exit(0 if success else 1)
