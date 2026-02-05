# Fetcher Architecture & Flow Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Fetcher Module                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐      ┌──────────────────┐                  │
│  │  Input: URL     │      │ Validation       │                  │
│  └────────┬────────┘      │ - Schema check   │                  │
│           │               │ - Protocol check │                  │
│           └──────┬────────┴──────────────────┘                  │
│                  │                                               │
│           ┌──────▼──────────────────┐                           │
│           │  Rate Limiting Check    │                           │
│           │  (per-domain)           │                           │
│           │  - Check min_delay      │                           │
│           │  - Wait if needed       │                           │
│           └──────┬──────────────────┘                           │
│                  │                                               │
│           ┌──────▼──────────────────┐                           │
│           │  Blocking Check         │                           │
│           │  (per-domain)           │                           │
│           │  - Count recent blocks  │                           │
│           │  - Raise if too many    │                           │
│           └──────┬──────────────────┘                           │
│                  │                                               │
│           ┌──────▼──────────────────┐                           │
│           │  Add Random Delay       │                           │
│           │  (polite crawling)      │                           │
│           └──────┬──────────────────┘                           │
│                  │                                               │
│           ┌──────▼──────────────────┐                           │
│           │  HTTP Request           │                           │
│           │  - Random User-Agent    │                           │
│           │  - Session reuse        │                           │
│           │  - Optional proxy       │                           │
│           └──────┬──────────────────┘                           │
│                  │                                               │
│         ┌────────┴────────┐                                     │
│         │                 │                                     │
│    ┌────▼────┐      ┌──────▼────┐                              │
│    │ Success │      │  Error    │                              │
│    │ (200)   │      │ (4xx/5xx) │                              │
│    └────┬────┘      └──────┬────┘                              │
│         │                  │                                    │
│         │          ┌───────▼────────┐                          │
│         │          │  Retry Logic   │                          │
│         │          │  - 403/429?    │                          │
│         │          │  - Record block│                          │
│         │          │  - Exponential │                          │
│         │          │    backoff     │                          │
│         │          │  - Max retries?│                          │
│         │          └───────┬────────┘                          │
│         │                  │                                    │
│         └────────┬─────────┘                                    │
│                  │                                               │
│           ┌──────▼──────────────────┐                           │
│           │  Return HTML or Error   │                           │
│           │  (no parsing)           │                           │
│           └──────────────────────────┘                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Rate Limiting: Per-Domain State

```
┌──────────────────────────────────────────────────────────────┐
│  last_request_time: Dict[str, float]                          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  sahibinden.com   → 1707066850.234  (last request time)      │
│  hepsiemlak.com   → 1707066845.890                            │
│  example.com      → 1707066822.123                            │
│                                                                │
│  min_delay_between_requests = 60 / 10 = 6.0 seconds          │
│                                                                │
│  When requesting sahibinden.com again:                        │
│  elapsed = now - 1707066850.234 = 2.5s                       │
│  needs_wait = 6.0 - 2.5 = 3.5s                               │
│  await sleep(3.5s)  ← respects rate limit                    │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

## Block Detection: Rolling Window

```
Time window: 60 seconds
Max blocks before stop: 3

┌─────────────────────────────────────────────────────────────────┐
│  Scenario: Repeated 429 Responses                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  T=0s    Request 1 → 429 (Too Many Requests)                   │
│           block_history[domain] = [T0]                          │
│           count = 1/3 ⚠️  Continue                             │
│                                                                   │
│  T=5s    Request 2 → 429                                       │
│           block_history[domain] = [T0, T5]                      │
│           count = 2/3 ⚠️  Continue (backoff)                   │
│                                                                   │
│  T=12s   Request 3 → 429                                       │
│           block_history[domain] = [T0, T5, T12]                 │
│           count = 3/3 ❌ STOP!                                 │
│           → Raise BlockedError("Stopping to respect limits")    │
│                                                                   │
│           Why this is good:                                     │
│           • Server clearly wants us to stop                     │
│           • Continuing is disrespectful                         │
│           • Saves bandwidth and time                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Retry with Exponential Backoff

```
┌─────────────────────────────────────────────────────────────────┐
│  Failure Scenario: Network Timeout                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  max_retries = 3                                                │
│  initial_delay = 1.0s                                           │
│  backoff_factor = 2.0                                           │
│                                                                   │
│  Attempt 1: Fetch → TIMEOUT                                     │
│             wait = 1.0s                                         │
│             ⏳ Sleep 1.0s                                       │
│                                                                   │
│  Attempt 2: Fetch → TIMEOUT                                     │
│             wait = 1.0 * 2.0 = 2.0s                             │
│             ⏳ Sleep 2.0s                                       │
│                                                                   │
│  Attempt 3: Fetch → TIMEOUT                                     │
│             wait = 2.0 * 2.0 = 4.0s                             │
│             ⏳ Sleep 4.0s                                       │
│                                                                   │
│  Attempt 4: Max retries reached                                 │
│             ❌ Raise FetchError                                │
│                                                                   │
│  Total time waited: 1 + 2 + 4 = 7 seconds                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Concurrent Multi-Domain Crawling

```
Timeline: Crawling 2 domains simultaneously

sahibinden.com (rate: 10 req/min = 6s minimum)
hepsiemlak.com (rate: 10 req/min = 6s minimum)

Time  sahibinden.com          hepsiemlak.com
────────────────────────────────────────────────
0s    Fetch page1             → 6s+delay       
      Get 45KB                          
                                        
1s                            Fetch page1 (different domain!)
                              No wait needed
                              Get 38KB
                                        
6.5s  Wait 6s completed       
      Fetch page2             
      Get 42KB                         
                                      
7.5s                          Wait 6s completed
                              Fetch page2
                              Get 40KB
                                      
13s   Fetch page3             
      Get 48KB                
                              
14s                           Fetch page3
                              Get 35KB

Result:
✓ Both domains crawled concurrently
✓ Each domain respects its own rate limit
✓ Total time: ~14s (vs 26s if sequential)
✓ Efficient use of resources
```

## User-Agent Rotation

```
┌─────────────────────────────────────────────────────────────────┐
│  USER_AGENTS Pool (8 Agents)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Chrome / Windows 10                                         │
│  2. Chrome / macOS                                              │
│  3. Chrome / Linux                                              │
│  4. Firefox / Windows 10                                        │
│  5. Firefox / macOS                                             │
│  6. Firefox / Linux                                             │
│  7. Safari / macOS                                              │
│  8. Edge / Windows 10                                           │
│                                                                   │
│  On each request:                                               │
│  ua = random.choice(USER_AGENTS)  → one of 8 above             │
│                                                                   │
│  Sample sequence:                                               │
│  Request 1 → Chrome/Windows (selected randomly)                │
│  Request 2 → Firefox/Linux   (different)                        │
│  Request 3 → Safari/macOS    (different)                        │
│  Request 4 → Chrome/Linux    (possibly same browser, diff OS)  │
│                                                                   │
│  Benefits:                                                       │
│  ✓ Appears as different users                                  │
│  ✓ Avoids simple user-agent blocking                           │
│  ✓ More natural crawling pattern                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Impact Matrix

```
┌──────────────────┬────────────────┬──────────────┬────────────┐
│ Setting          │ Fast (60/min)  │ Normal (10)  │ Slow (1)   │
├──────────────────┼────────────────┼──────────────┼────────────┤
│ Min delay        │ 1.0s           │ 6.0s         │ 60.0s      │
│ Random delay     │ 1-3s           │ 1-3s         │ 1-3s       │
│ Total per req    │ 2-4s           │ 7-9s         │ 61-63s     │
│ 100 URLs time    │ ~200-400s      │ ~700-900s    │ ~6100-6300s│
│ Server impact    │ High           │ Low          │ Very Low   │
│ Detection risk   │ Higher         │ Medium       │ Lower      │
│ Best for         │ Dedicated proxy│ Normal crawl │ Respect-   │
│                  │                │              │ ful crawl  │
└──────────────────┴────────────────┴──────────────┴────────────┘
```
