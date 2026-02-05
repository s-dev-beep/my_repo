"""Saturation snapshot export and reporting.

Creates JSON snapshots of saturation state for each run,
enabling historical analysis and trend tracking.

READ-ONLY: No database modifications.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from pymongo.database import Database

from src.analytics.saturation_metrics import SaturationMetricsComputer
from src.analytics.district_tracker import DistrictTracker
from src.analytics.city_completion import CityCompletion
from src.analytics.stopping_rules import StoppingRuleSet


class SaturationSnapshot:
    """Creates and manages saturation state snapshots.
    
    READ-ONLY: Reads only from identity graph.
    """
    
    def __init__(
        self,
        db: Database,
        city: str = "Istanbul",
        snapshot_dir: str = "reports"
    ):
        """Initialize snapshot generator.
        
        Args:
            db: MongoDB database connection
            city: City to snapshot (default: Istanbul)
            snapshot_dir: Directory for snapshot files
        """
        self.db = db
        self.city = city
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = SaturationMetricsComputer(db, city)
        self.districts = DistrictTracker(db, city)
        self.city_completion = CityCompletion(db, city)
        self.rules = StoppingRuleSet(db, city)
    
    def create_full_snapshot(
        self,
        window_hours: int = 24,
        include_districts: bool = True,
        include_rules: bool = True
    ) -> Dict[str, Any]:
        """Create complete saturation snapshot.
        
        Combines all metrics, status, and decision logic into
        a comprehensive JSON report.
        
        Args:
            window_hours: Time window for metrics
            include_districts: Include per-district details
            include_rules: Include stopping rule evaluations
        
        Returns:
            Dict with complete snapshot data
        """
        now = datetime.utcnow()
        
        snapshot = {
            "timestamp": now.isoformat(),
            "city": self.city,
            "window_hours": window_hours,
            
            # Core saturation metrics
            "metrics": self.metrics.compute_all_metrics(window_hours),
            
            # City-level completion assessment
            "city_completion": self.city_completion.get_city_status(window_hours),
            
            # Completion projection
            "completion_projection": self.city_completion.project_completion_date(window_hours),
            
            # Stopping decision
            "stopping_decision": None,  # Set below if include_rules
            
            # Next recommended actions
            "next_actions": self.city_completion.get_next_actions(window_hours),
        }
        
        # Add per-district details if requested
        if include_districts:
            district_stats = self.districts.get_all_district_statuses(window_hours)
            snapshot["district_details"] = district_stats
            
            # Identify at-risk districts
            at_risk = self.districts.identify_at_risk_districts(window_hours, threshold=0.5)
            snapshot["at_risk_districts"] = at_risk
        
        # Add stopping rule evaluations if requested
        if include_rules:
            should_stop, evidence = self.rules.should_stop_crawling(window_hours)
            snapshot["stopping_decision"] = {
                "should_stop": should_stop,
                "evidence": evidence
            }
        
        return snapshot
    
    def save_snapshot(
        self,
        snapshot: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> Path:
        """Save snapshot to JSON file.
        
        Filename format: saturation_snapshot_{run_id}_{timestamp}.json
        
        Args:
            snapshot: Snapshot data to save
            run_id: Optional run ID (defaults to timestamp)
        
        Returns:
            Path to saved file
        """
        if run_id is None:
            now = datetime.utcnow()
            run_id = now.strftime("%Y%m%d_%H%M%S")
        
        filename = f"saturation_snapshot_{run_id}.json"
        filepath = self.snapshot_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        return filepath
    
    def create_and_save_snapshot(
        self,
        window_hours: int = 24,
        run_id: Optional[str] = None,
        include_districts: bool = True,
        include_rules: bool = True
    ) -> Dict[str, Any]:
        """Create and immediately save snapshot.
        
        Convenience method that creates full snapshot and saves it in one call.
        
        Args:
            window_hours: Time window for metrics
            run_id: Optional run ID for filename
            include_districts: Include per-district details
            include_rules: Include stopping rule evaluations
        
        Returns:
            Snapshot data
        """
        snapshot = self.create_full_snapshot(
            window_hours=window_hours,
            include_districts=include_districts,
            include_rules=include_rules
        )
        
        filepath = self.save_snapshot(snapshot, run_id)
        
        print(f"✓ Saturation snapshot saved: {filepath}")
        
        return snapshot
    
    def load_snapshot(self, filepath: str) -> Dict[str, Any]:
        """Load saved snapshot from JSON file.
        
        Args:
            filepath: Path to snapshot JSON file
        
        Returns:
            Snapshot data
        """
        with open(filepath, "r") as f:
            snapshot = json.load(f)
        
        return snapshot
    
    def compare_snapshots(
        self,
        snapshot1: Dict[str, Any],
        snapshot2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two snapshots to identify trends.
        
        Args:
            snapshot1: Earlier snapshot (baseline)
            snapshot2: Later snapshot (current)
        
        Returns:
            Dict with comparison results and trends
        """
        # Compare key metrics
        metrics1 = snapshot1["metrics"]
        metrics2 = snapshot2["metrics"]
        
        # NEW_PHONE_RATE trend
        rate1 = metrics1["new_phone_rate"]["rate"]
        rate2 = metrics2["new_phone_rate"]["rate"]
        rate_change = rate2 - rate1
        rate_trend = "↓ DECLINING" if rate_change < 0 else "↑ IMPROVING"
        
        # City saturation trend
        sat1 = snapshot1["city_completion"]["saturation_score"]
        sat2 = snapshot2["city_completion"]["saturation_score"]
        sat_change = sat2 - sat1
        sat_trend = "↑ INCREASING" if sat_change > 0 else "↓ DECREASING"
        
        # Total phones trend
        phones1 = snapshot1["city_completion"]["metrics"]["total_phones"]
        phones2 = snapshot2["city_completion"]["metrics"]["total_phones"]
        phones_added = phones2 - phones1
        
        # Confidence trend
        conf1 = snapshot1["city_completion"]["metrics"]["confidence_avg"]
        conf2 = snapshot2["city_completion"]["metrics"]["confidence_avg"]
        conf_change = conf2 - conf1
        
        # City status comparison
        status1 = snapshot1["city_completion"]["status"]
        status2 = snapshot2["city_completion"]["status"]
        
        comparison = {
            "baseline_timestamp": snapshot1["timestamp"],
            "current_timestamp": snapshot2["timestamp"],
            "city": snapshot1["city"],
            
            "metrics_comparison": {
                "new_phone_rate": {
                    "baseline": rate1,
                    "current": rate2,
                    "change": round(rate_change, 4),
                    "trend": rate_trend
                },
                "saturation_score": {
                    "baseline": sat1,
                    "current": sat2,
                    "change": round(sat_change, 3),
                    "trend": sat_trend
                },
                "total_phones": {
                    "baseline": phones1,
                    "current": phones2,
                    "added": phones_added
                },
                "confidence_avg": {
                    "baseline": conf1,
                    "current": conf2,
                    "change": round(conf_change, 3),
                    "improving": conf_change > 0
                }
            },
            
            "status_progression": {
                "baseline": status1,
                "current": status2,
                "progressed": status2 != status1
            },
            
            "analysis": self._analyze_trends(
                snapshot1, snapshot2, rate_change, sat_change
            ),
            
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return comparison
    
    def _analyze_trends(
        self,
        snap1: Dict[str, Any],
        snap2: Dict[str, Any],
        rate_change: float,
        sat_change: float
    ) -> str:
        """Analyze trends and provide interpretation.
        
        Args:
            snap1: First snapshot
            snap2: Second snapshot
            rate_change: Change in new phone rate
            sat_change: Change in saturation score
        
        Returns:
            String interpretation of trends
        """
        if rate_change < -0.02 and sat_change > 0.05:
            return "⚠️  SATURATION ACCELERATING - Discovery rate declining rapidly"
        elif rate_change < 0 and sat_change > 0:
            return "📊 NORMAL SATURATION - Discovery slowing, data maturing"
        elif rate_change >= 0 and sat_change > 0.1:
            return "🎯 COMPLETING - Saturation increasing with stable discovery"
        elif rate_change >= 0:
            return "✅ HEALTHY - Discovery pace stable"
        else:
            return "❓ MIXED SIGNALS - Observe trend continuation"
    
    def generate_summary_report(
        self,
        snapshot: Dict[str, Any]
    ) -> str:
        """Generate human-readable summary report from snapshot.
        
        Args:
            snapshot: Snapshot data
        
        Returns:
            Formatted text report
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"SATURATION ANALYSIS REPORT - {snapshot['city'].upper()}")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {snapshot['timestamp']}")
        lines.append("")
        
        # City Status
        city = snapshot["city_completion"]
        lines.append("CITY STATUS")
        lines.append("-" * 40)
        lines.append(f"  Status: {city['status']}")
        lines.append(f"  Saturation Score: {city['saturation_score']:.1%}")
        lines.append(f"  Total Phones: {city['metrics']['total_phones']}")
        lines.append(f"  Growth Rate (24h): {city['metrics']['overall_growth_rate']:.1%}")
        lines.append(f"  Avg Confidence: {city['metrics']['confidence_avg']:.2f}")
        lines.append("")
        
        # Key Metrics
        metrics = snapshot["metrics"]
        lines.append("KEY METRICS")
        lines.append("-" * 40)
        npr = metrics["new_phone_rate"]
        lines.append(f"  New Phone Rate: {npr['rate']:.1%} ({npr['new_phones']} in {npr['total_in_window']} active)")
        prr = metrics["phone_revisit_rate"]
        lines.append(f"  Revisit Rate: {prr['rate']:.1%} ({prr['revisited_phones']} revisited)")
        ey = metrics["enrichment_yield"]
        lines.append(f"  Enrichment Yield: {ey['yield']:.2f} ({ey['phones_enriched']} enriched)")
        lines.append("")
        
        # District Summary
        if "district_details" in snapshot:
            dist = snapshot["district_details"]["summary"]
            lines.append("DISTRICT SUMMARY")
            lines.append("-" * 40)
            lines.append(f"  Total Districts: {dist['total_districts']}")
            lines.append(f"  Active: {dist['active_count']} | Slowing: {dist['slowing_count']} | Saturated: {dist['saturated_count']}")
            lines.append("")
        
        # Stopping Decision
        if "stopping_decision" in snapshot and snapshot["stopping_decision"]:
            decision = snapshot["stopping_decision"]["evidence"]
            lines.append("STOPPING DECISION")
            lines.append("-" * 40)
            lines.append(f"  Should Stop: {decision.get('should_stop', False)}")
            lines.append(f"  Recommendation: {decision.get('recommendation', 'N/A')}")
            lines.append("")
        
        # Next Actions
        actions = snapshot["next_actions"]["recommendations"]
        lines.append("RECOMMENDED NEXT ACTIONS")
        lines.append("-" * 40)
        for action in actions:
            lines.append(f"  → {action}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
