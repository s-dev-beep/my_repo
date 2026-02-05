# STEP 9: Observability & Quality Gates

## Overview

STEP 9 adds structured reporting and quality validation to the crawler, enabling production-grade observability without changing existing business logic.

### What's New

1. **Structured JSON Reporting** - Complete audit trail of every crawl run
2. **Quality Gates** - Deterministic rejection rules for low-quality data
3. **Failure Categorization** - Classify failures by type
4. **Event Tracking** - Record successes, failures, and rejections

## Architecture

### Components Added

```
src/core/reporting.py
├── Reporter         (Event tracker)
├── QualityGates     (Validation rules)
├── CrawlReport      (Report structure)
├── FailureRecord    (Failure tracking)
├── QualityRejection (Rejection tracking)
└── SuccessRecord    (Success tracking)
```

### Integration Points

```python
# Crawler now optionally accepts a Reporter
crawler = Crawler(
    parser=SahibindenParser(),
    reporter=Reporter(),           # Optional
    enable_quality_gates=True      # Optional
)
```

**Backward Compatible:** Existing code works without changes.

## Quality Gates

### Gate 1: Low Confidence + No Phone

**Rule:** Reject if `confidence='low'` AND `phone_number` is None

**Reason:** Unreliable data without contact information

**Example:**
```python
{
    'office_name': 'UNKNOWN OFFICE',
    'agent_name': None,
    'phone_number': None,  # Missing
    'city': 'Istanbul',
    'district': None,
    'confidence': 'low'     # Low quality
}
# REJECTED: "Low confidence listing with no phone number"
```

### Gate 2: Missing Location

**Rule:** Reject if BOTH `city` AND `district` are None

**Reason:** Cannot categorize listing geographically

**Example:**
```python
{
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': None,        # Missing
    'district': None,    # Missing
    'confidence': 'medium'
}
# REJECTED: "Missing both city and district location data"
```

### Gate 3: Sparse Parsed Data

**Rule:** Reject if parser extracted < 2 meaningful fields

**Fields considered:** office_name, agent_name, phone_number, city, district

**Example:**
```python
{
    'office_name': 'SOME OFFICE',
    'agent_name': None,
    'phone_number': None,
    'city': None,
    'district': None,
    'listing_url': 'https://...'
}
# REJECTED: "Parser extracted only 1 meaningful field(s), minimum is 2"
```

## Failure Categories

### fetch_failed
- HTTP errors (404, 500, etc.)
- Network timeouts
- Connection failures
- Blocking (403/429)

### parse_failed
- HTML parsing errors
- Missing expected elements
- Parser returned None
- Structure changes

### normalize_failed
- Data validation errors
- Missing required fields
- Invalid formats

### persist_failed
- Database connection errors
- Validation failures
- Constraint violations

### quality_rejected
- Failed quality gate validation
- Low-quality data rejected

## Report Structure

### Complete Example

```json
{
  "run_id": "crawl_20260202_101530",
  "start_time": "2026-02-02T10:15:30.123456",
  "end_time": "2026-02-02T10:16:45.789012",
  "duration_seconds": 75.67,
  "parser_type": "sahibinden",
  "total_urls": 10,
  
  "successful": [
    {
      "url": "https://www.sahibinden.com/ilan/emlak-konut-kiralik-123",
      "listing_id": "507f1f77bcf86cd799439011",
      "operation": "inserted",
      "timestamp": "2026-02-02T10:15:35.123456",
      "confidence": "high"
    },
    {
      "url": "https://www.sahibinden.com/ilan/emlak-konut-kiralik-456",
      "listing_id": "507f1f77bcf86cd799439020",
      "operation": "updated",
      "timestamp": "2026-02-02T10:15:42.789012",
      "confidence": "medium"
    }
  ],
  
  "failures": [
    {
      "url": "https://invalid-domain.com/ilan/test",
      "category": "fetch_failed",
      "reason": "Network error: Name or service not known",
      "timestamp": "2026-02-02T10:15:40.123456",
      "step": "fetch",
      "details": null
    },
    {
      "url": "https://www.sahibinden.com/ilan/broken-page-999",
      "category": "parse_failed",
      "reason": "Parser returned None",
      "timestamp": "2026-02-02T10:15:50.123456",
      "step": "parse",
      "details": null
    }
  ],
  
  "quality_rejections": [
    {
      "url": "https://www.sahibinden.com/ilan/low-quality-789",
      "reason": "Low confidence listing with no phone number",
      "timestamp": "2026-02-02T10:15:55.123456",
      "data_snapshot": {
        "office_name": "UNKNOWN",
        "agent_name": null,
        "phone_number": null,
        "city": "Istanbul",
        "district": null,
        "listing_url": "https://www.sahibinden.com/ilan/low-quality-789",
        "source": "sahibinden",
        "confidence": "low"
      }
    }
  ],
  
  "stats": {
    "total": 10,
    "fetched": 8,
    "parsed": 7,
    "normalized": 6,
    "inserted": 4,
    "updated": 1,
    "failed": 3,
    "quality_rejected": 1
  },
  
  "failure_breakdown": {
    "fetch_failed": 1,
    "parse_failed": 1,
    "normalize_failed": 0,
    "persist_failed": 1,
    "quality_rejected": 1
  }
}
```

## Usage

### Basic Usage with Reporting

```python
import asyncio
from pathlib import Path
from src.core.crawler import Crawler
from src.core.reporting import Reporter
from src.adapters.sahibinden.parser import SahibindenParser

async def main():
    # Create reporter
    reporter = Reporter(
        run_id="crawl_20260202_101530",
        parser_type="sahibinden"
    )
    
    # Create crawler with reporter
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        enable_quality_gates=True
    )
    
    # Run crawl
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-123",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-456",
    ]
    
    stats = await crawler.run(urls)
    
    # Generate and save report
    report = reporter.generate_report()
    report.save(Path("reports/my_crawl.json"))
    
    print(f"Successful: {len(report.successful)}")
    print(f"Failed: {len(report.failures)}")
    print(f"Rejected: {len(report.quality_rejections)}")

asyncio.run(main())
```

### Disable Quality Gates

```python
# Accept all data regardless of quality
crawler = Crawler(
    parser=SahibindenParser(),
    reporter=reporter,
    enable_quality_gates=False  # Disabled
)
```

### Without Reporter (Original Behavior)

```python
# Backward compatible - works exactly as before
crawler = Crawler(parser=SahibindenParser())
stats = await crawler.run(urls)
# No report generated
```

## Log Output Examples

### Successful Processing

```
INFO [crawler] [1/10] Processing: https://www.sahibinden.com/ilan/emlak-konut-kiralik-123
INFO [fetcher] Successfully fetched 45230 bytes
INFO [parser] Parsing Sahibinden listing
INFO [normalizer] Normalized: sahibinden listing with confidence=high
INFO [mongo] Inserted listing (id=507f1f77bcf86cd799439011)
INFO [crawler] ✓ Inserted listing: https://... (id=507f1f77bcf86cd799439011)
```

### Quality Rejection

```
INFO [crawler] [2/10] Processing: https://www.sahibinden.com/ilan/low-quality-456
INFO [fetcher] Successfully fetched 32100 bytes
INFO [parser] Parsing Sahibinden listing
INFO [normalizer] Normalized: sahibinden listing with confidence=low
WARNING [crawler] Quality rejection at normalize: https://... - Low confidence listing with no phone number
INFO [reporting] Quality rejection: https://... - Low confidence listing with no phone number
ERROR [crawler] Normalization failed for https://...: Quality gate failed: Low confidence listing with no phone number
```

### Fetch Failure

```
INFO [crawler] [3/10] Processing: https://invalid-domain.com/ilan/test
ERROR [fetcher] Network error: Name or service not known
ERROR [crawler] Fetch failed for https://invalid-domain.com/ilan/test: Network error
ERROR [crawler] Failed to process https://invalid-domain.com/ilan/test: Network error
```

## Reading Reports

### Python Script

```python
import json
from pathlib import Path

# Read report
with open("reports/crawl_20260202_101530.json") as f:
    report = json.load(f)

# Analyze
print(f"Total URLs: {report['stats']['total']}")
print(f"Success rate: {
    (report['stats']['inserted'] + report['stats']['updated']) / 
    report['stats']['total'] * 100
}%")

# Check quality rejections
for rejection in report['quality_rejections']:
    print(f"Rejected: {rejection['url']}")
    print(f"  Reason: {rejection['reason']}")
```

### Command Line (jq)

```bash
# Get summary
cat reports/crawl_20260202_101530.json | jq '{
  run_id,
  total: .stats.total,
  successful: (.stats.inserted + .stats.updated),
  failed: .stats.failed,
  quality_rejected: .stats.quality_rejected
}'

# List quality rejections
cat reports/crawl_20260202_101530.json | \
  jq '.quality_rejections[] | {url, reason}'

# Failure breakdown
cat reports/crawl_20260202_101530.json | jq '.failure_breakdown'
```

## Design Decisions

### Why JSON Reports?

- **Structured:** Machine-readable for analysis
- **Portable:** Works across systems
- **Queryable:** Easy to process with jq, Python, etc.
- **Archivable:** Long-term storage and auditing

### Why Deterministic Quality Gates?

- **No ML:** Simple, understandable rules
- **No Fuzzy Matching:** Deterministic outcomes
- **Fast:** No external API calls
- **Reproducible:** Same input → same result

### Why Event-Based Tracking?

- **Real-time:** Track as events occur
- **Complete:** No events missed
- **Flexible:** Easy to add new event types
- **Async-safe:** Works with async crawler

## Integration Points

### CLI Integration (Future)

```bash
crawler crawl \
  --city istanbul \
  --with-report \
  --report-path reports/istanbul_$(date +%Y%m%d).json

# Output:
# Report saved to: reports/istanbul_20260202.json
# Successful: 245, Failed: 5, Rejected: 12
```

### Monitoring Integration (Future)

```python
# Send metrics to monitoring system
report = reporter.generate_report()

metrics = {
    'total': report.stats['total'],
    'success_rate': (report.stats['inserted'] + report.stats['updated']) / report.stats['total'],
    'rejection_rate': report.stats['quality_rejected'] / report.stats['total'],
    'failure_rate': report.stats['failed'] / report.stats['total']
}

send_to_grafana(metrics)
```

### Alert Integration (Future)

```python
# Alert on high failure rate
if report.stats['failed'] / report.stats['total'] > 0.2:
    send_alert(f"High failure rate: {report.stats['failed']}/{report.stats['total']}")

# Alert on blocking
if report.failure_breakdown['fetch_failed'] > 5:
    send_alert("Possible blocking detected")
```

## Testing

### Syntax Validation

```bash
python3 -m py_compile src/core/reporting.py
python3 -m py_compile examples/run_with_report.py
```

### Run Demo

```bash
export MONGO_URI='mongodb://localhost:27017'
python examples/run_with_report.py
```

### Check Reports

```bash
ls -lh reports/
cat reports/*.json | jq .stats
```

## Files

- `src/core/reporting.py` (500 lines) - Reporter and quality gates
- `examples/run_with_report.py` (400 lines) - Usage examples
- `STEP9_README.md` (this file) - Documentation

## Summary

STEP 9 adds production-grade observability:

✅ **Structured JSON Reports** - Complete audit trail  
✅ **Quality Gates** - Deterministic validation  
✅ **Failure Categorization** - Classify errors  
✅ **Event Tracking** - Record all events  
✅ **Backward Compatible** - Optional features  
✅ **No Business Logic Changes** - Pure observability layer  

The crawler now provides full visibility into crawl runs while maintaining all existing functionality.
