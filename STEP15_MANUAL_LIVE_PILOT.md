# STEP 15 — Manual Live Crawl Pilot

**Status:** Design + Execution Plan (Manual Run)  
**Pilot Date:** [To Be Scheduled]  
**Duration:** Single 2-hour execution window  
**Scope:** Sahibinden, single city, 10–20 apartment listings  
**Supervisor:** [To Be Assigned]  
**Audience:** Developers, Ops, Product (decision-makers)

---

## 1. Executive Summary

### What This Is

A **controlled, single-run live crawl experiment** to test:
- Real HTTP handling (not synthetic data)
- Extraction logic against live HTML
- Block detection accuracy
- Data integrity safeguards
- Team's ability to monitor and abort

### What This Is NOT

- ❌ Continuous monitoring
- ❌ Automated crawling (STEP 16/17 decision)
- ❌ Large-scale testing
- ❌ Feature optimization

### Why Now

- ✅ STEP 1–13 are complete and validated
- ✅ STEP 14 policy is defined and approved
- ✅ We need one **ground truth run** before scaling decisions
- ✅ Blockers are known (Sahibinden blocks aggressive crawling); pilot tests our response

### Success Criteria

| Outcome | Result | Next Step |
|---------|--------|-----------|
| **Success** | ≥90% extraction, ≤5% errors, no blocks, clean data | Proceed to STEP 16 (automation design) |
| **Partial Success** | ≥80% extraction, ≤10% errors, 1 block, recoverable | Adjust rules, rerun once |
| **Failure** | <80% extraction OR persistent blocks OR data quality issues | Escalate; may need proxy strategy (Phase 2) |

---

## 2. Pilot Scope

### 2.1 Domain & Geography

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Domain** | sahibinden.com | Known to block; good test of defense mechanisms |
| **Category** | Apartment rental | Most common listings |
| **City** | Istanbul | Largest market; most frequent updates |
| **District** | Taksim or similar | ~50–100 listings max |
| **URLs** | 10–20 (manually selected) | Bounded; prevents accidental scaling |
| **Page Load Rate** | 1 per 3–5 seconds | Below rate limit; allows monitoring |

### 2.2 URL Selection Strategy

**Manual Curation (Not Automated Crawl):**

1. Visit sahibinden.com search UI directly
2. Filter: Apartment, Istanbul, Taksim, last 7 days
3. Screenshot or note 10–20 listing URLs
4. Store in `/examples/pilot_urls.txt`:

```
https://www.sahibinden.com/arama/listing/id/XXXXX
https://www.sahibinden.com/arama/listing/id/XXXXX
...
(15 URLs total)
```

**URL Quality Checks:**
- ✓ URLs point to active listings (non-404)
- ✓ Mix of new and old listings
- ✓ Mix of high and low prices (tests data range)
- ✓ At least 5 with images (tests HTML size variation)
- ✓ At least 2 with special characters (tests encoding)

### 2.3 Execution Window

**Date & Time (UTC):**
- **When:** Off-peak hours (e.g., Sunday 2–4 AM UTC, or Thursday 11 PM–1 AM UTC)
- **Why:** Lower site traffic; reduces competition for resources; easier to spot if we're detected
- **Duration:** 2 hours maximum (hard stop)
- **Backup Window:** [+1 week, same time] if aborted on first attempt

**Timezone Conversion:**
```
UTC 2–4 AM    = Istanbul 5–7 AM (early morning, low traffic)
UTC 11 PM–1 AM = Istanbul 2–4 AM (very low traffic)
```

---

## 3. Execution Checklist

### 3.1 Pre-Flight (24 Hours Before)

**Configuration Audit:**

- [ ] Rate limiter configured: 5 req/min (per STEP 14)
- [ ] Timeout set to 15 seconds
- [ ] Max concurrent connections: 1 (single-threaded; safest)
- [ ] Request delay: 3–5 seconds between requests (manual control)
- [ ] User-Agent: Realistic (e.g., `Mozilla/5.0 ... Chrome/120.0`)
- [ ] Referer: None (don't reveal scraper intent)

**Database Audit:**

- [ ] Backup taken: `mongodump --out /backups/pilot_backup_{timestamp}`
- [ ] Backup verified: Can restore (test on replica if available)
- [ ] Target collection empty or understood (is this an update run?)
- [ ] Schema validated: All expected fields present
- [ ] Indexes present: Query performance OK

**Code Audit:**

- [ ] Extraction rules reviewed (compare to STEP 9 parser)
- [ ] Block detection logic confirmed (STEP 14 § 4.1)
- [ ] Cooldown logic in place (hardcoded 24h for Sahibinden)
- [ ] Logging statements confirmed (each request logged)
- [ ] No debug mode enabled (no verbose output spam)

**Network Audit:**

- [ ] DNS resolution works: `nslookup sahibinden.com`
- [ ] HTTPS connectivity: `openssl s_client -connect sahibinden.com:443`
- [ ] No proxy configured (direct connection, as per STEP 14)
- [ ] Firewall: No outbound blocks to sahibinden.com
- [ ] Latency reasonable: `ping -c 3 sahibinden.com` (should be <100ms)

**Team Audit:**

- [ ] Supervisor assigned and confirmed available
- [ ] Kill-switch procedure practiced (everyone knows how to stop)
- [ ] Slack #data-ops channel prepared for real-time updates
- [ ] On-call engineer aware (for escalation)
- [ ] Database admin available (in case of emergency rollback)

**Pre-Flight Sign-Off:**

```
Checklist Lead: ________________     Date: ________________
Database Owner: ________________     Date: ________________
Supervisor: ________________     Date: ________________
```

### 3.2 Launch (Start of Execution Window)

**T-30 min: Final Readiness**

- [ ] All team members online and in Slack
- [ ] Monitor dashboard open (disk, memory, network, DB)
- [ ] Log file monitoring ready: `tail -f /logs/pilot_{date}.log`
- [ ] Backup verified once more: Restore test successful
- [ ] Kill-switch procedure confirmed one more time

**T-0: Crawl Start**

```bash
# Example command (pseudocode; adjust for actual CLI)
python -m src crawl \
  --mode manual_pilot \
  --input-file /examples/pilot_urls.txt \
  --domain sahibinden.com \
  --rate-limit 5 \
  --timeout 15 \
  --concurrent 1 \
  --abort-on-block \
  --log-file /logs/pilot_2026-02-02.log \
  --report-file /reports/pilot_2026-02-02.json \
  --run-id pilot_sahibinden_20260202

# Launch in dedicated terminal window
# Supervisor attaches to terminal and never leaves
```

**Supervisor's Role During Run:**

```
Every 30 seconds, check:
  ✓ Log file updates (new requests appear)
  ✓ Error count rising? (should stay < 2)
  ✓ Blocks detected? (watch for 403, 429, captcha)
  ✓ Database inserts working? (check DB logs)
  ✓ Latency reasonable? (< 15s per request)
  ✓ Network connectivity stable?

Every 5 minutes, log status:
  "T+5min: 5 requests processed, 0 errors, 0 blocks, DB OK"
  "T+10min: 10 requests processed, 1 timeout, 0 blocks, DB OK"
  ...

If any alarm triggers:
  1. Pause (don't abort immediately)
  2. Investigate (15-second window)
  3. Decide: resume or abort
  4. Log decision with reason
```

### 3.3 Runtime Monitoring Signals

**Green Flags (Good Signs):**

| Signal | Indicates | Action |
|--------|-----------|--------|
| Status 200 on all requests | Server accepts us | Continue |
| Response size 50–500 KB | Normal HTML payload | Continue |
| Latency 2–5 seconds | Server responding normally | Continue |
| Parse success 100% | Extraction logic working | Continue |
| Zero error-pattern matches | No 403, 429, captcha | Continue |
| Database inserts atomic | No conflicts | Continue |

**Yellow Flags (Pause & Investigate):**

| Signal | Indicates | Action |
|--------|-----------|--------|
| Status 200 but response < 1 KB | Blank page or error page | Pause; inspect HTML |
| Latency > 10s (1–2 requests) | Server slow or suspicious | Wait 30s; resume |
| Parse success 80–90% | Some extraction failures | Check log; continue if pattern clear |
| 1× 403 on any request | Possible bot detection | Pause; wait 60s; one retry |
| Database insert warning (non-fatal) | Schema mismatch or validation fail | Log; continue with next URL |
| Network timeout (>15s) | Connection issue | Pause; wait 30s; retry once |

**Red Flags (Abort Immediately):**

| Signal | Indicates | Action |
|--------|-----------|--------|
| 2+ consecutive 403 | Site blocking us | **ABORT ALL** |
| 429 status code | Rate limit hit | **ABORT ALL** |
| Captcha page detected | Bot wall | **ABORT ALL** |
| Database write error | Can't store data safely | **ABORT ALL** |
| Memory spike (>1 GB) | Memory leak or bomb | **ABORT ALL** |
| Disk < 500 MB | Risk of corruption | **ABORT ALL** |
| Connection refused | Server offline or blocking | **ABORT ALL** |

### 3.4 Abort Conditions

**Hard Stops (No Human Override):**

1. **2 consecutive 403s** → Stop immediately
2. **1 × 429** → Stop immediately
3. **Captcha detected** → Stop immediately
4. **Database write failure** → Stop immediately
5. **Supervisor's discretion** (any concern) → Stop immediately

**Soft Pauses (Investigate, Then Decide):**

1. **Single timeout** → Pause 30s; retry once; if fails again, skip URL
2. **Single 503/502** → Pause 60s; retry once; if fails again, skip URL
3. **Parse error on 1 URL** → Log; skip URL; continue
4. **High latency (>10s)** → Log; continue if consistent
5. **Duplicate URL error** → Log; skip; continue

**Kill Switch Procedure:**

```bash
# In supervisor's terminal:
# Press Ctrl+C to stop gracefully
# If stuck (unresponsive), kill process:
kill -TERM $(pgrep -f "python -m src crawl")

# Wait 10 seconds for graceful shutdown
# If still running:
kill -KILL $(pgrep -f "python -m src crawl")

# Verify killed:
ps aux | grep crawl

# Immediately after kill:
1. Save log file (cp /logs/pilot_*.log /logs/pilot_*.ABORTED.log)
2. Post to Slack: "ABORT: [reason], processed N/15 URLs"
3. Do NOT run cleanup or retry (manual decision required)
```

---

## 4. Expected Outcomes

### 4.1 Success Scenario

**What We Expect:**

```
✓ 15 URLs fetched successfully (100%)
✓ 0 HTTP errors (0 failures)
✓ 0 blocks (no 403, 429, captcha)
✓ 15 records extracted and parsed (100% parse success)
✓ 15 records inserted into database (100% write success)
✓ All records pass schema validation
✓ Extraction confidence > 0.95 for all fields
✓ Run completes in < 15 minutes
✓ No supervisor intervention needed
```

**What We'll Do:**

```
1. Wait 24 hours (cooldown courtesy)
2. Run second batch: 15 more URLs (validate repeatability)
3. If second batch also succeeds:
   → Approve STEP 16 (automation design)
   → Plan Phase 2 (real-time updates, proxy negotiation)
4. If second batch fails:
   → May indicate Sahibinden is detecting pattern
   → Escalate; may need proxy strategy earlier
```

**Confidence Level:** ⭐⭐⭐⭐⭐ (High; ready to proceed)

---

### 4.2 Partial Success Scenario

**What We Might See:**

```
✓ 12/15 URLs fetched (80%)
✓ 2 timeouts (requests slow or server unresponsive)
✓ 1 403 Forbidden (possible block, isolated)
✓ 12 records extracted (80% parse success)
✓ 12 records inserted (100% write of extracted data)
✓ 12 records pass schema validation
✓ Extraction confidence 0.90–0.95 for most fields
✓ Run completes in 20–25 minutes
✓ 1 supervisor pause (to investigate 403)
```

**What We'll Do:**

```
1. Analyze: Is 403 a real block or a fluke?
   - Check logs: error_code, response_body, timestamp
   - If isolated: likely fluke (server-side issue, not bot detection)
   - If patterns: may indicate detection
2. Wait 48–72 hours (extended courtesy cooldown)
3. Run second batch with same configuration
4. If second batch repeats:
   → 403 is repeatable (Sahibinden recognizes us)
   → May need to adjust: User-Agent, referer, delays
   → Or escalate: need proxy strategy
5. If second batch succeeds:
   → First run was fluke; proceed normally
   → Approve STEP 16
```

**Confidence Level:** ⭐⭐⭐⭐ (Medium-High; proceed with caution)

---

### 4.3 Failure Scenario

**What We Might See:**

```
✗ < 10 URLs fetched (< 67%)
✗ Multiple timeouts (server unresponsive)
✗ 2+ 403s (site blocking)
✗ 1 captcha (bot detection confirmed)
✗ Parse errors on > 20% of fetched pages
✗ Database write errors (critical)
✗ < 50% records successfully inserted
✗ Schema validation fails on >10% of records
✗ Supervisor forced to abort (kill-switch triggered)
```

**What We'll Do:**

```
1. Analyze failure root cause:
   - Is it HTTP (site blocking)?
   - Is it parsing (extraction logic broken)?
   - Is it database (storage failure)?
   - Is it network (our connection issue)?
2. Do NOT immediately retry (respect cooldown, site's signal)
3. Escalate decision:
   - If HTTP block: Need proxy strategy (Phase 2)
   - If parsing: Fix extraction rules (return to STEP 9)
   - If database: Fix schema/storage (return to STEP 5)
   - If network: Investigate infrastructure
4. Await product decision:
   - Accept proxy cost for automation?
   - Focus on API integration instead?
   - Pause crawling indefinitely?
5. Schedule retry: Not before [+2 weeks]
```

**Confidence Level:** ⭐ (Low; do not proceed without major changes)

---

## 5. Metrics to Collect

### 5.1 HTTP Metrics

**Per Request:**

```json
{
  "request_id": "uuid",
  "timestamp": "2026-02-02T02:30:45Z",
  "url": "https://www.sahibinden.com/arama/listing/id/XXXXX",
  "method": "GET",
  "status_code": 200,
  "response_size_bytes": 127345,
  "latency_ms": 2340,
  "error": null
}
```

**Aggregate (Per Run):**

- Total requests: 15
- Successful (200): 15 (100%)
- Client errors (4xx): 0 (0%)
- Server errors (5xx): 0 (0%)
- Timeouts: 0
- Average latency: 2.8s
- Min latency: 1.2s
- Max latency: 5.1s
- Response size range: 45 KB – 320 KB

### 5.2 Extraction Metrics

**Per Page:**

```json
{
  "request_id": "uuid",
  "parsed_fields": {
    "title": {
      "extracted": "3-bedroom apartment near Taksim",
      "confidence": 0.98,
      "schema_valid": true
    },
    "price": {
      "extracted": 50000,
      "confidence": 0.95,
      "schema_valid": true
    },
    ...
  },
  "total_fields_extracted": 18,
  "total_fields_valid": 18,
  "parse_success": true,
  "parse_error": null
}
```

**Aggregate (Per Run):**

- Pages attempted: 15
- Pages successfully parsed: 15 (100%)
- Pages failed to parse: 0 (0%)
- Total fields extracted: 270 (18 fields × 15 pages)
- Valid fields: 268 (99%)
- Invalid fields: 2 (0.7%)
- Parse errors: 0
- Average confidence per field: 0.96

**Confidence Distribution:**

```
0.95–1.00: 250 fields (92%)
0.90–0.95: 18 fields (7%)
0.80–0.90: 2 fields (1%)
<0.80: 0 fields (0%)
```

### 5.3 Database Metrics

**Per Insertion:**

```json
{
  "request_id": "uuid",
  "collection": "listings_pilot",
  "operation": "insert_one",
  "status": "success",
  "inserted_id": "mongodb_id_...",
  "latency_ms": 45,
  "error": null
}
```

**Aggregate (Per Run):**

- Insert attempts: 15
- Inserts successful: 15 (100%)
- Inserts failed: 0 (0%)
- Write errors: 0
- Average insert latency: 48ms
- Max insert latency: 120ms
- Schema validation errors: 0

### 5.4 Block Detection Metrics

**Monitoring:**

- 403 Forbidden: 0
- 429 Too Many Requests: 0
- Captcha detected: 0
- Blank pages: 0
- Content mismatch: 0
- SSL errors: 0
- DNS errors: 0
- Connection refused: 0

### 5.5 Data Quality Metrics

**Completeness:**

```
Required fields present: 15/15 (100%)
Optional fields present: 13/15 (87%)
Images extracted: 10/15 (67%)
Descriptions complete: 15/15 (100%)
Location info complete: 15/15 (100%)
```

**Consistency:**

```
Price format consistent: 15/15 (100%)
Date format consistent: 15/15 (100%)
Field types match schema: 15/15 (100%)
No duplicates detected: 15/15 (100%)
```

---

## 6. Post-Run Validation

### 6.1 Immediate (During Run: T+0 to T+30 min)

**Live Monitoring:**

- [ ] Console output shows requests processed
- [ ] Log file grows (new entries every 10s)
- [ ] Database inserts appear in real-time (optional: run count query)
- [ ] No error spikes in supervisor's observation
- [ ] Supervisor documents timeline in `/reports/pilot_2026-02-02_TIMELINE.txt`

**Example Timeline:**

```
T+2:00  Run started, processing pilot_urls.txt
T+3:45  5 requests processed, 0 errors, 0 blocks
T+8:30  10 requests processed, 0 errors, 0 blocks
T+14:00 15 requests processed, 0 errors, 0 blocks
T+14:15 Database inserts verified (count = 15)
T+14:30 Run completed successfully
```

### 6.2 Immediate Post-Run (T+30 to T+60 min)

**Database Validation:**

```javascript
// Query: Verify all records inserted
db.listings_pilot.count({ run_id: "pilot_sahibinden_20260202" })
// Expected: 15

// Query: Check for duplicates
db.listings_pilot.aggregate([
  { $match: { run_id: "pilot_sahibinden_20260202" } },
  { $group: { _id: "$url", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
// Expected: 0 results (no duplicates)

// Query: Verify schema compliance
db.listings_pilot.find(
  { run_id: "pilot_sahibinden_20260202" },
  { title: 1, price: 1, location: 1 }
)
// Spot-check: All required fields present, no nulls
```

**File Validation:**

- [ ] Log file written: `/logs/pilot_2026-02-02.log` (~5–10 MB)
- [ ] Report file written: `/reports/pilot_2026-02-02.json` (~50–100 KB)
- [ ] Backup intact: `/backups/pilot_backup_pre.dump` (restore test?)
- [ ] No sensitive data in logs (passwords, tokens)

**Data Sample Spot-Check:**

```bash
# Pick 3 random records; inspect manually
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client['crawler_db']
for doc in db.listings_pilot.find({'run_id': 'pilot_sahibinden_20260202'}).limit(3):
    print(doc)
"
# Check: Do prices look reasonable? Titles sensible? Dates correct?
```

### 6.3 24-Hour Post-Run Review

**Data Quality Report:**

```
Requested to produce: /reports/pilot_2026-02-02_REVIEW.md

# Pilot Run Review: Sahibinden, 15 URLs, 2026-02-02

## Run Summary
- URLs processed: 15/15 (100%)
- HTTP success: 15/15 (100%)
- Parse success: 15/15 (100%)
- Database inserts: 15/15 (100%)
- Runtime: 14 minutes
- Blocks detected: 0

## HTTP Metrics
- Status codes: All 200
- Response sizes: 45–320 KB
- Latency: 1.2–5.1s (avg 2.8s)
- Errors: 0

## Extraction Metrics
- Fields extracted: 270/270 (100%)
- Average confidence: 0.96
- Schema validation errors: 0

## Block Signals
- 403 Forbidden: 0
- 429 Rate limited: 0
- Captcha detected: 0
- Blank pages: 0

## Decision
✅ SUCCESS: Proceed to batch 2 (24h cooldown observed)
   or
⚠️  PARTIAL: Investigate [specific issue], re-run in 48h
   or
❌ FAILURE: Escalate to product; may need proxy strategy
```

---

## 7. GO / NO-GO Decision Matrix

### 7.1 Decision Criteria

**Automatic GO (Proceed with Batch 2):**

```
IF (
  http_success_rate >= 95% AND
  parse_success_rate >= 95% AND
  database_write_rate >= 95% AND
  blocks_detected == 0 AND
  supervisor_assessment == "PASS"
)
THEN: "GO — Proceed with Batch 2"
```

**Automatic NO-GO (Escalate to Product):**

```
IF (
  http_success_rate < 80% OR
  parse_success_rate < 80% OR
  database_write_rate < 80% OR
  blocks_detected >= 2 OR
  supervisor_assessment == "FAIL"
)
THEN: "NO-GO — Escalate; requires fixes"
```

**Manual Review (Conditional GO):**

```
IF (
  80% <= http_success_rate < 95% OR
  80% <= parse_success_rate < 95% OR
  80% <= database_write_rate < 95% OR
  blocks_detected == 1 OR
  supervisor_assessment == "CONDITIONAL"
)
THEN: "CONDITIONAL GO — Fix [issue], retest"
```

### 7.2 Decision Matrix Table

| Metric | GO | CONDITIONAL | NO-GO |
|--------|----|-----------|----|
| **HTTP Success Rate** | ≥95% | 80–95% | <80% |
| **Parse Success Rate** | ≥95% | 80–95% | <80% |
| **Database Write Rate** | ≥95% | 80–95% | <80% |
| **Blocks Detected** | 0 | 1 | ≥2 |
| **Extraction Confidence** | ≥0.95 | 0.90–0.95 | <0.90 |
| **Schema Compliance** | 100% | 90–100% | <90% |
| **Supervisor Assessment** | "PASS" | "CONDITIONAL" | "FAIL" |

**Outcome:**

- **All GO:** ✅ Proceed immediately
- **Mix of GO/CONDITIONAL:** ⚠️ Review conditional metrics; may proceed with caution
- **Any NO-GO:** ❌ Stop; escalate; do not retry without fixes

### 7.3 Decision Logic

```
If "GO" on ≥6/7 metrics:
  → Batch 2 approved (same config, repeat 24h later)
  → If Batch 2 also GO: STEP 16 automation design approved
  → If Batch 2 fails: Investigate why (Sahibinden detection?)

If "CONDITIONAL" on 2–3 metrics:
  → Identify root cause of each
  → Apply fix (e.g., adjust rate limit, fix parser)
  → Rerun once (same URLs or new batch; supervisor decision)
  → Re-evaluate

If any "NO-GO":
  → Stop immediately
  → Escalate to product team
  → Schedule product decision meeting
  → Do NOT retry without approval + documented fix
```

---

## 8. Post-Mortem Template

### 8.1 Post-Mortem Document Structure

**File:** `/reports/pilot_2026-02-02_POST_MORTEM.md`

**Template:**

```markdown
# Pilot Post-Mortem: Sahibinden Live Crawl

**Date:** 2026-02-02  
**Supervisor:** [Name]  
**Duration:** [actual time, e.g., 14 minutes]  
**Status:** [SUCCESS | PARTIAL | FAILURE]  

## Executive Summary
[1 paragraph: what happened, did we achieve goal?]

## Metrics Summary
- URLs processed: X/15
- HTTP success: X/15 (Y%)
- Parse success: X/15 (Y%)
- Blocks: [0 | 1 | 2+]
- Supervisor interventions: [0 | 1 | N]

## Timeline
[Extracted from TIMELINE.txt; key events]

T+2:00  Run started
T+3:45  First 5 requests OK
...
T+14:30 Run completed

## What Went Well
- [ ] HTTP handling robust
- [ ] Parser extracted cleanly
- [ ] Database writes fast
- [ ] No supervisor needed
- [ ] [other]

## What Didn't Go Well
- [ ] Single timeout (URL X) — may be flaky
- [ ] Parser missed field in 1 record — selector outdated?
- [ ] [other]

## Blocks Encountered
[If any]
- 403 Forbidden on URL: [link]
  - Status: Isolated or pattern?
  - Action: Skip or investigate?
  - Cooldown: Observed [24h | other]

## Data Quality Assessment
- Completeness: [%]
- Consistency: [Y/N]
- Duplication: [0 duplicates]
- Schema compliance: [%]
- Extraction confidence: [avg %]

## Root Cause Analysis
[If failures or issues]
- Issue: [description]
- Root cause: [why did it happen?]
- Preventive measure: [how to avoid next time?]

## Recommendations
- [ ] Proceed to Batch 2 (same config, 24h later)
- [ ] Adjust config before Batch 2 (specify)
- [ ] Fix extraction rule (specify)
- [ ] Escalate (specify reason)
- [ ] Halt crawling (specify reason)

## Decision
**GO / NO-GO / CONDITIONAL:** [Decision based on metrics]

**Justification:** [1-2 sentences]

## Next Steps
1. [Action]
2. [Action]
3. [Action]

---
**Signed:** [Supervisor name + date]  
**Reviewed by:** [Manager/Tech lead name + date]
```

### 8.2 What Gets Documented

**Always Document:**
- ✅ Exact URLs processed (in report JSON)
- ✅ Exact response codes per URL
- ✅ Parse errors with HTML snippets (first 500 chars)
- ✅ Database insert errors (if any)
- ✅ Block signals (403, 429, captcha)
- ✅ Timing (latencies, duration)
- ✅ Supervisor notes (any concerns, pauses)
- ✅ Data sample (3–5 example records from DB)

**Never Document:**
- ❌ Full HTML responses (too much data)
- ❌ Full database records (privacy concern)
- ❌ Passwords, API keys, auth tokens
- ❌ Personal employee information

### 8.3 Decision Logic from Post-Mortem

**Outcome: SUCCESS → Decision**

```
If all metrics ≥95% and blocks == 0:
  → Proceed to STEP 16 immediately
  → Schedule Batch 2 for 24h later (optional; for validation)
  → Start automation design
```

**Outcome: PARTIAL → Decision**

```
If metrics 80–95% and blocks == 1:
  → Identify root cause (parse rule? timeout? Sahibinden?)
  → Fix or document workaround
  → Retest: Batch 2 with same config (validate repeatable)
  → If Batch 2 succeeds: Proceed to STEP 16
  → If Batch 2 fails: Escalate; may need proxy strategy
```

**Outcome: FAILURE → Decision**

```
If metrics <80% or blocks ≥2:
  → Escalate to product team immediately
  → Product decides: 
     a) Fix (return to STEP 9/11, retry)
     b) Proxy strategy (Phase 2 planning)
     c) Pause crawling (focus on other features)
  → Do NOT retry without documented approval + fixes
```

---

## 9. Pre-Pilot Checklist (Final)

### Pre-Execution (48 Hours Before)

- [ ] Supervisor name and availability confirmed
- [ ] Backup tested (can restore in <5 minutes)
- [ ] Rate limiter code reviewed (5 req/min hardcoded)
- [ ] URLs manually selected and saved to `/examples/pilot_urls.txt`
- [ ] Log file path confirmed: `/logs/pilot_2026-02-02.log`
- [ ] Report file path confirmed: `/reports/pilot_2026-02-02.json`
- [ ] Kill-switch procedure documented and practiced
- [ ] Slack #data-ops channel set to "do not disturb" (notifications on)
- [ ] Team informed (developers, ops, product)

### 24 Hours Before

- [ ] Configuration audit checklist completed (§ 3.1)
- [ ] Database audit checklist completed (§ 3.1)
- [ ] Network audit checklist completed (§ 3.1)
- [ ] All checklists signed off

### 1 Hour Before

- [ ] Supervisor online and ready
- [ ] Monitor dashboard open
- [ ] Kill-switch procedure confirmed once more
- [ ] All team members notified (now or about to start)

### At Launch

- [ ] Supervisor attached to terminal
- [ ] Crawl command ready (copy-paste, no typing)
- [ ] Abort criteria written on paper (physical reference)
- [ ] Post-mortem template opened in editor (ready for notes)

---

## 10. Risk Assessment

### 10.1 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Sahibinden blocks us immediately** | Run aborts, 0 data | Expected risk; 24h cooldown; retry later |
| **Parser broken on live HTML** | Parse errors > 50% | Pre-flight parser audit; test samples first |
| **Database write fails** | Partial data loss | Backup + test restore; abort on write error |
| **Network connectivity lost** | Run hangs or fails | Monitor network; timeout 15s (kill after) |
| **Supervisor makes wrong abort call** | Lose valid data / collect bad data | Clear abort criteria; documented signals |
| **Concurrent crawl detected** | Data corruption | Ensure no other crawls running; lock file |
| **Disk full during run** | Crash; data loss | Monitor disk; check before launch (>1 GB free) |
| **Supervisor falls asleep** | Unmonitored crawling | Single-batch 2h max; alarm at T+1h |

### 10.2 Contingency Plans

**If Sahibinden Blocks Immediately:**
```
→ Stop crawl (abort trigger hit)
→ Wait 24 hours
→ Retry Batch 2 in 24h window
→ If blocked again: Escalate to product
  (May need proxy strategy or different approach)
```

**If Parser Broken:**
```
→ Abort run (fix required)
→ Return to STEP 9 (parser validation)
→ Fix extraction logic
→ Test on synthetic data first
→ Reschedule pilot when ready
```

**If Database Write Fails:**
```
→ Abort run immediately (data integrity risk)
→ Restore database from backup
→ Investigate write error (schema? connection?)
→ Fix issue
→ Restart pilot
```

**If Network Lost:**
```
→ Kill process immediately
→ Check connectivity (ping sahibinden.com)
→ Save any partial logs
→ Wait for network restoration
→ Restart pilot (if within 24h window)
```

---

## 11. Success Metrics Summary

### If Pilot Succeeds: What We Know

✅ Live HTML extraction works (real data, not synthetic)  
✅ Our parser is durable (edge cases handled)  
✅ Block detection is accurate (we know when to stop)  
✅ Database can handle live inserts (no corruption)  
✅ Team can monitor and abort (process works)  
✅ Sahibinden doesn't permanently block us (reputationally OK)  

### What We Can Build Next

→ **STEP 16:** Automated crawling design (per STEP 14 policy)  
→ Proxy negotiation (Phase 2, if needed)  
→ Real-time update strategy  
→ Multi-domain expansion  
→ Production infrastructure  

---

## 12. Appendix: Related Documents

- **STEP 14:** Live Crawling Policy (must follow strictly)
- **STEP 11:** CLI Structure (commands and modes)
- **STEP 9:** Parser Usage (extraction logic)
- **STEP 5:** Database schema (collection structure)
- **FETCHER_USAGE.md:** HTTP client constraints

---

## 13. Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-02 | 1.0 | Initial design document |

---

## Sign-Off

**This is a DESIGN DOCUMENT for a MANUAL PILOT RUN.**

**Before execution:**

1. ✓ Supervisor acknowledged and assigned
2. ✓ Pre-flight checklist completed and signed
3. ✓ Team notified (Slack, email)
4. ✓ This document reviewed by tech lead / manager

**After execution:**

1. ✓ Post-mortem completed within 24 hours
2. ✓ Decision (GO / CONDITIONAL / NO-GO) documented
3. ✓ Next steps communicated to product team

**Guiding Principle:** Safety > Speed. Data Integrity > Volume. Abort Early.

---

*End of STEP15_MANUAL_LIVE_PILOT.md*
