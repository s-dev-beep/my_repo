# STEP 10: Example Execution Logs

This document shows example console output for different execution modes and safety conditions.

---

## Example 1: Dry Run Mode

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEP 10: EXECUTION MODES & SAFETY CONTROLS                ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
DEMO 1: DRY RUN MODE
================================================================================
Purpose: Validate URLs and data without writing to database
Use case: Testing new parsers, validating URL lists

[2026-02-02 14:30:22] [INFO] Crawler initialized: parser=sahibinden, db=real_estate_crawler, run_mode=dry_run, quality_gates=enabled
[2026-02-02 14:30:22] [INFO] Reporter initialized: run_id=dry_run_demo
[2026-02-02 14:30:22] [INFO] Starting crawl: 3 URLs to process
[2026-02-02 14:30:22] [INFO] Execution mode: dry_run
[2026-02-02 14:30:22] [INFO] DRY RUN: No database writes will be performed

[2026-02-02 14:30:23] [INFO] [1/3] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456
[2026-02-02 14:30:24] [DEBUG] Fetched 15234 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456
[2026-02-02 14:30:24] [DEBUG] Parsed data: ['office_name', 'agent_name', 'phone_number', 'city', 'district', 'listing_url']
[2026-02-02 14:30:24] [DEBUG] Normalized: confidence=high
[2026-02-02 14:30:24] [INFO] [DRY RUN] Would persist listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456 (confidence=high)

[2026-02-02 14:30:25] [INFO] [2/3] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-234567
[2026-02-02 14:30:26] [DEBUG] Fetched 14892 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-234567
[2026-02-02 14:30:26] [DEBUG] Parsed data: ['office_name', 'agent_name', 'phone_number', 'city', 'district', 'listing_url']
[2026-02-02 14:30:26] [DEBUG] Normalized: confidence=high
[2026-02-02 14:30:26] [INFO] [DRY RUN] Would persist listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-234567 (confidence=high)

[2026-02-02 14:30:27] [INFO] [3/3] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-345678
[2026-02-02 14:30:28] [DEBUG] Fetched 13456 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-345678
[2026-02-02 14:30:28] [DEBUG] Parsed data: ['office_name', 'phone_number', 'city', 'district', 'listing_url']
[2026-02-02 14:30:28] [DEBUG] Normalized: confidence=medium
[2026-02-02 14:30:28] [INFO] [DRY RUN] Would persist listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-345678 (confidence=medium)

[2026-02-02 14:30:28] [INFO] Crawl completed: CrawlStats(total=3, fetched=0, parsed=0, normalized=0, inserted=3, updated=0, skipped=0, failed=0)
[2026-02-02 14:30:28] [INFO] ================================================================================
[2026-02-02 14:30:28] [INFO] CRAWL SUMMARY
[2026-02-02 14:30:28] [INFO] ================================================================================
[2026-02-02 14:30:28] [INFO] Total URLs:             3
[2026-02-02 14:30:28] [INFO] Successfully fetched:   0
[2026-02-02 14:30:28] [INFO] Successfully parsed:    0
[2026-02-02 14:30:28] [INFO] Successfully normalized:   0
[2026-02-02 14:30:28] [INFO] Inserted (new):         3
[2026-02-02 14:30:28] [INFO] Updated (existing):     0
[2026-02-02 14:30:28] [INFO] Skipped (duplicates):   0
[2026-02-02 14:30:28] [INFO] Failed:                 0
[2026-02-02 14:30:28] [INFO] ================================================================================
[2026-02-02 14:30:28] [INFO] Success rate: 100.0%
[2026-02-02 14:30:28] [INFO] Report saved to: reports/dry_run_demo.json

✓ Dry run completed: CrawlStats(total=3, fetched=0, parsed=0, normalized=0, inserted=3, updated=0, skipped=0, failed=0)
✓ Report saved to: reports/dry_run_demo.json
✓ Run mode: dry_run
✓ No database writes were performed
```

---

## Example 2: Safe Run Mode

```
================================================================================
DEMO 2: SAFE RUN MODE
================================================================================
Purpose: Only persist high-quality listings (high/medium confidence)
Use case: Production runs where data quality is critical

[2026-02-02 14:35:10] [INFO] Crawler initialized: parser=sahibinden, db=real_estate_crawler, run_mode=safe_run, quality_gates=enabled
[2026-02-02 14:35:10] [INFO] Reporter initialized: run_id=safe_run_demo
[2026-02-02 14:35:10] [INFO] Starting crawl: 5 URLs to process
[2026-02-02 14:35:10] [INFO] Execution mode: safe_run
[2026-02-02 14:35:10] [INFO] SAFE RUN: Only high/medium confidence listings will persist

[2026-02-02 14:35:11] [INFO] [1/5] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456
[2026-02-02 14:35:12] [DEBUG] Fetched 15234 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456
[2026-02-02 14:35:12] [DEBUG] Parsed data: ['office_name', 'agent_name', 'phone_number', 'city', 'district', 'listing_url']
[2026-02-02 14:35:12] [DEBUG] Normalized: confidence=high
[2026-02-02 14:35:12] [INFO] ✓ [SAFE RUN] Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456 (id=507f1f77bcf86cd799439011, confidence=high)

[2026-02-02 14:35:13] [INFO] [2/5] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-234567
[2026-02-02 14:35:14] [DEBUG] Fetched 13456 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-234567
[2026-02-02 14:35:14] [DEBUG] Parsed data: ['office_name', 'phone_number', 'city', 'district', 'listing_url']
[2026-02-02 14:35:14] [DEBUG] Normalized: confidence=medium
[2026-02-02 14:35:14] [INFO] ✓ [SAFE RUN] Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-234567 (id=507f1f77bcf86cd799439022, confidence=medium)

[2026-02-02 14:35:15] [INFO] [3/5] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-izmir-low-345678
[2026-02-02 14:35:16] [DEBUG] Fetched 9876 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-izmir-low-345678
[2026-02-02 14:35:16] [DEBUG] Parsed data: ['office_name', 'city', 'listing_url']
[2026-02-02 14:35:16] [DEBUG] Normalized: confidence=low
[2026-02-02 14:35:16] [INFO] [SAFE RUN] Skipped low confidence listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-izmir-low-345678 (confidence=low)

[2026-02-02 14:35:17] [INFO] Crawl completed: CrawlStats(total=5, fetched=5, parsed=5, normalized=5, inserted=3, updated=0, skipped=2, failed=0)
[2026-02-02 14:35:17] [INFO] ================================================================================
[2026-02-02 14:35:17] [INFO] CRAWL SUMMARY
[2026-02-02 14:35:17] [INFO] ================================================================================
[2026-02-02 14:35:17] [INFO] Total URLs:             5
[2026-02-02 14:35:17] [INFO] Successfully fetched:   5
[2026-02-02 14:35:17] [INFO] Successfully parsed:    5
[2026-02-02 14:35:17] [INFO] Successfully normalized:   5
[2026-02-02 14:35:17] [INFO] Inserted (new):         3
[2026-02-02 14:35:17] [INFO] Updated (existing):     0
[2026-02-02 14:35:17] [INFO] Skipped (duplicates):   2
[2026-02-02 14:35:17] [INFO] Failed:                 0
[2026-02-02 14:35:17] [INFO] ================================================================================
[2026-02-02 14:35:17] [INFO] Success rate: 60.0%
[2026-02-02 14:35:17] [INFO] Report saved to: reports/safe_run_demo.json

✓ Safe run completed: CrawlStats(total=5, fetched=5, parsed=5, normalized=5, inserted=3, updated=0, skipped=2, failed=0)
✓ Report saved to: reports/safe_run_demo.json
✓ Run mode: safe_run
✓ Only high/medium confidence listings were persisted
```

---

## Example 3: Safety Stop - Fetch Failure Rate

```
================================================================================
DEMO 4: SAFETY STOP - FETCH FAILURE RATE
================================================================================
Purpose: Stop crawl if too many URLs fail to fetch
Safety threshold: 50% fetch failure rate

[2026-02-02 14:40:00] [INFO] Crawler initialized: parser=sahibinden, db=real_estate_crawler, run_mode=full_run, quality_gates=enabled
[2026-02-02 14:40:00] [INFO] Reporter initialized: run_id=safety_fetch_demo
[2026-02-02 14:40:00] [INFO] Starting crawl: 50 URLs to process
[2026-02-02 14:40:00] [INFO] Execution mode: full_run

[2026-02-02 14:40:01] [INFO] [1/50] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-100001
[2026-02-02 14:40:02] [DEBUG] Fetched 15234 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-100001
[2026-02-02 14:40:02] [INFO] ✓ Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-100001 (id=507f1f77bcf86cd799440001)

[2026-02-02 14:40:03] [INFO] [2/50] Processing: https://invalid-domain-00001.com/ilan/test
[2026-02-02 14:40:08] [ERROR] Fetch failed for https://invalid-domain-00001.com/ilan/test: Network error after 3 retries: Name or service not known
[2026-02-02 14:40:08] [ERROR] Failed to process https://invalid-domain-00001.com/ilan/test: Network error after 3 retries: Name or service not known

[2026-02-02 14:40:09] [INFO] [3/50] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-100002
[2026-02-02 14:40:10] [DEBUG] Fetched 14892 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-100002
[2026-02-02 14:40:10] [INFO] ✓ Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-100002 (id=507f1f77bcf86cd799440002)

... [processing continues with mix of successes and failures] ...

[2026-02-02 14:41:10] [INFO] [20/50] Processing: https://invalid-domain-00010.com/ilan/test
[2026-02-02 14:41:15] [ERROR] Fetch failed for https://invalid-domain-00010.com/ilan/test: Network error after 3 retries: Name or service not known
[2026-02-02 14:41:15] [ERROR] Failed to process https://invalid-domain-00010.com/ilan/test: Network error after 3 retries: Name or service not known

[2026-02-02 14:41:15] [ERROR] SAFETY STOP: Fetch failure rate 60.0% exceeds threshold 50.0% (12/20 failed)
[2026-02-02 14:41:15] [WARNING] Crawl stopped early: Fetch failure rate 60.0% exceeds threshold 50.0% (12/20 failed)
[2026-02-02 14:41:15] [WARNING] Safety stop condition triggered, halting crawl

[2026-02-02 14:41:15] [INFO] Crawl completed: CrawlStats(total=50, fetched=9, parsed=8, normalized=8, inserted=8, updated=0, skipped=0, failed=12)
[2026-02-02 14:41:15] [INFO] ================================================================================
[2026-02-02 14:41:15] [INFO] CRAWL SUMMARY
[2026-02-02 14:41:15] [INFO] ================================================================================
[2026-02-02 14:41:15] [INFO] Total URLs:            50
[2026-02-02 14:41:15] [INFO] Successfully fetched:   9
[2026-02-02 14:41:15] [INFO] Successfully parsed:    8
[2026-02-02 14:41:15] [INFO] Successfully normalized:   8
[2026-02-02 14:41:15] [INFO] Inserted (new):         8
[2026-02-02 14:41:15] [INFO] Updated (existing):     0
[2026-02-02 14:41:15] [INFO] Skipped (duplicates):   0
[2026-02-02 14:41:15] [INFO] Failed:                12
[2026-02-02 14:41:15] [INFO] ================================================================================
[2026-02-02 14:41:15] [INFO] Success rate: 16.0%
[2026-02-02 14:41:15] [INFO] Report saved to: reports/safety_fetch_demo.json

✓ Safety stop triggered: CrawlStats(total=50, fetched=9, parsed=8, normalized=8, inserted=8, updated=0, skipped=0, failed=12)
✓ Report saved to: reports/safety_fetch_demo.json
✓ Stop reason: Fetch failure rate 60.0% exceeds threshold 50.0% (12/20 failed)
```

---

## Example 4: Safety Stop - Consecutive Blocks

```
================================================================================
DEMO 5: SAFETY STOP - CONSECUTIVE BLOCKS
================================================================================
Purpose: Stop crawl if too many consecutive fetches fail
Safety threshold: 3 consecutive failures (indicating IP block)

[2026-02-02 14:45:00] [INFO] Crawler initialized: parser=sahibinden, db=real_estate_crawler, run_mode=full_run, quality_gates=enabled
[2026-02-02 14:45:00] [INFO] Reporter initialized: run_id=safety_blocks_demo
[2026-02-02 14:45:00] [INFO] Starting crawl: 30 URLs to process
[2026-02-02 14:45:00] [INFO] Execution mode: full_run

[2026-02-02 14:45:01] [INFO] [1/30] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-200001
[2026-02-02 14:45:02] [DEBUG] Fetched 15234 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-200001
[2026-02-02 14:45:02] [INFO] ✓ Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-200001 (id=507f1f77bcf86cd799450001)

[2026-02-02 14:45:03] [INFO] [2/30] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-200002
[2026-02-02 14:45:04] [DEBUG] Fetched 14892 bytes from https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-200002
[2026-02-02 14:45:04] [INFO] ✓ Inserted listing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-200002 (id=507f1f77bcf86cd799450002)

[2026-02-02 14:45:05] [INFO] [3/30] Processing: https://blocked-url-00001.com/ilan/test
[2026-02-02 14:45:08] [ERROR] Fetch failed for https://blocked-url-00001.com/ilan/test: HTTP 403 Forbidden - Possible IP block
[2026-02-02 14:45:08] [ERROR] Failed to process https://blocked-url-00001.com/ilan/test: HTTP 403 Forbidden - Possible IP block

[2026-02-02 14:45:09] [INFO] [4/30] Processing: https://blocked-url-00002.com/ilan/test
[2026-02-02 14:45:12] [ERROR] Fetch failed for https://blocked-url-00002.com/ilan/test: HTTP 403 Forbidden - Possible IP block
[2026-02-02 14:45:12] [ERROR] Failed to process https://blocked-url-00002.com/ilan/test: HTTP 403 Forbidden - Possible IP block

[2026-02-02 14:45:13] [INFO] [5/30] Processing: https://blocked-url-00003.com/ilan/test
[2026-02-02 14:45:16] [ERROR] Fetch failed for https://blocked-url-00003.com/ilan/test: HTTP 403 Forbidden - Possible IP block
[2026-02-02 14:45:16] [ERROR] Failed to process https://blocked-url-00003.com/ilan/test: HTTP 403 Forbidden - Possible IP block

[2026-02-02 14:45:17] [ERROR] SAFETY STOP: Consecutive fetch failures (3) reached threshold (3). Possible rate limiting or IP block.
[2026-02-02 14:45:17] [WARNING] Crawl stopped early: Consecutive fetch failures (3) reached threshold (3). Possible rate limiting or IP block.
[2026-02-02 14:45:17] [WARNING] Safety stop condition triggered, halting crawl

[2026-02-02 14:45:17] [INFO] Crawl completed: CrawlStats(total=30, fetched=2, parsed=2, normalized=2, inserted=2, updated=0, skipped=0, failed=3)
[2026-02-02 14:45:17] [INFO] ================================================================================
[2026-02-02 14:45:17] [INFO] CRAWL SUMMARY
[2026-02-02 14:45:17] [INFO] ================================================================================
[2026-02-02 14:45:17] [INFO] Total URLs:            30
[2026-02-02 14:45:17] [INFO] Successfully fetched:   2
[2026-02-02 14:45:17] [INFO] Successfully parsed:    2
[2026-02-02 14:45:17] [INFO] Successfully normalized:   2
[2026-02-02 14:45:17] [INFO] Inserted (new):         2
[2026-02-02 14:45:17] [INFO] Updated (existing):     0
[2026-02-02 14:45:17] [INFO] Skipped (duplicates):   0
[2026-02-02 14:45:17] [INFO] Failed:                 3
[2026-02-02 14:45:17] [INFO] ================================================================================
[2026-02-02 14:45:17] [INFO] Success rate: 6.7%
[2026-02-02 14:45:17] [INFO] Report saved to: reports/safety_blocks_demo.json

✓ Safety stop triggered: CrawlStats(total=30, fetched=2, parsed=2, normalized=2, inserted=2, updated=0, skipped=0, failed=3)
✓ Report saved to: reports/safety_blocks_demo.json
✓ Stop reason: Consecutive fetch failures (3) reached threshold (3). Possible rate limiting or IP block.
```

---

## Key Log Patterns

### Dry Run Mode
- `[INFO] Execution mode: dry_run`
- `[INFO] DRY RUN: No database writes will be performed`
- `[INFO] [DRY RUN] Would persist listing: ...`

### Safe Run Mode
- `[INFO] Execution mode: safe_run`
- `[INFO] SAFE RUN: Only high/medium confidence listings will persist`
- `[INFO] ✓ [SAFE RUN] Inserted listing: ... (confidence=high)`
- `[INFO] [SAFE RUN] Skipped low confidence listing: ... (confidence=low)`

### Full Run Mode
- `[INFO] Execution mode: full_run`
- `[INFO] ✓ Inserted listing: ...`
- `[INFO] ✓ Updated listing: ...`

### Safety Stops
- `[ERROR] SAFETY STOP: [reason]`
- `[WARNING] Crawl stopped early: [reason]`
- `[WARNING] Safety stop condition triggered, halting crawl`

### Normal Completion
- `[INFO] Crawl completed: CrawlStats(...)`
- `[INFO] Success rate: X.X%`
- No stop_reason in report
