# Setup Instructions - NordVPN Integration

## Step 1: Install NordVPN CLI

First, install NordVPN using Homebrew:

```bash
brew install nordvpn
```

This will download and install the NordVPN command-line interface on your Mac.

## Step 2: Enter Your Credentials

Run the credentials setup script I just created:

```bash
/Users/mustafaaksoz/Bot/setup_nordvpn_credentials.sh
```

Or simply:

```bash
cd /Users/mustafaaksoz/Bot
./setup_nordvpn_credentials.sh
```

This script will:
1. Check that NordVPN CLI is installed ✓
2. Prompt you for your NordVPN email
3. Prompt you for your NordVPN password (hidden input)
4. Test the login to verify credentials work
5. Ask if you want to save credentials to your shell config (~/.zshrc)
6. Provide guidance on 2FA if needed

## Step 3: Verify Installation

After running the setup script, verify everything is working:

```bash
echo $NORDVPN_USER
echo $NORDVPN_PASS
```

If both show your credentials, you're ready to proceed!

---

## ⚠️ About 2FA (Two-Factor Authentication)

### The Issue
If you have 2FA enabled on your NordVPN account, the CLI authentication **will likely fail** because:
- The NordVPN CLI doesn't natively support 2FA authentication
- It only supports email/password authentication

### Your Options

**Option 1: Disable 2FA (RECOMMENDED)** ✅
- Go to your NordVPN account settings: https://account.nordvpn.com/
- Disable Two-Factor Authentication
- The CLI will work perfectly
- Re-enable it later if desired (it's in your account settings)

**Option 2: Check for App-Specific Passwords**
- Some VPN providers offer app-specific passwords
- Log into your NordVPN account and check Settings → Security
- Look for "Application Passwords" or similar option
- If available, use the app password instead of your account password

**Option 3: Use a Different VPN Provider (Fallback)**
- If 2FA is critical to your security, consider:
  - ExpressVPN (has better CLI support)
  - Surfshark (CLI supports some forms of auth)
  - Proton VPN (some CLI options available)

### Recommendation

For this testing phase, I'd recommend **Option 1** (temporarily disable 2FA):

1. Go to https://account.nordvpn.com/
2. Settings → Security
3. Disable Two-Factor Authentication
4. Run the setup script
5. (Optional) Re-enable 2FA later after testing is complete

This takes 2 minutes and won't compromise your account security permanently.

---

## Quick Test After Setup

Once credentials are set, test the connectivity:

```bash
cd /Users/mustafaaksoz/Bot
python test_nordvpn_routing.py
```

Expected output:
```
✓ Credentials found
✓ NordVPN CLI available
✓ Logged in successfully
✓ Connected to Turkey VPN
✓ Disconnected from VPN
✓ VPN CONNECTIVITY TEST PASSED
```

---

## If You Get an Error

### Error: "Login failed"
**Cause**: 2FA is enabled or credentials are wrong
**Solution**: Check 2FA is disabled, verify email/password

### Error: "Connection failed"
**Cause**: NordVPN service not running
**Solution**: 
```bash
brew services start nordvpn
nordvpn connect Turkey
```

### Error: "NordVPN CLI not installed"
**Cause**: Homebrew installation failed
**Solution**: 
```bash
# Try again
brew install nordvpn

# Or install via direct download
# https://downloads.nordcdn.com/apps/macos/general/nordvpn-installer.dmg
```

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Install NordVPN: `brew install nordvpn` | 2 min |
| 2 | Run setup script: `./setup_nordvpn_credentials.sh` | 1 min |
| 3 | (Optional) Disable 2FA in account settings | 2 min |
| 4 | Verify: `echo $NORDVPN_USER` | 1 min |
| **Total** | **Ready to test!** | **6 min** |

Ready? Run the setup script now:
```bash
/Users/mustafaaksoz/Bot/setup_nordvpn_credentials.sh
```
