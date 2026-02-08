"""STEP 10: Execution Modes & Safety Controls Demo

Demonstrates the three execution modes and safety stop conditions:

1. DRY RUN - Validate without database writes
2. SAFE RUN - Only persist high/medium confidence
3. FULL RUN - Persist everything (default)

Also demonstrates safety stop conditions:
- Fetch failure rate threshold
- Consecutive block detection
- Quality rejection rate threshold
"""

import asyncio
from pathlib import Path

from src.adapters.sahibinden.parser import SahibindenParser
from src.core.crawler import Crawler
from src.core.reporting import Reporter


# ═══════════════════════════════════════════════════════════════════════════════
# SAMPLE URLS FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════════

# Mix of valid and invalid URLs to test safety conditions
SAMPLE_URLS = [
    # Valid URLs (these would work if pages existed)
    "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456",
    "https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-234567",
    "https://www.sahibinden.com/ilan/emlak-konut-kiralik-ankara-cankaya-345678",
    "https://www.sahibinden.com/ilan/emlak-konut-kiralik-izmir-bornova-456789",
    "https://www.sahibinden.com/ilan/emlak-konut-kiralik-bursa-osmangazi-567890",
]

# URLs that will trigger failures (for safety testing)
FAILING_URLS = [
    "https://invalid-domain-12345.com/ilan/test",
    "https://invalid-domain-67890.com/ilan/test",
    "https://invalid-domain-11111.com/ilan/test",
    "https://invalid-domain-22222.com/ilan/test",
    "https://invalid-domain-33333.com/ilan/test",
    "https://invalid-domain-44444.com/ilan/test",
]


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 1: DRY RUN MODE
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_dry_run():
    """Demonstrate dry_run mode - no database writes."""
    
    print("=" * 80)
    print("DEMO 1: DRY RUN MODE")
    print("=" * 80)
    print("Purpose: Validate URLs and data without writing to database")
    print("Use case: Testing new parsers, validating URL lists")
    print()
    
    # Initialize reporter with dry_run mode
    reporter = Reporter(
        run_id="dry_run_demo",
        parser_type="sahibinden",
        run_mode="dry_run"
    )
    
    # Initialize crawler in dry_run mode
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="dry_run"
    )
    
    # Run crawl (will not write to database)
    stats = await crawler.run(SAMPLE_URLS[:3])
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "dry_run_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Dry run completed: {stats}")
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ Run mode: {report.run_mode}")
    print(f"✓ No database writes were performed")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 2: SAFE RUN MODE
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_safe_run():
    """Demonstrate safe_run mode - only high/medium confidence persists."""
    
    print("=" * 80)
    print("DEMO 2: SAFE RUN MODE")
    print("=" * 80)
    print("Purpose: Only persist high-quality listings (high/medium confidence)")
    print("Use case: Production runs where data quality is critical")
    print()
    
    # Initialize reporter with safe_run mode
    reporter = Reporter(
        run_id="safe_run_demo",
        parser_type="sahibinden",
        run_mode="safe_run"
    )
    
    # Initialize crawler in safe_run mode
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="safe_run",
        enable_quality_gates=True
    )
    
    # Run crawl (only high/medium confidence will be persisted)
    stats = await crawler.run(SAMPLE_URLS[:3])
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "safe_run_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Safe run completed: {stats}")
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ Run mode: {report.run_mode}")
    print(f"✓ Only high/medium confidence listings were persisted")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 3: FULL RUN MODE
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_full_run():
    """Demonstrate full_run mode - persist everything."""
    
    print("=" * 80)
    print("DEMO 3: FULL RUN MODE")
    print("=" * 80)
    print("Purpose: Persist all listings regardless of confidence")
    print("Use case: Data collection, archival, research")
    print()
    
    # Initialize reporter with full_run mode
    reporter = Reporter(
        run_id="full_run_demo",
        parser_type="sahibinden",
        run_mode="full_run"
    )
    
    # Initialize crawler in full_run mode (default)
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="full_run",
        enable_quality_gates=True
    )
    
    # Run crawl (everything will be persisted)
    stats = await crawler.run(SAMPLE_URLS[:3])
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "full_run_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Full run completed: {stats}")
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ Run mode: {report.run_mode}")
    print(f"✓ All listings were persisted")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 4: SAFETY STOP - FETCH FAILURE RATE
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_safety_fetch_failures():
    """Demonstrate safety stop on high fetch failure rate."""
    
    print("=" * 80)
    print("DEMO 4: SAFETY STOP - FETCH FAILURE RATE")
    print("=" * 80)
    print("Purpose: Stop crawl if too many URLs fail to fetch")
    print("Safety threshold: 50% fetch failure rate")
    print()
    
    # Initialize reporter
    reporter = Reporter(
        run_id="safety_fetch_demo",
        parser_type="sahibinden",
        run_mode="full_run"
    )
    
    # Initialize crawler with safety limits
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="full_run",
        safety_config={
            "max_fetch_failure_rate": 0.5,  # Stop if >50% fail
            "max_consecutive_blocks": 10,
            "max_quality_rejection_rate": 0.9,
            "min_urls_before_checks": 5,  # Apply checks after 5 URLs
        }
    )
    
    # Use URLs that will fail (will trigger safety stop)
    stats = await crawler.run(FAILING_URLS)
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "safety_fetch_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Safety stop triggered: {stats}")
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ Stop reason: {report.stop_reason}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 5: SAFETY STOP - CONSECUTIVE BLOCKS
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_safety_consecutive_blocks():
    """Demonstrate safety stop on consecutive fetch failures."""
    
    print("=" * 80)
    print("DEMO 5: SAFETY STOP - CONSECUTIVE BLOCKS")
    print("=" * 80)
    print("Purpose: Stop crawl if too many consecutive fetches fail")
    print("Safety threshold: 3 consecutive failures (indicating IP block)")
    print()
    
    # Initialize reporter
    reporter = Reporter(
        run_id="safety_blocks_demo",
        parser_type="sahibinden",
        run_mode="full_run"
    )
    
    # Initialize crawler with strict consecutive block limit
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="full_run",
        safety_config={
            "max_fetch_failure_rate": 0.9,  # High threshold
            "max_consecutive_blocks": 3,  # Stop after 3 consecutive failures
            "max_quality_rejection_rate": 0.9,
            "min_urls_before_checks": 1,  # Apply checks immediately
        }
    )
    
    # Use failing URLs (will trigger consecutive block detection)
    stats = await crawler.run(FAILING_URLS[:5])
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "safety_blocks_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Safety stop triggered: {stats}")
    print(f"✓ Report saved to: {report_path}")
    print(f"✓ Stop reason: {report.stop_reason}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO 6: CUSTOM SAFETY CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_custom_safety_config():
    """Demonstrate custom safety configuration."""
    
    print("=" * 80)
    print("DEMO 6: CUSTOM SAFETY CONFIGURATION")
    print("=" * 80)
    print("Purpose: Configure custom safety thresholds per crawl")
    print()
    
    # Custom safety configuration
    custom_safety = {
        "max_fetch_failure_rate": 0.3,      # Stop at 30% failure rate
        "max_consecutive_blocks": 2,         # Stop after 2 consecutive failures
        "max_quality_rejection_rate": 0.6,   # Stop at 60% quality rejections
        "min_urls_before_checks": 3,         # Apply checks after 3 URLs
    }
    
    print("Custom safety config:")
    for key, value in custom_safety.items():
        print(f"  {key}: {value}")
    print()
    
    # Initialize reporter
    reporter = Reporter(
        run_id="custom_safety_demo",
        parser_type="sahibinden",
        run_mode="full_run"
    )
    
    # Initialize crawler with custom safety config
    crawler = Crawler(
        parser=SahibindenParser(),
        mongo_uri="mongodb://localhost:27017",
        reporter=reporter,
        run_mode="full_run",
        safety_config=custom_safety
    )
    
    # Run with sample URLs
    stats = await crawler.run(SAMPLE_URLS)
    
    # Generate and save report
    report = reporter.generate_report()
    report_path = Path("reports") / "custom_safety_demo.json"
    report.save(report_path)
    
    print()
    print(f"✓ Custom safety crawl completed: {stats}")
    print(f"✓ Report saved to: {report_path}")
    if report.stop_reason:
        print(f"✓ Stop reason: {report.stop_reason}")
    else:
        print(f"✓ No safety stops triggered")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Run demo menu."""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "STEP 10: EXECUTION MODES & SAFETY CONTROLS" + " " * 16 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    print("Available demos:")
    print("  1. Dry Run Mode (validation without DB writes)")
    print("  2. Safe Run Mode (only high/medium confidence)")
    print("  3. Full Run Mode (persist everything)")
    print("  4. Safety Stop: Fetch Failure Rate")
    print("  5. Safety Stop: Consecutive Blocks")
    print("  6. Custom Safety Configuration")
    print("  7. Run all demos")
    print()
    
    choice = input("Select demo (1-7): ").strip()
    
    demos = {
        "1": demo_dry_run,
        "2": demo_safe_run,
        "3": demo_full_run,
        "4": demo_safety_fetch_failures,
        "5": demo_safety_consecutive_blocks,
        "6": demo_custom_safety_config,
    }
    
    if choice in demos:
        await demos[choice]()
    elif choice == "7":
        # Run all demos
        for demo_func in demos.values():
            await demo_func()
            print("\n" + "-" * 80 + "\n")
    else:
        print("Invalid choice")
    
    print()
    print("✓ Demo completed!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
