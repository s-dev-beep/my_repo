# NordVPN Setup - macOS GUI App (Updated)

## ⚠️ Important Discovery

The NordVPN macOS app **does NOT include a command-line interface (CLI)**. The `brew install nordvpn` command installs the **GUI application only**.

This means we'll use the NordVPN app manually instead of automating it.

---

## ✅ What You Already Have

Good news! You already successfully installed NordVPN:
```
/Applications/NordVPN.app
```

---

## 🚀 Simple Setup (5 Minutes)

### Step 1: Open and Configure NordVPN App

Run this script to open the app:
```bash
/Users/mustafaaksoz/Bot/setup_nordvpn_manual.sh
```

Or manually:
```bash
open -a "NordVPN"
```

### Step 2: Log In & Connect to Turkey

In the NordVPN app:

1. **Log in** with your NordVPN credentials
   - Email: your_email@nordvpn.com
   - Password: your_password
   - ⚠️ If you have 2FA enabled, you'll need to disable it in account settings first

2. **Connect to Turkey:**
   - Click the search bar or country list
   - Type "Turkey" 
   - Click "Quick Connect" for Turkey
   - Wait for "Connected" status (green checkmark)

3. **Verify connection:**
   ```bash
   curl https://ipinfo.io/country
   ```
   Expected output: `TR` (Turkey)

### Step 3: Test Sahibinden Access

With VPN connected, run the test:
```bash
cd /Users/mustafaaksoz/Bot
python test_vpn_manual.py
```

Expected output:
```
✓ Current IP: 185.xxx.xxx.xxx
✓ Location: Istanbul, TR
✓ ISP: NordVPN
✅ Connected to Turkey VPN!

✓ Fetch successful: 45230 bytes
  Has listing content: True
  Has phone data: True
  Is error page: False
✅ SUCCESS! Sahibinden is accessible through VPN!
```

### Step 4: Run Full Test (10 URLs)

If Step 3 passes, run the complete test:
```bash
python src/experiments/live_access_test_vpn.py
```

This will test 10 URLs with realistic delays.

---

## 📊 Expected Results

**Before VPN (STEP 24):**
- Success: 0/3 (0%)
- All blocked with 403 errors

**After VPN (with Turkey connection):**
- Success: 7-9/10 (70-90%)
- Clean Turkey IP bypasses blocking

---

## 🔧 About 2FA (Two-Factor Authentication)

If you get "Login failed" in the NordVPN app:

1. Go to https://account.nordvpn.com/
2. Settings → Security
3. Disable "Two-Factor Authentication"
4. Try logging in again

The NordVPN macOS app **might** support 2FA (unlike the CLI), but disabling it temporarily makes setup easier.

---

## ⚙️ How This Works

Since we can't automate the VPN connection via CLI:

1. **You manually connect** via the NordVPN GUI app
2. **Our Python scripts** use the existing VPN connection automatically
3. **All HTTP requests** route through the VPN tunnel
4. **Sahibinden sees** a clean Turkey IP instead of your blacklisted IP

The connection happens at the **system network level**, so all Python requests automatically use it.

---

## 🧪 Quick Test Commands

```bash
# 1. Check if VPN is connected
curl https://ipinfo.io/country
# Expected: TR

# 2. Check current IP
curl https://ipinfo.io/ip
# Expected: NordVPN IP (185.x.x.x range)

# 3. Test single URL
python test_vpn_manual.py

# 4. Test 10 URLs with delays
python src/experiments/live_access_test_vpn.py
```

---

## ❓ FAQ

**Q: Do I need to keep the NordVPN app open?**
A: Yes, keep it running and connected while testing.

**Q: Can I automate this?**
A: Not easily on macOS. The GUI app doesn't provide CLI access. You could use OpenVPN directly (more complex setup) or keep the app running.

**Q: What if I still get 403 errors?**
A: The VPN IP might also be blacklisted. Try:
- Disconnect and reconnect (gets new IP)
- Try a different Turkey server
- Wait 5 minutes between attempts

**Q: How do I disconnect?**
A: Click "Disconnect" in the NordVPN app.

---

## 🎯 Next Steps

1. ✅ NordVPN app is installed
2. ⏳ Log in to NordVPN app
3. ⏳ Connect to Turkey
4. ⏳ Run: `python test_vpn_manual.py`
5. ⏳ Run: `python src/experiments/live_access_test_vpn.py`
6. ⏳ Verify 70%+ success rate

---

**Ready to test?** Connect to Turkey in the NordVPN app, then run:
```bash
python test_vpn_manual.py
```
