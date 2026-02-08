---
title: STEP 24 Results - Live Access Test Report
date: 2026-02-03
---

# STEP 24: Live Access Test Results

## Test Execution

**Goal:** Test 10 URLs with realistic 10-15 second delays between requests to determine if Sahibinden allows low-rate HTTP access.

**Configuration:**
- URLs: 10 listings from Sancaktepe district
- Delay: 10-15 seconds between requests (random)
- Retries: 0 (single attempt per URL)
- Proxy: Disabled
- Rate limit: 6 requests/minute

**Report:** [reports/step24_live_test.json](../reports/step24_live_test.json)

---

## Results

| Metric | Value |
|--------|-------|
| **Requests Attempted** | 3 (stopped at blocking) |
| **Successful** | 0/3 (0%) |
| **Blocked** | 1/3 (403 repeated) |
| **Errors** | 2/3 (403 status) |
| **Total Duration** | 24.2 seconds |
| **Blocked At Request** | #3 |

---

## Key Finding

**⚠️ SAHIBINDEN BLOCKS IMMEDIATELY ON FIRST REQUEST**

- Request 1: **403 Forbidden** (instantly)
- Request 2: **403 Forbidden** (instantly)
- Request 3: **Repeated blocking detected** (safety abort triggered)

**Status code: 403 (Forbidden)** - This is **not a rate limit (429)**, it's **active blocking**.

---

## Interpretation

Sahibinden is detecting and rejecting the HTTP requests **immediately**, even on the very first request, suggesting:

1. **Browser/User-Agent detection:** Standard Python HTTP client headers are detected as bot
2. **IP-based blocking:** IP may be pre-blacklisted or flagged as datacenter/VPN
3. **Active anti-scraping:** 403 Forbidden (not 429) indicates intentional block, not rate limit

---

## What This Means

| Approach | Verdict | Notes |
|----------|---------|-------|
| **More delays between requests** | ❌ Won't help | Blocking is immediate |
| **Session persistence** | ❌ Won't help | First request already blocked |
| **Stealth user-agent rotation** | ⚠️ Partial hope | Might help but not alone |
| **Residential proxy pool** | ✅ Likely solution | Different IPs bypass blocks |
| **Browser engine (Playwright)** | ✅ Worth testing | Renders JS, looks more human |
| **Their API** | ✅ Best solution | Direct data without scraping |

---

## Recommended Next Steps

### Immediate (Priority 1)
Test the **STEP 23 browser-based approach** with Playwright/Chromium to see if:
- JavaScript rendering helps
- Browser fingerprint is less detectable
- Session cookies are maintained

### Short-term (Priority 2)
**Investigate Sahibinden's mobile API:**
- Open browser DevTools
- Load a listing page
- Monitor Network tab for API calls
- Likely endpoints: `/api/search`, `/api/listing/`, GraphQL endpoints

### Medium-term (Priority 3)
**Contact Sahibinden directly:**
- Ask for data access agreement
- Offer value (lead generation, listings integration)
- Request API credentials
- Likely fastest path to success

### If evasion needed (Priority 4)
- **Residential proxy service** (ScraperAPI, Bright Data, etc.)
- **Cost:** $50-300/month depending on volume
- **Benefit:** Different IPs bypass the 403 block

---

## Data Points Saved

```
Run ID:      step24_20260203_020420
Test URLs:   3 attempted (stopped at blocking)
Duration:    24 seconds
Status:      BLOCKED IMMEDIATELY
Next Test:   STEP 23 Browser Feasibility (Playwright)
```

---

## Conclusion

**Direct HTTP scraping of Sahibinden is currently impossible without proxies.**

The 403 status code (not 429 rate limit) indicates active, intentional blocking of HTTP clients.

**Next phase:** Test browser-based access (STEP 23) to determine if rendering engines are allowed.
