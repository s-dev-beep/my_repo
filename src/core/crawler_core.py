"""Core crawler orchestration logic.

STEP 8: PIPELINE ORCHESTRATION
STEP 10: EXECUTION MODES & SAFETY CONTROLS

Extracted from crawler.py for better modularity.
This module contains the main Crawler class and pipeline orchestration logic.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.core.logger import setup_logger
from src.core.fetcher import Fetcher, FetchError, BlockedError
from src.core.parser import Parser
from src.core.normalizer import Normalizer
from src.core.deduplicator import Deduplicator
from src.db.mongo import MongoDBConnection
from src.core.reporting import Reporter, QualityGates
from src.core.crawler_modes import get_execution_mode
from src.core.crawler_safety import SafetyChecker

logger = setup_logger(__name__)


@dataclass
class CrawlStats:
    """Statistics for a crawl run."""
    
    total: int = 0
    """Total URLs processed."""
    
    fetched: int = 0
    """Successfully fetched."""
    
    parsed: int = 0
    """Successfully parsed."""
    
    normalized: int = 0
    """Successfully normalized."""
    
    inserted: int = 0
    """New listings inserted."""
    
    updated: int = 0
    """Existing listings updated."""
    
    skipped: int = 0
    """Skipped (duplicates in memory)."""
    
    failed: int = 0
    """Failed to process."""
    
    consecutive_fetch_failures: int = 0
    """Consecutive fetch failures (for early stop)."""
    
    def __str__(self) -> str:
        """Format stats as human-readable string."""
        return (
            f"CrawlStats(total={self.total}, "
            f"fetched={self.fetched}, "
            f"parsed={self.parsed}, "
            f"normalized={self.normalized}, "
            f"inserted={self.inserted}, "
            f"updated={self.updated}, "
            f"skipped={self.skipped}, "
            f"failed={self.failed})"
        )


class Crawler:
    """Pipeline orchestrator for real estate listings.
    
    Coordinates the flow:
    1. Fetch HTML from URLs (Fetcher)
    2. Parse HTML to extract data (Parser)
    3. Normalize data to clean format (Normalizer)
    4. Check for duplicates (Deduplicator)
    5. Persist to MongoDB (MongoDBConnection)
    
    Design principles:
    - Process one listing at a time (no batching)
    - Continue on individual failures
    - Respect rate limits
    - Clear logging at each step
    - Track statistics
    """
    
    def __init__(
        self,
        parser: Parser,
        mongo_uri: Optional[str] = None,
        db_name: str = "real_estate_crawler",
        fetcher_config: Optional[Dict[str, Any]] = None,
        reporter: Optional[Reporter] = None,
        enable_quality_gates: bool = True,
        run_mode: str = "full_run",
        safety_config: Optional[Dict[str, Any]] = None,
        source: str = "sahibinden",
    ):
        """Initialize crawler with components.
        
        Args:
            parser: Parser instance for the target site
            mongo_uri: MongoDB connection URI (or set MONGO_URI env var)
            db_name: MongoDB database name
            fetcher_config: Optional config for Fetcher (rate limits, etc.)
            reporter: Optional Reporter for tracking events
            enable_quality_gates: Whether to apply quality validation
            run_mode: Execution mode - dry_run, safe_run, or full_run
            safety_config: Safety stop conditions config
            source: Data source (sahibinden, hepsiemlak, google) - STEP 18
        """
        # Validate inputs
        if not isinstance(parser, Parser):
            raise ValueError("parser must be an instance of Parser")
        
        # Initialize components
        self.parser = parser
        self.normalizer = Normalizer()
        self.deduplicator = Deduplicator()
        
        # Fetcher configuration
        fetcher_kwargs = fetcher_config or {}
        self.fetcher = Fetcher(**fetcher_kwargs)
        
        # Database configuration
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        
        # Statistics
        self.stats = CrawlStats()
        
        # Reporting
        self.reporter = reporter
        self.enable_quality_gates = enable_quality_gates
        
        # Execution mode (STEP 18: Pass source to execution mode)
        self.run_mode = run_mode
        self.source = source
        self.execution_mode = get_execution_mode(run_mode, source=source)
        
        # Safety configuration
        default_safety_config = {
            "max_fetch_failure_rate": 0.5,
            "max_consecutive_blocks": 5,
            "max_quality_rejection_rate": 0.7,
            "min_urls_before_checks": 10,
        }
        self.safety_config = safety_config or default_safety_config
        self.safety_checker = SafetyChecker(self.safety_config)
        
        logger.info(
            f"Crawler initialized: "
            f"parser={parser.site_adapter}, "
            f"db={db_name}, "
            f"run_mode={run_mode}, "
            f"quality_gates={'enabled' if enable_quality_gates else 'disabled'}"
        )
    
    async def run(self, urls: List[str]) -> CrawlStats:
        """Run the crawling pipeline on a list of URLs.
        
        Processes one URL at a time:
        1. Fetch HTML
        2. Parse data
        3. Normalize
        4. Check for duplicates
        5. Persist to database
        
        If one listing fails, logs the error and continues with next.
        
        Args:
            urls: List of listing URLs to crawl
            
        Returns:
            CrawlStats object with processing statistics
            
        Raises:
            ValueError: If urls is empty
        """
        if not urls:
            raise ValueError("URLs list cannot be empty")
        
        # Reset statistics
        self.stats = CrawlStats()
        self.stats.total = len(urls)
        
        # Initialize reporter if provided
        if self.reporter:
            self.reporter.set_total_urls(len(urls))
        
        logger.info(f"Starting crawl: {len(urls)} URLs to process")
        
        # Log execution mode
        logger.info(f"Execution mode: {self.run_mode}")
        if self.run_mode == "dry_run":
            logger.info("DRY RUN: No database writes will be performed")
        elif self.run_mode == "safe_run":
            logger.info("SAFE RUN: Only high/medium confidence listings will persist")
        
        # Connect fetcher
        await self.fetcher.connect()
        
        try:
            # Open MongoDB connection
            with MongoDBConnection(uri=self.mongo_uri, db_name=self.db_name) as db:
                # Process each URL
                for idx, url in enumerate(urls, 1):
                    logger.info(f"[{idx}/{len(urls)}] Processing: {url}")
                    
                    # Check safety conditions before processing
                    should_stop, stop_reason = self.safety_checker.should_stop(
                        idx, self.stats, self.reporter, self.enable_quality_gates
                    )
                    if should_stop:
                        if self.reporter:
                            self.reporter.set_stop_reason(stop_reason)
                        logger.warning("Safety stop condition triggered, halting crawl")
                        break
                    
                    try:
                        await self._process_listing(url, db)
                    except Exception as e:
                        logger.error(f"Failed to process {url}: {e}", exc_info=True)
                        self.stats.failed += 1
                        # Record failure in reporter if available
                        if self.reporter:
                            category, step = self._categorize_failure(e)
                            self.reporter.record_failure(
                                url=url,
                                category=category,
                                reason=str(e),
                                step=step
                            )
                        continue
        
        finally:
            # Disconnect fetcher
            await self.fetcher.disconnect()
        
        # Log summary
        logger.info(f"Crawl completed: {self.stats}")
        self._log_summary()
        
        return self.stats
    
    async def _process_listing(self, url: str, db: MongoDBConnection) -> None:
        """Process a single listing through the pipeline.
        
        Args:
            url: Listing URL
            db: MongoDB connection
            
        Raises:
            FetchError: If fetching fails
            BlockedError: If repeated blocking detected
            Exception: For any other processing errors
        """
        # STEP 1: FETCH
        html = await self._fetch_url(url)
        
        # STEP 2: PARSE
        parsed_data = await self._parse_html(url, html)
        
        # STEP 3: NORMALIZE
        normalized_data = await self._normalize_data(url, parsed_data)
        
        # STEP 4: DEDUPLICATE
        await self._check_duplicate(url, normalized_data)
        
        # STEP 5: PERSIST
        await self._persist_listing(url, normalized_data, db)
    
    async def _fetch_url(self, url: str) -> str:
        """Fetch HTML from URL."""
        try:
            html = await self.fetcher.fetch(url)
            self.stats.fetched += 1
            self.stats.consecutive_fetch_failures = 0  # Reset on success
            if self.reporter:
                self.reporter.increment_stat("fetched")
            logger.debug(f"Fetched {len(html)} bytes from {url}")
            return html
        except (FetchError, BlockedError) as e:
            logger.error(f"Fetch failed for {url}: {e}")
            self.stats.consecutive_fetch_failures += 1
            raise
    
    async def _parse_html(self, url: str, html: str) -> Dict[str, Any]:
        """Parse HTML to extract data."""
        try:
            parsed_data = self.parser.parse_listing_page(html, url)
            if not parsed_data:
                logger.warning(f"Parser returned None for {url}")
                raise ValueError("Parser returned None")
            
            self.stats.parsed += 1
            if self.reporter:
                self.reporter.increment_stat("parsed")
            
            # Quality gate: Check parsed data
            if self.enable_quality_gates:
                rejection_reason = QualityGates.check_parsed_data(parsed_data)
                if rejection_reason:
                    logger.warning(f"Quality rejection at parse: {url} - {rejection_reason}")
                    if self.reporter:
                        self.reporter.record_quality_rejection(
                            url=url,
                            reason=rejection_reason,
                            data_snapshot=parsed_data
                        )
                    raise ValueError(f"Quality gate failed: {rejection_reason}")
            
            logger.debug(f"Parsed data: {list(parsed_data.keys())}")
            return parsed_data
        except Exception as e:
            logger.error(f"Parse failed for {url}: {e}")
            raise
    
    async def _normalize_data(self, url: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parsed data."""
        try:
            normalized_data = self.normalizer.normalize(parsed_data)
            self.stats.normalized += 1
            if self.reporter:
                self.reporter.increment_stat("normalized")
            
            # Quality gate: Check normalized data
            if self.enable_quality_gates:
                rejection_reason = QualityGates.check_normalized_data(normalized_data)
                if rejection_reason:
                    logger.warning(f"Quality rejection at normalize: {url} - {rejection_reason}")
                    if self.reporter:
                        self.reporter.record_quality_rejection(
                            url=url,
                            reason=rejection_reason,
                            data_snapshot=normalized_data
                        )
                    raise ValueError(f"Quality gate failed: {rejection_reason}")
            
            logger.debug(f"Normalized: confidence={normalized_data.get('confidence')}")
            return normalized_data
        except Exception as e:
            logger.error(f"Normalization failed for {url}: {e}")
            raise
    
    async def _check_duplicate(self, url: str, normalized_data: Dict[str, Any]) -> None:
        """Check for duplicate listing."""
        try:
            listing_dedup = self.deduplicator.check_listing(normalized_data)
            
            if not listing_dedup.is_new:
                logger.info(
                    f"Duplicate listing detected (in-memory): {url}. "
                    f"Reason: {listing_dedup.reason}"
                )
                self.stats.skipped += 1
            else:
                logger.debug(f"New listing (in-memory): {url}")
                # Register in deduplicator
                if listing_dedup.dedupe_key:
                    self.deduplicator.add_listing(listing_dedup.dedupe_key)
        except Exception as e:
            logger.error(f"Deduplication check failed for {url}: {e}")
            # Continue anyway - database will handle deduplication
    
    async def _persist_listing(
        self,
        url: str,
        normalized_data: Dict[str, Any],
        db: MongoDBConnection
    ) -> None:
        """Persist listing based on execution mode."""
        try:
            listing_id, operation = self.execution_mode.persist_listing(
                url, normalized_data, db
            )
            
            # Update stats
            if operation == 'inserted' or operation == 'simulated':
                self.stats.inserted += 1
            elif operation == 'updated':
                self.stats.updated += 1
            elif operation == 'skipped':
                self.stats.skipped += 1
            
            # Record success in reporter
            if self.reporter and operation in ["inserted", "updated", "simulated"]:
                self.reporter.record_success(
                    url=url,
                    listing_id=listing_id,
                    operation=operation if operation != "simulated" else "inserted",
                    confidence=normalized_data.get('confidence', 'unknown')
                )
        except Exception as e:
            logger.error(f"Database persistence failed for {url}: {e}")
            raise
    
    def _categorize_failure(self, exception: Exception) -> tuple[str, str]:
        """Categorize failure by exception type.
        
        Returns:
            Tuple of (category, step)
        """
        if isinstance(exception, (FetchError, BlockedError)):
            return "fetch_failed", "fetch"
        elif "parse" in str(exception).lower() or "Parser" in str(type(exception).__name__):
            return "parse_failed", "parse"
        elif "normal" in str(exception).lower():
            return "normalize_failed", "normalize"
        else:
            return "persist_failed", "persist"
    
    def _log_summary(self) -> None:
        """Log a formatted summary of crawl statistics."""
        logger.info("=" * 80)
        logger.info("CRAWL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total URLs:        {self.stats.total:>6}")
        logger.info(f"Successfully fetched: {self.stats.fetched:>6}")
        logger.info(f"Successfully parsed:  {self.stats.parsed:>6}")
        logger.info(f"Successfully normalized: {self.stats.normalized:>6}")
        logger.info(f"Inserted (new):    {self.stats.inserted:>6}")
        logger.info(f"Updated (existing): {self.stats.updated:>6}")
        logger.info(f"Skipped (duplicates): {self.stats.skipped:>6}")
        logger.info(f"Failed:            {self.stats.failed:>6}")
        logger.info("=" * 80)
        
        # Calculate success rate
        if self.stats.total > 0:
            success_rate = (
                (self.stats.inserted + self.stats.updated) / self.stats.total * 100
            )
            logger.info(f"Success rate: {success_rate:.1f}%")
    
    async def stop(self) -> None:
        """Gracefully stop the crawler.
        
        Closes all open connections.
        """
        logger.info("Stopping crawler...")
        await self.fetcher.disconnect()
        logger.info("Crawler stopped")
