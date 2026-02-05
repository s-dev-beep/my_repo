"""Enrichment layer - read-only improvements to existing identities.

STEP 19: Enrichment Queue

This module provides a read-only enrichment layer that:
1. Identifies phone identities needing data improvement
2. Fetches minimal public data from external sources
3. Passes observations to IdentityGraphResolver
4. Lets graph decide to append or reject

Key principle: Identity graph is the ONLY writer.
Enrichment only reads and suggests.
"""

from src.enrichment.enrichment_queue import EnrichmentQueue
from src.enrichment.enrichment_runner import EnrichmentRunner
from src.enrichment.enrichment_task import EnrichmentTask

__all__ = [
    "EnrichmentQueue",
    "EnrichmentRunner",
    "EnrichmentTask",
]
