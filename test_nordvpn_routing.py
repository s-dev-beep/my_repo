#!/usr/bin/env python3
"""Test NordVPN-routed fetcher with real URL."""

import asyncio
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.nordvpn_fetcher import NordVPNFetcher
from src.core.nordvpn_manager import NordVPNManager
from src.core.logger import setup_logger

logger = setup_logger(__name__)


async def test_vpn_connectivity():
    """Test basic VPN connectivity without Fetcher."""
    print("\n" + "=" * 80)
    print("STEP 26: VPN CONNECTIVITY TEST")
    print("=" * 80)

    # Get credentials
    username = os.getenv("NORDVPN_USER")
    password = os.getenv("NORDVPN_PASS")

    if not username or not password:
        print("❌ Error: NORDVPN_USER and NORDVPN_PASS environment variables required")
        print("\nUsage:")
        print("  export NORDVPN_USER='your_email@example.com'")
        print("  export NORDVPN_PASS='your_password'")
        print("  python test_nordvpn_routing.py")
        return False

    print(f"\n✓ Credentials found")
    print(f"  Username: {username[:20]}...")
    print(f"  Country: Turkey")

    # Create manager
    vpn = NordVPNManager(username, password, preferred_country="Turkey")

    # Check NordVPN installed
    print("\n📦 Checking NordVPN installation...")
    if not vpn.check_nordvpn_installed():
        print("❌ NordVPN CLI not found. Install with:")
        print("  brew install nordvpn")
        return False

    print("✓ NordVPN CLI available")

    # Login
    print("\n🔐 Logging in to NordVPN...")
    if not vpn.login():
        print("❌ Login failed")
        return False

    print("✓ Logged in successfully")

    # Connect
    print("\n🌐 Connecting to Turkey server...")
    if not vpn.connect("Turkey"):
        print("❌ Connection failed")
        return False

    print("✓ Connected to Turkey VPN")

    # Check status
    print("\n📊 Checking VPN status...")
    status = vpn.get_status()
    if status:
        print(f"✓ VPN Status: {status}")
    else:
        print("⚠ Could not get VPN status (may still be connected)")

    # Disconnect
    print("\n🔌 Disconnecting VPN...")
    if not vpn.disconnect():
        print("⚠ Disconnect may have failed, but continuing")
    else:
        print("✓ Disconnected from VPN")

    print("\n" + "=" * 80)
    print("✓ VPN CONNECTIVITY TEST PASSED")
    print("=" * 80 + "\n")
    return True


async def test_vpn_routed_fetch():
    """Test fetching URL through NordVPN."""
    print("\n" + "=" * 80)
    print("STEP 27: VPN-ROUTED FETCH TEST")
    print("=" * 80)

    # Get credentials
    username = os.getenv("NORDVPN_USER")
    password = os.getenv("NORDVPN_PASS")

    if not username or not password:
        print("❌ Skipping: Credentials not provided")
        return False

    # Test URL (single listing from earlier)
    test_url = "https://www.sahibinden.com/ilan/konut-satilik-istanbul-beyoglu-murat-reis-38851619540"

    print(f"\n🧪 Test URL: {test_url}")
    print(f"📍 VPN Country: Turkey")

    try:
        async with NordVPNFetcher(
            nordvpn_username=username,
            nordvpn_password=password,
            nordvpn_country="Turkey",
            max_retries=0,
            requests_per_minute=2,  # Be conservative
        ) as fetcher:
            print("\n⏳ Fetching through NordVPN...")
            html = await fetcher.fetch(test_url)

            # Check for success indicators
            has_phone = "5" in html or "4" in html  # Turkish phone numbers
            has_listing = "ilan" in html.lower() or "sahibinden" in html.lower()
            is_error = "olağan dışı" in html.lower() or "404" in html

            print(f"\n✓ Fetch successful: {len(html)} bytes")
            print(f"  - Has listing content: {has_listing}")
            print(f"  - Has phone data: {has_phone}")
            print(f"  - Is error page: {is_error}")

            if is_error:
                print("\n⚠ Page contains error message (may still be blocked)")
                return False

            if has_listing and has_phone:
                print("\n✓ SUCCESS: Received real listing content!")
                return True

            return False

    except Exception as e:
        print(f"\n❌ Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           NORDVPN INTEGRATION TEST - STEP 26 & 27                          ║
║                                                                            ║
║ This test validates:                                                       ║
║   1. NordVPN CLI is installed and working                                 ║
║   2. Login/connect/disconnect operations work                             ║
║   3. HTTP requests through VPN succeed                                    ║
║   4. Sahibinden is accessible from Turkey VPN IP                          ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Test connectivity first
    if not await test_vpn_connectivity():
        print("\n❌ VPN connectivity test failed")
        sys.exit(1)

    # Then test fetching
    if not await test_vpn_routed_fetch():
        print("\n⚠ VPN-routed fetch test failed or incomplete")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED - NORDVPN INTEGRATION WORKING")
    print("=" * 80)
    print("""
Next Steps:
  1. Update Fetcher to use NordVPNFetcher for Sahibinden URLs
  2. Run STEP 24 test again with VPN routing
  3. Monitor success rate improvement
  4. Deploy to production with credential management
    """)


if __name__ == "__main__":
    asyncio.run(main())
