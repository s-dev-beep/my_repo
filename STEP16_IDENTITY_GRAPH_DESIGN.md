# STEP 16 — Phone-Anchored Identity Graph Architecture

**Date:** February 2, 2026  
**Status:** Design Document (Post-STEP 15 Pivot)  
**Purpose:** Define the transition from "listing crawler" to "agent identity graph"  
**Audience:** Engineering, Product, AI Agent Prompts

---

## Executive Context

After STEP 15 pilot validation, we confirmed:
- ✅ Crawler system is technically sound
- ❌ Sahibinden blocks aggressive listing extraction
- ✅ **Pivot opportunity:** Focus on agent identity, not listing volume

**New Mission:**  
Build a **phone-number-anchored identity graph** for Turkish real estate agents, prioritizing data quality and temporal integrity over listing coverage.

**Why This Works:**
- Phone numbers are stable (agents keep same number for years)
- Minimal crawling footprint (1 phone per listing, not 20+ fields)
- Enrichment-first strategy (cross-reference sources)
- City-district segmentation (Istanbul → Ankara → İzmir)

---

## 1. Canonical Data Contract

**Core Principle:**

> **Phone number is the identity anchor. Everything else is temporal, versioned, and evidence-backed.**

**Non-Negotiable Rules:**
- No destructive updates
- No silent overwrites
- History is a feature, not a bug
- Every field must have SourceEvidence

---

### 1.1 PhoneIdentity (ROOT ENTITY)

**Schema:**

```yaml
PhoneIdentity:
  phone_e164: string           # PRIMARY KEY (E.164 format: +905551234567)
  first_seen_at: datetime      # When we first discovered this phone
  last_seen_at: datetime       # Most recent observation
  sources:                     # List of platforms where observed
    - sahibinden
    - hepsiemlak
    - google
  status: enum                 # active | dormant | reassigned
  confidence_score: float      # 0.0 – 1.0 (based on cross-validation)
  observation_count: int       # How many times we've seen this phone
```

**Rules:**

1. **Never deleted** — Even if agent disappears
2. **Never merged** — One phone = one identity forever
3. **Exists even if name/office missing** — Phone-first approach
4. **Status transitions:**
   - `active`: Seen in last 30 days
   - `dormant`: Not seen for 30–180 days
   - `reassigned`: Evidence suggests phone changed ownership (conflict detection)

**MongoDB Collection:** `phone_identities`

**Indexes:**
```javascript
db.phone_identities.createIndex({ phone_e164: 1 }, { unique: true })
db.phone_identities.createIndex({ last_seen_at: -1 })
db.phone_identities.createIndex({ status: 1 })
```

---

### 1.2 AgentProfile (VERSIONED ENTITY)

**Schema:**

```yaml
AgentProfile:
  agent_profile_id: uuid       # Unique ID per name variant
  phone_e164: string           # FK → PhoneIdentity
  full_name: string            # Raw name as seen on listing
  normalized_name: string      # Uppercase, trimmed, normalized
  first_seen_at: datetime      # When this name variant appeared
  last_seen_at: datetime       # Last observation of this variant
  confidence: enum             # high | medium | low
  is_current: boolean          # True if most recent variant
```

**Rules:**

1. **Names are append-only** — Never overwrite
2. **Same phone + different name → new AgentProfile** — Track name changes
3. **"Latest" is inferred by `last_seen_at`** — Flag as `is_current: true`
4. **Name normalization:**
   - Uppercase all Turkish characters
   - Remove titles (Bay, Bayan, Mr., Ms.)
   - Trim whitespace
   - Detect encoding issues (ş vs. s, ı vs. i)

**Example:**

```javascript
// Same phone, three name variants over time
{
  agent_profile_id: "uuid-1",
  phone_e164: "+905551234567",
  full_name: "Ahmet Yılmaz",
  normalized_name: "AHMET YILMAZ",
  first_seen_at: "2025-01-15",
  last_seen_at: "2025-06-20",
  is_current: false
}
{
  agent_profile_id: "uuid-2",
  phone_e164: "+905551234567",
  full_name: "Ahmet Y.",
  normalized_name: "AHMET Y",
  first_seen_at: "2025-07-01",
  last_seen_at: "2025-10-30",
  is_current: false
}
{
  agent_profile_id: "uuid-3",
  phone_e164: "+905551234567",
  full_name: "Ahmet Yılmaz - Emlak Danışmanı",
  normalized_name: "AHMET YILMAZ",
  first_seen_at: "2025-11-01",
  last_seen_at: "2026-02-02",
  is_current: true
}
```

**MongoDB Collection:** `agent_profiles`

**Indexes:**
```javascript
db.agent_profiles.createIndex({ phone_e164: 1, last_seen_at: -1 })
db.agent_profiles.createIndex({ normalized_name: 1 })
db.agent_profiles.createIndex({ is_current: 1 })
```

---

### 1.3 AgentLocationHistory (TEMPORAL)

**Schema:**

```yaml
AgentLocationHistory:
  id: uuid
  phone_e164: string           # FK → PhoneIdentity
  city: string                 # Istanbul, Ankara, İzmir
  district: string             # Kadıköy, Beşiktaş, etc.
  start_date: datetime         # When agent started covering this area
  end_date: datetime | null    # Null if still active
  source: enum                 # sahibinden | hepsiemlak | google
  confidence: enum             # high | medium | low
```

**Rules:**

1. **Multiple active locations allowed** — Agents can cover multiple districts
2. **If new location appears → close old one** — Set `end_date` on previous
3. **City+district required for "active" status** — Missing = low confidence
4. **District-level granularity only** — No street addresses

**Example:**

```javascript
// Agent moved from Kadıköy to Üsküdar
{
  id: "uuid-1",
  phone_e164: "+905551234567",
  city: "Istanbul",
  district: "Kadıköy",
  start_date: "2025-01-15",
  end_date: "2025-11-01",
  source: "sahibinden",
  confidence: "high"
}
{
  id: "uuid-2",
  phone_e164: "+905551234567",
  city: "Istanbul",
  district: "Üsküdar",
  start_date: "2025-11-01",
  end_date: null,  // Still active
  source: "sahibinden",
  confidence: "high"
}
```

**MongoDB Collection:** `agent_location_history`

**Indexes:**
```javascript
db.agent_location_history.createIndex({ phone_e164: 1, end_date: 1 })
db.agent_location_history.createIndex({ city: 1, district: 1 })
db.agent_location_history.createIndex({ end_date: 1 })  // Null = active
```

---

### 1.4 OfficeEntity (ORGANIZATIONAL)

**Schema:**

```yaml
Office:
  office_id: uuid
  office_name: string
  normalized_name: string
  city: string
  district: string
  first_seen_at: datetime
  last_seen_at: datetime
  confidence: enum             # high | medium | low
  status: enum                 # active | inactive
```

**Rules:**

1. **Offices can change names → new entity, linked historically**
2. **Same name + different district ≠ same office**
3. **Office deduplication key:** `normalized_name + city + district`

**MongoDB Collection:** `offices`

**Indexes:**
```javascript
db.offices.createIndex({ normalized_name: 1, city: 1, district: 1 })
db.offices.createIndex({ last_seen_at: -1 })
```

---

### 1.5 AgentOfficeHistory (CRITICAL RELATIONSHIP)

**Schema:**

```yaml
AgentOfficeHistory:
  id: uuid
  phone_e164: string           # FK → PhoneIdentity
  office_id: uuid              # FK → Office
  role: enum                   # agent | partner | owner | unknown
  start_date: datetime
  end_date: datetime | null
  source: enum                 # sahibinden | hepsiemlak | google
  confidence: enum             # high | medium | low
```

**Rules:**

1. **One active office per agent at a time** — Soft rule (can be violated)
2. **Office changes are history events, not updates**
3. **Role detection:**
   - "Sahibi" → owner
   - "Ortak" → partner
   - Default → agent

**MongoDB Collection:** `agent_office_history`

**Indexes:**
```javascript
db.agent_office_history.createIndex({ phone_e164: 1, end_date: 1 })
db.agent_office_history.createIndex({ office_id: 1, end_date: 1 })
```

---

### 1.6 SourceEvidence (AUDIT & SAFETY)

**Schema:**

```yaml
SourceEvidence:
  id: uuid
  phone_e164: string           # FK → PhoneIdentity
  source: enum                 # sahibinden | hepsiemlak | google
  url: string                  # Original listing/page URL
  fields_detected:             # Which fields were extracted
    - phone
    - name
    - office
    - city
    - district
  raw_html_hash: string        # SHA256 of raw HTML (for verification)
  timestamp: datetime
  confidence: enum             # high | medium | low
```

**Rules:**

1. **Every field must be backed by at least one SourceEvidence**
2. **No inference without evidence** — If we didn't see it, we don't claim it
3. **Evidence is immutable** — Never deleted, even if data changes
4. **Used for conflict resolution** — If two sources disagree, check evidence

**MongoDB Collection:** `source_evidence`

**Indexes:**
```javascript
db.source_evidence.createIndex({ phone_e164: 1, timestamp: -1 })
db.source_evidence.createIndex({ source: 1, timestamp: -1 })
db.source_evidence.createIndex({ url: 1 })
```

---

## 2. Istanbul Discovery Stopping Algorithm

**Purpose:** Prevent infinite scraping and respect block detection.

---

### 2.1 Definitions

```text
NEW_PHONE_RATE = (new phones discovered in last N listings) / N
DISTRICT_COVERAGE = (districts with ≥ 10 agents) / (total Istanbul districts)
ACTIVE_PHONE_RATE = (phones seen in last 30 days) / (total phones)
```

**Parameters:**
- `N = 500` (sliding window size)
- `MIN_AGENTS_PER_DISTRICT = 10`
- `TOTAL_ISTANBUL_DISTRICTS = 39`

---

### 2.2 Hard Stop Conditions (ANY = ABORT)

```text
1. NEW_PHONE_RATE < 5% over last 500 listings
   → Diminishing returns; we've seen most agents

2. DISTRICT_COVERAGE ≥ 95%
   → 37/39 districts covered with ≥10 agents each

3. Consecutive 403/429 ≥ 2 within 60 minutes
   → Site blocking us; respect cooldown (STEP 14 policy)

4. Fetch failure rate ≥ 50%
   → Safety stop (STEP 14 § 4.4)
```

---

### 2.3 Soft Stop (Pause & Review)

```text
1. NEW_PHONE_RATE between 5–10%
   → Approaching saturation; manual review recommended

2. Repeated same phones across districts
   → Same agents covering multiple areas (expected, but log it)

3. Confidence drops below 85% average
   → Data quality degrading; may indicate site changes
```

**Action on Soft Stop:**
- Pause crawling for 24 hours
- Run data quality report
- Manually inspect 10 random new listings
- Decide: Resume or halt

---

### 2.4 Istanbul Completion Criteria

Istanbul is considered **DONE** when:

```text
✔ ≥90% of agents have:
   - phone (required)
   - city (required)
   - district (required)

✔ ≥85% have office association

✔ All 39 districts observed at least once

✔ No new phones discovered in last 7 days

✔ NEW_PHONE_RATE < 5% sustained for 1 week
```

**After Istanbul is DONE:**
- **Freeze Istanbul crawling** — No new listing extraction
- **Enrichment only** — Fill missing office/name data via Hepsiemlak/Google
- **Move to Ankara** — Repeat process

---

## 3. VS Code AI Agent — Master Prompt

**Purpose:** Standardize AI-assisted extraction for consistency.

**Copy this exactly into your AI agent configuration:**

```text
You are a senior data engineer and crawling architect.

Context:
- We are building a phone-number-anchored identity graph for real estate agents in Turkey.
- Phone numbers are immutable identity anchors.
- Names, offices, and locations are temporal and versioned.
- NO destructive updates.
- ALL data must be evidence-backed.

Objectives:
1. Extract from Sahibinden ONLY:
   - phone number (mandatory)
   - agent name (if present)
   - office name (if present)
   - city (required)
   - district (required)
2. Abort page processing immediately after extraction.
3. Never paginate deeply.
4. Never retry aggressively.
5. Prefer slow, single-request execution.

Rules:
- Phone number is mandatory; if missing → discard listing.
- City + district are required for "active" status.
- Do not deduplicate by name.
- Do not infer offices or locations.
- Always append history, never overwrite.
- Respect block detection and safety stops.

Priority Cities:
1. Istanbul (all 39 districts)
2. Ankara
3. İzmir

Output Format:
- Emit structured entities matching the Canonical Data Contract (STEP 16).
- Attach SourceEvidence for every extracted field.
- If blocked, STOP and report — do not attempt bypass.

Ethics & Safety:
- Public data only.
- No login, no session hijacking.
- No CAPTCHA solving.
- Abort early, not late.
- Follow STEP 14 Live Crawling Policy strictly.

You must follow this exactly. No exceptions.
```

---

## 4. Enrichment Workflow

**Purpose:** Fill missing data using secondary sources (Hepsiemlak, Google).

---

### 4.1 When Enrichment Is Triggered

```text
IF:
  - phone exists in PhoneIdentity
  - BUT (office_id IS NULL OR district IS NULL)
  - AND confidence < high
THEN:
  → Queue for enrichment
```

**Enrichment Queue Priority:**
1. Istanbul agents with missing office
2. Istanbul agents with missing district
3. Ankara agents (same logic)
4. İzmir agents (same logic)

---

### 4.2 Hepsiemlak Enrichment

**Search Key:** Phone number (exact match)

**Process:**

1. Query Hepsiemlak search API/UI for phone
2. Extract:
   - Office name
   - City
   - District
3. Compare with Sahibinden data:
   - **Match** → Raise confidence to `high`
   - **Conflict** → Append new AgentLocationHistory record; keep both
4. Insert SourceEvidence record

**Rules:**
- Hepsiemlak **never overrides** Sahibinden
- It only **confirms** or **extends** existing data
- Max 1 enrichment request per phone per 7 days

**Rate Limit:** 5 requests/minute (per STEP 14)

---

### 4.3 Google Enrichment (LAST RESORT)

**Targets:**
- Google Maps (office addresses)
- Office websites (contact pages)

**Extract:**
- Office address
- City
- District
- Phone match confirmation

**Rules:**
- Only enrich **offices**, not agents directly
- Only used when **both Sahibinden + Hepsiemlak** missing data
- Must manually verify 10% of Google-sourced data (spot-check)

**Rate Limit:** 3 requests/minute (per STEP 14)

---

### 4.4 Confidence Escalation Logic

```text
Sahibinden only                      → medium confidence
Sahibinden + Hepsiemlak (match)      → high confidence
Sahibinden + Hepsiemlak (conflict)   → medium confidence + history event
Sahibinden + Google (match)          → high confidence
All three sources (match)            → high confidence + flag for review
Conflict detected                    → medium confidence + manual review queue
```

**Example:**

```javascript
// Before enrichment
{
  phone_e164: "+905551234567",
  confidence_score: 0.7,  // medium
  sources: ["sahibinden"]
}

// After Hepsiemlak enrichment (match)
{
  phone_e164: "+905551234567",
  confidence_score: 0.95,  // high
  sources: ["sahibinden", "hepsiemlak"]
}
```

---

## 5. Migration from Current Schema

**Current System (STEP 1–15):**
- Listing-centric (listings → offices → agents)
- Destructive updates (upsert logic)
- No history tracking

**New System (STEP 16+):**
- Phone-centric (phones → agents → offices → locations)
- Append-only history
- Evidence-backed

---

### 5.1 Migration Steps

**Phase 1: Parallel Run (2 weeks)**

1. Deploy new schema (6 collections) alongside old
2. Run crawler in dual-write mode:
   - Write to old schema (listings, offices, agents)
   - Write to new schema (phone_identities, agent_profiles, etc.)
3. Compare outputs; validate consistency

**Phase 2: Backfill (1 week)**

1. Extract phones from existing `listings` collection
2. Create PhoneIdentity records
3. Create AgentProfile records (one per unique name)
4. Create SourceEvidence records (retroactive)
5. Mark all as `source: sahibinden`, `confidence: medium`

**Phase 3: Cutover (1 day)**

1. Stop crawler
2. Run final consistency check
3. Switch to new schema exclusively
4. Archive old schema (read-only)

**Phase 4: Enrichment Kickoff (ongoing)**

1. Queue all phones for Hepsiemlak enrichment
2. Process at 5 req/min
3. Track confidence score improvements

---

### 5.2 Data Quality Validation

**Before Migration:**
```bash
# Count unique phones in old schema
db.agents.distinct("phone_number").length

# Expected: ~5,000–10,000 (Istanbul pilot)
```

**After Migration:**
```bash
# Count PhoneIdentity records
db.phone_identities.countDocuments({})

# Should match old count ±5%
```

**Smoke Tests:**
```javascript
// Test: Every phone has at least one AgentProfile
db.phone_identities.aggregate([
  {
    $lookup: {
      from: "agent_profiles",
      localField: "phone_e164",
      foreignField: "phone_e164",
      as: "profiles"
    }
  },
  { $match: { profiles: { $size: 0 } } }
])
// Expected: 0 results

// Test: Every AgentProfile has SourceEvidence
db.agent_profiles.aggregate([
  {
    $lookup: {
      from: "source_evidence",
      localField: "phone_e164",
      foreignField: "phone_e164",
      as: "evidence"
    }
  },
  { $match: { evidence: { $size: 0 } } }
])
// Expected: 0 results
```

---

## 6. Why This Works (vs. Traditional Scraping)

### Traditional Scraper (Fails)

```
Problem: Scrapes all listing fields aggressively
→ High request volume
→ Triggers bot detection
→ Blocked within minutes
→ Requires proxies/CAPTCHAs
→ Cat-and-mouse escalation
→ Eventually banned
```

### Phone-Anchored Graph (Succeeds)

```
Approach: Extract minimal data (phone + location only)
→ Low request volume
→ Stays under radar
→ Enrichment happens offline (Hepsiemlak/Google)
→ Temporal history prevents re-scraping
→ Sustainable long-term
```

**Key Differences:**

| Aspect | Traditional Scraper | Phone-Anchored Graph |
|--------|-------------------|---------------------|
| **Goal** | All listing details | Agent identity only |
| **Requests** | 20+ fields × 1000s listings | 5 fields × 1 listing per phone |
| **Crawl Depth** | Infinite (new listings daily) | Finite (phones saturate) |
| **Update Strategy** | Re-scrape everything | Only new phones + enrichment |
| **Block Risk** | High (aggressive) | Low (minimal footprint) |
| **Data Quality** | Temporal snapshots | Historical timeline |

---

## 7. Implementation Roadmap

### Week 1: Schema Design

- [ ] Finalize MongoDB collections (6 collections)
- [ ] Create indexes
- [ ] Write migration scripts
- [ ] Deploy to staging

### Week 2: Parallel Run

- [ ] Dual-write mode (old + new schema)
- [ ] Run 500 listings through both pipelines
- [ ] Compare outputs
- [ ] Fix discrepancies

### Week 3: Backfill

- [ ] Migrate existing listings → PhoneIdentity
- [ ] Generate AgentProfile records
- [ ] Create SourceEvidence (retroactive)
- [ ] Validate data integrity

### Week 4: Cutover

- [ ] Switch to new schema exclusively
- [ ] Archive old schema
- [ ] Update CLI commands
- [ ] Update documentation

### Week 5+: Enrichment

- [ ] Queue all phones for Hepsiemlak enrichment
- [ ] Run at 5 req/min
- [ ] Monitor confidence score improvements
- [ ] Manual spot-checks (10% sample)

---

## 8. Success Metrics (6 Months)

### Coverage Metrics

```
✔ Istanbul: 10,000+ unique phones
✔ Ankara: 5,000+ unique phones
✔ İzmir: 3,000+ unique phones
✔ District coverage: ≥95% Istanbul districts
✔ Office association: ≥85% of agents
```

### Quality Metrics

```
✔ High confidence: ≥60% of phones
✔ Medium confidence: ≥35% of phones
✔ Low confidence: ≤5% of phones
✔ Conflict rate: <2% (sources disagree)
✔ Evidence coverage: 100% (every field backed)
```

### Operational Metrics

```
✔ Block rate: <5% (sustainable crawling)
✔ Enrichment success: ≥80% (Hepsiemlak matches)
✔ Crawl frequency: 1× per week (Istanbul), 2× per week (new cities)
✔ Database growth: <10 GB (year 1)
```

---

## 9. Appendix: Related Documents

- **STEP 14:** Live Crawling Policy (safety rules)
- **STEP 15:** Manual Live Pilot (validation results)
- **STEP15_PRODUCT_DECISION.md:** Strategic options post-pilot
- **SCHEMA.md:** Legacy schema (pre-STEP 16)

---

## 10. Final Reality Check

**What we are building is NOT a scraper.**

It's a:
- **Phone-anchored identity graph** (CRM-quality dataset)
- **Temporal agent history system** (tracks movements, name changes, office changes)
- **City-district segmented intelligence layer** (geographic coverage)
- **Enrichment-aware, safety-first platform** (cross-validates sources)

**Why this works long-term:**

1. **Minimal footprint** — 1 phone per listing, not 20 fields
2. **Finite goal** — Phones saturate; listings don't
3. **History preservation** — No need to re-scrape old data
4. **Enrichment offline** — Secondary sources fill gaps without hammering Sahibinden
5. **Safety-first** — Respects blocks, aborts early

**Why others fail:**

1. **Aggressive scraping** — Extract everything, get blocked
2. **Infinite treadmill** — New listings every day, never done
3. **Destructive updates** — Lose history, need to re-scrape
4. **Single source** — No validation, low confidence
5. **Cat-and-mouse** — Proxies, CAPTCHAs, escalation, ban

---

**This is the right architecture. Execute with discipline.**

---

*End of STEP16_IDENTITY_GRAPH_DESIGN.md*
