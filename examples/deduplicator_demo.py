"""Deduplicator Demo - Example usage of entity deduplication & resolution.

This script demonstrates how to use the Deduplicator to detect duplicate
offices, agents, and listings from normalized data.

The deduplicator uses deterministic, key-based matching:
- Office: office_name + phone_number
- Agent: agent_name + phone_number
- Listing: listing_url

Missing keys cannot be deduplicated and are always treated as new.

Usage:
    python examples/deduplicator_demo.py
"""

from src.core.deduplicator import Deduplicator


# ============================================================================
# NORMALIZED DATA EXAMPLES
# ============================================================================

# Example 1: Complete office listing with all contact info (high confidence)
OFFICE_LISTING_1 = {
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Kadıköy',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456',
    'source': 'sahibinden',
    'confidence': 'high'
}

# Example 2: Same office and agent (duplicate)
OFFICE_LISTING_1_DUPLICATE = {
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Beşiktaş',  # Different location, same office+agent+phone
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-999999',
    'source': 'sahibinden',
    'confidence': 'high'
}

# Example 3: Private seller with minimal contact info
PRIVATE_SELLER = {
    'office_name': None,
    'agent_name': 'MEHMET DEMIR',
    'phone_number': '+905558889900',
    'city': 'Ankara',
    'district': 'Çankaya',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-12345',
    'source': 'sahibinden',
    'confidence': 'medium'
}

# Example 4: Same private seller (duplicate agent)
PRIVATE_SELLER_DUPLICATE = {
    'office_name': None,
    'agent_name': 'MEHMET DEMIR',
    'phone_number': '+905558889900',  # Same phone
    'city': 'Ankara',
    'district': 'Kızılcaahamam',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-67890',
    'source': 'sahibinden',
    'confidence': 'medium'
}

# Example 5: Different agent, same phone (new agent)
DIFFERENT_AGENT_SAME_PHONE = {
    'office_name': None,
    'agent_name': 'FATMA KAPLAN',
    'phone_number': '+905321234567',  # Different person, but same phone as office
    'city': 'İstanbul',
    'district': 'Pendik',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-istanbul-pendik-11111',
    'source': 'sahibinden',
    'confidence': 'medium'
}

# Example 6: Very incomplete listing (missing office and agent)
INCOMPLETE_LISTING = {
    'office_name': None,
    'agent_name': None,
    'phone_number': None,
    'city': 'İzmir',
    'district': 'Alsancak',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-izmir-77777',
    'source': 'sahibinden',
    'confidence': 'low'
}

# Example 7: Another incomplete listing (cannot deduplicate office/agent)
INCOMPLETE_LISTING_2 = {
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': None,  # Missing agent name
    'phone_number': '+905321234567',
    'city': 'Bursa',
    'district': 'Nilüfer',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-bursa-88888',
    'source': 'sahibinden',
    'confidence': 'low'
}

# Example 8: Hepsiemlak listing (different URL)
HEPSIEMLAK_LISTING = {
    'office_name': 'PREMIUM EMLAK',
    'agent_name': 'ALI DEMIR',
    'phone_number': '+905321111111',
    'city': 'Antalya',
    'district': 'Kemer',
    'listing_url': 'https://www.hepsiemlak.com/ilan/antalya-kemer-789',
    'source': 'hepsiemlak',
    'confidence': 'high'
}


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_entity(label: str, entity: dict):
    """Print entity details."""
    print(f"📋 {label}")
    print(f"   Office: {entity.get('office_name')}")
    print(f"   Agent: {entity.get('agent_name')}")
    print(f"   Phone: {entity.get('phone_number')}")
    print(f"   Location: {entity.get('city')}, {entity.get('district')}")
    print(f"   URL: {entity.get('listing_url')[:50]}...")
    print()


def print_result(result, entity_type: str, label: str):
    """Print deduplication result."""
    status = "✓ DUPLICATE" if not result.is_new else "✓ NEW"
    print(f"   {status:15} | {label:30} | {result.reason}")


def demo_listing_deduplication():
    """Demonstrate listing deduplication by URL."""
    print_section("LISTING DEDUPLICATION (by URL)")
    
    dedup = Deduplicator()
    
    # Scenario 1: New listing
    print("1️⃣  First listing (new)")
    result = dedup.check_listing(OFFICE_LISTING_1)
    print_result(result, "Listing", "www.sahibinden.com/.../123456")
    
    # Register it
    dedup.add_listing(OFFICE_LISTING_1['listing_url'])
    
    # Scenario 2: Same listing again (duplicate)
    print("\n2️⃣  Same listing URL again (duplicate)")
    result = dedup.check_listing(OFFICE_LISTING_1)
    print_result(result, "Listing", "www.sahibinden.com/.../123456")
    
    # Scenario 3: Different listing
    print("\n3️⃣  Different listing URL (new)")
    result = dedup.check_listing(HEPSIEMLAK_LISTING)
    print_result(result, "Listing", "www.hepsiemlak.com/.../789")
    
    # Scenario 4: Missing URL
    print("\n4️⃣  Missing listing URL (cannot deduplicate → new)")
    incomplete = {'office_name': 'Test'}  # No URL
    result = dedup.check_listing(incomplete)
    print_result(result, "Listing", "(no URL)")
    
    stats = dedup.stats()
    print(f"\n📊 Stats: {stats}")


def demo_office_deduplication():
    """Demonstrate office deduplication by name + phone."""
    print_section("OFFICE DEDUPLICATION (by name + phone)")
    
    dedup = Deduplicator()
    
    # Scenario 1: New office
    print("1️⃣  First office (new)")
    result = dedup.check_office(OFFICE_LISTING_1)
    print_result(result, "Office", "EV GAYRIMENKUL + 0532...")
    
    # Register it
    dedup.add_office(
        OFFICE_LISTING_1['office_name'],
        OFFICE_LISTING_1['phone_number']
    )
    
    # Scenario 2: Same office, different listing
    print("\n2️⃣  Same office & phone, different location/listing (duplicate)")
    result = dedup.check_office(OFFICE_LISTING_1_DUPLICATE)
    print_result(result, "Office", "EV GAYRIMENKUL + 0532...")
    
    # Scenario 3: Different office
    print("\n3️⃣  Different office (new)")
    result = dedup.check_office(HEPSIEMLAK_LISTING)
    print_result(result, "Office", "PREMIUM EMLAK + 0532...")
    
    # Scenario 4: Missing office name
    print("\n4️⃣  Missing office name (cannot deduplicate → new)")
    result = dedup.check_office(PRIVATE_SELLER)
    print_result(result, "Office", "(no name) + 0555...")
    
    # Scenario 5: Missing phone
    print("\n5️⃣  Office name but missing phone (cannot deduplicate → new)")
    result = dedup.check_office(INCOMPLETE_LISTING_2)
    print_result(result, "Office", "EV GAYRIMENKUL + (no phone)")
    
    stats = dedup.stats()
    print(f"\n📊 Stats: {stats}")


def demo_agent_deduplication():
    """Demonstrate agent deduplication by name + phone."""
    print_section("AGENT DEDUPLICATION (by name + phone)")
    
    dedup = Deduplicator()
    
    # Scenario 1: New agent
    print("1️⃣  First agent (new)")
    result = dedup.check_agent(OFFICE_LISTING_1)
    print_result(result, "Agent", "AHMET YILMAZ + 0532...")
    
    # Register it
    dedup.add_agent(
        OFFICE_LISTING_1['agent_name'],
        OFFICE_LISTING_1['phone_number']
    )
    
    # Scenario 2: Same agent, different listing
    print("\n2️⃣  Same agent & phone, different listing (duplicate)")
    result = dedup.check_agent(OFFICE_LISTING_1_DUPLICATE)
    print_result(result, "Agent", "AHMET YILMAZ + 0532...")
    
    # Scenario 3: Different agent
    print("\n3️⃣  Different agent (new)")
    result = dedup.check_agent(PRIVATE_SELLER)
    print_result(result, "Agent", "MEHMET DEMIR + 0555...")
    
    # Scenario 4: Same phone, different agent name
    print("\n4️⃣  Different agent name, but same phone (NEW - different person)")
    result = dedup.check_agent(DIFFERENT_AGENT_SAME_PHONE)
    print_result(result, "Agent", "FATMA KAPLAN + 0532...")
    
    # Scenario 5: Missing agent name
    print("\n5️⃣  Missing agent name (cannot deduplicate → new)")
    result = dedup.check_agent(INCOMPLETE_LISTING)
    print_result(result, "Agent", "(no name) + (no phone)")
    
    stats = dedup.stats()
    print(f"\n📊 Stats: {stats}")


def demo_full_workflow():
    """Demonstrate full deduplication workflow with multiple entities."""
    print_section("FULL WORKFLOW: Processing Multiple Listings")
    
    dedup = Deduplicator()
    
    listings = [
        ("1. Office listing (complete)", OFFICE_LISTING_1),
        ("2. Private seller (agent only)", PRIVATE_SELLER),
        ("3. Office duplicate (same office)", OFFICE_LISTING_1_DUPLICATE),
        ("4. Agent duplicate", PRIVATE_SELLER_DUPLICATE),
        ("5. Incomplete listing", INCOMPLETE_LISTING),
        ("6. Different office", HEPSIEMLAK_LISTING),
    ]
    
    for i, (label, entity) in enumerate(listings, 1):
        print(f"{i}. Processing: {label}")
        print("-" * 80)
        
        # Check listing
        listing_result = dedup.check_listing(entity)
        print(f"   Listing  | {'NEW' if listing_result.is_new else 'DUPLICATE':9} | {listing_result.reason}")
        if listing_result.is_new and listing_result.dedupe_key:
            dedup.add_listing(listing_result.dedupe_key)
        
        # Check office
        office_result = dedup.check_office(entity)
        print(f"   Office   | {'NEW' if office_result.is_new else 'DUPLICATE':9} | {office_result.reason}")
        if office_result.is_new and office_result.dedupe_key:
            parts = office_result.dedupe_key.split('#')
            if len(parts) == 2:
                dedup.add_office(parts[0], parts[1])
        
        # Check agent
        agent_result = dedup.check_agent(entity)
        print(f"   Agent    | {'NEW' if agent_result.is_new else 'DUPLICATE':9} | {agent_result.reason}")
        if agent_result.is_new and agent_result.dedupe_key:
            parts = agent_result.dedupe_key.split('#')
            if len(parts) == 2:
                dedup.add_agent(parts[0], parts[1])
        
        print()
    
    stats = dedup.stats()
    print("=" * 80)
    print(f"📊 FINAL STATS")
    print(f"   Listings: {stats['listings']}")
    print(f"   Offices: {stats['offices']}")
    print(f"   Agents: {stats['agents']}")
    print("=" * 80)


def demo_batch_loading():
    """Demonstrate loading multiple entities at once."""
    print_section("BATCH LOADING: Loading Multiple Entities")
    
    dedup = Deduplicator()
    
    # Start with some existing entities
    existing_entities = [
        OFFICE_LISTING_1,
        PRIVATE_SELLER,
        HEPSIEMLAK_LISTING,
    ]
    
    print("Loading 3 existing entities...")
    dedup.load_entities(existing_entities)
    
    stats = dedup.stats()
    print(f"\n📊 After loading:")
    print(f"   Listings: {stats['listings']}")
    print(f"   Offices: {stats['offices']}")
    print(f"   Agents: {stats['agents']}")
    
    # Now test if new ones are duplicates
    print(f"\nChecking if duplicates are detected:")
    print("-" * 80)
    
    result = dedup.check_listing(OFFICE_LISTING_1_DUPLICATE)
    print(f"   Listing duplicate: {not result.is_new} ✓" if not result.is_new else f"   Listing duplicate: {not result.is_new} ✗")
    
    result = dedup.check_office(OFFICE_LISTING_1_DUPLICATE)
    print(f"   Office duplicate: {not result.is_new} ✓" if not result.is_new else f"   Office duplicate: {not result.is_new} ✗")
    
    result = dedup.check_agent(OFFICE_LISTING_1_DUPLICATE)
    print(f"   Agent duplicate: {not result.is_new} ✓" if not result.is_new else f"   Agent duplicate: {not result.is_new} ✗")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "DEDUPLICATOR DEMO - Entity Deduplication & Resolution".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demo_listing_deduplication()
    demo_office_deduplication()
    demo_agent_deduplication()
    demo_full_workflow()
    demo_batch_loading()
    
    print("\n✅ Demo complete!\n")


if __name__ == '__main__':
    main()
