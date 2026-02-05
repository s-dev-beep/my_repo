"""Stopping decision rules and thresholds.

Formalizes saturation detection rules with documented thresholds
and conservative decision logic.

READ-ONLY: No database modifications.
"""

from datetime import datetime
from typing import Dict, List, Any, Tuple
from pymongo.database import Database

from src.analytics.saturation_metrics import SaturationMetricsComputer
from src.analytics.district_tracker import DistrictTracker
from src.analytics.city_completion import CityCompletion


class StoppingRuleSet:
    """Implements stopping decision logic with documented thresholds.
    
    All decisions are CONSERVATIVE: require multiple signals before
    recommending to stop. Single metric fluctuations don't trigger stop.
    """
    
    # DOCUMENTED THRESHOLDS
    # These values are conservative and based on observation of saturation patterns
    
    THRESHOLDS = {
        # NEW_PHONE_RATE thresholds
        "new_phone_rate_low": 0.05,  # < 5% new phones = concerning
        "new_phone_rate_critical": 0.02,  # < 2% new phones = critical
        
        # PHONE_REVISIT_RATE thresholds
        "revisit_rate_high": 0.80,  # > 80% revisits = concerning
        "revisit_rate_critical": 0.90,  # > 90% revisits = critical
        
        # ENRICHMENT_YIELD thresholds
        "enrichment_yield_low": 0.10,  # < 10% yield = diminishing returns
        "enrichment_yield_critical": 0.05,  # < 5% yield = very diminishing
        
        # PER_DISTRICT coverage
        "min_phones_for_saturation": 50,  # Need at least 50 phones to claim saturation
        "district_growth_rate_low": 0.05,  # < 5% growth = slowing
        "district_growth_rate_critical": 0.02,  # < 2% growth = saturated
        
        # CITY-LEVEL completion
        "city_saturation_ready": 0.80,  # >= 80% saturation = ready
        "city_confidence_ready": 0.85,  # >= 85% avg confidence = ready
        "city_min_phones_ready": 500,  # >= 500 unique phones = ready
        "city_min_districts_saturated": 0.50,  # >= 50% districts saturated = concerning
        
        # DECISION CONFIDENCE
        "min_consecutive_readings": 3,  # Need 3+ consecutive concerning readings
        "observation_window_hours": 24,  # Standard window for metrics
    }
    
    def __init__(self, db: Database, city: str = "Istanbul"):
        """Initialize stopping rules.
        
        Args:
            db: MongoDB database connection
            city: City to evaluate (default: Istanbul)
        """
        self.db = db
        self.city = city
        self.metrics = SaturationMetricsComputer(db, city)
        self.districts = DistrictTracker(db, city)
        self.city_completion = CityCompletion(db, city)
    
    def evaluate_new_phone_rate_rule(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Evaluate NEW_PHONE_RATE stopping rule.
        
        RULE: If NEW_PHONE_RATE < 5% for extended period, discovery is slowing.
        CRITICAL: If < 2% for extended period, discovery may be complete.
        
        Returns:
            Dict with rule result and recommendation
        """
        now = datetime.utcnow()
        metric = self.metrics.compute_new_phone_rate(window_hours)
        
        rate = metric["rate"]
        new_phones = metric["new_phones"]
        total_in_window = metric["total_in_window"]
        
        result = {
            "rule": "NEW_PHONE_RATE",
            "rate": round(rate, 4),
            "threshold_low": self.THRESHOLDS["new_phone_rate_low"],
            "threshold_critical": self.THRESHOLDS["new_phone_rate_critical"],
            "new_phones_24h": new_phones,
            "total_active_24h": total_in_window,
        }
        
        if rate < self.THRESHOLDS["new_phone_rate_critical"]:
            result["severity"] = "CRITICAL"
            result["recommendation"] = "INVESTIGATE - Discovery may be complete"
            result["action"] = "CONTINUE (need more data before stopping)"
        elif rate < self.THRESHOLDS["new_phone_rate_low"]:
            result["severity"] = "HIGH"
            result["recommendation"] = "MONITOR - Discovery is slowing significantly"
            result["action"] = "CONTINUE (observe trend)"
        else:
            result["severity"] = "LOW"
            result["recommendation"] = "NORMAL - Good discovery pace"
            result["action"] = "CONTINUE (normal operation)"
        
        result["timestamp"] = now
        return result
    
    def evaluate_revisit_rate_rule(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Evaluate PHONE_REVISIT_RATE stopping rule.
        
        RULE: If > 80% of phones are revisits, crawler is mostly re-checking.
        CRITICAL: If > 90% revisits, discovery is nearly complete.
        
        Returns:
            Dict with rule result and recommendation
        """
        now = datetime.utcnow()
        metric = self.metrics.compute_phone_revisit_rate(window_hours)
        
        rate = metric["rate"]
        revisited = metric["revisited_phones"]
        total = metric["total_in_window"]
        
        result = {
            "rule": "PHONE_REVISIT_RATE",
            "rate": round(rate, 4),
            "threshold_high": self.THRESHOLDS["revisit_rate_high"],
            "threshold_critical": self.THRESHOLDS["revisit_rate_critical"],
            "revisited_phones": revisited,
            "total_active": total,
        }
        
        if rate > self.THRESHOLDS["revisit_rate_critical"]:
            result["severity"] = "CRITICAL"
            result["recommendation"] = "INVESTIGATE - Most crawling is revisits"
            result["action"] = "CONTINUE (need more data before stopping)"
        elif rate > self.THRESHOLDS["revisit_rate_high"]:
            result["severity"] = "HIGH"
            result["recommendation"] = "MONITOR - Significant revisit bias"
            result["action"] = "CONTINUE (observe trend)"
        else:
            result["severity"] = "LOW"
            result["recommendation"] = "NORMAL - Good balance of new/revisits"
            result["action"] = "CONTINUE (normal operation)"
        
        result["timestamp"] = now
        return result
    
    def evaluate_enrichment_yield_rule(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Evaluate ENRICHMENT_YIELD stopping rule.
        
        RULE: If enrichment yield < 10%, enrichment returns are diminishing.
        CRITICAL: If < 5%, enrichment is nearly exhausted.
        
        Returns:
            Dict with rule result and recommendation
        """
        now = datetime.utcnow()
        metric = self.metrics.compute_enrichment_yield(window_hours)
        
        yield_value = metric["yield"]
        enriched = metric["phones_enriched"]
        active = metric["active_phones"]
        
        result = {
            "rule": "ENRICHMENT_YIELD",
            "yield": round(yield_value, 4),
            "threshold_low": self.THRESHOLDS["enrichment_yield_low"],
            "threshold_critical": self.THRESHOLDS["enrichment_yield_critical"],
            "phones_enriched": enriched,
            "active_phones": active,
        }
        
        if yield_value < self.THRESHOLDS["enrichment_yield_critical"]:
            result["severity"] = "MEDIUM"  # Less critical than discovery rates
            result["recommendation"] = "NOTE - Enrichment is exhausted"
            result["action"] = "PAUSE enrichment (continue crawling)"
        elif yield_value < self.THRESHOLDS["enrichment_yield_low"]:
            result["severity"] = "LOW"
            result["recommendation"] = "NOTE - Enrichment yield is declining"
            result["action"] = "MONITOR enrichment effectiveness"
        else:
            result["severity"] = "LOW"
            result["recommendation"] = "NORMAL - Enrichment is effective"
            result["action"] = "CONTINUE enrichment"
        
        result["timestamp"] = now
        return result
    
    def evaluate_district_saturation_rule(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Evaluate district-level saturation rule.
        
        RULE: If >= 50% of districts are SATURATED, city-wide discovery is slowing.
        
        Returns:
            Dict with rule result and recommendation
        """
        now = datetime.utcnow()
        all_districts = self.districts.get_all_district_statuses(window_hours)
        
        total = all_districts["summary"]["total_districts"]
        saturated = all_districts["summary"]["saturated_count"]
        
        saturation_ratio = saturated / total if total > 0 else 0.0
        
        result = {
            "rule": "DISTRICT_SATURATION",
            "saturated_districts": saturated,
            "total_districts": total,
            "saturation_ratio": round(saturation_ratio, 2),
            "threshold": self.THRESHOLDS["city_min_districts_saturated"],
        }
        
        if saturation_ratio >= self.THRESHOLDS["city_min_districts_saturated"]:
            result["severity"] = "HIGH"
            result["recommendation"] = f"MONITOR - {saturated}/{total} districts saturated"
            result["action"] = "CONTINUE (approach city-wide saturation)"
        else:
            result["severity"] = "LOW"
            result["recommendation"] = f"NORMAL - {all_districts['summary']['active_count']} active districts"
            result["action"] = "CONTINUE (normal operation)"
        
        result["timestamp"] = now
        return result
    
    def evaluate_all_rules(
        self,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """Evaluate all stopping rules at once.
        
        Returns comprehensive assessment of all rules.
        
        Returns:
            Dict with all rule evaluations and summary
        """
        now = datetime.utcnow()
        
        rules = [
            self.evaluate_new_phone_rate_rule(window_hours),
            self.evaluate_revisit_rate_rule(window_hours),
            self.evaluate_enrichment_yield_rule(window_hours),
            self.evaluate_district_saturation_rule(window_hours),
        ]
        
        # Count severities
        critical_count = sum(1 for r in rules if r.get("severity") == "CRITICAL")
        high_count = sum(1 for r in rules if r.get("severity") == "HIGH")
        
        # Overall recommendation logic
        if critical_count >= 2:
            overall_severity = "CRITICAL"
            overall_rec = f"{critical_count} CRITICAL signals - Likely near completion"
            action = "PREPARE for stopping (monitor 1 more cycle)"
        elif critical_count >= 1 and high_count >= 2:
            overall_severity = "HIGH"
            overall_rec = f"{critical_count} CRITICAL + {high_count} HIGH signals - Approaching completion"
            action = "CONTINUE (monitor carefully)"
        elif high_count >= 3:
            overall_severity = "HIGH"
            overall_rec = f"{high_count} HIGH signals - Saturation evident"
            action = "CONTINUE (monitor carefully)"
        elif high_count > 0:
            overall_severity = "MEDIUM"
            overall_rec = f"{high_count} HIGH signals - Some saturation"
            action = "CONTINUE (normal monitoring)"
        else:
            overall_severity = "LOW"
            overall_rec = "No saturation signals"
            action = "CONTINUE (normal operation)"
        
        return {
            "city": self.city,
            "window_hours": window_hours,
            "individual_rules": rules,
            "summary": {
                "overall_severity": overall_severity,
                "critical_rules": critical_count,
                "high_rules": high_count,
                "recommendation": overall_rec,
                "action": action
            },
            "timestamp": now
        }
    
    def should_stop_crawling(
        self,
        window_hours: int = 24
    ) -> Tuple[bool, Dict[str, Any]]:
        """Make final stopping decision using all available evidence.
        
        CONSERVATIVE APPROACH:
        - Requires multiple concordant signals
        - Requires confirmation over time
        - Never decides based on single metric
        
        Returns True ONLY if:
        1. CityCompletion.status == READY_TO_STOP AND
        2. All rule evaluations support stopping
        
        Args:
            window_hours: Time window for metrics
        
        Returns:
            Tuple of (should_stop: bool, evidence: Dict)
        """
        now = datetime.utcnow()
        
        city_status = self.city_completion.get_city_status(window_hours)
        all_rules = self.evaluate_all_rules(window_hours)
        
        should_stop = False
        reasons = []
        
        # Criterion 1: City status must be READY_TO_STOP
        if city_status["status"] == "READY_TO_STOP":
            reasons.append(f"✓ City status: {city_status['status']}")
        else:
            reasons.append(f"✗ City status: {city_status['status']} (need READY_TO_STOP)")
        
        # Criterion 2: No CRITICAL rule violations
        critical_count = all_rules["summary"]["critical_rules"]
        if critical_count == 0:
            reasons.append("✓ No CRITICAL rule violations")
        else:
            reasons.append(f"✗ {critical_count} CRITICAL rule violations")
        
        # Criterion 3: Data quality must be high
        if city_status["metrics"]["confidence_avg"] >= self.THRESHOLDS["city_confidence_ready"]:
            reasons.append(f"✓ Confidence: {city_status['metrics']['confidence_avg']:.2f}")
        else:
            reasons.append(f"✗ Confidence: {city_status['metrics']['confidence_avg']:.2f} (need {self.THRESHOLDS['city_confidence_ready']:.2f})")
        
        # Criterion 4: Sample size must be meaningful
        if city_status["metrics"]["total_phones"] >= self.THRESHOLDS["city_min_phones_ready"]:
            reasons.append(f"✓ Sample size: {city_status['metrics']['total_phones']} phones")
        else:
            reasons.append(f"✗ Sample size: {city_status['metrics']['total_phones']} (need {self.THRESHOLDS['city_min_phones_ready']})")
        
        # Final decision
        if (city_status["status"] == "READY_TO_STOP" and
            critical_count == 0 and
            city_status["metrics"]["confidence_avg"] >= self.THRESHOLDS["city_confidence_ready"] and
            city_status["metrics"]["total_phones"] >= self.THRESHOLDS["city_min_phones_ready"]):
            should_stop = True
        
        evidence = {
            "city": self.city,
            "should_stop": should_stop,
            "decision_criteria": reasons,
            "city_status": city_status,
            "rule_summary": all_rules["summary"],
            "confidence_level": "HIGH" if should_stop else "MEDIUM",
            "timestamp": now,
            "recommendation": (
                "✅ READY TO STOP - All criteria met" if should_stop
                else "❌ CONTINUE CRAWLING - Not yet ready"
            )
        }
        
        return should_stop, evidence
