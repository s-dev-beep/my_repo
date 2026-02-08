#!/bin/bash

# Simple NordVPN Control for macOS using the GUI app
# This script controls the NordVPN.app using AppleScript

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║               NordVPN Manual Setup (macOS GUI App)                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if NordVPN.app is installed
if [ ! -d "/Applications/NordVPN.app" ]; then
    echo "❌ NordVPN.app not found in /Applications/"
    echo ""
    echo "Please install NordVPN from: https://nordvpn.com/download/mac/"
    exit 1
fi

echo "✅ NordVPN.app found"
echo ""

# Open NordVPN app
echo "📱 Opening NordVPN app..."
open -a "NordVPN"
sleep 2

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "                     MANUAL SETUP REQUIRED"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "The NordVPN macOS app doesn't have a command-line interface."
echo "Please complete these steps MANUALLY in the NordVPN app:"
echo ""
echo "1️⃣  Log in with your NordVPN credentials in the app window"
echo ""
echo "2️⃣  Connect to Turkey:"
echo "    • Click the country list"
echo "    • Search for 'Turkey'"
echo "    • Click 'Quick Connect' for Turkey"
echo ""
echo "3️⃣  Verify connection:"
echo "    • The app should show 'Connected' with a green checkmark"
echo "    • You should see 'Turkey' as the connected country"
echo ""
echo "4️⃣  Keep the app running while testing our Python scripts"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Once connected, verify your IP is in Turkey:"
echo ""
echo "  curl https://ipinfo.io/country"
echo ""
echo "Expected output: TR (Turkey)"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "After connecting, run the test script:"
echo ""
echo "  cd /Users/mustafaaksoz/Bot"
echo "  python src/experiments/live_access_test_vpn.py"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
