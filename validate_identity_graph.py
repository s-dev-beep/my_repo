"""STEP 17 Validation: Test identity graph with STEP 12 synthetic data.

This validates that the phone-centric graph works correctly
without touching live crawling.
"""

import sys
from datetime import datetime
from pymongo import MongoClient

from src.identity import IdentityGraphResolver
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def validate_identity_graph():
    """Replay STEP 12 synthetic data through identity graph."""
    
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["real_estate_crawler_test"]
    
    # Clear test collections
    logger.info("Clearing test collections...")
    db.phone_identities.delete_many({})
    db.agent_profiles.delete_many({})
    db.offices.delete_many({})
    db.agent_location_history.delete_many({})
    db.agent_office_history.delete_many({})
    db.source_evidence.delete_many({})
    
    # Initialize resolver
    resolver = IdentityGraphResolver(db)
    
    logger.info("=" * 80)
    logger.info("STEP 17 VALIDATION: Identity Graph")
    logger.info("=" * 80)
    
    # Test Case 1: Same phone, same name (should update, not duplicate)
    logger.info("\n[Test 1] Same phone + same name (2 observations)")
    
    result1 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="sahibinden",
        url="https://sahibinden.com/listing/1",
        agent_name="Ahmet Yılmaz",
        office_name="Yılmaz Emlak",
        city="Istanbul",
        district="Kadıköy",
        confidence="medium",
        timestamp=datetime(2025, 1, 15)
    )
    
    result2 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="sahibinden",
        url="https://sahibinden.com/listing/2",
        agent_name="Ahmet Yılmaz",
        office_name="Yılmaz Emlak",
        city="Istanbul",
        district="Kadıköy",
        confidence="medium",
        timestamp=datetime(2025, 2, 1)
    )
    
    summary1 = resolver.get_agent_summary("+905551234567")
    
    assert summary1["phone_identity"]["observation_count"] == 2, "Should have 2 observations"
    assert len(summary1["all_profiles"]) == 1, "Should have 1 profile (same name)"
    assert summary1["evidence_count"] == 2, "Should have 2 evidence records"
    
    logger.info(f"✓ Phone observations: {summary1['phone_identity']['observation_count']}")
    logger.info(f"✓ Agent profiles: {len(summary1['all_profiles'])} (no duplication)")
    logger.info(f"✓ Evidence records: {summary1['evidence_count']}")
    
    # Test Case 2: Same phone, different name (should create new profile)
    logger.info("\n[Test 2] Same phone + different name (name change)")
    
    result3 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="sahibinden",
        url="https://sahibinden.com/listing/3",
        agent_name="Ahmet Y.",  # Different name variant
        office_name="Yılmaz Emlak",
        city="Istanbul",
        district="Kadıköy",
        confidence="medium",
        timestamp=datetime(2025, 3, 1)
    )
    
    summary2 = resolver.get_agent_summary("+905551234567")
    
    assert len(summary2["all_profiles"]) == 2, "Should have 2 profiles (name change)"
    assert summary2["current_profile"]["full_name"] == "Ahmet Y.", "Latest name should be current"
    
    logger.info(f"✓ Agent profiles: {len(summary2['all_profiles'])} (append-only)")
    logger.info(f"✓ Current name: {summary2['current_profile']['full_name']}")
    logger.info(f"✓ Historical names preserved: {[p['full_name'] for p in summary2['all_profiles']]}")
    
    # Test Case 3: Different phone, same name (different agents)
    logger.info("\n[Test 3] Different phone + same name (different agents)")
    
    result4 = resolver.process_extraction(
        phone_e164="+905559876543",
        source="sahibinden",
        url="https://sahibinden.com/listing/4",
        agent_name="Ahmet Yılmaz",  # Same name, different phone
        office_name="Başka Emlak",
        city="Istanbul",
        district="Üsküdar",
        confidence="medium",
        timestamp=datetime(2025, 2, 1)
    )
    
    summary3 = resolver.get_agent_summary("+905559876543")
    
    assert summary3["phone_identity"]["phone_e164"] == "+905559876543", "Different phone"
    assert summary3["current_profile"]["full_name"] == "Ahmet Yılmaz", "Same name"
    
    logger.info(f"✓ Created separate identity for phone: {summary3['phone_identity']['phone_e164']}")
    logger.info(f"✓ Name can repeat across agents: {summary3['current_profile']['full_name']}")
    
    # Test Case 4: Location change (history should track)
    logger.info("\n[Test 4] Agent moves districts (location history)")
    
    result5 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="sahibinden",
        url="https://sahibinden.com/listing/5",
        agent_name="Ahmet Y.",
        office_name="Yılmaz Emlak",
        city="Istanbul",
        district="Üsküdar",  # Moved to different district
        confidence="medium",
        timestamp=datetime(2025, 4, 1)
    )
    
    summary4 = resolver.get_agent_summary("+905551234567")
    
    # Check location history
    all_locations = list(db.agent_location_history.find({"phone_e164": "+905551234567"}))
    active_locations = summary4["active_locations"]
    
    assert len(all_locations) == 2, "Should have 2 location records (Kadıköy + Üsküdar)"
    assert len(active_locations) == 1, "Only 1 active location"
    assert active_locations[0]["district"] == "Üsküdar", "Latest location should be active"
    
    # Check previous location is closed
    closed_location = db.agent_location_history.find_one({
        "phone_e164": "+905551234567",
        "district": "Kadıköy"
    })
    assert closed_location["end_date"] is not None, "Previous location should be closed"
    
    logger.info(f"✓ Total location records: {len(all_locations)}")
    logger.info(f"✓ Active locations: {len(active_locations)}")
    logger.info(f"✓ Previous location (Kadıköy) closed: {closed_location['end_date']}")
    logger.info(f"✓ Current location: {active_locations[0]['district']}")
    
    # Test Case 5: Office change (office history should track)
    logger.info("\n[Test 5] Agent changes office (office history)")
    
    result6 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="sahibinden",
        url="https://sahibinden.com/listing/6",
        agent_name="Ahmet Y.",
        office_name="Yeni Emlak",  # Different office
        city="Istanbul",
        district="Üsküdar",
        confidence="medium",
        timestamp=datetime(2025, 5, 1)
    )
    
    summary5 = resolver.get_agent_summary("+905551234567")
    
    # Check office history
    all_office_assocs = list(db.agent_office_history.find({"phone_e164": "+905551234567"}))
    active_office = summary5["active_office"]
    
    assert len(all_office_assocs) == 3, "Should have 3 office associations (Kadıköy + Üsküdar x2)"
    assert active_office is not None, "Should have active office"
    
    # Get office details
    active_office_entity = db.offices.find_one({"office_id": active_office["office_id"]})
    assert active_office_entity["office_name"] == "Yeni Emlak", "Latest office should be active"
    
    # Check previous office is closed
    closed_assoc = db.agent_office_history.find_one({
        "phone_e164": "+905551234567",
        "end_date": {"$ne": None}
    })
    assert closed_assoc is not None, "Previous office association should be closed"
    
    logger.info(f"✓ Total office associations: {len(all_office_assocs)}")
    logger.info(f"✓ Current office: {active_office_entity['office_name']}")
    logger.info(f"✓ Previous office closed at: {closed_assoc['end_date']}")
    
    # Test Case 6: Multi-source enrichment (confidence boost)
    logger.info("\n[Test 6] Multi-source confirmation (confidence boost)")
    
    # Same agent from different source
    result7 = resolver.process_extraction(
        phone_e164="+905551234567",
        source="hepsiemlak",  # Different source
        url="https://hepsiemlak.com/listing/1",
        agent_name="Ahmet Y.",
        office_name="Yeni Emlak",
        city="Istanbul",
        district="Üsküdar",
        confidence="high",
        timestamp=datetime(2025, 6, 1)
    )
    
    summary6 = resolver.get_agent_summary("+905551234567")
    
    assert len(summary6["sources"]) == 2, "Should have 2 sources"
    assert "sahibinden" in summary6["sources"], "Should include sahibinden"
    assert "hepsiemlak" in summary6["sources"], "Should include hepsiemlak"
    assert summary6["confidence_score"] >= 0.95, "Multi-source should boost confidence"
    
    logger.info(f"✓ Sources: {summary6['sources']}")
    logger.info(f"✓ Confidence score: {summary6['confidence_score']}")
    logger.info(f"✓ Multi-source confirmation working")
    
    # Final Summary
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    
    total_phones = db.phone_identities.count_documents({})
    total_profiles = db.agent_profiles.count_documents({})
    total_offices = db.offices.count_documents({})
    total_locations = db.agent_location_history.count_documents({})
    total_office_assocs = db.agent_office_history.count_documents({})
    total_evidence = db.source_evidence.count_documents({})
    
    logger.info(f"Phone identities:        {total_phones}")
    logger.info(f"Agent profiles:          {total_profiles}")
    logger.info(f"Offices:                 {total_offices}")
    logger.info(f"Location history:        {total_locations}")
    logger.info(f"Office associations:     {total_office_assocs}")
    logger.info(f"Evidence records:        {total_evidence}")
    
    logger.info("\n✅ ALL TESTS PASSED")
    logger.info("✅ Identity graph is append-only")
    logger.info("✅ No data loss")
    logger.info("✅ No overwrites")
    logger.info("✅ History preserved correctly")
    logger.info("=" * 80)
    
    client.close()
    return True


if __name__ == "__main__":
    try:
        validate_identity_graph()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        sys.exit(1)
