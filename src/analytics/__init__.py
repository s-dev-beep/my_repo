"""Analytics module for saturation measurement and completion assessment.

This module provides read-only analysis of discovery saturation for Istanbul.

READ-ONLY CONSTRAINT:
- All classes only READ from identity graph
- No database writes
- No crawler invocation
- No enrichment invocation
- No identity changes
- Deterministic logic only

Key Components:
- SaturationMetricsComputer: Computes NEW_PHONE_RATE, REVISIT_RATE, ENRICHMENT_YIELD, coverage
- DistrictTracker: Tracks per-district saturation status and scoring
- CityCompletion: Assesses city-wide completion readiness
- StoppingRuleSet: Implements stopping decision logic with thresholds
- SaturationSnapshot: Creates and manages JSON snapshots for reporting

Basic Usage:

    from pymongo import MongoClient
    from src.analytics.saturation_snapshot import SaturationSnapshot
    
    client = MongoClient("mongodb://localhost:27017")
    db = client.real_estate
    
    snapshot_gen = SaturationSnapshot(db)
    snapshot = snapshot_gen.create_and_save_snapshot(
        window_hours=24,
        run_id="crawl_20260202_175806"
    )
    
    print(snapshot_gen.generate_summary_report(snapshot))
    
    # Check if ready to stop
    should_stop, evidence = snapshot_gen.rules.should_stop_crawling()
    if should_stop:
        print("✅ READY TO STOP - Discovery is complete")
    else:
        print("❌ CONTINUE CRAWLING - More discovery needed")
"""

from src.analytics.saturation_metrics import SaturationMetricsComputer
from src.analytics.district_tracker import DistrictTracker
from src.analytics.city_completion import CityCompletion
from src.analytics.stopping_rules import StoppingRuleSet
from src.analytics.saturation_snapshot import SaturationSnapshot

__all__ = [
    "SaturationMetricsComputer",
    "DistrictTracker",
    "CityCompletion",
    "StoppingRuleSet",
    "SaturationSnapshot",
]
