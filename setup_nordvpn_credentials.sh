#!/bin/bash

# NordVPN Credentials Setup Script
# This script prompts you to enter your NordVPN credentials securely

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                   NordVPN Credentials Setup                                 ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if NordVPN is installed
if ! command -v nordvpn &> /dev/null; then
    echo "❌ NordVPN CLI is not installed"
    echo ""
    echo "To install NordVPN on macOS:"
    echo "  brew install nordvpn"
    echo ""
    exit 1
fi

echo "✓ NordVPN CLI found: $(nordvpn --version)"
echo ""

# Prompt for email
read -p "📧 Enter your NordVPN email: " NORDVPN_USER
echo ""

# Prompt for password (hidden)
read -s -p "🔐 Enter your NordVPN password: " NORDVPN_PASS
echo ""
echo ""

# Test the credentials by attempting login
echo "🔐 Testing credentials with NordVPN..."
echo ""

if nordvpn login --username "$NORDVPN_USER" --password "$NORDVPN_PASS" 2>&1 | grep -qi "logged in"; then
    echo "✅ Login successful!"
    echo ""
    echo "Your credentials are working. Export them as environment variables:"
    echo ""
    echo "  export NORDVPN_USER='$NORDVPN_USER'"
    echo "  export NORDVPN_PASS='$NORDVPN_PASS'"
    echo ""
    echo "Or add to your shell config (~/.zshrc or ~/.bash_profile):"
    echo ""
    echo "  export NORDVPN_USER='$NORDVPN_USER'"
    echo "  export NORDVPN_PASS='$NORDVPN_PASS'"
    echo ""
    echo "💾 Would you like me to add these to your shell config? (y/n): "
    read -r ADD_TO_CONFIG
    
    if [[ "$ADD_TO_CONFIG" =~ ^[Yy]$ ]]; then
        SHELL_RC="$HOME/.zshrc"
        
        # Add to .zshrc
        {
            echo ""
            echo "# NordVPN Credentials (STEP 26)"
            echo "export NORDVPN_USER='$NORDVPN_USER'"
            echo "export NORDVPN_PASS='$NORDVPN_PASS'"
        } >> "$SHELL_RC"
        
        echo "✅ Credentials added to $SHELL_RC"
        echo ""
        echo "Reload your shell: source $SHELL_RC"
    fi
else
    echo "❌ Login failed. Please check your credentials."
    echo ""
    echo "Possible reasons:"
    echo "  • Incorrect email or password"
    echo "  • 2FA is enabled (see note below)"
    echo ""
    exit 1
fi

# Logout (cleanup)
nordvpn logout 2>&1 > /dev/null || true

echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "ℹ️  2FA (Two-Factor Authentication) Note:"
echo ""
echo "If 2FA is enabled on your NordVPN account, the CLI login might fail."
echo "You have these options:"
echo ""
echo "1. RECOMMENDED: Disable 2FA in your NordVPN account settings"
echo "   (The CLI doesn't support 2FA authentication)"
echo ""
echo "2. ALTERNATIVE: Check if NordVPN offers app-specific passwords"
echo "   (Not always available, depends on your account)"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
