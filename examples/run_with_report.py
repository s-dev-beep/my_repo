"""STEP 9: Crawl with Reporting and Quality Gates

This example demonstrates:
1. Structured JSON reporting
2. Quality gate validation
3. Failure categorization
4. Report generation and saving
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime

from src.core.crawler import Crawler
from src.core.reporting import Reporter
from src.adapters.sahibinden.parser import SahibindenParser
from src.core.logger import setup_logger

logger = setup_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Basic Crawl with Reporting
# ═══════════════════════════════════════════════════════════════════════════════

async def example_basic_reporting():
    """Basic example: crawl with automatic report generation."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 1: BASIC CRAWL WITH REPORTING")
    print("=" * 80)
    
    # Sample URLs
    urls = [
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-456",
        "https://www.sahibinden.com/ilan/emlak-konut-kiralik-izmir-bornova-789",
    ]
    
    # Initialize reporter
    reporter = Reporter(
        run_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        parser_type="sahibinden"
    )
    
    # Initialize crawler with reporter
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        reporter=reporter,
        enable_quality_gates=True  # Enable quality validation
    )
    
    try:
        # Run crawl
        stats = await crawler.run(urls)
        
        # Generate report
        report = reporter.generate_report()
        
        # Save report to JSON file
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / f"{reporter.run_id}.json"
        report.save(report_path)
        
        # Print summary
        print("\n" + "-" * 80)
        print("CRAWL SUMMARY")
        print("-" * 80)
        print(f"Report saved to: {report_path}")
        print(f"\nStatistics:")
        print(f"  Total URLs:          {stats.total}")
        print(f"  Successfully processed: {stats.inserted + stats.updated}")
        print(f"  Failed:              {stats.failed}")
        print(f"\nReport breakdown:")
        print(f"  Successes:           {len(report.successful)}")
        print(f"  Failures:            {len(report.failures)}")
        print(f"  Quality rejected:    {len(report.quality_rejections)}")
        
        # Print failure breakdown
        if report.failure_breakdown:
            print(f"\nFailure categories:")
            for category, count in report.failure_breakdown.items():
                if count > 0:
                    print(f"  {category:20} {count}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        print(f"\n❌ Crawl failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Quality Gates in Action
# ═══════════════════════════════════════════════════════════════════════════════

async def example_quality_gates():
    """Example showing quality gate rejections."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: QUALITY GATES IN ACTION")
    print("=" * 80)
    
    # URLs that might trigger quality gates
    urls = [
        "https://www.sahibinden.com/ilan/good-listing-123",  # Should pass
        "https://www.sahibinden.com/ilan/low-quality-456",   # May fail: low confidence + no phone
        "https://www.sahibinden.com/ilan/missing-location-789",  # May fail: no city/district
        "https://www.sahibinden.com/ilan/sparse-data-999",   # May fail: < 2 fields
    ]
    
    reporter = Reporter(
        run_id=f"quality_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        parser_type="sahibinden"
    )
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        reporter=reporter,
        enable_quality_gates=True  # Quality gates ENABLED
    )
    
    try:
        stats = await crawler.run(urls)
        report = reporter.generate_report()
        
        # Save report
        report_path = Path("reports") / f"{reporter.run_id}.json"
        report.save(report_path)
        
        print("\n" + "-" * 80)
        print("QUALITY GATE RESULTS")
        print("-" * 80)
        print(f"Total URLs:          {len(urls)}")
        print(f"Passed quality:      {len(report.successful)}")
        print(f"Quality rejected:    {len(report.quality_rejections)}")
        
        # Show rejection details
        if report.quality_rejections:
            print("\nRejection details:")
            for rejection in report.quality_rejections:
                print(f"\n  URL: {rejection.url}")
                print(f"  Reason: {rejection.reason}")
                print(f"  Timestamp: {rejection.timestamp}")
        
        print(f"\nFull report saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Disable Quality Gates
# ═══════════════════════════════════════════════════════════════════════════════

async def example_no_quality_gates():
    """Example with quality gates disabled (accept everything)."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: QUALITY GATES DISABLED")
    print("=" * 80)
    
    urls = [
        "https://www.sahibinden.com/ilan/any-listing-123",
        "https://www.sahibinden.com/ilan/any-listing-456",
    ]
    
    reporter = Reporter(
        run_id=f"no_gates_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        parser_type="sahibinden"
    )
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        reporter=reporter,
        enable_quality_gates=False  # Quality gates DISABLED
    )
    
    try:
        stats = await crawler.run(urls)
        report = reporter.generate_report()
        
        report_path = Path("reports") / f"{reporter.run_id}.json"
        report.save(report_path)
        
        print("\n" + "-" * 80)
        print("NO QUALITY GATES - All listings accepted")
        print("-" * 80)
        print(f"Processed:           {stats.total}")
        print(f"Quality rejections:  {len(report.quality_rejections)} (expected 0)")
        print(f"Report saved to:     {report_path}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Failure Categorization
# ═══════════════════════════════════════════════════════════════════════════════

async def example_failure_categorization():
    """Example showing different failure categories."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 4: FAILURE CATEGORIZATION")
    print("=" * 80)
    
    # Mix of valid and invalid URLs
    urls = [
        "https://www.sahibinden.com/ilan/valid-123",
        "https://invalid-domain.com/ilan/test",  # Fetch failure
        "not-a-valid-url",  # Fetch failure
        "https://www.sahibinden.com/ilan/valid-456",
    ]
    
    reporter = Reporter(
        run_id=f"failures_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        parser_type="sahibinden"
    )
    
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        reporter=reporter,
        enable_quality_gates=True
    )
    
    try:
        stats = await crawler.run(urls)
        report = reporter.generate_report()
        
        report_path = Path("reports") / f"{reporter.run_id}.json"
        report.save(report_path)
        
        print("\n" + "-" * 80)
        print("FAILURE CATEGORIZATION")
        print("-" * 80)
        print(f"Total URLs:          {stats.total}")
        print(f"Successful:          {stats.inserted + stats.updated}")
        print(f"Failed:              {stats.failed}")
        
        print("\nFailure breakdown:")
        for category, count in report.failure_breakdown.items():
            if count > 0:
                print(f"  {category:20} {count}")
        
        # Show failure details
        if report.failures:
            print("\nFailure details:")
            for failure in report.failures:
                print(f"\n  URL: {failure.url}")
                print(f"  Category: {failure.category}")
                print(f"  Reason: {failure.reason}")
                print(f"  Step: {failure.step}")
        
        print(f"\nFull report saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: Reading and Analyzing Reports
# ═══════════════════════════════════════════════════════════════════════════════

def example_read_report():
    """Example: read and analyze a saved report."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE 5: READING SAVED REPORTS")
    print("=" * 80)
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print("No reports directory found")
        return
    
    # Find latest report
    report_files = list(reports_dir.glob("*.json"))
    if not report_files:
        print("No reports found")
        return
    
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\nReading: {latest_report}")
    
    # Read JSON
    import json
    with open(latest_report, 'r') as f:
        report_data = json.load(f)
    
    # Analyze
    print("\n" + "-" * 80)
    print("REPORT ANALYSIS")
    print("-" * 80)
    print(f"Run ID:              {report_data['run_id']}")
    print(f"Parser:              {report_data['parser_type']}")
    print(f"Start time:          {report_data['start_time']}")
    print(f"Duration:            {report_data['duration_seconds']:.2f}s")
    
    print(f"\nStatistics:")
    for key, value in report_data['stats'].items():
        print(f"  {key:20} {value}")
    
    success_rate = (
        (report_data['stats']['inserted'] + report_data['stats']['updated']) / 
        report_data['stats']['total'] * 100
    )
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    print(f"\nSuccessful listings: {len(report_data['successful'])}")
    if report_data['successful']:
        print("  Sample successful URLs:")
        for record in report_data['successful'][:3]:
            print(f"    - {record['url']} ({record['operation']}, {record['confidence']})")
    
    print(f"\nQuality rejections: {len(report_data['quality_rejections'])}")
    if report_data['quality_rejections']:
        print("  Rejection reasons:")
        for rejection in report_data['quality_rejections']:
            print(f"    - {rejection['reason']}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Run all examples."""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 18 + "STEP 9: OBSERVABILITY & QUALITY GATES DEMO" + " " * 18 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Check MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("\n⚠️  WARNING: MONGO_URI environment variable not set")
        print("   Some examples may fail without a MongoDB connection")
        print("   Set it with: export MONGO_URI='mongodb://localhost:27017'")
        print()
    
    print("\nThis demo will:")
    print("1. Run crawls with quality gates enabled")
    print("2. Track all events (successes, failures, rejections)")
    print("3. Generate JSON reports")
    print("4. Save reports to ./reports/ directory")
    print("\n(Note: Examples use placeholder URLs)")
    
    try:
        # Run examples
        await example_basic_reporting()
        
        # Uncomment to run other examples:
        # await example_quality_gates()
        # await example_no_quality_gates()
        # await example_failure_categorization()
        
        # Read saved reports
        # example_read_report()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED")
        print("=" * 80)
        print("\nCheck ./reports/ directory for generated JSON reports")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE NOTES
# ═══════════════════════════════════════════════════════════════════════════════

"""
QUALITY GATES EXPLAINED:

The system applies these deterministic rules:

1. Low Confidence + No Phone
   - If normalized data has confidence='low' AND phone_number is None
   - Reason: Unreliable data without contact info
   
2. Missing Location
   - If BOTH city and district are None
   - Reason: Cannot categorize listing geographically
   
3. Sparse Parsed Data
   - If parser extracted < 2 meaningful fields
   - Fields: office_name, agent_name, phone_number, city, district
   - Reason: Insufficient data extracted

FAILURE CATEGORIES:

- fetch_failed: HTTP errors, network issues, timeouts
- parse_failed: HTML parsing errors, structure changes
- normalize_failed: Data validation errors
- persist_failed: Database errors
- quality_rejected: Failed quality gates

REPORT STRUCTURE:

{
  "run_id": "crawl_20260202_101530",
  "start_time": "2026-02-02T10:15:30.123456",
  "end_time": "2026-02-02T10:16:45.789012",
  "duration_seconds": 75.67,
  "parser_type": "sahibinden",
  "total_urls": 10,
  
  "successful": [
    {
      "url": "https://...",
      "listing_id": "507f...",
      "operation": "inserted",
      "timestamp": "2026-02-02T10:15:35.123456",
      "confidence": "high"
    }
  ],
  
  "failures": [
    {
      "url": "https://...",
      "category": "fetch_failed",
      "reason": "HTTP 404 for https://...",
      "timestamp": "2026-02-02T10:15:40.123456",
      "step": "fetch"
    }
  ],
  
  "quality_rejections": [
    {
      "url": "https://...",
      "reason": "Low confidence listing with no phone number",
      "timestamp": "2026-02-02T10:15:42.123456",
      "data_snapshot": {...}
    }
  ],
  
  "stats": {
    "total": 10,
    "fetched": 9,
    "parsed": 8,
    "normalized": 8,
    "inserted": 5,
    "updated": 2,
    "failed": 2,
    "quality_rejected": 1
  },
  
  "failure_breakdown": {
    "fetch_failed": 1,
    "parse_failed": 0,
    "normalize_failed": 0,
    "persist_failed": 1,
    "quality_rejected": 1
  }
}

RUNNING THIS DEMO:

    # Set MongoDB connection
    export MONGO_URI='mongodb://localhost:27017'
    
    # Run the demo
    python examples/run_with_report.py
    
    # Check generated reports
    ls -lh reports/

INTEGRATION WITH EXISTING CODE:

The crawler is backward compatible. To use without reporting:

    # Without reporter (original behavior)
    crawler = Crawler(parser=SahibindenParser())
    stats = await crawler.run(urls)
    
    # With reporter (new in STEP 9)
    reporter = Reporter()
    crawler = Crawler(
        parser=SahibindenParser(),
        reporter=reporter,
        enable_quality_gates=True
    )
    stats = await crawler.run(urls)
    report = reporter.generate_report()
    report.save(Path("report.json"))
"""

if __name__ == "__main__":
    asyncio.run(main())
