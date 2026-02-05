"""CLI command handlers.

STEP 11: Command Line Interface

This module implements the 'crawl' command by orchestrating
the existing Crawler class. No crawler logic is modified.
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from src.core.logger import setup_logger
from src.core.crawler import Crawler
from src.core.reporting import Reporter
from src.cli.loaders import (
    load_urls_from_file,
    load_config_file,
    detect_parser_type,
    create_parser,
)
from src.experiments import AccessSurfaceExperiment, BrowserFeasibilityTest

logger = setup_logger(__name__)


async def crawl_command(
    url_file: str,
    mode: Optional[str] = None,
    limit: Optional[int] = None,
    config_path: Optional[str] = None,
    report_path: Optional[str] = None,
) -> int:
    """Execute the crawl command.
    
    This is pure orchestration - calls existing Crawler with no modifications.
    
    Args:
        url_file: Path to file with URLs
        mode: Execution mode (dry_run, safe_run, full_run) or None for config default
        limit: Max URLs to process or None for all
        config_path: Custom config file path or None for default
        report_path: Custom report path or None for auto-generated
    
    Returns:
        Exit code:
            0 = success
            1 = invalid input
            2 = safety stop triggered
            3 = runtime error
    """
    try:
        # ========================================================================
        # STEP 1: Load URLs from file
        # ========================================================================
        logger.info(f"Loading URLs from: {url_file}")
        try:
            urls = load_urls_from_file(url_file)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load URLs: {e}")
            return 1
        
        # Apply limit if specified
        if limit is not None:
            original_count = len(urls)
            urls = urls[:limit]
            logger.info(f"Limited to first {limit} URLs (out of {original_count})")
        
        # ========================================================================
        # STEP 2: Load configuration
        # ========================================================================
        try:
            config = load_config_file(config_path)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load config: {e}")
            return 1
        
        # ========================================================================
        # STEP 3: Override config with CLI flags
        # ========================================================================
        # Override run_mode if specified
        if mode is not None:
            if 'crawler' not in config:
                config['crawler'] = {}
            config['crawler']['run_mode'] = mode
            logger.info(f"Overriding run_mode with CLI flag: {mode}")
        
        # Get final run_mode (from CLI or config)
        run_mode = config.get('crawler', {}).get('run_mode', 'full_run')
        logger.info(f"Execution mode: {run_mode}")
        
        # Get safety config
        safety_config = config.get('crawler', {}).get('safety', {})
        
        # Get MongoDB config
        mongo_uri = config.get('database', {}).get('mongo_uri')
        db_name = config.get('database', {}).get('db_name', 'real_estate_crawler')
        
        # ========================================================================
        # STEP 4: Detect parser type and create parser
        # ========================================================================
        try:
            parser_type = detect_parser_type(urls)
            parser = create_parser(parser_type)
        except ValueError as e:
            logger.error(f"Failed to create parser: {e}")
            return 1
        
        # ========================================================================
        # STEP 5: Create Reporter
        # ========================================================================
        # Generate run_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"crawl_{timestamp}"
        
        reporter = Reporter(
            run_id=run_id,
            parser_type=parser_type,
            run_mode=run_mode,
        )
        
        # ========================================================================
        # STEP 6: Create Crawler instance (uses existing Crawler as-is)
        # ========================================================================
        logger.info("Initializing Crawler...")
        crawler = Crawler(
            parser=parser,
            mongo_uri=mongo_uri,
            db_name=db_name,
            reporter=reporter,
            run_mode=run_mode,
            safety_config=safety_config if safety_config else None,
        )
        
        # ========================================================================
        # STEP 7: Run the crawl
        # ========================================================================
        logger.info(f"Starting crawl with {len(urls)} URLs...")
        logger.info(f"Parser: {parser_type}")
        logger.info(f"Mode: {run_mode}")
        
        # Run crawl (returns CrawlStats)
        stats = await crawler.run(urls)
        
        # Generate report from reporter
        report = reporter.generate_report()
        
        # ========================================================================
        # STEP 8: Save report
        # ========================================================================
        # Generate report path if not specified
        if report_path is None:
            report_path = f"reports/{run_id}.json"
        
        # Ensure reports directory exists
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        report.save(report_file)
        logger.info(f"Report saved to: {report_path}")
        
        # ========================================================================
        # STEP 9: Determine exit code
        # ========================================================================
        # Check if safety stop was triggered
        if report.stop_reason:
            logger.warning(f"Crawl stopped early: {report.stop_reason}")
            return 2
        
        # Check for failures
        if stats.failed > 0:
            logger.warning(
                f"Crawl completed with {stats.failed} failures. "
                "See report for details."
            )
        
        # Success
        logger.info(
            f"Crawl completed successfully: "
            f"{len(report.successful)} succeeded, "
            f"{len(report.failures)} failed, "
            f"{len(report.quality_rejections)} quality rejected"
        )
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Crawl interrupted by user")
        return 3
    
    except Exception as e:
        logger.error(f"Crawl failed with runtime error: {e}", exc_info=True)
        return 3


async def access_surface_command(
    listing_url: str,
    agent_url: str,
    office_url: str,
    search_url: str,
    config_path: Optional[str] = None,
    report_path: Optional[str] = None,
) -> int:
    """Execute STEP 22-A access surface experiment.

    Returns:
        Exit code:
            0 = success (no blocking)
            2 = blocked/aborted (403/429)
            3 = runtime error
    """
    try:
        # Load configuration for MongoDB
        try:
            config = load_config_file(config_path)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load config: {e}")
            return 1

        mongo_uri = config.get("database", {}).get("mongo_uri")
        db_name = config.get("database", {}).get("db_name", "real_estate_crawler")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if report_path is None:
            report_path = f"reports/step22a_{timestamp}.json"

        experiment = AccessSurfaceExperiment(
            mongo_uri=mongo_uri,
            db_name=db_name,
            requests_per_minute=3,
        )

        report = await experiment.run(
            listing_url=listing_url,
            agent_profile_url=agent_url,
            office_url=office_url,
            search_url=search_url,
            report_path=report_path,
        )

        if report.get("summary", {}).get("aborted"):
            logger.warning(
                "Access surface experiment aborted: "
                f"{report['summary'].get('abort_reason')}"
            )
            return 2

        logger.info("Access surface experiment completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Access surface experiment failed: {e}", exc_info=True)
        return 3


async def browser_feasibility_command(
    url: str,
    report_path: Optional[str] = None,
    screenshot_path: Optional[str] = None,
    headless: bool = False,
) -> int:
    """Execute STEP 23 browser-based feasibility test.

    Returns:
        Exit code:
            0 = success
            2 = block detected
            3 = runtime error
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if report_path is None:
            report_path = f"reports/step23_{timestamp}.json"
        if screenshot_path is None:
            screenshot_path = f"reports/step23_{timestamp}.png"

        tester = BrowserFeasibilityTest(headed=not headless)
        report = tester.run(
            url=url,
            report_path=report_path,
            screenshot_path=screenshot_path,
        )

        if report.get("result", {}).get("block_detected"):
            logger.warning("Browser feasibility test detected blocking")
            return 2

        logger.info("Browser feasibility test completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Browser feasibility test failed: {e}", exc_info=True)
        return 3
