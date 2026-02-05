"""Saturation metrics computation.

Computes discovery saturation indicators for Istanbul:
- NEW_PHONE_RATE: Proportion of new phones in recent window
- PHONE_REVISIT_RATE: How often we see existing phones
- ENRICHMENT_YIELD: How much enrichment improves data quality
- PER_DISTRICT_COVERAGE: Geographic coverage metrics

All read-only. No database writes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pymongo.database import Database
from pymongo.collection import Collection


class SaturationMetricsComputer:
    """Computes all saturation metrics for a city/district.
    
    READ-ONLY: No database modifications.
    """
    
    def __init__(self, db: Database, city: str = "Istanbul"):
        """Initialize metrics computer.
        
        Args:
            db: MongoDB database connection
            city: City to compute metrics for (default: Istanbul)
        """
        self.db = db
        self.city = city
        self.phone_identities = db.phone_identities
        self.agent_profiles = db.agent_profiles
        self.offices = db.offices
        self.source_evidence = db.source_evidence
        self.agent_location_history = db.agent_location_history
    
    def compute_new_phone_rate(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Compute NEW_PHONE_RATE: % of new phones in recent window.
        
        NEW_PHONE_RATE = new_phones / total_phones_in_window
        
        - new_phones: phones with first_seen_at in [now-window, now]
        - total_phones_in_window: all phones with last_seen_at in [now-window, now]
        
        INTERPRETATION:
        - 1.0 (100%) = all phones are new = high discovery rate
        - 0.5 (50%) = half new, half revisits = moderate discovery
        - 0.0 (0%) = zero new phones = saturation point
        - Threshold: < 0.05 (< 5% new phones) = SATURATION LIKELY
        
        Args:
            window_hours: Time window in hours (default: 24)
        
        Returns:
            Dict with:
            - rate: float 0-1
            - new_phones: count
            - total_in_window: count
            - window_start: datetime
            - window_end: datetime
        """
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)
        
        # Count phones first seen in window
        new_phones = self.phone_identities.count_documents({
            "first_seen_at": {"$gte": window_start, "$lte": now}
        })
        
        # Count phones seen in window (any activity)
        total_in_window = self.phone_identities.count_documents({
            "last_seen_at": {"$gte": window_start, "$lte": now}
        })
        
        # Compute rate
        rate = new_phones / total_in_window if total_in_window > 0 else 0.0
        
        return {
            "metric": "NEW_PHONE_RATE",
            "rate": rate,
            "new_phones": new_phones,
            "total_in_window": total_in_window,
            "window_hours": window_hours,
            "window_start": window_start,
            "window_end": now,
            "timestamp": now
        }
    
    def compute_phone_revisit_rate(
        self,
        window_hours: int = 24,
        min_observations: int = 2
    ) -> Dict[str, Any]:
        """Compute PHONE_REVISIT_RATE: % of phones with multiple observations.
        
        PHONE_REVISIT_RATE = revisited_phones / total_phones_in_window
        
        - revisited_phones: observation_count >= min_observations
        - total_phones_in_window: phones active in window
        
        INTERPRETATION:
        - 0.9 (90%) = most phones seen multiple times = crawler is revisiting
        - 0.5 (50%) = half revisits = balanced discovery/revisit
        - 0.2 (20%) = mostly new phones = active discovery
        - Threshold: > 0.8 (> 80% revisits) = SATURATION LIKELY
        
        Args:
            window_hours: Time window in hours (default: 24)
            min_observations: Minimum observations to count as "revisited"
        
        Returns:
            Dict with:
            - rate: float 0-1
            - revisited_phones: count
            - total_in_window: count
        """
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)
        
        # Get all phones active in window
        active_in_window = self.phone_identities.aggregate([
            {
                "$match": {
                    "last_seen_at": {"$gte": window_start, "$lte": now}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "revisited": {
                        "$sum": {
                            "$cond": [
                                {"$gte": ["$observation_count", min_observations]},
                                1,
                                0
                            ]
                        }
                    }
                }
            }
        ])
        
        result = next(active_in_window, {"total": 0, "revisited": 0})
        total = result.get("total", 0)
        revisited = result.get("revisited", 0)
        
        rate = revisited / total if total > 0 else 0.0
        
        return {
            "metric": "PHONE_REVISIT_RATE",
            "rate": rate,
            "revisited_phones": revisited,
            "total_in_window": total,
            "min_observations": min_observations,
            "window_hours": window_hours,
            "timestamp": now
        }
    
    def compute_enrichment_yield(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Compute ENRICHMENT_YIELD: effectiveness of enrichment process.
        
        ENRICHMENT_YIELD = (phones_enriched / active_phones) * quality_improvement
        
        - phones_enriched: count with last_enriched_at in window
        - active_phones: phones active in window
        - quality_improvement: average confidence score change
        
        INTERPRETATION:
        - 0.0 = no enrichment happening = not improving data
        - 0.5 = moderate enrichment = some improvement
        - 1.0+ = extensive enrichment = high improvement
        - Threshold: < 0.1 (< 10% yield) = ENRICHMENT SATURATED
        
        Args:
            window_hours: Time window in hours (default: 24)
        
        Returns:
            Dict with:
            - yield: float (unitless)
            - phones_enriched: count
            - active_phones: count
            - avg_confidence_before: float
            - avg_confidence_after: float
            - avg_improvement: float
        """
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)
        
        # Count phones enriched in window
        enriched_in_window = self.phone_identities.count_documents({
            "last_enriched_at": {"$gte": window_start, "$lte": now}
        })
        
        # Count active phones in window
        active_in_window = self.phone_identities.count_documents({
            "last_seen_at": {"$gte": window_start, "$lte": now}
        })
        
        # Get average confidence before enrichment (for phones enriched in window)
        enriched_phones = list(
            self.phone_identities.find(
                {"last_enriched_at": {"$gte": window_start, "$lte": now}},
                {"confidence_score": 1}
            )
        )
        
        if enriched_phones:
            avg_confidence = sum(p.get("confidence_score", 0.0) for p in enriched_phones) / len(enriched_phones)
        else:
            avg_confidence = 0.0
        
        # Enrichment rate (proportion of active phones getting enriched)
        enrichment_rate = enriched_in_window / active_in_window if active_in_window > 0 else 0.0
        
        # Quality improvement (normalized confidence change)
        # Assume enrichment adds ~0.1 to confidence on average
        avg_improvement = 0.1 * enrichment_rate
        
        # Total yield
        yield_value = enrichment_rate * (1 + avg_improvement)
        
        return {
            "metric": "ENRICHMENT_YIELD",
            "yield": yield_value,
            "enrichment_rate": enrichment_rate,
            "phones_enriched": enriched_in_window,
            "active_phones": active_in_window,
            "avg_confidence": avg_confidence,
            "estimated_improvement": avg_improvement,
            "window_hours": window_hours,
            "timestamp": now
        }
    
    def compute_per_district_coverage(
        self,
        city: str = "Istanbul"
    ) -> Dict[str, Any]:
        """Compute PER_DISTRICT_COVERAGE metrics.
        
        For each district in city, compute:
        - phone_count: unique phones observed
        - listing_count: total listings from phone observations
        - confidence_avg: average confidence score
        - last_activity: most recent observation
        - growth_rate: phones added in last 24h
        
        INTERPRETATION:
        - Districts with high phone_count but low growth_rate = saturated
        - Districts with high growth_rate = active discovery
        - Districts with low phone_count = under-coverage
        
        Returns:
            Dict with:
            - city: city name
            - districts: List[Dict] with per-district metrics
            - summary: aggregate statistics
        """
        now = datetime.utcnow()
        yesterday = now - timedelta(hours=24)
        
        # Get location history for city
        district_stats = self.agent_location_history.aggregate([
            {
                "$match": {
                    "city": city,
                    "end_date": None  # Currently active location
                }
            },
            {
                "$group": {
                    "_id": "$district",
                    "phone_count": {"$sum": 1},
                    "total_observations": {"$sum": "$observation_count"},
                }
            },
            {
                "$sort": {"phone_count": -1}
            }
        ])
        
        districts = []
        for stat in district_stats:
            district = stat["_id"]
            
            # Count phones in this district
            phones_in_district = list(
                self.agent_location_history.find(
                    {"city": city, "district": district, "end_date": None},
                    {"phone_e164": 1}
                )
            )
            phone_list = [p["phone_e164"] for p in phones_in_district]
            
            if phone_list:
                # Get confidence scores for these phones
                confidences = list(
                    self.phone_identities.find(
                        {"phone_e164": {"$in": phone_list}},
                        {"confidence_score": 1}
                    )
                )
                avg_confidence = (
                    sum(c.get("confidence_score", 0.0) for c in confidences) / len(confidences)
                    if confidences else 0.0
                )
                
                # Count newly discovered phones (first_seen in last 24h)
                new_phones_24h = self.phone_identities.count_documents({
                    "phone_e164": {"$in": phone_list},
                    "first_seen_at": {"$gte": yesterday, "$lte": now}
                })
                
                # Most recent activity
                most_recent = self.phone_identities.find_one(
                    {"phone_e164": {"$in": phone_list}},
                    {"last_seen_at": 1},
                    sort=[("last_seen_at", -1)]
                )
                last_activity = most_recent.get("last_seen_at") if most_recent else None
            else:
                avg_confidence = 0.0
                new_phones_24h = 0
                last_activity = None
            
            districts.append({
                "district": district,
                "phone_count": len(phone_list),
                "listing_count": stat.get("total_observations", 0),
                "confidence_avg": round(avg_confidence, 3),
                "last_activity": last_activity,
                "new_phones_24h": new_phones_24h,
                "growth_rate": (new_phones_24h / len(phone_list)) if phone_list else 0.0
            })
        
        # Compute summary statistics
        total_phones = sum(d["phone_count"] for d in districts)
        total_listings = sum(d["listing_count"] for d in districts)
        avg_confidence = (
            sum(d["confidence_avg"] * d["phone_count"] for d in districts) / total_phones
            if total_phones > 0 else 0.0
        )
        total_new_24h = sum(d["new_phones_24h"] for d in districts)
        overall_growth = (total_new_24h / total_phones) if total_phones > 0 else 0.0
        
        return {
            "metric": "PER_DISTRICT_COVERAGE",
            "city": city,
            "districts": districts,
            "summary": {
                "total_districts": len(districts),
                "total_phones": total_phones,
                "total_listings": total_listings,
                "avg_confidence": round(avg_confidence, 3),
                "new_phones_24h": total_new_24h,
                "overall_growth_rate": round(overall_growth, 4)
            },
            "timestamp": now
        }
    
    def compute_all_metrics(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Compute all saturation metrics in one call.
        
        Returns a comprehensive snapshot of discovery saturation.
        
        Args:
            window_hours: Time window for window-based metrics
        
        Returns:
            Dict with all metrics computed
        """
        return {
            "new_phone_rate": self.compute_new_phone_rate(window_hours),
            "phone_revisit_rate": self.compute_phone_revisit_rate(window_hours),
            "enrichment_yield": self.compute_enrichment_yield(window_hours),
            "per_district_coverage": self.compute_per_district_coverage(self.city),
            "computed_at": datetime.utcnow()
        }
