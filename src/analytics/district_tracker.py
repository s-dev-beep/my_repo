"""District-level saturation tracking.

Tracks individual district status and saturation indicators.

READ-ONLY: No database modifications.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Literal
from pymongo.database import Database


DistrictStatus = Literal["ACTIVE", "SLOWING", "SATURATED"]


class DistrictTracker:
    """Tracks discovery status per district.
    
    READ-ONLY: Reads only from identity graph.
    """
    
    def __init__(self, db: Database, city: str = "Istanbul"):
        """Initialize district tracker.
        
        Args:
            db: MongoDB database connection
            city: City to track (default: Istanbul)
        """
        self.db = db
        self.city = city
        self.phone_identities = db.phone_identities
        self.agent_location_history = db.agent_location_history
    
    def get_district_phones(self, district: str) -> List[str]:
        """Get all phone numbers active in district.
        
        Args:
            district: District name
        
        Returns:
            List of phone_e164 values
        """
        locations = self.agent_location_history.find(
            {
                "city": self.city,
                "district": district,
                "end_date": None  # Currently active
            },
            {"phone_e164": 1}
        )
        return list(set(loc["phone_e164"] for loc in locations))
    
    def get_district_status(
        self,
        district: str,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Compute comprehensive status for a district.
        
        Returns:
        - status: ACTIVE | SLOWING | SATURATED
        - new_phones_24h: count of new discoveries today
        - total_phones: cumulative phone count
        - growth_rate: new_phones / total_phones
        - confidence_avg: average confidence score
        - last_activity: most recent observation timestamp
        
        SATURATION RULES:
        1. SATURATED if:
           - growth_rate < 0.02 (< 2% new phones in 24h) AND
           - total_phones > 50 (meaningful sample size)
        
        2. SLOWING if:
           - growth_rate < 0.05 (< 5% new phones in 24h) OR
           - confidence_avg > 0.90 (data is very complete)
        
        3. ACTIVE otherwise (growth_rate >= 0.05)
        
        Args:
            district: District name
            window_hours: Time window for growth calculation
        
        Returns:
            Dict with status and metrics
        """
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)
        
        # Get all phones in district
        all_phones = self.get_district_phones(district)
        total_phones = len(all_phones)
        
        if total_phones == 0:
            return {
                "district": district,
                "city": self.city,
                "status": "ACTIVE",
                "reason": "no_phones_yet",
                "new_phones_24h": 0,
                "total_phones": 0,
                "growth_rate": 1.0,  # Start as active
                "confidence_avg": 0.0,
                "last_activity": None,
                "timestamp": now
            }
        
        # Count new phones discovered in window
        new_phones_24h = self.phone_identities.count_documents({
            "phone_e164": {"$in": all_phones},
            "first_seen_at": {"$gte": window_start, "$lte": now}
        })
        
        # Compute growth rate
        growth_rate = new_phones_24h / total_phones if total_phones > 0 else 1.0
        
        # Get average confidence
        confidences = list(
            self.phone_identities.find(
                {"phone_e164": {"$in": all_phones}},
                {"confidence_score": 1}
            )
        )
        confidence_avg = (
            sum(c.get("confidence_score", 0.0) for c in confidences) / len(confidences)
            if confidences else 0.0
        )
        
        # Get most recent activity
        most_recent = self.phone_identities.find_one(
            {"phone_e164": {"$in": all_phones}},
            {"last_seen_at": 1},
            sort=[("last_seen_at", -1)]
        )
        last_activity = most_recent.get("last_seen_at") if most_recent else None
        
        # Determine status based on rules
        reason = ""
        if total_phones >= 50 and growth_rate < 0.02:
            status = "SATURATED"
            reason = f"low_growth ({growth_rate:.1%}), large_sample ({total_phones})"
        elif growth_rate < 0.05 or confidence_avg > 0.90:
            status = "SLOWING"
            reason = f"growth_rate={growth_rate:.1%} or confidence={confidence_avg:.2f}"
        else:
            status = "ACTIVE"
            reason = f"growth_rate={growth_rate:.1%}, confidence={confidence_avg:.2f}"
        
        return {
            "district": district,
            "city": self.city,
            "status": status,
            "reason": reason,
            "new_phones_24h": new_phones_24h,
            "total_phones": total_phones,
            "growth_rate": round(growth_rate, 4),
            "confidence_avg": round(confidence_avg, 3),
            "last_activity": last_activity,
            "timestamp": now
        }
    
    def get_all_district_statuses(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get status for all districts in city.
        
        Returns:
            Dict with:
            - districts: List[Dict] with per-district status
            - summary: aggregate statistics
            - saturated_count: number of saturated districts
            - slowing_count: number of slowing districts
            - active_count: number of active districts
        """
        now = datetime.utcnow()
        
        # Get unique districts from location history
        district_docs = self.agent_location_history.find(
            {"city": self.city},
            {"district": 1}
        ).distinct("district")
        
        districts = []
        for district in sorted(district_docs):
            status_info = self.get_district_status(district, window_hours)
            districts.append(status_info)
        
        # Count statuses
        saturated_count = sum(1 for d in districts if d["status"] == "SATURATED")
        slowing_count = sum(1 for d in districts if d["status"] == "SLOWING")
        active_count = sum(1 for d in districts if d["status"] == "ACTIVE")
        
        # Compute overall growth rate
        total_phones = sum(d["total_phones"] for d in districts)
        total_new_24h = sum(d["new_phones_24h"] for d in districts)
        overall_growth = (total_new_24h / total_phones) if total_phones > 0 else 0.0
        
        return {
            "city": self.city,
            "window_hours": window_hours,
            "districts": districts,
            "summary": {
                "total_districts": len(districts),
                "saturated_count": saturated_count,
                "slowing_count": slowing_count,
                "active_count": active_count,
                "total_phones": total_phones,
                "new_phones_24h": total_new_24h,
                "overall_growth_rate": round(overall_growth, 4)
            },
            "timestamp": now
        }
    
    def get_saturation_score(
        self,
        district: str,
        window_hours: int = 24
    ) -> float:
        """Compute a scalar saturation score for district (0-1).
        
        Score interpretation:
        - 0.0 = completely unsaturated (very high growth)
        - 0.33 = moderately saturated (SLOWING status)
        - 0.67 = highly saturated (SATURATED status, low growth)
        - 1.0 = maximally saturated (zero growth for long time)
        
        Computation:
        1. Start with growth_rate-based score
        2. Adjust for sample size (need at least 50 phones to be confident)
        3. Adjust for confidence levels (high confidence = more saturated)
        
        Args:
            district: District name
            window_hours: Time window for growth calculation
        
        Returns:
            Saturation score 0-1
        """
        status = self.get_district_status(district, window_hours)
        
        growth_rate = status["growth_rate"]
        total_phones = status["total_phones"]
        confidence_avg = status["confidence_avg"]
        
        # Base score from growth rate (inverted: low growth = high saturation)
        # At 10% growth: score = 0.1
        # At 1% growth: score = 0.4
        # At 0% growth: score = 1.0
        if growth_rate >= 0.1:
            growth_score = 0.0
        elif growth_rate >= 0.05:
            growth_score = (0.1 - growth_rate) * 2  # Linear 0-0.1
        elif growth_rate >= 0.02:
            growth_score = (0.05 - growth_rate) * 10  # Linear 0-0.3
        else:
            growth_score = 1.0 - growth_rate  # Linear 0.98-1.0, clamped to 1.0
        
        # Confidence adjustment
        # High confidence (0.9+) indicates data is complete
        confidence_factor = min(confidence_avg / 0.9, 1.0)
        
        # Sample size adjustment
        # Need at least 50 phones to be confident in saturation claim
        if total_phones < 50:
            sample_factor = total_phones / 50.0
        else:
            sample_factor = 1.0
        
        # Combine factors
        saturation_score = growth_score * confidence_factor * sample_factor
        
        return round(min(saturation_score, 1.0), 3)
    
    def identify_at_risk_districts(
        self,
        window_hours: int = 24,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Identify districts approaching saturation.
        
        Returns districts with saturation_score >= threshold,
        ordered from most to least saturated.
        
        Args:
            window_hours: Time window for metrics
            threshold: Saturation score threshold (0-1)
        
        Returns:
            List of districts sorted by saturation score (descending)
        """
        all_districts = self.get_all_district_statuses(window_hours)
        
        at_risk = []
        for district_info in all_districts["districts"]:
            district_name = district_info["district"]
            saturation_score = self.get_saturation_score(district_name, window_hours)
            
            if saturation_score >= threshold:
                at_risk.append({
                    "district": district_name,
                    "saturation_score": saturation_score,
                    "status": district_info["status"],
                    "growth_rate": district_info["growth_rate"],
                    "total_phones": district_info["total_phones"],
                    "confidence_avg": district_info["confidence_avg"]
                })
        
        # Sort by saturation score (descending)
        at_risk.sort(key=lambda x: x["saturation_score"], reverse=True)
        
        return at_risk
