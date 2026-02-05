"""Pipeline orchestrator for crawling real estate listings.

STEP 8: PIPELINE ORCHESTRATION
STEP 10: EXECUTION MODES & SAFETY CONTROLS

This module wires together all existing components:
- Fetcher: Downloads HTML
- Parser: Extracts data from HTML
- Normalizer: Cleans and standardizes data
- Deduplicator: Identifies duplicates
- MongoDB: Persists data

Flow: Fetch → Parse → Normalize → Deduplicate → Persist

STEP 10 additions:
- Execution modes: dry_run, safe_run, full_run
- Safety stop conditions: fetch failures, consecutive blocks, quality rejections
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
    
    # STEP 10: Safety tracking
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
    
    Example:
        >>> from src.adapters.sahibinden.parser import SahibindenParser
        >>> 
        >>> crawler = Crawler(
        ...     parser=SahibindenParser(),
        ...     mongo_uri="mongodb://localhost:27017"
        ... )
        >>> 
        >>> urls = [
        ...     "https://www.sahibinden.com/ilan/emlak-konut-kiralik-123",
        ...     "https://www.sahibinden.com/ilan/emlak-konut-kiralik-456"
        ... ]
        >>> 
        >>> stats = await crawler.run(urls)
        >>> print(stats)
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
    ):
        """Initialize crawler with components.
        
        Args:
            parser: Parser instance for the target site
            mongo_uri: MongoDB connection URI (or set MONGO_URI env var)
            db_name: MongoDB database name
            fetcher_config: Optional config for Fetcher (rate limits, etc.)
            reporter: Optional Reporter for tracking events (STEP 9)
            enable_quality_gates: Whether to apply quality validation (STEP 9)
            run_mode: Execution mode - dry_run, safe_run, or full_run (STEP 10)
            safety_config: Safety stop conditions config (STEP 10)
        """
        # Validate inputs
        if not isinstance(parser, Parser):
            raise ValueError("parser must be an instance of Parser")
        
        if run_mode not in ["dry_run", "safe_run", "full_run"]:
            raise ValueError(f"Invalid run_mode: {run_mode}. Must be dry_run, safe_run, or full_run")
        
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
        
        # Reporting (STEP 9)
        self.reporter = reporter
        self.enable_quality_gates = enable_quality_gates
        
        # STEP 10: Execution mode
        self.run_mode = run_mode
        
        # STEP 10: Safety configuration
        self.safety_config = safety_config or {
            "max_fetch_failure_rate": 0.5,
            "max_consecutive_blocks": 5,
            "max_quality_rejection_rate": 0.7,
            "min_urls_before_checks": 10,
        }
        
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
        
        # STEP 10: Log execution mode
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
                    
                    # STEP 10: Check safety conditions before processing
                    if self._should_stop_early(idx):
                        logger.warning("Safety stop condition triggered, halting crawl")
                        break
                    
                    try:
                        await self._process_listing(url, db)
                    except Exception as e:
                        logger.error(f"Failed to process {url}: {e}", exc_info=True)
                        self.stats.failed += 1
                        # Record failure in reporter if available
                        if self.reporter:
                            # Determine failure category from exception type
                            if isinstance(e, (FetchError, BlockedError)):
                                category = "fetch_failed"
                                step = "fetch"
                            elif "parse" in str(e).lower() or "Parser" in str(type(e).__name__):
                                category = "parse_failed"
                                step = "parse"
                            elif "normal" in str(e).lower():
                                category = "normalize_failed"
                                step = "normalize"
                            else:
                                category = "persist_failed"
                                step = "persist"
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
        try:
            html = await self.fetcher.fetch(url)
            self.stats.fetched += 1
            self.stats.consecutive_fetch_failures = 0  # Reset on success
            if self.reporter:
                self.reporter.increment_stat("fetched")
            logger.debug(f"Fetched {len(html)} bytes from {url}")
        except (FetchError, BlockedError) as e:
            logger.error(f"Fetch failed for {url}: {e}")
            self.stats.consecutive_fetch_failures += 1
            raise
        
        # STEP 2: PARSE
        try:
            parsed_data = self.parser.parse_listing_page(html, url)
            if not parsed_data:
                logger.warning(f"Parser returned None for {url}")
                raise ValueError("Parser returned None")
            
            self.stats.parsed += 1
            if self.reporter:
                self.reporter.increment_stat("parsed")
            
            # QUALITY GATE: Check parsed data (STEP 9)
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
        except Exception as e:
            logger.error(f"Parse failed for {url}: {e}")
            raise
        
        # STEP 3: NORMALIZE
        try:
            normalized_data = self.normalizer.normalize(parsed_data)
            self.stats.normalized += 1
            if self.reporter:
                self.reporter.increment_stat("normalized")
            
            # QUALITY GATE: Check normalized data (STEP 9)
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
            
            logger.debug(
                f"Normalized: confidence={normalized_data.get('confidence')}"
            )
        except Exception as e:
            logger.error(f"Normalization failed for {url}: {e}")
            raise
        
        # STEP 4: DEDUPLICATE
        try:
            listing_dedup = self.deduplicator.check_listing(normalized_data)
            
            if not listing_dedup.is_new:
                logger.info(
                    f"Duplicate listing detected (in-memory): {url}. "
                    f"Reason: {listing_dedup.reason}"
                )
                self.stats.skipped += 1
                # Still persist to database (upsert will update if changed)
                # But we know it's a duplicate in this crawl session
            else:
                logger.debug(f"New listing (in-memory): {url}")
                # Register in deduplicator
                if listing_dedup.dedupe_key:
                    self.deduplicator.add_listing(listing_dedup.dedupe_key)
        
        except Exception as e:
            logger.error(f"Deduplication check failed for {url}: {e}")
            # Continue anyway - we'll let database handle deduplication
        
        # STEP 5: PERSIST
        try:
            # STEP 10: Check run mode before persisting
            if self.run_mode == "dry_run":
                # Dry run: simulate persistence but don't write to database
                logger.info(f"[DRY RUN] Would persist listing: {url} (confidence={normalized_data.get('confidence')})")
                listing_id = "dry_run_simulated_id"
                operation = "simulated"
                self.stats.inserted += 1
                
            elif self.run_mode == "safe_run":
                # Safe run: only persist high/medium confidence
                confidence = normalized_data.get('confidence', 'unknown')
                if confidence in ['high', 'medium']:
                    listing_id, operation = db.upsert_listing(normalized_data)
                    if operation == 'inserted':
                        self.stats.inserted += 1
                        logger.info(f"✓ [SAFE RUN] Inserted listing: {url} (id={listing_id}, confidence={confidence})")
                    elif operation == 'updated':
                        self.stats.updated += 1
                        logger.info(f"✓ [SAFE RUN] Updated listing: {url} (id={listing_id}, confidence={confidence})")
                else:
                    logger.info(f"[SAFE RUN] Skipped low confidence listing: {url} (confidence={confidence})")
                    listing_id = "skipped_low_confidence"
                    operation = "skipped"
                    self.stats.skipped += 1
                    
            else:  # full_run
                # Full run: persist everything
                listing_id, operation = db.upsert_listing(normalized_data)
                if operation == 'inserted':
                    self.stats.inserted += 1
                    logger.info(f"✓ Inserted listing: {url} (id={listing_id})")
                elif operation == 'updated':
                    self.stats.updated += 1
                    logger.info(f"✓ Updated listing: {url} (id={listing_id})")
            
            # Record success in reporter (STEP 9)
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
    
    def _should_stop_early(self, current_idx: int) -> bool:
        """Check if crawler should stop early based on safety conditions.
        
        STEP 10: Safety stop conditions:
        1. Fetch failure rate exceeds threshold
        2. Too many consecutive fetch blocks/failures
        3. Quality rejection rate exceeds threshold
        
        Args:
            current_idx: Current URL index (1-based)
            
        Returns:
            True if should stop, False otherwise
        """
        min_urls = self.safety_config["min_urls_before_checks"]
        
        # Don't apply checks until minimum URLs processed
        if current_idx < min_urls:
            return False
        
        # Check 1: Fetch failure rate
        total_attempted = self.stats.fetched + self.stats.failed
        if total_attempted > 0:
            fetch_failure_rate = self.stats.failed / total_attempted
            max_fetch_failure_rate = self.safety_config["max_fetch_failure_rate"]
            
            if fetch_failure_rate > max_fetch_failure_rate:
                reason = (
                    f"Fetch failure rate {fetch_failure_rate:.1%} exceeds "
                    f"threshold {max_fetch_failure_rate:.1%} "
                    f"({self.stats.failed}/{total_attempted} failed)"
                )
                logger.error(f"SAFETY STOP: {reason}")
                if self.reporter:
                    self.reporter.set_stop_reason(reason)
                return True
        
        # Check 2: Consecutive fetch failures (blocks)
        max_consecutive = self.safety_config["max_consecutive_blocks"]
        if self.stats.consecutive_fetch_failures >= max_consecutive:
            reason = (
                f"Consecutive fetch failures ({self.stats.consecutive_fetch_failures}) "
                f"reached threshold ({max_consecutive}). Possible rate limiting or IP block."
            )
            logger.error(f"SAFETY STOP: {reason}")
            if self.reporter:
                self.reporter.set_stop_reason(reason)
            return True
        
        # Check 3: Quality rejection rate
        if self.reporter and self.enable_quality_gates:
            total_parsed = self.stats.parsed
            quality_rejected = self.reporter.stats.get("quality_rejected", 0)
            
            if total_parsed > 0:
                quality_rejection_rate = quality_rejected / total_parsed
                max_quality_rejection_rate = self.safety_config["max_quality_rejection_rate"]
                
                if quality_rejection_rate > max_quality_rejection_rate:
                    reason = (
                        f"Quality rejection rate {quality_rejection_rate:.1%} exceeds "
                        f"threshold {max_quality_rejection_rate:.1%} "
                        f"({quality_rejected}/{total_parsed} rejected)"
                    )
                    logger.error(f"SAFETY STOP: {reason}")
                    if self.reporter:
                        self.reporter.set_stop_reason(reason)
                    return True
        
        return False
