"""STEP 18: Validate Crawler → Identity Graph Integration.

This script validates that the crawler now correctly routes all
persistence through the identity graph instead of writing directly
to MongoDB.

Test approach:
1. Use same synthetic data from STEP 17 validation
2. Run data through FULL crawler pipeline (fetch → parse → normalize → identity graph)
3. Verify identical graph structure to STEP 17
4. Confirm no listings collection writes (only identity graph collections)

Expected results (same as STEP 17):
- 2 phone identities
- 3 agent profiles (Ahmet Yılmaz, Mehmet Yılmaz, Ahmet Demir)
- 4 offices
- 3 location history records
- 3 office association records (Kadıköy→Üsküdar move + office change)
- 7 source evidence records
"""

import asyncio
from datetime import datetime
from pymongo import MongoClient
from typing import Dict, Any

from src.core.logger import setup_logger
from src.adapters.sahibinden.parser import SahibindenParser
from src.core.crawler_core import Crawler

logger = setup_logger(__name__)


# Synthetic normalized data (reuse from STEP 17)
SYNTHETIC_OBSERVATIONS = [
    # Observation 1: Ahmet Yılmaz in Kadıköy
    {
        "url": "https://sahibinden.com/listing1",
        "source": "sahibinden",
        "confidence": "high",
        "timestamp": datetime(2024, 1, 15, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Ahmet Yılmaz",
                "office_name": "Yılmaz Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Kadıköy",
            },
            "confidence": "high",
        },
    },
    # Observation 2: Same phone, same name, same location (no change)
    {
        "url": "https://sahibinden.com/listing2",
        "source": "sahibinden",
        "confidence": "high",
        "timestamp": datetime(2024, 1, 16, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Ahmet Yılmaz",
                "office_name": "Yılmaz Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Kadıköy",
            },
            "confidence": "high",
        },
    },
    # Observation 3: Same phone, DIFFERENT name (Mehmet) - append profile
    {
        "url": "https://sahibinden.com/listing3",
        "source": "sahibinden",
        "confidence": "medium",
        "timestamp": datetime(2024, 1, 17, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Mehmet Yılmaz",
                "office_name": "Yılmaz Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Kadıköy",
            },
            "confidence": "medium",
        },
    },
    # Observation 4: Same phone, moved to Üsküdar (close old location)
    {
        "url": "https://sahibinden.com/listing4",
        "source": "sahibinden",
        "confidence": "high",
        "timestamp": datetime(2024, 2, 1, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Ahmet Yılmaz",
                "office_name": "Yılmaz Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Üsküdar",
            },
            "confidence": "high",
        },
    },
    # Observation 5: Same phone, Üsküdar, NEW office (close old office)
    {
        "url": "https://sahibinden.com/listing5",
        "source": "sahibinden",
        "confidence": "high",
        "timestamp": datetime(2024, 2, 10, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Ahmet Yılmaz",
                "office_name": "Yeni Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Üsküdar",
            },
            "confidence": "high",
        },
    },
    # Observation 6: Hepsiemlak confirms Ahmet Yılmaz (boost confidence)
    {
        "url": "https://hepsiemlak.com/listing1",
        "source": "hepsiemlak",
        "confidence": "high",
        "timestamp": datetime(2024, 2, 15, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905551234567",
                "agent_name": "Ahmet Yılmaz",
                "office_name": "Yeni Emlak",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Üsküdar",
            },
            "confidence": "high",
        },
    },
    # Observation 7: DIFFERENT phone, different agent
    {
        "url": "https://sahibinden.com/listing6",
        "source": "sahibinden",
        "confidence": "high",
        "timestamp": datetime(2024, 2, 20, 10, 0, 0),
        "normalized_data": {
            "agent": {
                "phone_number": "+905559876543",
                "agent_name": "Ahmet Demir",
                "office_name": "Demir Gayrimenkul",
            },
            "listing": {
                "city": "İstanbul",
                "district": "Beşiktaş",
            },
            "confidence": "high",
        },
    },
]


class MockFetcher:
    """Mock fetcher that returns empty HTML (we already have normalized data)."""
    
    async def connect(self):
        """Initialize connection."""
        pass
    
    async def fetch(self, url: str) -> str:
        """Return empty HTML since we're bypassing parse step."""
        return "<html></html>"
    
    async def disconnect(self):
        """Cleanup."""
        pass
    
    async def close(self):
        """Cleanup."""
        pass


class MockParser:
    """Mock parser that returns minimal valid dict including URL."""
    
    def parse_listing_page(self, html: str, url: str) -> Dict[str, Any]:
        """Return minimal dict to pass parser validation, including URL."""
        # Return minimal structure with URL so MockNormalizer can look it up
        return {
            "agent": {},
            "listing": {"url": url}
        }


class MockNormalizer:
    """Mock normalizer that looks up pre-prepared normalized data."""
    
    def __init__(self, observations: list):
        """Store mapping of URL → normalized data."""
        self.data_map = {obs["url"]: obs["normalized_data"] for obs in observations}
        logger.info(f"MockNormalizer initialized with {len(self.data_map)} URLs")
        for url in self.data_map.keys():
            logger.info(f"  - {url}")
    
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return pre-prepared normalized data based on URL in raw_data."""
        # The raw_data should contain a URL field
        url = raw_data.get("url") or raw_data.get("listing", {}).get("url")
        logger.info(f"MockNormalizer.normalize called with URL: {url}")
        
        if url in self.data_map:
            result = self.data_map[url]
            logger.info(f"  → Returning pre-prepared data with phone {result.get('agent', {}).get('phone_number')}")
            return result
        else:
            logger.warning(f"  → URL not found in data map, returning empty dict")
            return {}


async def test_step18_integration():
    """Test complete crawler → identity graph integration.
    
    This mimics STEP 17 validation but routes through crawler instead
    of calling IdentityGraphResolver directly.
    """
    # Setup MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_step18_integration"]
    
    # Clean slate
    logger.info("Dropping test database for clean slate...")
    client.drop_database("test_step18_integration")
    
    # Initialize crawler with mocked components
    logger.info("Initializing crawler with identity graph routing...")
    
    # We'll manually inject normalized data, so we need mock components
    parser = SahibindenParser()
    
    crawler = Crawler(
        parser=parser,
        mongo_uri="mongodb://localhost:27017/",
        db_name="test_step18_integration",
        run_mode="full_run",
        source="sahibinden",
        enable_quality_gates=False,  # Disable quality gates for test
    )
    
    # HACK: Replace components with mocks that return our synthetic data
    crawler.fetcher = MockFetcher()
    crawler.parser = MockParser()
    crawler.normalizer = MockNormalizer(SYNTHETIC_OBSERVATIONS)
    
    # Process all observations through crawler
    logger.info("Processing 7 synthetic observations through crawler...")
    
    urls_by_source = {}
    for obs in SYNTHETIC_OBSERVATIONS:
        source = obs["source"]
        if source not in urls_by_source:
            urls_by_source[source] = []
        urls_by_source[source].append(obs["url"])
    
    # Process sahibinden URLs
    if "sahibinden" in urls_by_source:
        crawler.source = "sahibinden"
        crawler.execution_mode = get_execution_mode("full_run", source="sahibinden")
        await crawler.run(urls_by_source["sahibinden"])
    
    # Process hepsiemlak URLs
    if "hepsiemlak" in urls_by_source:
        crawler.source = "hepsiemlak"
        crawler.execution_mode = get_execution_mode("full_run", source="hepsiemlak")
        await crawler.run(urls_by_source["hepsiemlak"])
    
    # Verify graph structure
    logger.info("\n" + "="*60)
    logger.info("VALIDATION RESULTS")
    logger.info("="*60)
    
    # 1. Phone identities
    phone_identities = list(db.phone_identities.find({}))
    logger.info(f"\n✓ Phone Identities: {len(phone_identities)}")
    for phone in phone_identities:
        logger.info(f"  - {phone['phone_e164']} (status={phone['status']}, confidence={phone['confidence_score']})")
    
    assert len(phone_identities) == 2, f"Expected 2 phones, got {len(phone_identities)}"
    
    # 2. Agent profiles
    agent_profiles = list(db.agent_profiles.find({}))
    logger.info(f"\n✓ Agent Profiles: {len(agent_profiles)}")
    for profile in agent_profiles:
        logger.info(f"  - {profile.get('name', 'N/A')} (phone={profile.get('phone_e164', 'N/A')}, first_seen={profile.get('first_seen', 'N/A')})")
    
    assert len(agent_profiles) == 3, f"Expected 3 profiles, got {len(agent_profiles)}"
    
    # 3. Offices
    offices = list(db.offices.find({}))
    logger.info(f"\n✓ Offices: {len(offices)}")
    for office in offices:
        logger.info(f"  - {office['office_name']} in {office['city']}/{office['district']}")
    
    assert len(offices) == 4, f"Expected 4 offices, got {len(offices)}"
    
    # 4. Location history
    location_history = list(db.agent_location_history.find({}))
    logger.info(f"\n✓ Location History: {len(location_history)}")
    for loc in location_history:
        status = "OPEN" if loc["end_date"] is None else "CLOSED"
        logger.info(f"  - {loc['city']}/{loc['district']} ({status})")
    
    assert len(location_history) == 3, f"Expected 3 location records, got {len(location_history)}"
    
    # 5. Office associations
    office_associations = list(db.agent_office_history.find({}))
    logger.info(f"\n✓ Office Associations: {len(office_associations)}")
    for assoc in office_associations:
        status = "OPEN" if assoc["end_date"] is None else "CLOSED"
        logger.info(f"  - Office {assoc['office_id']} ({status})")
    
    assert len(office_associations) == 4, f"Expected 4 office associations, got {len(office_associations)}"
    
    # 6. Source evidence
    evidence = list(db.source_evidence.find({}))
    logger.info(f"\n✓ Source Evidence: {len(evidence)}")
    for ev in evidence:
        logger.info(f"  - {ev['source']} @ {ev['url']}")
    
    assert len(evidence) == 7, f"Expected 7 evidence records, got {len(evidence)}"
    
    # 7. NO LISTINGS COLLECTION (critical validation)
    listings_count = db.listings.count_documents({})
    logger.info(f"\n✓ Listings Collection: {listings_count} (MUST BE 0)")
    
    assert listings_count == 0, f"Expected 0 listings (identity graph only), got {listings_count}"
    
    logger.info("\n" + "="*60)
    logger.info("✅ ALL VALIDATIONS PASSED")
    logger.info("="*60)
    logger.info("\nIntegration successful:")
    logger.info("- Crawler routes ALL writes through identity graph")
    logger.info("- No direct MongoDB writes from crawler")
    logger.info("- Graph structure matches STEP 17 expectations")
    logger.info("- Phone-centric model working correctly")
    
    # Cleanup
    await crawler.fetcher.close()
    client.close()


if __name__ == "__main__":
    from src.core.crawler_modes import get_execution_mode
    asyncio.run(test_step18_integration())
