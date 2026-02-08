# STEP 14 — Live Crawling Policy

**Status:** Design Document (No Implementation)  
**Effective:** February 2, 2026  
**Purpose:** Define safe, ethical, and sustainable guidelines for live property listing extraction  
**Audience:** Developers, DevOps, Legal/Compliance, Product Managers

---

## 1. Why This Exists

### The Problem
We have a **validated, proven crawler system** (Steps 1–13) that works reliably against static test data and synthetic fixtures. Moving to live production crawling introduces:

- **Ethical risk:** Aggressive crawling damages business reputation and violates terms of service
- **Legal risk:** Automated extraction may violate computer fraud/abuse laws in some jurisdictions
- **Technical risk:** Live sites block, rate-limit, or serve poisoned data
- **Data risk:** Partial or concurrent updates corrupt our database
- **Sustainability risk:** Fast blocking → reactive escalation → permanent ban

### The Solution
This policy enforces **safety-first, data-integrity-first decision-making** before any live crawling occurs. It explicitly prevents:

- Uncontrolled automation that damages reputation
- Blind scaling without detection/response mechanisms
- Data poisoning from partial updates
- Indefinite retries that annoy site operators
- "Move fast and break things" mentality

**Principle:** Abort early, not late. When in doubt, stop.

---

## 2. Live Crawling Permission Policy

### 2.1 When Live Crawling IS Allowed

**Manual Validation Mode** (Human-Initiated, Supervised)
- **Who:** Developers or authorized researchers only
- **When:** Validating extraction logic against live data (bounded, ad-hoc)
- **Duration:** Minutes to hours, not continuous
- **Supervision:** Human actively monitors logs in real-time
- **Approval:** No formal gate (developer discretion)
- **Scope:** Single domain, single page category at a time
- **Rate:** ≤ 5 requests/minute (see § 3.2)
- **Example:** "Let me verify the price parser against current sahibinden.com pages"

**Manual Production Crawl** (Human-Initiated, Bounded)
- **Who:** Developers or senior engineers
- **When:** Scheduled historical snapshots (weekly/monthly baseline)
- **Duration:** Hours, with clear start/stop times
- **Supervision:** Human monitors exceptions and blocks; prepared to abort
- **Approval:** Documented plan filed in team Slack/issue tracker
- **Scope:** All domains, all categories (within budget)
- **Rate:** ≤ 20 requests/minute sustained, ≤ 50 requests/minute burst (see § 3)
- **Frequency:** No more than 1× per calendar day per domain
- **Fallback:** Must have manual kill-switch and abort criteria defined **before launch**
- **Example:** "Sunday 2am snapshot of all listings for last 7 days"

**Automated Crawling** (Policy TBD)
- **Current Status:** NOT PERMITTED (requires separate future policy)
- **When Allowed:** Only after Phase 2 planning (estimated Q3 2026)
- **Prerequisites:** 
  - Live ops team in place
  - Site operator agreement obtained
  - Rate limits formally negotiated
  - Automated detection/response system deployed and tested
  - Database failsafe mechanisms proven
- **Note:** Automated crawling requires its own policy document (STEP 15)

### 2.2 When Live Crawling MUST Stop

**Automatic Abort Triggers** (No human discretion)

| Trigger | Action | Cooldown |
|---------|--------|----------|
| 403 Forbidden (≥5 consecutive) | Stop domain immediately | 24 hours |
| 429 Too Many Requests | Stop domain immediately | 4 hours |
| Captcha wall detected | Stop domain immediately | 7 days |
| Connection timeout (≥3 consecutive, >30s) | Stop domain, investigate network | 2 hours |
| Domain becomes inaccessible (≥10 min) | Stop domain | 1 hour |
| SSL/TLS certificate invalid | Stop domain | 24 hours |
| Response body size anomaly (>2× normal) | Stop domain, manual review | 1 hour |

**Manual Abort Triggers** (Human judgment, immediate effect)

- Team member safety concern (any)
- Suspected data corruption or poisoning
- Legal/compliance red flag
- Monitor alarms (high error rates, unusual patterns)
- Time-based abort (reached planned end time)
- Resource exhaustion (disk, memory, database connection pool)
- Site operator contact (direct email, support request, Whois contact)

**Escalation Path:**
1. **Immediate:** Stop crawling for that domain
2. **Within 5 minutes:** Notify #data-ops Slack channel with reason code
3. **Within 30 minutes:** Post-incident log summary (errors, counts, abort reason)
4. **Within 24 hours:** Retrospective with blocking analysis

### 2.3 No Permission Required For

- Running test suite against synthetic data (test_*.py)
- Dry-run CLI mode (see STEP 11)
- Validation mode with --dry-run flag
- Analyzing historical live data already in database

---

## 3. Traffic Budget

### 3.1 Global Constraints (All Domains Combined)

| Metric | Limit | Rationale |
|--------|-------|-----------|
| **Per minute** | 30 req/min sustained | Stays under "bot" radar; friendly to shared hosting |
| **Per hour** | 1,200 req/hour | ≈20 requests/minute average |
| **Per day** | 28,800 req/day | ≈10 hours of steady crawling |
| **Concurrent connections** | ≤ 4 | Prevents connection pool exhaustion |
| **Request timeout** | 15 seconds | Aggressive sites are often slow |

### 3.2 Per-Domain Constraints

| Metric | Limit | Rationale |
|--------|-------|-----------|
| **Per minute** | 20 req/min | Majority of budget for one domain |
| **Per hour** | 800 req/hour | ≈13 requests/minute average |
| **Per day** | 20,000 req/day | ≈5 hours of dedicated crawling |
| **Time between requests** | ≥ 3 seconds | Politeness; avoids connection pooling issues |
| **Requests within 10-min window** | ≤ 150 | Burst limits (15 req/min × 10 min) |

### 3.3 Burst Behavior

**Allowed:** Start at lower rate, gradually increase per domain after successful requests  
**Not Allowed:** Rapid spike to max rate; hammer a single page with retries

**Example Schedule (Validation Mode):**
```
Minute 0–2:   5 req/min (warm-up, test connectivity)
Minute 2–10:  10 req/min (steady extraction)
Minute 10+:   Stop and analyze
```

### 3.4 Budget Resets

- **Per-minute**: Rolling window (last 60 seconds)
- **Per-hour**: Calendar hour (XX:00–XX:59 UTC)
- **Per-day**: UTC midnight (00:00 UTC)
- **Per-domain daily**: Reset at same UTC time globally

### 3.5 Budget Enforcement

**Method:** In-memory rate limiter (token bucket)

```
for each request:
  if global_requests_this_minute >= 30:
    wait until next minute
  if domain_requests_this_minute >= 20:
    wait until reset
  if domain_requests_this_hour >= 800:
    pause domain for 1 hour
  if time_since_last_request < 3 seconds:
    wait (3s - time_since_last_request)
  send request
  log: timestamp, domain, status, size, latency
```

**No Excuses:** These are hard limits. Not soft guidelines. Not "usually respected." Hard.

---

## 4. Block Detection & Response

### 4.1 What Counts as a Block

**HTTP Status Codes (5xx = investigation, not abuse)**

| Code | Interpretation | Action |
|------|-----------------|--------|
| 403 Forbidden | Site explicitly rejects; may indicate bot detection | **BLOCK DOMAIN** |
| 429 Too Many Requests | Rate limit exceeded (explicit) | **BLOCK DOMAIN** (respect the signal) |
| 401 Unauthorized | Auth required; we don't have it | Check if proxy needed; else BLOCK |
| 410 Gone | Content permanently deleted | Ignore (not a block) |
| 5xx Server Error | Site problem, not us | **RETRY** with backoff |
| Timeout (>30s) | Slow server or network path issue | **INVESTIGATE** (see § 4.3) |

**Content Patterns (Heuristic Signals)**

| Pattern | Evidence | Action |
|---------|----------|--------|
| **Captcha page** | HTML contains reCAPTCHA, hCaptcha, or "prove you're human" | **BLOCK DOMAIN** for 7 days |
| **Redirect loop** | ≥3 Location headers in sequence | **INVESTIGATE** |
| **Blank response** | Status 200 but body < 500 bytes (not a normal listing page) | **BLOCK DOMAIN** (1 hour cooldown) |
| **Content mismatch** | Expected selector (e.g., .listing-title) not found in ≥90% of pages | **PAUSE DOMAIN** (manual review) |
| **IP geofencing** | Repeated 403 or "access denied" message | Contact ops; may need proxy rotation (Phase 2) |

### 4.2 Block Thresholds

**Trigger after:**

| Condition | Threshold | Action |
|-----------|-----------|--------|
| 403 errors | 5 consecutive | Stop domain; cooldown 24h |
| 429 errors | 1 occurrence | Stop domain; cooldown 4h |
| Captcha | 1 occurrence | Stop domain; cooldown 7d |
| Timeout (>30s) | 3 consecutive | Stop domain; investigate network; cooldown 2h |
| Blank responses | 10% of responses | Stop domain; manual review |
| SSL errors | Any | Stop domain; cooldown 24h |

**No escalation:** Once threshold is hit, stop. Do not test "just one more" time.

### 4.3 Cool-Down Strategies

**Cooldown Duration:**

- **2 hours:** Temporary network issues, timeout-related
- **4 hours:** Rate limit (429) detected
- **24 hours:** 403, SSL errors, or data integrity concern
- **7 days:** Captcha or human verification detected

**Cool-Down Behavior:**

```
for domain in blocked_domains:
  if current_time < blocked_domain.cooldown_until:
    skip domain entirely
  else:
    clear block; allow resume on next run
```

**Manual Extension:**

Team lead can extend cooldown beyond automatic window if:
- Site operator contact received
- Legal/compliance review flagged concerns
- Data quality issues detected in that domain's records

### 4.4 Abort Rules

**STOP ALL CRAWLING IF:**

1. ≥3 domains blocked simultaneously (site-wide defense detected)
2. Unrecoverable database error (cannot write data)
3. Disk space < 500 MB (prevent corruption)
4. Cumulative error rate > 40% over 1 hour
5. Manual kill switch activated
6. Team member escalates in Slack with "ABORT"

**PAUSE (Don't stop all, just this domain) IF:**

1. Single domain 403 (but continue other domains)
2. Single domain timeout (but continue other domains)
3. Data quality concern limited to one domain

---

## 5. Failure Taxonomy

### 5.1 Failure Classes

**A. Network Failures** (Infrastructure/transport)

| Failure | Root Cause | How to Log | How to Act |
|---------|-----------|-----------|-----------|
| Timeout | Server slow or unreachable | `network_timeout: {duration_ms, domain}` | Retry with backoff; abort if ≥3× |
| Connection refused | Server offline or blocking | `connection_refused: {domain, ip}` | Cooldown 1h; may indicate block |
| SSL error | Certificate invalid or revoked | `ssl_error: {domain, error}` | Cooldown 24h; investigate separately |
| DNS failure | Domain not resolvable | `dns_error: {domain}` | Cooldown 1h; not a crawling issue |
| No route to host | Network path broken | `network_unreachable: {domain}` | Cooldown 1h; investigate ISP/routing |

**B. Content Failures** (Server responds, but data unusable)

| Failure | Root Cause | How to Log | How to Act |
|---------|-----------|-----------|-----------|
| Blank page | 200 OK but HTML empty/malformed | `content_blank: {domain, size_bytes}` | Cooldown 1h; manual review |
| Captcha | Bot detection triggered | `captcha_detected: {domain}` | Cooldown 7d; escalate |
| 403 Forbidden | Access explicitly denied | `forbidden: {domain}` | Cooldown 24h; likely blocklist |
| 429 Rate limited | Rate limit hit (explicit) | `rate_limited: {domain}` | Cooldown 4h; respect signal |
| Malformed data | Parser fails (selector not found, parse error) | `parse_error: {domain, page_url, error}` | Log and skip page; continue domain |

**C. Policy Failures** (Violates our rules)

| Failure | Root Cause | How to Log | How to Act |
|---------|-----------|-----------|-----------|
| Budget exceeded | Reached per-domain or global limit | `budget_exceeded: {domain, metric, limit}` | Pause domain; reset at window boundary |
| Cooldown active | Domain in cooldown window | `cooldown_active: {domain, until_time}` | Skip domain; try again later |
| Duplicate request | Requesting same URL within 24h | `duplicate_request: {domain, url, last_fetch_time}` | Skip request; log for dedup stats |
| Unsafe abort trigger | Threshold met | `abort_trigger: {domain, reason, threshold}` | Stop domain; increment block counter |

**D. Data Failures** (Data quality/integrity)

| Failure | Root Cause | How to Log | How to Act |
|---------|-----------|-----------|-----------|
| Partial update | Run interrupted; some records incomplete | `partial_update: {run_id, records_pending}` | Flag run as "INCOMPLETE"; do not use for analysis |
| Poisoned data | Content changed mid-crawl; out-of-order timestamps | `poisoned_data: {domain, records_affected, reason}` | Mark records with `data_quality: SUSPECT`; manual review |
| Schema mismatch | Record doesn't match expected schema | `schema_error: {domain, record_id, error}` | Reject record; log to report; continue crawl |
| Concurrency collision | Two crawls updated same listing simultaneously | `concurrency_collision: {listing_id, run_ids}` | Mark later record as superseded; keep both with timestamps |

### 5.2 Logging Format

**All failures logged to:** `/logs/{YYYY-MM-DD}.log`

**Standard Format:**
```
[TIMESTAMP] [LEVEL] [CODE] [DOMAIN] [DETAIL]
LEVEL: NETWORK, CONTENT, POLICY, DATA, ERROR, WARN, INFO
CODE: timeout, forbidden, rate_limited, blank_page, captcha_detected, parse_error, budget_exceeded, etc.

Example:
[2026-02-02 15:43:22] [NETWORK] [timeout] [sahibinden.com] duration_ms=31200, retries_remaining=0
[2026-02-02 15:43:25] [CONTENT] [rate_limited] [hepsiemlak.com] cooldown_until=2026-02-02_19:43:25
[2026-02-02 15:44:10] [DATA] [poisoned_data] [sahibinden.com] records_affected=3, reason=concurrent_update_detected
```

### 5.3 Failure Thresholds

**Per Run:**

- Abort if ≥ 40% of all requests fail
- Abort if ≥ 3 domains blocked simultaneously
- Warn if ≥ 20% of requests fail
- Warn if parser errors > 5% of valid responses

**Per Domain:**

- Block if 5 consecutive 403s
- Block if 1 × 429
- Block if 1 × captcha
- Block if 3 consecutive timeouts
- Warn if error rate > 30% for that domain

**Per Day:**

- If ≥ 4 domains blocked, review traffic budget
- If cumulative bandwidth > 500 MB, flag for review
- If >1,000 parse errors across all domains, review extraction logic

---

## 6. Execution Modes

### 6.1 Validation Mode

**Purpose:** Verify extraction logic against live data (supervised, bounded)

**Command:**
```bash
python -m src validate --domain sahibinden.com --category apartment --limit 5 --dry-run
```

**Constraints:**
- ≤ 5 requests/minute
- ≤ 10 minutes duration (hard stop)
- Single domain + category
- Dry-run flag (no database writes)
- Requires terminal monitoring (not background)

**Output:**
- Console log with extraction results
- No database modifications
- Report saved to `/reports/validation_{timestamp}.json`

**When to Use:**
- "Does the parser work on current pages?"
- "What does a live page look like now?"
- "Let me test one domain before full run"

**When NOT to Use:**
- Continuous monitoring
- Full-coverage extraction
- Automated scheduling

---

### 6.2 Manual Production Crawl

**Purpose:** Bounded, supervised full extraction (all domains, all categories)

**Command:**
```bash
python -m src crawl \
  --mode production \
  --domains all \
  --rate-limit 20 \
  --timeout 15 \
  --abort-on-block \
  --report-file /reports/crawl_{timestamp}.json \
  --supervisor-email ops@example.com
```

**Constraints:**
- ≤ 20 req/min sustained, ≤ 50 req/min burst (global)
- ≤ 20 req/min per domain
- Human monitors logs in real-time (terminal attached)
- Explicit abort criteria defined before launch
- Maximum 8-hour continuous run
- Supervisor email/Slack notification for blocks

**Pre-Launch Checklist:**

- [ ] Database backup created (+ verify restore works once)
- [ ] Abort criteria documented in Slack/issue
- [ ] Kill-switch procedure known to team
- [ ] Monitoring dashboard open (disk, memory, DB)
- [ ] Team member assigned as "on-call" for run
- [ ] Time-based stop time documented (e.g., "stops at 3 AM UTC")

**Abort Criteria (Examples):**

```
ABORT immediately if:
- 403 on 3+ domains
- Captcha detected on any domain
- Database insert error
- Disk space < 500 MB
- Error rate > 40%
- Database latency > 2s (per insert)
- Manual kill-switch activated
```

**Output:**
- Real-time console log (must stay attached)
- Database records inserted (live)
- Report file: `/reports/crawl_{timestamp}.json` with:
  - Requests sent / received
  - Errors by category
  - Domains blocked
  - Data quality stats
  - Run abort reason (if any)

**Post-Run:**
- Manual spot-check: Query 10 random new records
- Validate schema compliance
- Compare against previous crawl (new vs updated)
- File retrospective if any blocks occurred

**When to Use:**
- Weekly/monthly baseline snapshot
- Testing new extraction rules against live data
- Validating data model changes

**When NOT to Use:**
- Continuous background monitoring
- Automated/unattended operation
- "Just one more domain" after planned end time

---

### 6.3 Future Automated Mode (Policy TBD)

**Current Status:** NOT PERMITTED

**Will Be Required For:**
- Real-time listing updates
- Scheduled background jobs
- 24/7 monitoring

**Requires (Prerequisites):**
- [ ] Separate governance policy document (STEP 15)
- [ ] Automated block detection + response system
- [ ] Database failsafe (rollback, dedup, conflict resolution)
- [ ] Ops team trained and on-call
- [ ] Monitoring/alerting fully deployed
- [ ] Site operator agreement (if applicable)
- [ ] Legal review completed
- [ ] Rate limit negotiation (if applicable)
- [ ] Proxy rotation system (if applicable)

**Policy Will Cover:**
- Automated scheduling constraints
- Self-healing recovery logic
- Escalation thresholds
- Database consistency guarantees
- Monitoring + alerting rules

---

## 7. Data Safety Guarantees

### 7.1 Preventing Partial/Poisoned Data

**During a Crawl Run:**

1. **Transactions:** Each page extraction is atomic
   ```
   insert {domain, url, data, timestamp, run_id}
   OR rollback if parse error
   ```

2. **Run Tagging:** Every record includes:
   - `run_id`: Unique identifier (UUID)
   - `crawl_start`: Timestamp of crawl start
   - `crawl_duration`: How long run took
   - `data_freshness`: Time between crawl and live page

3. **Heartbeat Logging:** Every 100 requests, log status:
   ```
   [15:30:00] Processed 100 records (sahibinden: 45, hepsiemlak: 55)
   [15:30:00] Errors: 2 timeouts, 1 parse fail
   [15:30:00] Blocks: none
   [15:30:00] Database: 100 inserts OK, 0 conflicts
   ```

4. **No Partial Writes on Error:**
   - If parse fails → skip page, continue domain
   - If database fails → log error, **pause domain**, don't retry indefinitely
   - If abort triggered → stop immediately, don't queue pending requests

### 7.2 When to Discard Runs Entirely

**Mark Run as "INVALID" (Do Not Use) If:**

| Condition | Reason | Action |
|-----------|--------|--------|
| Abort triggered before 50% completion | Insufficient coverage | Mark `run_status: INCOMPLETE` |
| ≥3 domains blocked | Site-wide defense likely | Mark `run_status: COMPROMISED` |
| Cumulative error rate > 40% | Data quality suspect | Mark `run_status: HIGH_ERROR_RATE` |
| Database write failure > 5% | Data integrity risk | Mark `run_status: WRITE_ERRORS` |
| Human abort (kill-switch) | Reason TBD by team | Mark `run_status: ABORTED` + reason |
| Concurrent crawl detected (same domain) | Conflict risk | Mark `run_status: CONCURRENT_RUN` |

**Recovery:**
```
If run marked INVALID:
  - Don't use for analytics
  - Don't publish to API
  - Log reason in `/reports/{run_id}_INVALID.txt`
  - Retry in next scheduled window (don't re-run immediately)
```

### 7.3 Tagging Live Data vs Synthetic

**Every Record Includes:**

```json
{
  "id": "...",
  "domain": "sahibinden.com",
  "data": { ... },
  "metadata": {
    "source": "live_crawl" | "synthetic" | "manual_entry",
    "run_id": "uuid-...",
    "crawl_timestamp": "2026-02-02T15:30:00Z",
    "data_freshness_seconds": 3,
    "extraction_confidence": 0.95,
    "run_status": "VALID" | "INCOMPLETE" | "COMPROMISED" | "HIGH_ERROR_RATE"
  }
}
```

**Usage Rules:**

- **Live data** (`source: live_crawl`): Use for production analysis only if `run_status: VALID`
- **Synthetic data** (`source: synthetic`): Use for testing, demos, backup analysis
- **Manual data** (`source: manual_entry`): Use for validation/verification only

**Database Query Example:**
```javascript
// Only valid live data
db.listings.find({
  "metadata.source": "live_crawl",
  "metadata.run_status": "VALID",
  "metadata.crawl_timestamp": { $gte: ISODate("2026-01-01") }
})
```

### 7.4 Conflict Resolution

**If Two Crawls Update Same Listing:**

```json
// Record 1 (older run)
{
  "id": "listing-123",
  "run_id": "run-A",
  "crawl_timestamp": "2026-02-01T10:00:00Z",
  "price": 500000,
  "status": "active"
}

// Record 2 (newer run, same listing)
{
  "id": "listing-123",
  "run_id": "run-B",
  "crawl_timestamp": "2026-02-02T10:00:00Z",
  "price": 490000,
  "status": "active"
}
```

**Policy:**
- Keep both records
- Mark Record 1 as superseded by Record 2
- Use Record 2 for current state
- Use Record 1 for historical trend analysis
- Log: `superseded_by: "run-B"`

**Database Schema (pseudo):**
```
listings:
  - id
  - run_id
  - crawl_timestamp
  - data (price, status, etc.)
  - superseded_by (reference to newer run_id, nullable)
  - is_current (boolean, true = latest for this listing)
```

---

## 8. Execution Rules (DO / DO NOT)

### DO ✅

- ✅ Start with validation mode to test new domains
- ✅ Respect rate limits; exceed by 0% (hard stop)
- ✅ Stop immediately upon hitting block thresholds
- ✅ Log every failure with category code (NETWORK, CONTENT, POLICY, DATA)
- ✅ Monitor real-time logs during production crawls
- ✅ Pause domains; don't retry failed requests forever
- ✅ Tag live data with run_id and crawl_timestamp
- ✅ Mark invalid runs as such (don't silently use bad data)
- ✅ Abort early (at 40% error rate, not 50%)
- ✅ File post-incident summaries if blocks occurred
- ✅ Use cooldown periods; don't test "just once more"
- ✅ Keep database backups before each production crawl
- ✅ Have kill-switch procedure known to team
- ✅ Document abort criteria before launch
- ✅ Escalate policy violations immediately

### DO NOT ❌

- ❌ Automate crawling without separate STEP 15 policy
- ❌ Exceed traffic budget by "just a little bit"
- ❌ Retry rate-limited (429) requests immediately
- ❌ Ignore captcha walls; they're permanent blocks
- ❌ Write poisoned data without marking it invalid
- ❌ Run concurrent crawls on same domain
- ❌ Use live data from INVALID runs for analytics
- ❌ Resume domain before cooldown expires
- ❌ Hammer a single page with sequential retries
- ❌ Run unattended production crawls
- ❌ Increase rate limits "just for today"
- ❌ Bypass abort triggers with manual overrides
- ❌ Ignore team escalation (ABORT message)
- ❌ Mix synthetic and live data in same dataset without tagging
- ❌ Crawl without pre-run checklist
- ❌ Assume "it'll work this time" after being blocked

---

## 9. Summary Table: When to Do What

| Scenario | Mode | Supervisor | Duration | Rate | Approval | Action if Blocked |
|----------|------|------------|----------|------|----------|-------------------|
| "Does parser work on real data?" | Validation | Required | ≤10 min | 5/min | None | Cooldown 1-2h; try again |
| "Weekly baseline snapshot" | Production | Required | ≤8h | 20/min | Slack doc | Cooldown 24h; escalate |
| "CI/CD test automation" | Test (synthetic) | Not required | Minutes | Unlimited | None | N/A (test fails) |
| "Real-time monitoring" | (TBD) Automated | N/A | 24/7 | TBD | STEP 15 | TBD |
| "One-off domain verification" | Validation | Required | ≤5 min | 5/min | None | Cooldown 2h; document |
| "Compliance audit (historical)" | Query DB | Not required | Minutes | 0 (DB only) | None | N/A (no crawling) |

---

## 10. Appendix: Related Documents

- **STEP 1-13:** Crawler system design, implementation, validation
- **STEP 15:** Automated crawling policy (future; will reference this document)
- **SCHEMA.md:** Data model and record structure
- **FETCHER_USAGE.md:** HTTP client constraints and retry logic
- **NORMALISER_RULES.md:** Data extraction and validation rules
- **CLI_STRUCTURE.md:** Command-line interface and modes

---

## 11. Document History

| Date | Status | Changes |
|------|--------|---------|
| 2026-02-02 | Draft | Initial policy document; design only |

---

## Sign-Off

**This document is a DESIGN DOCUMENT. It contains no code, no infra, no automation.**

**Before any live crawling occurs, this policy must be:**
1. ✓ Reviewed by team
2. ✓ Acknowledged in Slack (explicit consent)
3. ✓ Posted in team docs (accessible reference)

**Live crawling is currently BLOCKED until:**
- This policy is approved
- Execution modes are tested against synthetic data
- Team has practiced kill-switch procedure
- Pre-run checklist is integrated into runbook

**Guiding Principle:** Safety > Coverage. Data Integrity > Volume. Reputation > Speed.

---

*End of STEP14_LIVE_CRAWLING_POLICY.md*
