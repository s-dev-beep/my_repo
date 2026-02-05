"""City-level completion assessment.

Determines when a city's discovery is complete based on:
- All districts at saturation OR
- Diminishing returns across city
- Confidence thresholds met

READ-ONLY: No database modifications.
"""

from datetime import datetime
from typing import Dict, List, Any, Literal
from pymongo.database import Database

from src.analytics.district_tracker import DistrictTracker


CityStatus = Literal["ACTIVE", "MATURING", "READY_TO_STOP"]


class CityCompletion:
    """Assesses city-level discovery completion.
    
    READ-ONLY: Reads only from identity graph.
    """
    
    def __init__(self, db: Database, city: str = "Istanbul"):
        """Initialize city completion tracker.
        
        Args:
            db: MongoDB database connection
            city: City to assess (default: Istanbul)
        """
        self.db = db
        self.city = city
        self.district_tracker = DistrictTracker(db, city)
        self.phone_identities = db.phone_identities
        self.agent_location_history = db.agent_location_history
    
    def compute_city_saturation_score(
        self,
        window_hours: int = 24
    ) -> float:
        """Compute scalar saturation score for entire city (0-1).
        
        Score interpretation:
        - 0.0 = actively discovering
        - 0.5 = maturing (slowing discovery)
        - 1.0 = saturated (minimal discovery)
        
        Computation:
        - Average saturation scores of all districts
        - Weighted by phone count in each district
        - Adjusts for number of saturated districts
        
        Args:
            window_hours: Time window for metrics
        
        Returns:
            Saturation score 0-1
        """
        all_districts = self.district_tracker.get_all_district_statuses(window_hours)
        
        if not all_districts["districts"]:
            return 0.0
        
        # Compute weighted average saturation score
        total_phones = 0
        weighted_saturation = 0.0
        
        for district_info in all_districts["districts"]:
            district_name = district_info["district"]
            phone_count = district_info["total_phones"]
            saturation_score = self.district_tracker.get_saturation_score(
                district_name, window_hours
            )
            
            total_phones += phone_count
            weighted_saturation += saturation_score * phone_count
        
        if total_phones == 0:
            return 0.0
        
        weighted_avg = weighted_saturation / total_phones
        
        # Bonus score if most districts are saturated
        saturated_count = all_districts["summary"]["saturated_count"]
        total_districts = all_districts["summary"]["total_districts"]
        
        if total_districts > 0:
            saturation_ratio = saturated_count / total_districts
            if saturation_ratio >= 0.8:
                # Most districts are saturated - boost confidence
                weighted_avg = min(weighted_avg * 1.2, 1.0)
        
        return round(min(weighted_avg, 1.0), 3)
    
    def get_city_status(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive city status.
        
        Returns:
        - status: ACTIVE | MATURING | READY_TO_STOP
        - saturation_score: 0-1
        - reason: explanation of status determination
        - district_summary: counts by status
        - metrics: key metrics supporting the assessment
        
        RULES:
        1. READY_TO_STOP if:
           - saturation_score >= 0.8 (80%+ saturated) AND
           - total_phones >= 500 (meaningful sample) AND
           - confidence_avg >= 0.85 (high data quality)
        
        2. MATURING if:
           - saturation_score >= 0.5 (50%+ saturated) OR
           - saturated_districts >= 50% of total
        
        3. ACTIVE otherwise
        
        Args:
            window_hours: Time window for metrics
        
        Returns:
            Dict with status and supporting metrics
        """
        now = datetime.utcnow()
        saturation_score = self.compute_city_saturation_score(window_hours)
        all_districts = self.district_tracker.get_all_district_statuses(window_hours)
        
        # Get overall metrics
        total_phones = all_districts["summary"]["total_phones"]
        total_districts = all_districts["summary"]["total_districts"]
        saturated_districts = all_districts["summary"]["saturated_count"]
        
        # Compute confidence average
        all_phones = self.phone_identities.find({}, {"confidence_score": 1})
        confidences = [p.get("confidence_score", 0.0) for p in all_phones]
        confidence_avg = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )
        
        # Determine status
        reasons = []
        
        if (saturation_score >= 0.8 and 
            total_phones >= 500 and 
            confidence_avg >= 0.85):
            status = "READY_TO_STOP"
            reasons = [
                f"saturation_score={saturation_score:.2%}",
                f"total_phones={total_phones}",
                f"confidence={confidence_avg:.2f}"
            ]
        elif saturation_score >= 0.5 or saturated_districts >= total_districts * 0.5:
            status = "MATURING"
            reasons = [
                f"saturation_score={saturation_score:.2%}",
                f"saturated_districts={saturated_districts}/{total_districts}"
            ]
        else:
            status = "ACTIVE"
            reasons = [
                f"saturation_score={saturation_score:.2%}",
                f"active_districts={all_districts['summary']['active_count']}/{total_districts}"
            ]
        
        return {
            "city": self.city,
            "status": status,
            "reason": " | ".join(reasons),
            "saturation_score": saturation_score,
            "district_summary": {
                "total": total_districts,
                "saturated": saturated_districts,
                "slowing": all_districts["summary"]["slowing_count"],
                "active": all_districts["summary"]["active_count"]
            },
            "metrics": {
                "total_phones": total_phones,
                "new_phones_24h": all_districts["summary"]["new_phones_24h"],
                "overall_growth_rate": all_districts["summary"]["overall_growth_rate"],
                "confidence_avg": round(confidence_avg, 3)
            },
            "timestamp": now,
            "window_hours": window_hours
        }
    
    def project_completion_date(
        self,
        window_hours: int = 24,
        target_saturation: float = 0.8
    ) -> Dict[str, Any]:
        """Project estimated date of reaching saturation target.
        
        Uses growth rate trends to estimate when saturation will be reached.
        
        CAVEAT: This is highly speculative and depends on:
        - Stable growth rates (may change with crawler improvements)
        - Unchanged crawler scope (no new sites/districts added)
        - Continued operation at current pace
        
        Args:
            window_hours: Time window for growth rate calculation
            target_saturation: Target saturation score (0-1)
        
        Returns:
            Dict with:
            - projected_date: estimated datetime
            - days_to_completion: estimated days
            - confidence: "low" | "medium" | "high"
            - assumptions: list of assumptions made
        """
        now = datetime.utcnow()
        current_saturation = self.compute_city_saturation_score(window_hours)
        all_districts = self.district_tracker.get_all_district_statuses(window_hours)
        
        # Remaining saturation needed
        remaining = target_saturation - current_saturation
        
        if remaining <= 0:
            return {
                "city": self.city,
                "status": "already_complete",
                "current_saturation": current_saturation,
                "target_saturation": target_saturation,
                "projected_date": now,
                "days_to_completion": 0,
                "confidence": "high",
                "timestamp": now
            }
        
        # Current growth rate (inverse of saturation growth)
        total_phones = all_districts["summary"]["total_phones"]
        new_phones_window = all_districts["summary"]["new_phones_24h"]
        
        if total_phones == 0 or new_phones_window == 0:
            return {
                "city": self.city,
                "status": "insufficient_data",
                "current_saturation": current_saturation,
                "target_saturation": target_saturation,
                "reason": "zero_phones_or_growth",
                "projected_date": None,
                "days_to_completion": None,
                "confidence": "low",
                "timestamp": now
            }
        
        # Daily new phones discovered
        daily_new_phones = new_phones_window * (24 / window_hours)
        
        # Estimate: saturation grows 1% for every 50 new phones
        # (assumes diminishing returns as we approach saturation)
        phones_per_saturation_point = 50 / 0.01  # 5000 phones per saturation point
        
        # Days needed to gain remaining saturation
        saturation_points_needed = remaining
        phones_needed = saturation_points_needed * phones_per_saturation_point
        days_needed = phones_needed / daily_new_phones if daily_new_phones > 0 else float('inf')
        
        # Clamp to reasonable estimate (0-365 days)
        days_needed = min(max(days_needed, 0), 365)
        
        # Confidence depends on:
        # - Stable growth rate (few variations)
        # - Large sample size (many districts)
        # - Consistent behavior (no outliers)
        if len(all_districts["districts"]) >= 10 and daily_new_phones >= 10:
            confidence = "medium"  # Never "high" for projections
        else:
            confidence = "low"
        
        from datetime import timedelta
        projected_date = now + timedelta(days=days_needed)
        
        return {
            "city": self.city,
            "status": "projecting",
            "current_saturation": round(current_saturation, 3),
            "target_saturation": target_saturation,
            "remaining_saturation": round(remaining, 3),
            "daily_new_phones": round(daily_new_phones, 1),
            "projected_date": projected_date,
            "days_to_completion": round(days_needed, 1),
            "confidence": confidence,
            "assumptions": [
                "Constant discovery rate (daily_new_phones)",
                "Linear saturation growth with discovery",
                "No crawler scope changes",
                "No major disruptions to data sources"
            ],
            "timestamp": now,
            "window_hours": window_hours
        }
    
    def is_ready_to_stop(self, window_hours: int = 24) -> bool:
        """Simple boolean check: should we stop crawling?
        
        Returns True if city status is READY_TO_STOP.
        
        Args:
            window_hours: Time window for metrics
        
        Returns:
            Boolean indicating readiness to stop
        """
        status = self.get_city_status(window_hours)
        return status["status"] == "READY_TO_STOP"
    
    def get_next_actions(self, window_hours: int = 24) -> Dict[str, Any]:
        """Get recommended actions based on city status.
        
        Suggests what to do next based on saturation assessment.
        
        Args:
            window_hours: Time window for metrics
        
        Returns:
            Dict with recommendations
        """
        city_status = self.get_city_status(window_hours)
        status = city_status["status"]
        
        if status == "READY_TO_STOP":
            recommendations = [
                "Stop live crawling for Istanbul",
                "Final data validation and cleanup",
                "Generate completion report",
                "Archive final dataset"
            ]
        elif status == "MATURING":
            recommendations = [
                "Continue crawling at current pace",
                "Focus enrichment on low-confidence phones",
                "Monitor district saturation progression",
                "Plan completion timeline"
            ]
        else:  # ACTIVE
            recommendations = [
                "Continue active crawling",
                "Prioritize high-growth districts",
                "Expand coverage where possible",
                "Regular monitoring of growth rates"
            ]
        
        return {
            "city": self.city,
            "current_status": status,
            "recommendations": recommendations,
            "next_review_in_hours": 24 if status == "READY_TO_STOP" else 12,
            "timestamp": datetime.utcnow()
        }
