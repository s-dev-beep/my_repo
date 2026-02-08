"""STEP 20: Integration demo with real MongoDB.

This script demonstrates the saturation measurement layer working with real data.

Usage:
    python examples/saturation_demo.py

This will:
1. Connect to MongoDB
2. Compute all saturation metrics
3. Generate a snapshot
4. Display status and recommendations
5. Check stopping readiness
"""

from datetime import datetime
from pymongo import MongoClient

from src.analytics import SaturationSnapshot


def main():
    """Run saturation analysis demo."""
    
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client.real_estate
    
    print("\n" + "=" * 80)
    print("STEP 20: SATURATION MEASUREMENT - LIVE ANALYSIS")
    print("=" * 80)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Database: {db.name}")
    print()
    
    # Initialize snapshot generator
    snapshot_gen = SaturationSnapshot(db, city="Istanbul", snapshot_dir="reports")
    
    # Create full snapshot
    print("Computing saturation metrics...")
    snapshot = snapshot_gen.create_full_snapshot(
        window_hours=24,
        include_districts=True,
        include_rules=True
    )
    
    # Display summary
    print("\n" + snapshot_gen.generate_summary_report(snapshot))
    
    # Save snapshot
    print("\nSaving snapshot...")
    filepath = snapshot_gen.save_snapshot(snapshot)
    print(f"✓ Snapshot saved: {filepath}")
    
    # Check stopping decision
    print("\n" + "=" * 80)
    print("STOPPING DECISION")
    print("=" * 80)
    
    if snapshot.get("stopping_decision"):
        decision = snapshot["stopping_decision"]["evidence"]
        print(f"\nShould Stop: {decision['should_stop']}")
        print(f"Confidence: {decision['confidence_level']}")
        print(f"\nDecision Criteria:")
        for criterion in decision["decision_criteria"]:
            print(f"  {criterion}")
        
        if decision["should_stop"]:
            print(f"\n🎉 {decision['recommendation']}")
        else:
            print(f"\n📊 {decision['recommendation']}")
    
    # Load and verify snapshot
    print("\n" + "=" * 80)
    print("SNAPSHOT VERIFICATION")
    print("=" * 80)
    
    loaded = snapshot_gen.load_snapshot(str(filepath))
    print(f"✓ Snapshot loaded successfully")
    print(f"  City: {loaded['city']}")
    print(f"  Timestamp: {loaded['timestamp']}")
    print(f"  Metrics computed: {list(loaded['metrics'].keys())}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
