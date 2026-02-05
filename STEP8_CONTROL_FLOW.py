"""
STEP 8: PIPELINE ORCHESTRATION - CONTROL FLOW VISUALIZATION

This document provides ASCII diagrams showing how the Crawler orchestrates
the complete pipeline.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL CONTROL FLOW
# ═══════════════════════════════════════════════════════════════════════════════

CONTROL_FLOW = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CRAWLER ORCHESTRATION                          │
└─────────────────────────────────────────────────────────────────────────────┘

INPUT: List[URL]
  │
  ├─► Initialize Components
  │   ├─ Fetcher (rate limiting, retries)
  │   ├─ Parser (site-specific adapter)
  │   ├─ Normalizer (data cleaning)
  │   ├─ Deduplicator (in-memory cache)
  │   └─ MongoDB (persistence)
  │
  ├─► Connect to MongoDB
  │
  └─► For Each URL:
      │
      ├─► STEP 1: FETCH
      │   ├─ Wait for rate limit
      │   ├─ Add random delay (politeness)
      │   ├─ HTTP GET request
      │   ├─ Retry on failure (3x with backoff)
      │   └─ Return HTML or raise FetchError
      │       │
      │       ├─► Success: html_content ─┐
      │       └─► Failure: log + continue ─┘
      │
      ├─► STEP 2: PARSE
      │   ├─ BeautifulSoup(html)
      │   ├─ Extract: office_name, agent_name, phone, city, district
      │   └─ Return Dict[str, Any] or None
      │       │
      │       ├─► Success: parsed_data ─┐
      │       └─► Failure: log + continue ─┘
      │
      ├─► STEP 3: NORMALIZE
      │   ├─ Uppercase names
      │   ├─ E.164 phone format
      │   ├─ Title case locations
      │   ├─ Detect source (sahibinden/hepsiemlak)
      │   └─ Calculate confidence (high/medium/low)
      │       │
      │       ├─► Success: normalized_data ─┐
      │       └─► Failure: log + continue ─┘
      │
      ├─► STEP 4: DEDUPLICATE (In-Memory)
      │   ├─ Check if URL in cache
      │   │   ├─ Yes → Mark as skipped
      │   │   └─ No → Add to cache
      │   └─ Continue to persist anyway
      │
      └─► STEP 5: PERSIST (Database)
          ├─ Upsert Office (name + phone)
          ├─ Upsert Agent (name + phone)
          ├─ Upsert Listing (URL)
          │   ├─ New → Insert (stats.inserted++)
          │   └─ Exists → Update (stats.updated++)
          └─ Return (listing_id, operation)

OUTPUT: CrawlStats
  ├─ total: 100
  ├─ fetched: 98
  ├─ parsed: 95
  ├─ normalized: 95
  ├─ inserted: 40
  ├─ updated: 55
  ├─ skipped: 5
  └─ failed: 5
"""


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING FLOW
# ═══════════════════════════════════════════════════════════════════════════════

ERROR_HANDLING = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ERROR HANDLING FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

For Each URL:
  │
  ├─ try:
  │   │
  │   ├─► FETCH
  │   │   ├─ Network timeout?
  │   │   │   └─► Retry with backoff (3x)
  │   │   │       ├─ Success → Continue
  │   │   │       └─ All failed → raise FetchError
  │   │   │
  │   │   ├─ HTTP 403/429 (blocking)?
  │   │   │   └─► Record block event
  │   │   │       ├─ < 5 blocks → Retry with backoff
  │   │   │       └─ ≥ 5 blocks → raise BlockedError
  │   │   │
  │   │   └─ HTTP 4xx/5xx?
  │   │       └─► raise FetchError
  │   │
  │   ├─► PARSE
  │   │   ├─ HTML invalid?
  │   │   │   └─► Return None → raise ValueError
  │   │   │
  │   │   └─ Element not found?
  │   │       └─► Return partial data (OK) or None
  │   │
  │   ├─► NORMALIZE
  │   │   ├─ Invalid phone format?
  │   │   │   └─► Return None (field optional)
  │   │   │
  │   │   └─ Missing listing_url?
  │   │       └─► raise ValueError
  │   │
  │   └─► PERSIST
  │       ├─ Validation error?
  │       │   └─► raise ValueError
  │       │
  │       └─ Connection error?
  │           └─► raise ConnectionFailure
  │
  └─ except Exception as e:
      ├─► Log error with full context
      ├─► Increment stats.failed
      └─► Continue with next URL

Result:
  ├─ Individual failures don't stop crawl
  ├─ All errors logged
  └─ Statistics show success rate
"""


# ═══════════════════════════════════════════════════════════════════════════════
# DEDUPLICATION STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

DEDUPLICATION = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TWO-LEVEL DEDUPLICATION                              │
└─────────────────────────────────────────────────────────────────────────────┘

Level 1: IN-MEMORY (Deduplicator)
  │
  ├─ Purpose: Catch duplicates in same crawl session
  ├─ Storage: Python set in memory
  ├─ Key: listing_url
  │
  └─ Flow:
      ├─ Check: url in self.listings?
      │   ├─ Yes → Mark as skipped (but still persist)
      │   └─ No → Add to set
      │
      └─ Advantage: Fast (O(1)), prevents redundant fetching

Level 2: DATABASE (MongoDB)
  │
  ├─ Purpose: Persistent deduplication across sessions
  ├─ Storage: MongoDB with unique indexes
  ├─ Keys:
  │   ├─ Listing: listing_url (unique index)
  │   ├─ Office: (office_name, phone_number) (compound index)
  │   └─ Agent: (agent_name, phone_number) (compound index)
  │
  └─ Flow:
      ├─ upsert_listing(normalized_data)
      │   ├─ Find existing by listing_url
      │   │   ├─ Found → UPDATE (stats.updated++)
      │   │   └─ Not found → INSERT (stats.inserted++)
      │   │
      │   └─ Also upsert related entities:
      │       ├─ upsert_office(name, phone)
      │       └─ upsert_agent(name, phone)
      │
      └─ Advantage: Authoritative, persistent

Why Both Levels?
  │
  ├─ In-Memory:
  │   ├─ ✓ Fast (no database lookup)
  │   ├─ ✓ Prevents redundant work in same session
  │   └─ ✗ Lost when crawler restarts
  │
  └─ Database:
      ├─ ✓ Persistent across sessions
      ├─ ✓ Authoritative source of truth
      └─ ✗ Requires database lookup

Example:
  │
  ├─ Run 1: [url1, url2, url1, url3]
  │   ├─ url1 (1st): In-memory miss, DB insert → stats.inserted++
  │   ├─ url2: In-memory miss, DB insert → stats.inserted++
  │   ├─ url1 (2nd): In-memory HIT → stats.skipped++
  │   │              DB upsert → stats.updated++ (no change)
  │   └─ url3: In-memory miss, DB insert → stats.inserted++
  │
  └─ Run 2 (restart): [url1, url4]
      ├─ url1: In-memory miss (new session), DB HIT → stats.updated++
      └─ url4: In-memory miss, DB insert → stats.inserted++
"""


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING FLOW
# ═══════════════════════════════════════════════════════════════════════════════

RATE_LIMITING = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                             RATE LIMITING FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

Configuration:
  ├─ requests_per_minute: 20 (default)
  ├─ min_delay_between_requests: 3.0s (60 / 20)
  ├─ random_delay_min: 1.0s
  └─ random_delay_max: 3.0s

Per-Domain Tracking:
  │
  └─ self.last_request_time: Dict[domain, timestamp]
      ├─ 'sahibinden.com': 1675342801.234
      ├─ 'hepsiemlak.com': 1675342795.567
      └─ ...

Before Each Request:
  │
  ├─► Extract domain from URL
  │   └─ "https://www.sahibinden.com/ilan/123"
  │       → "www.sahibinden.com"
  │
  ├─► Check last request time for this domain
  │   ├─ elapsed = now - last_request_time[domain]
  │   └─ if elapsed < min_delay:
  │       └─► wait_time = min_delay - elapsed
  │           └─► await asyncio.sleep(wait_time)
  │
  ├─► Add random delay (politeness)
  │   ├─ delay = random.uniform(1.0, 3.0)
  │   └─► await asyncio.sleep(delay)
  │
  ├─► Make request
  │
  └─► Update last_request_time[domain] = now

Total Delay:
  │
  └─ min_delay (3.0s) + random_delay (1-3s) = 4-6s between requests

Example Timeline:
  │
  ├─ 10:00:00 → Request URL1 (sahibinden.com)
  ├─ 10:00:05 → Request URL2 (sahibinden.com) [3s rate limit + 2s random]
  ├─ 10:00:10 → Request URL3 (sahibinden.com) [3s rate limit + 2s random]
  └─ 10:00:15 → Request URL4 (hepsiemlak.com) [0s rate limit + 2s random]
                                                 (different domain!)

Blocking Detection:
  │
  ├─ If HTTP 403/429:
  │   ├─ Record timestamp in block_history[domain]
  │   ├─ Count recent blocks (within 60s window)
  │   └─ if count >= 5:
  │       └─► raise BlockedError (stop crawling this domain)
  │
  └─ Prevents excessive requests when blocked
"""


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

STATISTICS = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STATISTICS TRACKING                                │
└─────────────────────────────────────────────────────────────────────────────┘

CrawlStats Dataclass:
  │
  ├─ total: 100          (input URLs)
  ├─ fetched: 98         (HTML downloaded)
  ├─ parsed: 95          (data extracted)
  ├─ normalized: 95      (data cleaned)
  ├─ inserted: 40        (new in database)
  ├─ updated: 55         (existing in database)
  ├─ skipped: 5          (duplicates in memory)
  └─ failed: 5           (errors)

Tracking Flow:
  │
  └─ For Each URL:
      │
      ├─ stats.total++ (at start)
      │
      ├─ Fetch success? → stats.fetched++
      │
      ├─ Parse success? → stats.parsed++
      │
      ├─ Normalize success? → stats.normalized++
      │
      ├─ Dedup check:
      │   ├─ In-memory duplicate? → stats.skipped++
      │   └─ New? → (no stat change)
      │
      ├─ Database persist:
      │   ├─ operation == 'inserted' → stats.inserted++
      │   └─ operation == 'updated' → stats.updated++
      │
      └─ Any exception? → stats.failed++

Final Summary:
  │
  ├─ Success rate = (inserted + updated) / total * 100
  ├─ Duplication rate = skipped / total * 100
  └─ Failure rate = failed / total * 100

Example Output:
  │
  ├─ Total URLs:             100
  ├─ Successfully fetched:    98
  ├─ Successfully parsed:     95
  ├─ Successfully normalized: 95
  ├─ Inserted (new):          40
  ├─ Updated (existing):      55
  ├─ Skipped (duplicates):     5
  ├─ Failed:                   5
  └─ Success rate: 95.0%
"""


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FLOW
# ═══════════════════════════════════════════════════════════════════════════════

DATA_FLOW = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA TRANSFORMATION FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

1. INPUT (URL)
   │
   └─ "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123"

2. FETCH (HTML)
   │
   └─ Raw HTML string (~45 KB)
      ├─ <html><head>...</head>
      ├─ <body>
      ├─   <div class="breadcrumb">İstanbul > Kadıköy</div>
      ├─   <div class="office">  Ev Gayrimenkul  </div>
      ├─   <div class="agent">ahmet yılmaz</div>
      └─   <div class="phone">0532 123 4567</div>

3. PARSE (Structured Data)
   │
   └─ {
       'office_name': '  Ev Gayrimenkul  ',  ← raw, messy
       'agent_name': 'ahmet yılmaz',          ← lowercase
       'phone_number': '0532 123 4567',       ← formatted
       'city': 'İSTANBUL',                    ← uppercase
       'district': 'kadıköy',                 ← lowercase
       'listing_url': 'https://...'
     }

4. NORMALIZE (Clean Data)
   │
   └─ {
       'office_name': 'EV GAYRIMENKUL',       ← uppercase, trimmed
       'agent_name': 'AHMET YILMAZ',          ← uppercase
       'phone_number': '+905321234567',       ← E.164 format
       'city': 'Istanbul',                    ← title case
       'district': 'Kadıköy',                 ← title case
       'listing_url': 'https://...',
       'source': 'sahibinden',                ← detected
       'confidence': 'high'                   ← calculated
     }

5. DEDUPLICATE (Check)
   │
   └─ DeduplicationResult(
       is_new=True,
       dedupe_key='https://...',
       reason='New listing URL'
     )

6. PERSIST (Database)
   │
   ├─ Office Document
   │   {
   │     '_id': ObjectId('507f...'),
   │     'office_name': 'EV GAYRIMENKUL',
   │     'phone_number': '+905321234567',
   │     'created_at': datetime(2026, 2, 2, 10, 0, 0),
   │     'updated_at': datetime(2026, 2, 2, 10, 0, 0)
   │   }
   │
   ├─ Agent Document
   │   {
   │     '_id': ObjectId('507f...'),
   │     'agent_name': 'AHMET YILMAZ',
   │     'phone_number': '+905321234567',
   │     'created_at': datetime(2026, 2, 2, 10, 0, 0),
   │     'updated_at': datetime(2026, 2, 2, 10, 0, 0)
   │   }
   │
   └─ Listing Document
       {
         '_id': ObjectId('507f...'),
         'listing_url': 'https://...',
         'office_name': 'EV GAYRIMENKUL',
         'agent_name': 'AHMET YILMAZ',
         'phone_number': '+905321234567',
         'city': 'Istanbul',
         'district': 'Kadıköy',
         'source': 'sahibinden',
         'confidence': 'high',
         'office_id': ObjectId('507f...'),    ← reference
         'agent_id': ObjectId('507f...'),     ← reference
         'created_at': datetime(2026, 2, 2, 10, 0, 0),
         'updated_at': datetime(2026, 2, 2, 10, 0, 0)
       }

7. OUTPUT (Statistics)
   │
   └─ CrawlStats(
       total=1,
       fetched=1,
       parsed=1,
       normalized=1,
       inserted=1,
       updated=0,
       skipped=0,
       failed=0
     )
"""


if __name__ == "__main__":
    print(CONTROL_FLOW)
    print("\n" * 2)
    print(ERROR_HANDLING)
    print("\n" * 2)
    print(DEDUPLICATION)
    print("\n" * 2)
    print(RATE_LIMITING)
    print("\n" * 2)
    print(STATISTICS)
    print("\n" * 2)
    print(DATA_FLOW)
