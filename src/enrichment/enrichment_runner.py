"""Enrichment runner - orchestrates enrichment from external sources.

STEP 19: Enrichment Queue

Coordinates:
1. Getting enrichment candidates
2. Fetching data from sources (Hepsiemlak, Google Places)
3. Passing enrichment to IdentityGraphResolver
4. Tracking enrichment progress
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo.database import Database

from src.core.logger import setup_logger
from src.identity import IdentityGraphResolver
from src.enrichment.enrichment_queue import EnrichmentQueue
from src.enrichment.enrichment_task import EnrichmentTask
from src.enrichment.sources.hepsiemlak_enricher import HepsiemlakEnricher
from src.enrichment.sources.google_places_enricher import GooglePlacesEnricher

logger = setup_logger(__name__)


class EnrichmentRunner:
    """Orchestrates enrichment of phone identities."""
    
    def __init__(
        self,
        db: Database,
        run_mode: str = "safe_run",
        google_api_key: Optional[str] = None
    ):
        """Initialize enrichment runner.
        
        Args:
            db: MongoDB database
            run_mode: dry_run | safe_run | full_run
            google_api_key: Optional Google Places API key
        """
        self.db = db
        self.run_mode = run_mode
        self.queue = EnrichmentQueue(db)
        self.graph = IdentityGraphResolver(db)
        
        # Initialize enrichment sources
        self.hepsiemlak = HepsiemlakEnricher(db)
        self.google = GooglePlacesEnricher(db, api_key=google_api_key)
        
        logger.info(
            f"EnrichmentRunner initialized: "
            f"mode={run_mode}, sources=hepsiemlak,google_places"
        )
    
    async def enrich_batch(
        self,
        limit: int = 10,
        timeout_seconds: float = 30.0
    ) -> Dict[str, Any]:
        """Enrich a batch of phone identities.
        
        Args:
            limit: Maximum phones to enrich in this batch
            timeout_seconds: Timeout for each enrichment source
            
        Returns:
            Dictionary with enrichment stats
        """
        # Get candidates
        candidates = self.queue.get_candidates(limit=limit)
        
        if not candidates:
            logger.info("No enrichment candidates found")
            return {
                "total_phones": 0,
                "successfully_enriched": 0,
                "failed": 0,
                "observations_added": 0,
            }
        
        logger.info(f"Starting enrichment batch: {len(candidates)} phones")
        
        # Track progress
        stats = {
            "total_phones": len(candidates),
            "successfully_enriched": 0,
            "failed": 0,
            "observations_added": 0,
            "phones": {}
        }
        
        # Process each candidate
        for candidate in candidates:
            phone_e164 = candidate["phone_e164"]
            confidence = candidate["confidence_score"]
            
            logger.info(f"\n[Enriching] {phone_e164} (confidence={confidence:.2f})")
            
            # Create enrichment task
            missing_fields = self.queue.get_missing_fields(phone_e164)
            task = EnrichmentTask(
                phone_e164=phone_e164,
                current_confidence=confidence,
                missing_fields=missing_fields
            )
            
            # Run enrichment with timeout
            try:
                result = await asyncio.wait_for(
                    self._enrich_phone(task),
                    timeout=timeout_seconds
                )
                
                stats["successfully_enriched"] += 1
                stats["observations_added"] += result["observations"]
                stats["phones"][phone_e164] = result
                
                logger.info(
                    f"✓ Enriched {phone_e164}: "
                    f"{result['observations']} observations added"
                )
                
            except asyncio.TimeoutError:
                logger.warning(f"Enrichment timeout for {phone_e164}")
                stats["failed"] += 1
                task.add_error("Enrichment timeout")
            except Exception as e:
                logger.error(f"Enrichment failed for {phone_e164}: {e}")
                stats["failed"] += 1
                task.add_error(str(e))
            finally:
                # Mark enriched regardless of success
                self.queue.mark_enriched(phone_e164)
        
        logger.info(
            f"\n{'='*60}\n"
            f"Enrichment batch complete:\n"
            f"- Total: {stats['total_phones']}\n"
            f"- Success: {stats['successfully_enriched']}\n"
            f"- Failed: {stats['failed']}\n"
            f"- Observations: {stats['observations_added']}\n"
            f"{'='*60}"
        )
        
        return stats
    
    async def _enrich_phone(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Enrich a single phone identity.
        
        Args:
            task: Enrichment task for this phone
            
        Returns:
            Dictionary with enrichment results
        """
        observations_added = 0
        
        # Try each source
        for source in task.sources_to_try:
            try:
                if source == "hepsiemlak":
                    observations = await self.hepsiemlak.enrich(
                        phone_e164=task.phone_e164,
                        missing_fields=task.missing_fields
                    )
                elif source == "google_places":
                    observations = await self.google.enrich(
                        phone_e164=task.phone_e164,
                        missing_fields=task.missing_fields
                    )
                else:
                    logger.warning(f"Unknown enrichment source: {source}")
                    continue
                
                # Process observations through identity graph
                for obs in observations:
                    try:
                        # Only write if not dry_run
                        if self.run_mode != "dry_run":
                            self.graph.add_enrichment_observation(
                                phone_e164=task.phone_e164,
                                field_name=obs["field_name"],
                                value=obs["value"],
                                source=source,
                                timestamp=obs.get("timestamp", datetime.utcnow())
                            )
                            observations_added += 1
                        else:
                            logger.debug(
                                f"[DRY RUN] Would add: "
                                f"{obs['field_name']}={obs['value']} "
                                f"from {source}"
                            )
                            observations_added += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to add observation for {task.phone_e164}: {e}"
                        )
                        continue
                
                logger.debug(f"✓ Enriched from {source}: {len(observations)} observations")
                
            except Exception as e:
                logger.warning(f"Enrichment from {source} failed: {e}")
                task.add_error(f"{source}: {str(e)}")
                continue
        
        task.mark_completed()
        return {
            "phone_e164": task.phone_e164,
            "observations": observations_added,
            "errors": task.errors,
        }
    
    async def continuous_enrich(
        self,
        batch_size: int = 10,
        batch_interval_seconds: float = 60.0,
        max_batches: Optional[int] = None
    ):
        """Run continuous enrichment in batches.
        
        Args:
            batch_size: Phones per batch
            batch_interval_seconds: Wait time between batches
            max_batches: Stop after N batches (None = infinite)
        """
        batch_count = 0
        
        logger.info(
            f"Starting continuous enrichment: "
            f"batch_size={batch_size}, "
            f"interval={batch_interval_seconds}s"
        )
        
        while max_batches is None or batch_count < max_batches:
            batch_count += 1
            logger.info(f"\n[Batch {batch_count}] Starting enrichment batch...")
            
            await self.enrich_batch(limit=batch_size)
            
            if max_batches is None or batch_count < max_batches:
                logger.info(
                    f"Waiting {batch_interval_seconds}s before next batch..."
                )
                await asyncio.sleep(batch_interval_seconds)
        
        logger.info(f"Continuous enrichment completed: {batch_count} batches")
